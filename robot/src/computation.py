'''
MIT License

Copyright (c) 2026 HES-SO Valais-Wallis, Engineering Track 304
'''

import json
import logging

import matplotlib.pyplot as plt
import numpy as np
from pybullet_planning import plan_joint_motion
from URBasic import TCP6D, Joint6D

from src.segment import JointSegment, MotionType, SideType
from src.config import *
from src.utils import *
from src.kinematics import get_fk

log = logging.getLogger(__name__)

def _hover_tcp(surface_tcp, hover_offset=None):
    if hover_offset is None:
        hover_offset = HOVER_OFFSET

    tcp_list = [surface_tcp.x, surface_tcp.y, surface_tcp.z,
                surface_tcp.rx, surface_tcp.ry, surface_tcp.rz]
    x_t, y_t, z_t, _, _, _ = tcp_trans(tcp_list, hover_offset)
    return TCP6D.createFromMetersRadians(
        x_t, y_t, z_t, surface_tcp.rx, surface_tcp.ry, surface_tcp.rz,
    )


def _validate_surface_points(checker, tcp_offset, surface_tcps, qnear=None):
    valid_checklist = []
    reasons = []
    joint_solutions = []

    for tcp in surface_tcps:
        ok, q, reason, _ = checker.validate_tcp(
            tcp_offset, tcp, qnear=qnear, check_obstacle=False,
            orientation_search=True, check_joint_jump=False,
        )
        valid_checklist.append(ok)
        reasons.append(reason)
        joint_solutions.append(q)
        if ok:
            qnear = q

    return valid_checklist, reasons, joint_solutions


def _split_into_runs(valid_checklist):
    runs = []
    start = None
    for i, v in enumerate(valid_checklist):
        if v and start is None:
            start = i
        elif not v and start is not None:
            runs.append((start, i - 1))
            start = None
    if start is not None:
        runs.append((start, len(valid_checklist) - 1))
    return runs


def _find_valid_hover(checker, tcp_offset, run_surface, surface_joints,
                      from_end, hover_offset=None, qnear_override=None):
    n = len(run_surface)
    indices = range(n - 1, -1, -1) if from_end else range(n)

    for trim, i in enumerate(indices):
        h_tcp = _hover_tcp(run_surface[i], hover_offset)
        qnear = qnear_override if qnear_override is not None else (surface_joints[i] if surface_joints is not None else None)
        ok, q, reason, h_used = checker.validate_tcp(
            tcp_offset, h_tcp, qnear=qnear,
            check_obstacle=True, orientation_search=True, check_joint_jump=False,
        )
        if ok:
            return h_used, q, trim
    return None, None, n

def load_traces(json_path):
    """Load trace JSON and normalize v1 → v2 format.

    Returns (traces, data) where traces is the normalized list
    and data is the full parsed dict
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    traces = data["traces"]

    # Legacy usage: Normalize v1 -> v2: spread face normal to each waypoint
    for trace in traces:
        if "face" in trace:
            trace["path"] = [[pt, trace["face"]] for pt in trace["path"]]

    return traces, data


def assemble_segments(tcp_offset, checker, validated_runs, surface_joints_per_trace, home,
                      surface_tcps_per_trace=None, default_normals_per_trace=None):
    print("\nAssembling segments...")

    segments = []
    current_joints = home
    current_label = "HOME"
    home_tcp = get_fk(home, tcp_offset)
    prev_h_exit = home_tcp

    for run_i, (trace_i, run_start, run_end, h_entry, h_exit, run_surface, q_entry, q_exit) in enumerate(validated_runs):
        entry_label = f"Run{run_i} hover-entry"
        exit_label = f"Run{run_i} hover-exit"
        trace_surface_joints = surface_joints_per_trace[trace_i]
        trace_surface_tcps = surface_tcps_per_trace[trace_i] if surface_tcps_per_trace else None
        trace_normals = default_normals_per_trace[trace_i] if default_normals_per_trace else None

        print(f"\n  [{current_label}] -> [{entry_label}]")
        segments.append(JointSegment(
            motion_type=MotionType.TRAVEL,
            color=1,
            side=SideType.LEFT,
            v=TRAVEL_V, a=TRAVEL_A,
            waypoints=[current_joints, q_entry],
            tcp_waypoints=[prev_h_exit, h_entry],
        ))
        print(f"    TRAVEL placeholder (2 wps)")

        print(f"  [{entry_label}] -> [Run{run_i} surface[0]]")
        approach_down_tcps = None
        if trace_surface_tcps is not None:
            approach_down_tcps = [h_entry, trace_surface_tcps[run_start]]
        segments.append(JointSegment(
            motion_type=MotionType.APPROACH,
            color=1,
            side=SideType.LEFT,
            waypoints=[q_entry, trace_surface_joints[run_start]],
            v=APPROACH_V, a=APPROACH_A,
            tcp_waypoints=approach_down_tcps,
        ))
        print(f"    APPROACH down OK")

        print(f"  [Run{run_i} surface[0]] -> [Run{run_i} surface[{len(run_surface)-1}]]")
        draw_tcps = trace_surface_tcps[run_start:run_end + 1] if trace_surface_tcps else None
        draw_normals = trace_normals[run_start:run_end + 1] if trace_normals else None
        segments.append(JointSegment(
            motion_type=MotionType.DRAW,
            color=1,
            side=SideType.LEFT,
            waypoints=trace_surface_joints[run_start:run_end + 1],
            v=DRAW_V, a=DRAW_A,
            tcp_waypoints=draw_tcps,
            default_normals=draw_normals,
        ))
        print(f"    DRAW OK ({len(run_surface)} pts)")

        print(f"  [Run{run_i} surface[{len(run_surface)-1}]] -> [{exit_label}]")
        approach_up_tcps = None
        if trace_surface_tcps is not None:
            approach_up_tcps = [trace_surface_tcps[run_end], h_exit]
        segments.append(JointSegment(
            motion_type=MotionType.APPROACH,
            color=1,
            side=SideType.LEFT,
            waypoints=[trace_surface_joints[run_end], q_exit],
            v=APPROACH_V, a=APPROACH_A,
            tcp_waypoints=approach_up_tcps,
        ))
        print(f"    APPROACH up OK")

        current_joints = q_exit
        current_label = exit_label
        prev_h_exit = h_exit

    print(f"\n  [{current_label}] -> [HOME]")
    segments.append(JointSegment(
        motion_type=MotionType.TRAVEL,
        color=1,
        side=SideType.LEFT,
        waypoints=[current_joints, home],
        v=TRAVEL_V, a=TRAVEL_A,
        tcp_waypoints=[prev_h_exit, home_tcp],
    ))
    print(f"    TRAVEL placeholder (2 wps)")

    print_segment_summary(segments)
    return segments


def print_segment_summary(segments):
    travel_count = sum(1 for s in segments if s.motion_type == MotionType.TRAVEL)
    approach_count = sum(1 for s in segments if s.motion_type == MotionType.APPROACH)
    draw_count = sum(1 for s in segments if s.motion_type == MotionType.DRAW)
    total_wps = sum(len(s.waypoints) for s in segments)
    print(f"\nPlan: {len(segments)} segments ({travel_count} TRAVEL, {approach_count} APPROACH, "
          f"{draw_count} DRAW), {total_wps} total waypoints")

    print(f"\nJoint plan:")
    for i, seg in enumerate(segments):
        n_joints = len(seg.waypoints) if seg.waypoints else 0
        print(f"  Segment {i}: {seg.motion_type.name:8s} - {n_joints:3d} joint waypoints")


def plan_travels(checker, segments):
    print("\nPlanning TRAVEL segments...")

    for seg_i, seg in enumerate(segments):
        if seg.motion_type != MotionType.TRAVEL:
            continue

        start_conf = seg.waypoints[0].toList()
        end_conf = seg.waypoints[-1].toList()

        checker.set_joint_angles(start_conf)
        path = plan_joint_motion(
            checker.robot_id, checker.joint_indices, end_conf,
            obstacles=checker.obstacle_ids,
            self_collisions=True,
            resolutions=[0.02, 0.02, 0.02, 0.02, 0.02, 0.02],
            # weights=[0.5, 0.5, 0.5, 1, 0.1, 0.1]
        )

        if path is not None:
            path = simplify_path(path)
            seg.waypoints = [Joint6D.createFromRadians(*conf) for conf in path]
            print(f"  Segment {seg_i}: TRAVEL planned ({len(seg.waypoints)} wps)")
        else:
            print(f"  Segment {seg_i}: TRAVEL FAILED (keeping placeholder)")


def simplify_path(path, tolerance=0.05):
    if len(path) <= 2:
        return path

    keep = [0]

    for i in range(1, len(path) - 1):
        a = np.array(path[keep[-1]])
        b = np.array(path[i])
        c = np.array(path[i + 1])

        t = np.dot(b - a, c - a) / max(np.dot(c - a, c - a), 1e-10)
        t = np.clip(t, 0, 1)
        projected = a + t * (c - a)

        if np.linalg.norm(b - projected) > tolerance:
            keep.append(i)

    keep.append(len(path) - 1)
    return [path[i] for i in keep]


def smoothing(tcp_offset, checker, segments, home):

    qnear = home
    total_updated = 0
    total_failed = 0

    for seg_i, seg in enumerate(segments):
        if seg.tcp_waypoints is None:
            if seg.waypoints:
                qnear = seg.waypoints[-1]
            continue

        seg_failed = 0
        new_waypoints = []
        for wp_i, tcp in enumerate(seg.tcp_waypoints):
            check_obs = seg.motion_type == MotionType.TRAVEL
            ok, q, reason, _ = checker.validate_tcp(
                tcp_offset, tcp, qnear=qnear, orientation_search=True,
                check_obstacle=check_obs, find_all=False,
            )
            if ok:
                new_waypoints.append(q)
                qnear = q
                total_updated += 1
            else:
                # Keep original joint if re-solve fails
                if seg.waypoints and wp_i < len(seg.waypoints):
                    original_q = seg.waypoints[wp_i]
                    new_waypoints.append(original_q)
                    # Check what's wrong with the original too
                    checker.set_joint_angles(original_q.toList())
                    orig_self = checker.in_self_collision()
                    orig_obs = checker.in_obstacle_collision()
                    qnear_list = [f"{v:+.4f}" for v in qnear.toList()]
                    orig_list = [f"{v:+.4f}" for v in original_q.toList()]
                    print(f"  Smoothing FAIL: seg {seg_i} ({seg.motion_type.name}) wp {wp_i}/{len(seg.tcp_waypoints)}")
                    print(f"    TCP:    ({tcp.x:.4f}, {tcp.y:.4f}, {tcp.z:.4f})")
                    print(f"    Reason: {reason}")
                    print(f"    qnear:  [{', '.join(qnear_list)}]")
                    print(f"    orig_q: [{', '.join(orig_list)}]")
                    print(f"    orig self-col: {orig_self}, orig obs-col: {orig_obs}")
                    qnear = original_q
                total_failed += 1
                seg_failed += 1

        seg.waypoints = new_waypoints
        if seg_failed:
            print(f"  Segment {seg_i} ({seg.motion_type.name}): {seg_failed}/{len(seg.tcp_waypoints)} failed")

        seg.waypoints = new_waypoints

    print(f"\nSmoothing done: {total_updated} updated, {total_failed} kept original")

def plot_joint_plan(segments, save_path):
    COLORS = {
        MotionType.TRAVEL: "blue",
        MotionType.APPROACH: "orange",
        MotionType.DRAW: "green",
    }

    fig, axes = plt.subplots(6, 1, figsize=(14, 10), sharex=True)
    fig.suptitle("Joint Plan")

    global_min = float("inf")
    global_max = float("-inf")

    for seg in segments:
        for wp in seg.waypoints:
            vals = wp.toList()
            for v in vals:
                if v < global_min:
                    global_min = v
                if v > global_max:
                    global_max = v

    padding = (global_max - global_min) * 0.05

    legend_added = set()
    wp_index = 0
    prev_wp = None

    for seg in segments:
        n = len(seg.waypoints)
        if n == 0:
            continue

        x = list(range(wp_index, wp_index + n))
        joints = [wp.toList() for wp in seg.waypoints]

        if prev_wp is not None:
            x = [wp_index - 1] + x
            joints = [prev_wp] + joints

        color = COLORS[seg.motion_type]
        label = seg.motion_type.name if seg.motion_type not in legend_added else None
        legend_added.add(seg.motion_type)

        for j in range(6):
            values = [joints[k][j] for k in range(len(joints))]
            axes[j].plot(x, values, color=color, label=label if j == 0 else None, linewidth=1)

        prev_wp = seg.waypoints[-1].toList()
        wp_index += n

    for j in range(6):
        axes[j].set_ylabel(f"J{j+1} (rad)")
        axes[j].set_ylim(global_min - padding, global_max + padding)
        axes[j].grid(True, alpha=0.3)

    axes[5].set_xlabel("Waypoint index")
    axes[0].legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    plt.close()
    print(f"Joint plan plot saved to {save_path}")



def _normal_from_tcp(tcp):
    from scipy.spatial.transform import Rotation
    return -Rotation.from_rotvec([tcp.rx, tcp.ry, tcp.rz]).as_matrix()[:, 2]


def _compute_normal_diffs(segments, use_joints=False, tcp_offset=None):
    all_x = []
    all_angles = []
    all_types = []
    wp_index = 0

    for seg in segments:
        if use_joints:
            if seg.waypoints is None or len(seg.waypoints) < 2:
                if seg.waypoints:
                    wp_index += len(seg.waypoints)
                continue
            tcps = [get_fk(q, tcp_offset) for q in seg.waypoints]
        else:
            if seg.tcp_waypoints is None or len(seg.tcp_waypoints) < 2:
                if seg.waypoints:
                    wp_index += len(seg.waypoints)
                continue
            tcps = seg.tcp_waypoints

        angles = []
        for i in range(1, len(tcps)):
            prev_n = _normal_from_tcp(tcps[i - 1])
            curr_n = _normal_from_tcp(tcps[i])
            dot = np.dot(prev_n, curr_n) / (np.linalg.norm(prev_n) * np.linalg.norm(curr_n))
            angles.append(np.degrees(np.arccos(np.clip(dot, -1, 1))))

        x = list(range(wp_index + 1, wp_index + len(tcps)))
        all_x.append(x)
        all_angles.append(angles)
        all_types.append(seg.motion_type)
        wp_index += len(tcps)

    return all_x, all_angles, all_types


def _plot_normal_diffs_on_ax(ax, all_x, all_angles, all_types, title):
    COLORS = {
        MotionType.TRAVEL: "blue",
        MotionType.APPROACH: "orange",
        MotionType.DRAW: "green",
    }
    legend_added = set()
    for x, angles, mtype in zip(all_x, all_angles, all_types):
        color = COLORS[mtype]
        label = mtype.name if mtype not in legend_added else None
        legend_added.add(mtype)
        ax.plot(x, angles, color=color, label=label, linewidth=1, marker='.', markersize=2)

    all_flat = []
    for angles in all_angles:
        all_flat.extend(angles)

    if all_flat:
        mean_val = np.mean(all_flat)
        median_val = np.median(all_flat)
        max_val = np.max(all_flat)
        above_5 = sum(1 for a in all_flat if a > 5)

        stats = f"mean={mean_val:.2f}  median={median_val:.2f}  max={max_val:.2f}  >5deg={above_5}/{len(all_flat)}"
        ax.text(0.01, 0.95, stats, transform=ax.transAxes, fontsize=8, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        print(f"  {title}: {stats}")

    ax.set_title(title)
    ax.set_ylabel("Angle diff (degrees)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)


def plot_normal_diff(segments, save_path, tcp_offset=None):
    before_x, before_angles, before_types = _compute_normal_diffs(segments, use_joints=False)

    if tcp_offset is not None:
        after_x, after_angles, after_types = _compute_normal_diffs(segments, use_joints=True, tcp_offset=tcp_offset)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
        _plot_normal_diffs_on_ax(ax1, before_x, before_angles, before_types, "Before smoothing")
        _plot_normal_diffs_on_ax(ax2, after_x, after_angles, after_types, "After smoothing")
        ax2.set_xlabel("Waypoint index")
    else:
        fig, ax1 = plt.subplots(figsize=(14, 4))
        _plot_normal_diffs_on_ax(ax1, before_x, before_angles, before_types, "Normal difference between consecutive waypoints")
        ax1.set_xlabel("Waypoint index")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    plt.close()
    print(f"Normal diff plot saved to {save_path}")


def correct_bottom_values(waypoints):

    for waypoint in waypoints:

        if waypoint[2] > MIN_HEIGHT_NORMAL_CORRECTION_MM:
            continue
        normal = np.array([waypoint[3], waypoint[4], waypoint[5]])
        vertical = np.array([0,0,1])

        if np.acos(np.dot(normal, vertical) / ( np.linalg.norm(normal) * np.linalg.norm(vertical)) > np.pi / 2):
            waypoint[5] = 0.0

    return waypoints

def hotfix_j6_correction(segments):

    for seg in segments:
        for waypoint in seg.waypoints:
            waypoint[5] = HOMEJ[5]

    # input("in hotfix correction")

    return segments

def add_angle_continuity(segments):
    prev_wp = None

    for seg in segments:
        if not seg.waypoints:
            continue
        for waypoint in seg.waypoints:
            if prev_wp is not None:
                for j in range(6):
                    while waypoint[j] - prev_wp[j] > np.pi:
                        waypoint[j] -= 2 * np.pi
                    while waypoint[j] - prev_wp[j] < -np.pi:
                        waypoint[j] += 2 * np.pi
            prev_wp = waypoint

    return segments
