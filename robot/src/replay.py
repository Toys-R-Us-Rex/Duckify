"""
Author: Pierre-Yves Savioz
Co-author: Claude AI (Anthropic)
"""


import argparse
import select
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import numpy as np
import matplotlib.pyplot as plt
import pybullet as pb

from src.logger import DataStore
from src.config import OBSTACLE_STLS, HOMEJ, CONE_AZIMUTH_STEP
from src.segment import MotionType
from src.safety import setup_checker
from src.transformation import extract_pybullet_pose

MOTION_COLORS = {
    MotionType.TRAVEL: "blue",
    MotionType.APPROACH: "orange",
    MotionType.DRAW: "green",
}


def flatten_segments(joint_data):
    all_segments = []
    for side, colors in joint_data.items():
        for color, segments in colors.items():
            all_segments.extend(segments)
    return all_segments


def replay(checker, segments, delay=0.02):
    input("\nPress ENTER to start replay...")
    print("Replaying all segments...")

    for i, seg in enumerate(segments):
        label = seg.motion_type.name
        n = len(seg.waypoints) if seg.waypoints else 0
        print(f"  Segment {i}: {label} ({n} waypoints)")
        if seg.waypoints:
            for wp in seg.waypoints:
                q = wp.toList() if hasattr(wp, 'toList') else list(wp)
                checker.set_joint_angles(q)
                if delay > 0:
                    time.sleep(delay)

    print("Replay complete.")


def replay_interpolated(checker, segments, steps=20, delay=0.005):
    input("\nPress ENTER to start interpolated replay...")
    print("Replaying with interpolation...")

    for i, seg in enumerate(segments):
        label = seg.motion_type.name
        n = len(seg.waypoints) if seg.waypoints else 0
        print(f"  Segment {i}: {label} ({n} waypoints)")
        if not seg.waypoints or len(seg.waypoints) < 2:
            if seg.waypoints:
                q = seg.waypoints[0].toList() if hasattr(seg.waypoints[0], 'toList') else list(seg.waypoints[0])
                checker.set_joint_angles(q)
            continue

        for j in range(len(seg.waypoints) - 1):
            q_start = np.array(seg.waypoints[j].toList() if hasattr(seg.waypoints[j], 'toList') else list(seg.waypoints[j]))
            q_end = np.array(seg.waypoints[j+1].toList() if hasattr(seg.waypoints[j+1], 'toList') else list(seg.waypoints[j+1]))
            for s in range(steps):
                t = s / steps
                q = q_start + t * (q_end - q_start)
                checker.set_joint_angles(q.tolist())
                if delay > 0:
                    time.sleep(delay)

        q_last = seg.waypoints[-1].toList() if hasattr(seg.waypoints[-1], 'toList') else list(seg.waypoints[-1])
        checker.set_joint_angles(q_last)

    print("Interpolated replay complete.")


def build_interpolated_trajectory(segments, steps=20):
    points = []
    colors = []
    for seg in segments:
        if not seg.waypoints or len(seg.waypoints) < 2:
            if seg.waypoints:
                q = seg.waypoints[0].toList() if hasattr(seg.waypoints[0], 'toList') else list(seg.waypoints[0])
                points.append(q)
                colors.append(MOTION_COLORS[seg.motion_type])
            continue

        color = MOTION_COLORS[seg.motion_type]
        for j in range(len(seg.waypoints) - 1):
            q_start = np.array(seg.waypoints[j].toList() if hasattr(seg.waypoints[j], 'toList') else list(seg.waypoints[j]))
            q_end = np.array(seg.waypoints[j+1].toList() if hasattr(seg.waypoints[j+1], 'toList') else list(seg.waypoints[j+1]))
            for s in range(steps):
                t = s / steps
                q = q_start + t * (q_end - q_start)
                points.append(q.tolist())
                colors.append(color)

        q_last = seg.waypoints[-1].toList() if hasattr(seg.waypoints[-1], 'toList') else list(seg.waypoints[-1])
        points.append(q_last)
        colors.append(color)

    return np.array(points), colors


def plot_interpolated_joints(segments, steps=20):
    data, colors = build_interpolated_trajectory(segments, steps)
    if len(data) == 0:
        print("No data to plot.")
        return

    fig, axes = plt.subplots(6, 1, figsize=(14, 10), sharex=True, sharey=True)
    fig.suptitle("Interpolated joint trajectory", fontsize=12)

    y_min = data.min() - 0.1
    y_max = data.max() + 0.1

    legend_added = set()
    i = 0
    while i < len(data) - 1:
        j = i + 1
        while j < len(data) and colors[j] == colors[i]:
            j += 1

        color = colors[i]
        x = list(range(i, j))
        label = None
        if color not in legend_added:
            for mt, c in MOTION_COLORS.items():
                if c == color:
                    label = mt.name
                    break
            legend_added.add(color)

        for k in range(6):
            values = data[i:j, k]
            axes[k].plot(x, values, color=color, label=label if k == 0 else None, linewidth=1)

        i = j

    for k in range(6):
        axes[k].set_ylabel(f"J{k+1} (rad)")
        axes[k].set_ylim(y_min, y_max)
        axes[k].grid(True, alpha=0.3)

    axes[5].set_xlabel("Interpolated step")
    axes[0].legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    plt.show()
    print("Plot closed.")


def categorize_reason(reason):
    if reason == "":
        return "Valid"
    if reason == "Self-collision":
        return "Self-collision"
    if reason == "Obstacle collision":
        return "Obstacle collision"
    if reason.startswith("Joint jump"):
        return "Joint jump"
    if reason.startswith("Joint "):
        return "Joint limits"
    if reason.startswith("Link "):
        return "Link Z"
    return "Other"


REASON_COLORS = {
    "Valid": "green",
    "Self-collision": "red",
    "Obstacle collision": "orange",
    "Joint limits": "blue",
    "Link Z": "purple",
    "Joint jump": "gray",
    "Other": "black",
}


RING_COLORS = ["#2196F3", "#FF9800", "#4CAF50", "#E91E63", "#9C27B0",
               "#00BCD4", "#FFEB3B", "#795548", "#607D8B", "#F44336",
               "#3F51B5"]


def get_ring_index(step_i, n_azimuth):
    if step_i == 0:
        return 0
    return ((step_i - 1) // n_azimuth) + 1


def update_ik_chart(fig, axes, steps, title, previous_joints):
    ax_valid, ax_invalid = axes
    ax_valid.clear()
    ax_invalid.clear()

    if not steps:
        ax_valid.set_title(title + " (no data)")
        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        return

    x = np.arange(6)
    joint_labels = ["J1", "J2", "J3", "J4", "J5", "J6"]

    valid_lines = []
    invalid_lines = []

    for step in steps:
        for joint, reason in step:
            joint_arr = np.array(joint.toList() if hasattr(joint, 'toList') else list(joint))
            l2 = np.sqrt(np.sum((joint_arr - previous_joints) ** 2)) if previous_joints is not None else 0.0
            if reason == "":
                valid_lines.append((joint_arr, l2, reason))
            else:
                invalid_lines.append((joint_arr, l2, reason))

    valid_lines.sort(key=lambda t: t[1])
    invalid_lines.sort(key=lambda t: t[1])

    if previous_joints is not None:
        ax_valid.plot(x, previous_joints, color="black", linewidth=2.5, linestyle="--", marker="o", markersize=4, label="Previous wp", zorder=10)
        ax_invalid.plot(x, previous_joints, color="black", linewidth=2.5, linestyle="--", marker="o", markersize=4, label="Previous wp", zorder=10)

    reason_colors = {
        "Self-collision": "red",
        "Obstacle collision": "orange",
        "Joint limits": "blue",
        "Link Z": "purple",
        "Joint jump": "gray",
        "Other": "black",
    }

    for i, (joints, l2, reason) in enumerate(valid_lines):
        alpha = max(0.3, 1.0 - i * 0.05)
        ax_valid.plot(x, joints, alpha=alpha, linewidth=1, marker=".", markersize=3, label=f"L2={l2:.3f}")

    ax_valid.set_xticks(x)
    ax_valid.set_xticklabels(joint_labels)
    ax_valid.set_ylabel("Angle (rad)")
    ax_valid.set_title(f"{title} | {len(valid_lines)} valid")
    ax_valid.grid(True, alpha=0.3)
    if valid_lines or previous_joints is not None:
        ax_valid.legend(fontsize=6, loc="upper left", ncol=2)

    plotted_reasons = set()

    for i, (joints, l2, reason) in enumerate(invalid_lines):
        cat = categorize_reason(reason)
        color = reason_colors.get(cat, "black")
        label = cat if cat not in plotted_reasons else None
        plotted_reasons.add(cat)
        alpha = max(0.2, 0.8 - i * 0.02)
        ax_invalid.plot(x, joints, color=color, alpha=alpha, linewidth=1, marker=".", markersize=3, label=label)

    ax_invalid.set_xticks(x)
    ax_invalid.set_xticklabels(joint_labels)
    ax_invalid.set_ylabel("Angle (rad)")
    ax_invalid.set_title(f"Invalid | {len(invalid_lines)} rejected")
    ax_invalid.grid(True, alpha=0.3)
    if invalid_lines or previous_joints is not None:
        ax_invalid.legend(fontsize=6, loc="upper left", ncol=2)

    fig.tight_layout()
    fig.canvas.draw_idle()
    fig.canvas.flush_events()


def slider_viewer(checker, segments):
    cid = checker.cid

    all_waypoints = []
    waypoint_info = []
    waypoint_segments = []
    waypoint_indices = []
    for segment_i, segment in enumerate(segments):
        if not segment.waypoints:
            continue
        for waypoint_i, waypoint in enumerate(segment.waypoints):
            joints = waypoint.toList() if hasattr(waypoint, 'toList') else list(waypoint)
            all_waypoints.append(joints)
            waypoint_info.append(f"Seg {segment_i} ({segment.motion_type.name}) wp {waypoint_i}")
            waypoint_segments.append(segment)
            waypoint_indices.append(waypoint_i)

    total = len(all_waypoints)
    if total == 0:
        print("No waypoints to view.")
        return

    print(f"\n{total} total waypoints across {len(segments)} segments")
    print("Use the slider in the PyBullet GUI or type a number in terminal.")
    print("Type 'ik' to show IK solutions for current waypoint.")
    print("Press ENTER (empty) to exit.\n")

    slider_id = pb.addUserDebugParameter("Waypoint", 0, total - 1, 0, physicsClientId=cid)
    update_btn_id = pb.addUserDebugParameter("Update Plot", 0, 1, 0, physicsClientId=cid)
    text_id = None
    ik_text_id = None
    last_index = -1
    last_btn_value = 0
    viewing_ik = False
    ik_slider_id = None

    plt.ion()
    ik_fig, ik_axes = plt.subplots(1, 2, figsize=(14, 5))
    plt.show(block=False)

    while pb.isConnected(cid):
        current = int(pb.readUserDebugParameter(slider_id, physicsClientId=cid))

        if viewing_ik and ik_slider_id is not None:
            segment = waypoint_segments[last_index]
            wp_i = waypoint_indices[last_index]
            if segment.ik_solutions and wp_i < len(segment.ik_solutions):
                flat_solutions = []
                for step in segment.ik_solutions[wp_i]:
                    flat_solutions.extend(step)
                if flat_solutions:
                    ik_index = int(pb.readUserDebugParameter(ik_slider_id, physicsClientId=cid))
                    ik_index = max(0, min(ik_index, len(flat_solutions) - 1))
                    joint, reason = flat_solutions[ik_index]
                    sol_joints = joint.toList() if hasattr(joint, 'toList') else list(joint)
                    checker.set_joint_angles(sol_joints)

        if current != last_index:
            last_index = current
            viewing_ik = False
            if ik_slider_id is not None:
                pb.removeUserDebugItem(ik_slider_id, physicsClientId=cid)
                ik_slider_id = None
            if ik_text_id is not None:
                pb.removeUserDebugItem(ik_text_id, physicsClientId=cid)
                ik_text_id = None

            checker.set_joint_angles(all_waypoints[current])

            if text_id is not None:
                pb.removeUserDebugItem(text_id, physicsClientId=cid)

            segment = waypoint_segments[current]
            wp_i = waypoint_indices[current]

            has_ik_data = segment.ik_solutions and wp_i < len(segment.ik_solutions)
            if has_ik_data:
                ik_count = 0
                valid_count = 0
                for step in segment.ik_solutions[wp_i]:
                    ik_count += len(step)
                    valid_count += sum(1 for j, r in step if r == "")
                info_str = f"{valid_count}/{ik_count} valid IK"
            else:
                info_str = "mid-travel (RRT)"

            text_id = pb.addUserDebugText(
                f"[{current}/{total-1}] {waypoint_info[current]} | {info_str}",
                [0, 0, 0.5],
                textColorRGB=[1, 1, 1],
                textSize=1.5,
                physicsClientId=cid,
            )
            print(f"  [{current}/{total-1}] {waypoint_info[current]} | {info_str}")

        btn_value = pb.readUserDebugParameter(update_btn_id, physicsClientId=cid)
        if btn_value != last_btn_value:
            last_btn_value = btn_value
            idx = last_index if last_index >= 0 else 0
            segment = waypoint_segments[idx]
            wp_i = waypoint_indices[idx]
            if segment.ik_solutions and wp_i < len(segment.ik_solutions):
                steps = segment.ik_solutions[wp_i]
                prev = np.array(all_waypoints[idx - 1]) if idx > 0 else None
                update_ik_chart(ik_fig, ik_axes, steps, f"[{idx}] {waypoint_info[idx]}", prev)

        if select.select([sys.stdin], [], [], 0.05)[0]:
            line = sys.stdin.readline().strip()
            if line == "":
                break
            elif line == "ik":
                segment = waypoint_segments[last_index]
                wp_i = waypoint_indices[last_index]
                if not segment.ik_solutions or wp_i >= len(segment.ik_solutions):
                    print("    No IK solutions stored for this waypoint.")
                    continue
                steps = segment.ik_solutions[wp_i]
                flat_count = 0
                for step_i, step in enumerate(steps):
                    label = "normal 0 (original)" if step_i == 0 else f"normal {step_i}"
                    valid_count = sum(1 for j, r in step if r == "")
                    print(f"    {label}: {len(step)} IK, {valid_count} valid")
                    for joint, reason in step:
                        sol_joints = joint.toList() if hasattr(joint, 'toList') else list(joint)
                        status = "VALID" if reason == "" else reason
                        print(f"      {[f'{v:+.4f}' for v in sol_joints]} -> {status}")
                    flat_count += len(step)
                if flat_count > 0:
                    viewing_ik = True
                    if ik_slider_id is not None:
                        pb.removeUserDebugItem(ik_slider_id, physicsClientId=cid)
                    ik_slider_id = pb.addUserDebugParameter("IK Solution", 0, flat_count - 1, 0, physicsClientId=cid)
                    if ik_text_id is not None:
                        pb.removeUserDebugItem(ik_text_id, physicsClientId=cid)
                    ik_text_id = pb.addUserDebugText(
                        f"Use 'IK Solution' slider to browse {flat_count} solutions",
                        [0, 0, 0.4],
                        textColorRGB=[1, 1, 0],
                        textSize=1.2,
                        physicsClientId=cid,
                    )
                    print(f"    Use 'IK Solution' slider to browse {flat_count} solutions in the GUI.")
                else:
                    print("    No valid IK solutions for this waypoint.")
            else:
                try:
                    target = int(line)
                    if 0 <= target < total:
                        last_index = -1
                        pb.removeUserDebugItem(slider_id, physicsClientId=cid)
                        slider_id = pb.addUserDebugParameter("Waypoint", 0, total - 1, target, physicsClientId=cid)
                    else:
                        print(f"    Out of range. Enter 0-{total-1}")
                except ValueError:
                    print("    Type a number, 'ik', or ENTER to exit.")

    plt.close(ik_fig)
    plt.ioff()
    print("Slider viewer closed.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=None, help="Path to data directory")
    parser.add_argument("--file", type=Path, default=None, help="Path to a specific joint_segments .pkl file")
    args = parser.parse_args()

    data_dir = args.data
    if not data_dir and args.file:
        data_dir = args.file.parent

    ds = DataStore(data_path=data_dir) if data_dir else DataStore()

    if args.file:
        joint_data = ds.load_joint_segments(file_path=args.file)
    else:
        joint_data = ds.load_joint_segments()

    obj2robot = ds.load_transformation()
    pos, quat, scale = extract_pybullet_pose(obj2robot)
    obstacles = list(OBSTACLE_STLS)
    for obs in obstacles:
        if 'position' not in obs:
            obs['position'] = pos
            obs['orientation'] = quat

    checker = setup_checker(obstacles, gui=True)
    pb.resetDebugVisualizerCamera(
        cameraDistance=0.6, cameraYaw=45, cameraPitch=-30,
        cameraTargetPosition=pos, physicsClientId=checker.cid,
    )
    checker.set_joint_angles(HOMEJ.toList())

    segments = flatten_segments(joint_data)
    print(f"\nLoaded {len(segments)} segments")
    for i, seg in enumerate(segments):
        n = len(seg.waypoints) if seg.waypoints else 0
        print(f"  Segment {i}: {seg.motion_type.name} ({n} waypoints)")

    while True:
        print("\n--- Options ---")
        print("  1: Replay animation")
        print("  2: Replay with interpolation")
        print("  3: Slider viewer")
        print("  4: Plot interpolated joints")
        print("  q: Quit")
        choice = input("Choice: ").strip()

        if choice == "1":
            replay(checker, segments)
        elif choice == "2":
            replay_interpolated(checker, segments)
        elif choice == "3":
            slider_viewer(checker, segments)
        elif choice == "4":
            plot_interpolated_joints(segments)
        elif choice == "q":
            break

    if pb.isConnected(checker.cid):
        pb.disconnect()
    print("Done.")


if __name__ == "__main__":
    main()