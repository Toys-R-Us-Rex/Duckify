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
from src.safety import wrapped_joint_distance

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


def _validate_surface_points(checker, tcp_offset, surface_tcps, previous_joint=None):
    valid_checklist = []
    reasons = []
    joint_solutions = []

    for tcp in surface_tcps:
        ok, joint, reason, used_tcp, solutions = checker.validate_tcp(
            tcp_offset, tcp, qnear=previous_joint, check_obstacle=False,
            orientation_search=True,
        )
        valid_checklist.append(ok)
        reasons.append(reason)
        joint_solutions.append(joint)
        if ok:
            previous_joint = joint

    return valid_checklist, reasons, joint_solutions


def _split_into_runs(valid_checklist):
    runs = []
    start = None
    for i, is_valid in enumerate(valid_checklist):
        if is_valid and start is None:
            start = i
        elif not is_valid and start is not None:
            runs.append((start, i - 1))
            start = None
    if start is not None:
        runs.append((start, len(valid_checklist) - 1))
    return runs


def _find_valid_hover(checker, tcp_offset, run_surface, surface_joints,
                      from_end, hover_offset=None, previous_joint_override=None):
    n = len(run_surface)
    indices = range(n - 1, -1, -1) if from_end else range(n)

    for trim, i in enumerate(indices):
        hover_tcp = _hover_tcp(run_surface[i], hover_offset)
        previous_joint = previous_joint_override if previous_joint_override is not None else (surface_joints[i] if surface_joints is not None else None)
        ok, joint, reason, used_tcp, solutions = checker.validate_tcp(
            tcp_offset, hover_tcp, qnear=previous_joint,
            check_obstacle=True, orientation_search=True,
        )
        if ok:
            return used_tcp, joint, trim
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


def _make_travel(from_joints, to_joints, from_tcp, to_tcp):
    return JointSegment(
        motion_type=MotionType.TRAVEL,
        color=1, side=SideType.LEFT,
        v=TRAVEL_V, a=TRAVEL_A,
        waypoints=[from_joints, to_joints],
        tcp_waypoints=[from_tcp, to_tcp],
    )


def _make_approach_down(hover_joint, surface_joint, hover_tcp=None, surface_tcp=None):
    tcp_waypoints = [hover_tcp, surface_tcp] if hover_tcp is not None else None
    return JointSegment(
        motion_type=MotionType.APPROACH,
        color=1, side=SideType.LEFT,
        v=APPROACH_V, a=APPROACH_A,
        waypoints=[hover_joint, surface_joint],
        tcp_waypoints=tcp_waypoints,
    )


def _make_draw(surface_joints, surface_tcps=None, normals=None):
    return JointSegment(
        motion_type=MotionType.DRAW,
        color=1, side=SideType.LEFT,
        v=DRAW_V, a=DRAW_A,
        waypoints=surface_joints,
        tcp_waypoints=surface_tcps,
        default_normals=normals,
    )


def _make_approach_up(surface_joint, hover_joint, surface_tcp=None, hover_tcp=None):
    tcp_waypoints = [surface_tcp, hover_tcp] if surface_tcp is not None else None
    return JointSegment(
        motion_type=MotionType.APPROACH,
        color=1, side=SideType.LEFT,
        v=APPROACH_V, a=APPROACH_A,
        waypoints=[surface_joint, hover_joint],
        tcp_waypoints=tcp_waypoints,
    )


def assemble_segments(tcp_offset, checker, validated_runs, surface_joints_per_trace, home,
                      surface_tcps_per_trace=None, default_normals_per_trace=None):
    print("\nAssembling segments...")

    segments = []
    current_joints = home
    home_tcp = get_fk(home, tcp_offset)
    previous_hover_tcp = home_tcp

    for run_i, (trace_i, run_start, run_end, hover_entry, hover_exit, run_surface, entry_joint, exit_joint) in enumerate(validated_runs):
        trace_joints = surface_joints_per_trace[trace_i]
        trace_tcps = surface_tcps_per_trace[trace_i] if surface_tcps_per_trace else None
        trace_normals = default_normals_per_trace[trace_i] if default_normals_per_trace else None

        segments.append(_make_travel(current_joints, entry_joint, previous_hover_tcp, hover_entry))

        segments.append(_make_approach_down(
            entry_joint, trace_joints[run_start],
            hover_entry, trace_tcps[run_start] if trace_tcps else None,
        ))

        draw_start = run_start + 1 if run_end - run_start >= 2 else run_start
        draw_end = run_end - 1 if run_end - run_start >= 2 else run_end
        segments.append(_make_draw(
            trace_joints[draw_start:draw_end + 1],
            trace_tcps[draw_start:draw_end + 1] if trace_tcps else None,
            trace_normals[draw_start:draw_end + 1] if trace_normals else None,
        ))

        segments.append(_make_approach_up(
            trace_joints[run_end], exit_joint,
            trace_tcps[run_end] if trace_tcps else None, hover_exit,
        ))

        current_joints = exit_joint
        previous_hover_tcp = hover_exit

    segments.append(_make_travel(current_joints, home, previous_hover_tcp, home_tcp))

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
    for i, segment in enumerate(segments):
        n_joints = len(segment.waypoints) if segment.waypoints else 0
        print(f"  Segment {i}: {segment.motion_type.name:8s} - {n_joints:3d} joint waypoints")


def plan_travels(checker, segments):
    print("\nPlanning TRAVEL segments...")

    for segment_i, segment in enumerate(segments):
        if segment.motion_type != MotionType.TRAVEL:
            continue

        start_conf = segment.waypoints[0].toList()
        end_conf = segment.waypoints[-1].toList()

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
            segment.waypoints = [Joint6D.createFromRadians(*conf) for conf in path]
            print(f"  Segment {segment_i}: TRAVEL planned ({len(segment.waypoints)} wps)")
        else:
            print(f"  Segment {segment_i}: TRAVEL FAILED (keeping placeholder)")


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

    previous_joint = home
    total_updated = 0
    total_failed = 0
    before_waypoints = []
    for segment in segments:
        if segment.waypoints:
            before_waypoints.append(list(segment.waypoints))
        else:
            before_waypoints.append([])

    for segment_i, segment in enumerate(segments):
        if segment.tcp_waypoints is None or segment.motion_type == MotionType.TRAVEL:
            if segment.waypoints:
                previous_joint = segment.waypoints[-1]
            continue

        segment_failed = 0
        new_waypoints = []
        segment.ik_solutions = []
        for waypoint_i, tcp in enumerate(segment.tcp_waypoints):
            check_obs = segment.motion_type == MotionType.TRAVEL
            check_jump = segment.motion_type in (MotionType.DRAW, MotionType.APPROACH)
            rings = 1 if segment.motion_type == MotionType.APPROACH else 0
            ok, joint, reason, used_tcp, solutions_by_step = checker.validate_tcp(
                tcp_offset, tcp, qnear=previous_joint, orientation_search=True,
                check_obstacle=check_obs, search_mode=CONE_SEARCH_MODE,
                check_joint_jump=check_jump, min_rings=rings,
            )
            segment.ik_solutions.append(solutions_by_step)
            if ok:
                if previous_joint is not None:
                    candidate_joints = np.array(joint.toList())
                    original_joints = candidate_joints.copy()
                    previous_joints = np.array(previous_joint.toList())
                    for j in range(6):
                        while candidate_joints[j] - previous_joints[j] > np.pi:
                            candidate_joints[j] -= 2 * np.pi
                        while candidate_joints[j] - previous_joints[j] < -np.pi:
                            candidate_joints[j] += 2 * np.pi
                        if abs(candidate_joints[j]) > MAX_JOINT_RANGE:
                            candidate_joints[j] = original_joints[j]
                    joint = Joint6D.createFromRadians(*candidate_joints.tolist())
                new_waypoints.append(joint)
                previous_joint = joint
                total_updated += 1
            else:
                fallback = None
                fallback_cost = float('inf')
                previous_arr = np.array(previous_joint.toList()) if previous_joint is not None else None
                for step in solutions_by_step:
                    for stored_joint, stored_reason in step:
                        if stored_reason != "":
                            continue
                        candidate_joints = np.array(stored_joint.toList())
                        if previous_arr is not None:
                            original_joints = candidate_joints.copy()
                            for j in range(6):
                                while candidate_joints[j] - previous_arr[j] > np.pi:
                                    candidate_joints[j] -= 2 * np.pi
                                while candidate_joints[j] - previous_arr[j] < -np.pi:
                                    candidate_joints[j] += 2 * np.pi
                                if abs(candidate_joints[j]) > MAX_JOINT_RANGE:
                                    candidate_joints[j] = original_joints[j]
                            cost = np.sum((candidate_joints - previous_arr) ** 2)
                        else:
                            cost = 0.0
                        if cost < fallback_cost:
                            fallback_cost = cost
                            fallback = Joint6D.createFromRadians(*candidate_joints.tolist())

                if fallback is not None:
                    print(f"  Smoothing FALLBACK: segment {segment_i} wp {waypoint_i} (closest valid, no jump check)")
                    new_waypoints.append(fallback)
                    previous_joint = fallback
                    total_updated += 1
                    continue

                if segment.waypoints and waypoint_i < len(segment.waypoints):
                    original_joint = segment.waypoints[waypoint_i]
                    new_waypoints.append(original_joint)
                    print(f"  Smoothing FAIL: segment {segment_i} ({segment.motion_type.name}) waypoint {waypoint_i}/{len(segment.tcp_waypoints)}")
                    print(f"    Reason: {reason}")
                    previous_joint = original_joint
                total_failed += 1
                segment_failed += 1

        segment.waypoints = new_waypoints
        if segment_failed:
            print(f"  Segment {segment_i} ({segment.motion_type.name}): {segment_failed}/{len(segment.tcp_waypoints)} failed")

    print(f"\nSmoothing done: {total_updated} updated, {total_failed} kept original")
    return before_waypoints

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

    for segment in segments:
        for waypoint in segment.waypoints:
            vals = waypoint.toList()
            for v in vals:
                if v < global_min:
                    global_min = v
                if v > global_max:
                    global_max = v

    padding = (global_max - global_min) * 0.05

    legend_added = set()
    waypoint_index = 0
    prev_waypoint = None

    for segment in segments:
        n = len(segment.waypoints)
        if n == 0:
            continue

        x = list(range(waypoint_index, waypoint_index + n))
        joints = [waypoint.toList() for waypoint in segment.waypoints]

        if prev_waypoint is not None:
            x = [waypoint_index - 1] + x
            joints = [prev_waypoint] + joints

        color = COLORS[segment.motion_type]
        label = segment.motion_type.name if segment.motion_type not in legend_added else None
        legend_added.add(segment.motion_type)

        for j in range(6):
            values = [joints[k][j] for k in range(len(joints))]
            axes[j].plot(x, values, color=color, label=label if j == 0 else None, linewidth=1)

        prev_waypoint = segment.waypoints[-1].toList()
        waypoint_index += n

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

def plot_smoothing_comparison(segments, before_waypoints, save_path):
    SEGMENT_COLORS = {
        MotionType.TRAVEL: "blue",
        MotionType.APPROACH: "orange",
        MotionType.DRAW: "green",
    }

    fig, axes = plt.subplots(6, 1, figsize=(14, 12), sharex=True)
    fig.suptitle("Smoothing comparison (before vs after)")

    before_x = []
    before_joints = [[] for unused in range(6)]
    after_x = []
    after_joints = [[] for unused in range(6)]
    segment_ranges = []

    wp_index = 0
    for segment_i, segment in enumerate(segments):
        if not segment.waypoints:
            continue

        n = len(segment.waypoints)
        seg_start = wp_index
        before_wps = before_waypoints[segment_i]

        for i in range(n):
            if i < len(before_wps):
                before_x.append(wp_index + i)
                vals = before_wps[i].toList() if hasattr(before_wps[i], 'toList') else list(before_wps[i])
                for j in range(6):
                    before_joints[j].append(vals[j])

            after_x.append(wp_index + i)
            vals = segment.waypoints[i].toList() if hasattr(segment.waypoints[i], 'toList') else list(segment.waypoints[i])
            for j in range(6):
                after_joints[j].append(vals[j])

        segment_ranges.append((seg_start, wp_index + n - 1, segment.motion_type))
        wp_index += n

    for j in range(6):
        ax = axes[j]
        ax.plot(before_x, before_joints[j], color="red", linewidth=1, alpha=0.7, label="Before" if j == 0 else None)
        ax.plot(after_x, after_joints[j], color="black", linewidth=1, label="After" if j == 0 else None)

        for seg_start, seg_end, mtype in segment_ranges:
            color = SEGMENT_COLORS[mtype]
            ax.axvspan(seg_start, seg_end, alpha=0.05, color=color)

        ax.set_ylabel(f"J{j+1} (rad)")
        ax.grid(True, alpha=0.3)

    legend_added = set()
    for seg_start, seg_end, mtype in segment_ranges:
        if mtype not in legend_added:
            axes[0].plot([], [], color=SEGMENT_COLORS[mtype], linewidth=4, alpha=0.3, label=mtype.name)
            legend_added.add(mtype)

    axes[0].legend(loc="upper right", fontsize=7)
    axes[5].set_xlabel("Waypoint index")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    plt.close()
    print(f"Smoothing comparison plot saved to {save_path}")


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

    for segment in segments:
        for waypoint in segment.waypoints:
            waypoint[5] = HOMEJ[5]

    return segments

def add_angle_continuity(segments):
    prev_waypoint = None

    for segment in segments:
        if not segment.waypoints:
            continue
        for waypoint in segment.waypoints:
            if prev_waypoint is not None:
                for j in range(6):
                    original = waypoint[j]
                    while waypoint[j] - prev_waypoint[j] > np.pi:
                        waypoint[j] -= 2 * np.pi
                    while waypoint[j] - prev_waypoint[j] < -np.pi:
                        waypoint[j] += 2 * np.pi
                    if abs(waypoint[j]) > MAX_JOINT_RANGE:
                        waypoint[j] = original
            prev_waypoint = waypoint

    return segments

def filterout_bottom_values(waypoints):

    filtered_waypoints = []

    for waypoint in waypoints:

        if waypoint[2] > MIN_HEIGHT_ACCEPTANCE:
            filtered_waypoints.append(waypoint)

    return filtered_waypoints
