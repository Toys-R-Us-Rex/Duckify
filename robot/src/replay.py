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
from src.config import OBSTACLE_STLS, HOMEJ
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


def slider_viewer(checker, segments):
    cid = checker.cid

    all_waypoints = []
    waypoint_info = []
    for seg_i, seg in enumerate(segments):
        if not seg.waypoints:
            continue
        for wp_i, wp in enumerate(seg.waypoints):
            q = wp.toList() if hasattr(wp, 'toList') else list(wp)
            all_waypoints.append(q)
            waypoint_info.append(f"Seg {seg_i} ({seg.motion_type.name}) wp {wp_i}")

    total = len(all_waypoints)
    if total == 0:
        print("No waypoints to view.")
        return

    print(f"\n{total} total waypoints across {len(segments)} segments")
    print("Use the slider in the PyBullet GUI to navigate. Press ENTER in terminal to exit.\n")

    slider_id = pb.addUserDebugParameter("Waypoint", 0, total - 1, 0, physicsClientId=cid)
    text_id = None
    last_index = -1

    while pb.isConnected(cid):
        current = int(pb.readUserDebugParameter(slider_id, physicsClientId=cid))
        if current != last_index:
            last_index = current
            checker.set_joint_angles(all_waypoints[current])

            if text_id is not None:
                pb.removeUserDebugItem(text_id, physicsClientId=cid)
            text_id = pb.addUserDebugText(
                f"[{current}/{total-1}] {waypoint_info[current]}",
                [0, 0, 0.5],
                textColorRGB=[1, 1, 1],
                textSize=1.5,
                physicsClientId=cid,
            )
            print(f"  [{current}/{total-1}] {waypoint_info[current]}")

        if select.select([sys.stdin], [], [], 0.05)[0]:
            sys.stdin.readline()
            break

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