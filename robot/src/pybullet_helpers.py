'''
MIT License

Copyright (c) 2026 HES-SO Valais-Wallis, Engineering Track 304

Author: All pybullet animations have been created with the help from ClaudeAI (Anthropic)
'''



import colorsys
import time
import pybullet as pb
from scipy.spatial.transform import Rotation

from src.computation import _validate_surface_points, _split_into_runs, _find_valid_hover
from src.computation import MotionType
from src.kinematics import get_fk
from src.utils import fmt_tcp

RUN_COLORS = [
    [1, 1, 0],       # yellow
    [0, 1, 0],       # green
    [0, 0.5, 1],     # blue
    [1, 0.5, 0],     # orange
    [1, 0, 1],       # magenta
    [0, 1, 1],       # cyan
    [0.5, 1, 0],     # lime
    [1, 0.7, 0.8],   # pink
    [0.6, 0.3, 1],   # purple
    [1, 1, 0.5],     # light yellow
]

SEGMENT_COLORS = {
    MotionType.TRAVEL:   [0, 0.5, 1],
    MotionType.APPROACH: [1, 0.5, 0],
    MotionType.DRAW:     [0, 1, 0],
}


def display_transformation_points(checker, obj2robot, ds, json_socle_path):
    import json
    import numpy as np
    cid = checker.cid

    with open(json_socle_path, "r") as f:
        calibration_pts = json.load(f)["calibration"]

    for _, pt in calibration_pts.items():
        p_h = np.array([*pt, 1.0])
        p_robot = (obj2robot.T_position @ p_h)[:3]
        draw_sphere(cid, p_robot.tolist(), [0, 1, 0], radius=0.003)

    if ds.check_worldtcp():
        _, tcps = ds.load_worldtcp()
        print(tcps)
        for tcp in tcps:
            draw_sphere(cid, tcp[:3], [1, 0, 0], radius=0.003)

    print(f"Transformation points: {len(calibration_pts)} green (computed), measured in red")


def draw_sphere(cid, position, color, radius=0.0008):
    vis = pb.createVisualShape(pb.GEOM_SPHERE, radius=radius, rgbaColor=[*color, 1],
                               physicsClientId=cid)
    return pb.createMultiBody(baseMass=0, baseVisualShapeIndex=vis, basePosition=position,
                              physicsClientId=cid)


def draw_tcp_marker(cid, tcp, color, radius=0.0004):
    pos = [tcp.x, tcp.y, tcp.z]
    bid = draw_sphere(cid, pos, color, radius=radius)
    rotvec = [tcp.rx, tcp.ry, tcp.rz]
    z_axis = -Rotation.from_rotvec(rotvec).as_matrix()[:, 2]
    end = [pos[k] + z_axis[k] * 3 * radius for k in range(3)]
    pb.addUserDebugLine(pos, end, color, lineWidth=1, physicsClientId=cid)
    return bid

def clear_bodies(cid, body_ids):
    pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING, 0, physicsClientId=cid)
    for bid in body_ids:
        pb.removeBody(bid, physicsClientId=cid)
    pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING, 1, physicsClientId=cid)


def preview_traces(checker, surface_tcps_per_trace):
    cid = checker.cid
    n_traces = len(surface_tcps_per_trace)
    for trace_i, surface_pts in enumerate(surface_tcps_per_trace):
        hue = trace_i / max(n_traces, 1)
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING, 0, physicsClientId=cid)
        for idx in range(1, len(surface_pts)):
            prev_wp = surface_pts[idx - 1].toList()[:3]
            cur_wp = surface_pts[idx].toList()[:3]
            pb.addUserDebugLine(prev_wp, cur_wp, [r, g, b], lineWidth=1, physicsClientId=cid)
        pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING, 1, physicsClientId=cid)

    print(f"\nShowing {len(surface_tcps_per_trace)} traces as rainbow lines (red=first, violet=last).")
    # input("Press ENTER to continue to validation...")
    # pb.removeAllUserDebugItems(physicsClientId=cid)

def validate_surface_points(checker, tcp_offset, surface_tcps_per_trace, home):
    valid_masks_per_trace = []
    surface_joints_per_trace = []

    for trace_i, surface_pts in enumerate(surface_tcps_per_trace):
        n_pts = len(surface_pts)
        print(f"  Trace {trace_i} ({n_pts} pts): ", end="", flush=True)

        valid_mask, reasons, surface_joints = _validate_surface_points(
            checker, tcp_offset, surface_pts, previous_joint=home,
        )
        valid_masks_per_trace.append(valid_mask)
        surface_joints_per_trace.append(surface_joints)

        ok_count = sum(valid_mask)
        fail_count = n_pts - ok_count
        for i, (ok, reason) in enumerate(zip(valid_mask, reasons)):
            if not ok:
                print(f"\n    pt {i} SKIP ({reason})", end="", flush=True)
        print(f"\n    => {ok_count} OK, {fail_count} skipped")

    return valid_masks_per_trace, surface_joints_per_trace


def visualize_validation(checker, surface_tcps_per_trace, valid_masks_per_trace):
    cid = checker.cid
    sphere_ids = []

    for trace_i, (surface_pts, valid_mask) in enumerate(zip(surface_tcps_per_trace, valid_masks_per_trace)):
        pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING, 0, physicsClientId=cid)
        for wp, ok in zip(surface_pts, valid_mask):
            color = [1, 1, 0] if ok else [1, 0, 0]
            bid = draw_tcp_marker(cid, wp, color)
            sphere_ids.append(bid)
        pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING, 1, physicsClientId=cid)

    return sphere_ids

def split_into_runs(valid_masks_per_trace):
    runs_per_trace = []

    for trace_i, valid_mask in enumerate(valid_masks_per_trace):
        runs = _split_into_runs(valid_mask)
        runs_per_trace.append(runs)

        if not runs:
            print(f"  Trace {trace_i}: NO valid runs, trace will be skipped")
        else:
            gaps = []
            for j in range(len(runs) - 1):
                gaps.append(f"{runs[j][1]+1}-{runs[j+1][0]-1}")
            gap_str = f", gaps at [{', '.join(gaps)}]" if gaps else ""
            print(f"  Trace {trace_i}: {len(runs)} run(s) - {[f'{s}-{e}' for s, e in runs]}{gap_str}")

    return runs_per_trace


def visualize_runs(checker, surface_tcps_per_trace, runs_per_trace):
    cid = checker.cid
    sphere_ids = []
    global_run_idx = 0

    for trace_i, runs in enumerate(runs_per_trace):
        if not runs:
            continue
        surface_pts = surface_tcps_per_trace[trace_i]

        pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING, 0, physicsClientId=cid)
        for run_start, run_end in runs:
            color = RUN_COLORS[global_run_idx % len(RUN_COLORS)]
            run_wps = surface_pts[run_start:run_end + 1]
            for j, wp in enumerate(run_wps):
                bid = draw_tcp_marker(cid, wp, color)
                sphere_ids.append(bid)
                if j > 0:
                    prev = run_wps[j - 1].toList()[:3]
                    cur = wp.toList()[:3]
                    pb.addUserDebugLine(prev, cur, color, lineWidth=1, physicsClientId=cid)
            print(f"    Run {global_run_idx} ({run_start}-{run_end}): color {color}")
            global_run_idx += 1
        pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING, 1, physicsClientId=cid)

    return sphere_ids

# For each run search a non colliding hover point, if not , trim the run
def find_hovers(checker, tcp_offset, surface_tcps_per_trace, runs_per_trace, surface_joints_per_trace, home=None):
    cid = checker.cid
    validated_runs = []
    hover_run_idx = 0
    prev_q = home

    for trace_i, (surface_pts, runs) in enumerate(zip(surface_tcps_per_trace, runs_per_trace)):
        trace_joints = surface_joints_per_trace[trace_i]
        for run_start, run_end in runs:
            run_color = RUN_COLORS[hover_run_idx % len(RUN_COLORS)]
            run_surface = surface_pts[run_start:run_end + 1]
            run_joints = trace_joints[run_start:run_end + 1]

            print(f"  Trace {trace_i} run ({run_start}-{run_end}) entry: ", end="", flush=True)
            h_entry, q_entry, entry_trim = _find_valid_hover(
                checker, tcp_offset, run_surface, run_joints, from_end=False,
                previous_joint_override=prev_q,
            )
            if h_entry is None:
                print(f"FAILED, discarding run")
                hover_run_idx += 1
                continue
            if entry_trim:
                print(f"trimmed {entry_trim} pts, ", end="")
            print("OK", end="")

            print(f" | exit: ", end="", flush=True)
            h_exit, q_exit, exit_trim = _find_valid_hover(
                checker, tcp_offset, run_surface, run_joints, from_end=True,
            )
            if h_exit is None:
                print(f"FAILED, discarding run")
                hover_run_idx += 1
                continue
            if exit_trim:
                print(f"trimmed {exit_trim} pts, ", end="")

            trimmed_surface = run_surface[entry_trim:len(run_surface) - exit_trim]
            if not trimmed_surface:
                print(f"EMPTY (trims overlap), discarding run")
                hover_run_idx += 1
                continue

            new_run_start = run_start + entry_trim
            new_run_end = run_end - exit_trim

            print(f"OK - {len(trimmed_surface)} draw pts")

            draw_tcp_marker(cid, h_entry, run_color)
            draw_tcp_marker(cid, h_exit, run_color)

            validated_runs.append((trace_i, new_run_start, new_run_end, h_entry, h_exit, trimmed_surface, q_entry, q_exit))
            prev_q = q_exit
            hover_run_idx += 1

    print(f"\n{len(validated_runs)} run(s) ready for planning.")
    return validated_runs


def visualize_plan(checker, tcp_offset, segments, debug=True):
    cid = checker.cid

    print("\nVisualizing final plan step by step...")
    print("  TRAVEL = blue, APPROACH = orange, DRAW = green\n")

    pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING, 0, physicsClientId=cid)

    for i, seg in enumerate(segments):
        color = SEGMENT_COLORS[seg.motion_type]
        width = 3 if seg.motion_type == MotionType.DRAW else 2
        label = seg.motion_type.name
        tcp_wps = [get_fk(q, tcp_offset) for q in seg.waypoints]
        print(f"  Segment {i}: {label} ({len(tcp_wps)} wps)  "
              f"{fmt_tcp(tcp_wps[0])} -> {fmt_tcp(tcp_wps[-1])}")

        for j, tcp in enumerate(tcp_wps):
            draw_tcp_marker(cid, tcp, color)
            if j > 0:
                prev = [tcp_wps[j - 1].x, tcp_wps[j - 1].y, tcp_wps[j - 1].z]
                pos = [tcp.x, tcp.y, tcp.z]
                pb.addUserDebugLine(prev, pos, color, lineWidth=width, physicsClientId=cid)

    pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING, 1, physicsClientId=cid)

    print(f"\n  {len(segments)} segments visualized")


def animate_plan(checker, segments, delay=0.02):
    cid = checker.cid
    input("\nPress ENTER to start arm animation...")
    print("\nAnimating arm through all segments...")

    for i, seg in enumerate(segments):
        label = seg.motion_type.name
        n = len(seg.waypoints) if seg.waypoints else 0
        print(f"  Segment {i}: {label} ({n} joint waypoints)")
        if seg.waypoints:
            for jw in seg.waypoints:
                q = jw.toList() if hasattr(jw, 'toList') else list(jw)
                checker.set_joint_angles(q)
                if delay > 0:
                    time.sleep(delay)

    print("Animation complete.")