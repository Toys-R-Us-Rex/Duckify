'''
MIT License

Copyright (c) 2026 HES-SO Valais-Wallis, Engineering Track 304

Docstrings generated with the assistance from Claude AI ( Anthropic )
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
    """
    Create a hover TCP above a surface point.

    Takes a surface TCP and moves it up along the tool axis by the hover
    offset. The orientation stays the same, only the position changes.

    Parameters
    ----------
    surface_tcp : TCP6D
        The on-surface TCP pose.
    hover_offset : list of float, optional
        6-element offset applied in tool frame. Uses HOVER_OFFSET from
        config if not given.

    Returns
    -------
    TCP6D
        The hover pose above the surface point.
    """
    if hover_offset is None:
        hover_offset = HOVER_OFFSET

    tcp_list = [surface_tcp.x, surface_tcp.y, surface_tcp.z,
                surface_tcp.rx, surface_tcp.ry, surface_tcp.rz]
    x_t, y_t, z_t, _, _, _ = tcp_trans(tcp_list, hover_offset)
    return TCP6D.createFromMetersRadians(
        x_t, y_t, z_t, surface_tcp.rx, surface_tcp.ry, surface_tcp.rz,
    )


def _validate_surface_points(checker, tcp_offset, surface_tcps, previous_joint=None):
    """
    Check which surface points are reachable by the robot.

    Goes through each TCP point, tries to find a valid IK solution with
    collision checking disabled (we only care about reachability here).
    Chains qnear from one point to the next so solutions stay consistent.

    Parameters
    ----------
    checker : CollisionChecker
        The pybullet collision checker instance.
    tcp_offset : ndarray, shape (4, 4)
        Tool offset matrix.
    surface_tcps : list of TCP6D
        Surface points to validate.
    previous_joint : Joint6D, optional
        Starting qnear for the first point.

    Returns
    -------
    valid_checklist : list of bool
        True for each reachable point, False otherwise.
    reasons : list of str
        Failure reason for each point (empty string if valid).
    joint_solutions : list of Joint6D or None
        The IK solution for each point, None if not reachable.
    """
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
    """
    Split a list of booleans into runs of consecutive True values.

    For example [True, True, False, True] gives [(0, 1), (3, 3)].
    Each run is a (start, end) tuple with inclusive indices.

    Parameters
    ----------
    valid_checklist : list of bool
        The validation results for each point.

    Returns
    -------
    list of tuple (int, int)
        Start and end indices of each consecutive valid run.
    """
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
    """
    Find a valid hover point at the start or end of a run.

    Tries each surface point (from the start or end depending on from_end)
    and checks if the hover above it is collision-free. Returns the first
    one that works, along with how many points were trimmed.

    Parameters
    ----------
    checker : CollisionChecker
        The pybullet collision checker.
    tcp_offset : ndarray, shape (4, 4)
        Tool offset matrix.
    run_surface : list of TCP6D
        The surface points in the run.
    surface_joints : list of Joint6D
        Pre-computed joint solutions for each surface point.
    from_end : bool
        If True, search from the last point backwards. Otherwise from
        the first point forward.
    hover_offset : list of float, optional
        Custom hover offset. Uses default if None.
    previous_joint_override : Joint6D, optional
        Force this as qnear instead of using surface_joints.

    Returns
    -------
    hover_tcp : TCP6D or None
        The hover pose that worked, or None if nothing was found.
    hover_joint : Joint6D or None
        Joint solution for the hover, or None.
    trim : int
        How many points were trimmed from this end to find a valid hover.
    """
    n = len(run_surface)
    if from_end:
        indices = range(n - 1, -1, -1)
    else:
        indices = range(n)

    for trim, i in enumerate(indices):
        hover_tcp = _hover_tcp(run_surface[i], hover_offset)

        if previous_joint_override is not None:
            previous_joint = previous_joint_override
        elif surface_joints is not None:
            previous_joint = surface_joints[i]
        else:
            previous_joint = None
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
            new_path = []
            for pt in trace["path"]:
                new_path.append([pt, trace["face"]])
            trace["path"] = new_path

    return traces, data


def _make_travel(from_joints, to_joints, from_tcp, to_tcp):
    """
    Create a TRAVEL segment between two joint configs.

    Travel segments are free-space moves where the pen is up. The path
    gets replaced later by the RRT planner in plan_travels().
    """
    return JointSegment(
        motion_type=MotionType.TRAVEL,
        color=1, side=SideType.LEFT,
        v=TRAVEL_V, a=TRAVEL_A,
        waypoints=[from_joints, to_joints],
        tcp_waypoints=[from_tcp, to_tcp],
    )


def _make_approach_down(hover_joint, surface_joint, hover_tcp=None, surface_tcp=None):
    """
    Create an APPROACH segment going from hover down to the surface.

    This is the pen-down motion before a draw starts.
    """
    tcp_waypoints = [hover_tcp, surface_tcp] if hover_tcp is not None else None
    return JointSegment(
        motion_type=MotionType.APPROACH,
        color=1, side=SideType.LEFT,
        v=APPROACH_V, a=APPROACH_A,
        waypoints=[hover_joint, surface_joint],
        tcp_waypoints=tcp_waypoints,
    )


def _make_draw(surface_joints, surface_tcps=None, normals=None):
    """
    Create a DRAW segment for on-surface drawing.

    The pen is on the surface and follows the waypoints at draw speed.
    """
    return JointSegment(
        motion_type=MotionType.DRAW,
        color=1, side=SideType.LEFT,
        v=DRAW_V, a=DRAW_A,
        waypoints=surface_joints,
        tcp_waypoints=surface_tcps,
        default_normals=normals,
    )


def _make_approach_up(surface_joint, hover_joint, surface_tcp=None, hover_tcp=None):
    """
    Create an APPROACH segment going from the surface up to hover.

    This is the pen-up motion after a draw is done.
    """
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
    """
    Build the full list of segments from the validated runs.

    For each run this creates: TRAVEL to hover, APPROACH down, DRAW on
    surface, APPROACH up. Also adds a TRAVEL from home to DRAWING_HOME
    at the start and a TRAVEL back to home at the end.

    The first and last surface points of each run are not duplicated in
    the DRAW segment since they are already in the APPROACH segments.

    Parameters
    ----------
    tcp_offset : ndarray, shape (4, 4)
        Tool offset matrix.
    checker : CollisionChecker
        The pybullet collision checker.
    validated_runs : list of tuple
        Each entry has (trace_i, run_start, run_end, hover_entry,
        hover_exit, run_surface, entry_joint, exit_joint).
    surface_joints_per_trace : list of list of Joint6D
        Joint solutions per trace, indexed by trace then point.
    home : Joint6D
        Home joint configuration.
    surface_tcps_per_trace : list of list of TCP6D, optional
        TCP waypoints per trace.
    default_normals_per_trace : list of list, optional
        Surface normals per trace.

    Returns
    -------
    list of JointSegment
        The full ordered list of segments for the robot to execute.
    """
    print("\nAssembling segments...")

    segments = []
    current_joints = home
    home_tcp = get_fk(home, tcp_offset)
    drawing_home_tcp = get_fk(DRAWING_HOME, tcp_offset)
    previous_hover_tcp = home_tcp

    segments.append(_make_travel(home, DRAWING_HOME, home_tcp, drawing_home_tcp))
    current_joints = DRAWING_HOME
    previous_hover_tcp = drawing_home_tcp

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
    """
    Print a summary of the segment plan to the console.

    Shows how many TRAVEL, APPROACH and DRAW segments there are,
    the total waypoint count, and details per segment.
    """
    travel_count = 0
    approach_count = 0
    draw_count = 0
    total_wps = 0
    for s in segments:
        if s.motion_type == MotionType.TRAVEL:
            travel_count += 1
        elif s.motion_type == MotionType.APPROACH:
            approach_count += 1
        elif s.motion_type == MotionType.DRAW:
            draw_count += 1
        total_wps += len(s.waypoints)
    print(f"\nPlan: {len(segments)} segments ({travel_count} TRAVEL, {approach_count} APPROACH, "
          f"{draw_count} DRAW), {total_wps} total waypoints")

    print(f"\nJoint plan:")
    for i, segment in enumerate(segments):
        n_joints = len(segment.waypoints) if segment.waypoints else 0
        print(f"  Segment {i}: {segment.motion_type.name:8s} - {n_joints:3d} joint waypoints")


def plan_travels(checker, segments):
    """
    Replace TRAVEL segment placeholders with actual collision-free paths.

    Uses the BiRRT planner from pybullet_planning to find a path between
    the start and end of each TRAVEL segment. The path gets simplified
    afterwards to remove unnecessary intermediate points.

    Parameters
    ----------
    checker : CollisionChecker
        The pybullet collision checker with loaded obstacles.
    segments : list of JointSegment
        The segment list. TRAVEL segments get their waypoints replaced
        in place.
    """
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
            waypoints = []
            for conf in path:
                waypoints.append(Joint6D.createFromRadians(*conf))
            segment.waypoints = waypoints
            print(f"  Segment {segment_i}: TRAVEL planned ({len(segment.waypoints)} wps)")
        else:
            print(f"  Segment {segment_i}: TRAVEL FAILED (keeping placeholder)")


def simplify_path(path, tolerance=0.05):
    """
    Remove unnecessary waypoints from a path.

    Walks through the path and keeps only the points that deviate from
    a straight line by more than the tolerance. First and last points
    are always kept.

    Parameters
    ----------
    path : list of list of float
        Joint configurations along the path.
    tolerance : float, optional
        Max allowed deviation before a point is kept. Default 0.05 rad.

    Returns
    -------
    list of list of float
        The simplified path with fewer waypoints.
    """
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

    simplified = []
    for i in keep:
        simplified.append(path[i])
    return simplified


def smoothing(tcp_offset, checker, segments, home):
    """
    Re-solve IK for all segments to get smoother joint trajectories.

    Goes through every waypoint that has a TCP and re-runs validate_tcp
    with the previous joint as qnear so the solutions chain nicely.
    If the normal IK fails, it tries a fallback by scanning all collected
    solutions and picking the closest valid one ignoring jump checks.

    The first and last TRAVEL segments (home and drawing_home) are
    skipped since they get path-planned separately.

    Parameters
    ----------
    tcp_offset : ndarray, shape (4, 4)
        Tool offset matrix.
    checker : CollisionChecker
        The pybullet collision checker.
    segments : list of JointSegment
        All segments. Waypoints are modified in place.
    home : Joint6D
        Home joint config, used as the initial qnear.

    Returns
    -------
    before_waypoints : list of list of Joint6D
        The original waypoints before smoothing, for comparison plots.
    """

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
        skip = (segment_i == 0 and segment.motion_type == MotionType.TRAVEL)
        skip = skip or (segment_i == len(segments) - 1 and segment.motion_type == MotionType.TRAVEL)
        if skip:
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
    """
    Plot all 6 joint values across the full segment plan.

    Each segment type (TRAVEL, APPROACH, DRAW) gets its own color.
    Saves the plot as a PNG file.

    Parameters
    ----------
    segments : list of JointSegment
        The full segment plan.
    save_path : Path or str
        Where to save the PNG.
    """
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

        joints = []
        for waypoint in segment.waypoints:
            joints.append(waypoint.toList())

        if prev_waypoint is not None:
            x = [waypoint_index - 1] + x
            joints = [prev_waypoint] + joints

        color = COLORS[segment.motion_type]
        if segment.motion_type not in legend_added:
            label = segment.motion_type.name
        else:
            label = None
        legend_added.add(segment.motion_type)

        for j in range(6):
            values = []
            for k in range(len(joints)):
                values.append(joints[k][j])
            if j == 0:
                axes[j].plot(x, values, color=color, label=label, linewidth=1)
            else:
                axes[j].plot(x, values, color=color, linewidth=1)

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
    """
    Plot a before vs after comparison of the smoothing pass.

    Shows the original joint values in red and the smoothed ones in black,
    with colored backgrounds for each segment type.

    Parameters
    ----------
    segments : list of JointSegment
        The segments after smoothing.
    before_waypoints : list of list of Joint6D
        The original waypoints before smoothing (from smoothing()).
    save_path : Path or str
        Where to save the PNG.
    """
    SEGMENT_COLORS = {
        MotionType.TRAVEL: "blue",
        MotionType.APPROACH: "orange",
        MotionType.DRAW: "green",
    }

    fig, axes = plt.subplots(6, 1, figsize=(14, 12), sharex=True)
    fig.suptitle("Smoothing comparison (before vs after)")

    before_x = []
    before_joints = [[], [], [], [], [], []]
    after_x = []
    after_joints = [[], [], [], [], [], []]
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
                if hasattr(before_wps[i], 'toList'):
                    vals = before_wps[i].toList()
                else:
                    vals = list(before_wps[i])
                for j in range(6):
                    before_joints[j].append(vals[j])

            after_x.append(wp_index + i)
            if hasattr(segment.waypoints[i], 'toList'):
                vals = segment.waypoints[i].toList()
            else:
                vals = list(segment.waypoints[i])
            for j in range(6):
                after_joints[j].append(vals[j])

        segment_ranges.append((seg_start, wp_index + n - 1, segment.motion_type))
        wp_index += n

    for j in range(6):
        ax = axes[j]
        if j == 0:
            ax.plot(before_x, before_joints[j], color="red", linewidth=1, alpha=0.7, label="Before")
            ax.plot(after_x, after_joints[j], color="black", linewidth=1, label="After")
        else:
            ax.plot(before_x, before_joints[j], color="red", linewidth=1, alpha=0.7)
            ax.plot(after_x, after_joints[j], color="black", linewidth=1)

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
    """
    Fix normals for waypoints near the bottom of the object.

    If a waypoint is below a certain height and its normal points
    downward, we zero out the Z component of the normal so the pen
    doesn't try to go through the table.

    Parameters
    ----------
    waypoints : list of list of float
        Each waypoint is [x, y, z, n1, n2, n3].

    Returns
    -------
    list of list of float
        The corrected waypoints.
    """

    for waypoint in waypoints:

        if waypoint[2] > MIN_HEIGHT_NORMAL_CORRECTION_MM:
            continue
        normal = np.array([waypoint[3], waypoint[4], waypoint[5]])
        vertical = np.array([0,0,1])

        if np.acos(np.dot(normal, vertical) / ( np.linalg.norm(normal) * np.linalg.norm(vertical)) > np.pi / 2):
            waypoint[5] = 0.0

    return waypoints

def hotfix_j6_correction(segments):
    """
    Force the 6th joint to the home value for all waypoints.

    This is a temporary fix because joint 6 sometimes drifts to weird
    values during IK. We just lock it to whatever HOMEJ has.

    Parameters
    ----------
    segments : list of JointSegment
        All segments. Waypoints are modified in place.

    Returns
    -------
    list of JointSegment
        Same segments with J6 corrected.
    """

    for segment in segments:
        for waypoint in segment.waypoints:
            waypoint[5] = HOMEJ[5]

    return segments

def add_angle_continuity(segments):
    """
    Unwrap joint angles so there are no big jumps between consecutive points.

    Walks through all waypoints across all segments and shifts each joint
    by +/- 2*pi to stay close to the previous value. If the shifted value
    goes out of the allowed range, we keep the original.

    Parameters
    ----------
    segments : list of JointSegment
        All segments. Waypoints are modified in place.

    Returns
    -------
    list of JointSegment
        Same segments with unwrapped joint angles.
    """
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
    """
    Remove waypoints that are too low (below the acceptance height).

    Points below MIN_HEIGHT_ACCEPTANCE are likely under the table or
    on the very bottom of the object, so we just drop them.

    Parameters
    ----------
    waypoints : list of list of float
        Each waypoint is [x, y, z, n1, n2, n3].

    Returns
    -------
    list of list of float
        Only the waypoints above the minimum height.
    """

    filtered_waypoints = []

    for waypoint in waypoints:

        if waypoint[2] > MIN_HEIGHT_ACCEPTANCE:
            filtered_waypoints.append(waypoint)

    return filtered_waypoints
