"""SimRobotControl -- mirrors the robot_control interface from ISCoin.

temporary helper tool ( later replaced by PyBullet )

Author:     Pierre-Yves Savioz (design, specification, testing)
Generated:  Implementation written entirely by Claude AI (Anthropic) under author direction
Course:     HES-SO Valais-Wallis, Engineering Track 304
URBasic:    API modelled on UrScriptExt by Martin Huus Bjerge,
            Rope Robotics ApS, Denmark (MIT License, 2017),
            modified by A. Amand, M. Richard, L. Azzalini (HES-SO).
"""

import logging
import math
import time
import numpy as np

from URBasic.waypoint6d import Joint6D, TCP6D, TCP6DDescriptor

log = logging.getLogger(__name__)

from .ros_bridge import read_joint_states, extract_6joints, publish_trajectory, estimate_duration
from robot.src.kinematics import (
    UR3E_DH, forward_kinematics_matrix,
    matrix_to_tcp6d, pose_to_matrix,
    analytical_ik, select_closest_ik,
)

T_DELAY = 0.1


class SimRobotControl:
    """Mirrors the robot_control interface from ISCoin (UrScriptExt)."""


    def __init__(self):
        self._tcp_offset = np.eye(4)  # no tool by default (identity)
        self._model_correction = np.eye(4)

    # Mirrors UrScript.set_tcp (urScript.py:1242)
    def set_tcp(self, pose):
        self._tcp_offset = pose_to_matrix(pose)

    # No URBasic equivalent -- Gazebo-specific hotfix for FK model offset
    def set_model_correction(self, pose):
        self._model_correction = pose_to_matrix(pose)

    # -- Read state ----------------------------------------------------------

    # Mirrors UrScript.get_actual_joint_positions (urScript.py:788)
    # Reads from Gazebo via ros_bridge instead of the UR controller
    def get_actual_joint_positions(self, wait=True):
        states = read_joint_states()
        values = extract_6joints(states["position"])
        return Joint6D.createFromRadians(*values)

    # Mirrors UrScript.get_actual_tcp_pose (urScript.py:828)
    # URBasic reads from controller; here we compute FK locally via src.kinematics
    def get_actual_tcp_pose(self, wait=True):
        joints = self.get_actual_joint_positions(wait=wait)
        T_flange = forward_kinematics_matrix(joints.toList())
        T_tcp = T_flange @ self._model_correction @ self._tcp_offset
        return matrix_to_tcp6d(T_tcp)

    # No URBasic equivalent -- URBasic relies on the controller for FK
    # Uses src.kinematics (DH-parameter based, see Denavit-Hartenberg convention)
    def get_fk(self, joints):
        T_flange = forward_kinematics_matrix(joints.toList())
        T_tcp = T_flange @ self._model_correction @ self._tcp_offset
        return matrix_to_tcp6d(T_tcp)

    # Mirrors UrScript.is_steady (urScript.py:1082)
    # URBasic checks controller state; here we read joint velocities from Gazebo
    def is_steady(self):
        states = read_joint_states()
        speeds = extract_6joints(states["velocity"])
        return all(abs(s) <= 0.01 for s in speeds)

    # -- Movement commands ---------------------------------------------------

    # Mirrors UrScript.freedrive_mode (urScript.py:492) -- no-op in Gazebo
    def freedrive_mode(self):
        print("Ignoring freedrive mode in simulation")
        return None

    # Mirrors UrScript.end_freedrive_mode (urScript.py:513) -- no-op in Gazebo
    def end_freedrive_mode(self):
        print("Ignoring end freedrive mode in simulation")
        return None

    # Mirrors UrScript.movej (urScript.py:108)
    # Same signature and default params; sends trajectory to Gazebo via ros_bridge
    def movej(self, joints, a=1.4, v=1.05, t=0, r=0, wait=True):
        positions = joints.toList()

        if t > 0:
            duration_sec = t
        else:
            duration_sec = estimate_duration(v)

        publish_trajectory([{
            "positions": positions,
            "duration_sec": duration_sec,
        }])
        print(f"movej sent (duration={duration_sec}s)")

        if wait:
            return self._wait_until_motion_done(
                target_joints=joints,
                timeout_sec=max(5.0, float(duration_sec) + 10.0),
            )

        return True

    # Mirrors UrScriptExt.movej_waypoints (urScriptExt.py:629)
    # Packs all waypoints into one ROS2 trajectory message
    def movej_waypoints(self, waypoints, wait=True):
        points = []
        cumulative_sec = 0

        for wp in waypoints:
            wp_dict = wp.getAsDict()
            positions = wp_dict["q"]
            v = wp_dict["v"]
            t_param = wp_dict["t"]

            if t_param > 0:
                duration = t_param
            else:
                duration = estimate_duration(v)

            cumulative_sec += duration
            points.append({
                "positions": positions,
                "duration_sec": cumulative_sec,
            })

        publish_trajectory(points)
        print(f"movej_waypoints sent ({len(points)} points, total={cumulative_sec}s)")

        if wait:
            final_target = Joint6D.createFromRadians(*points[-1]["positions"])
            return self._wait_until_motion_done(
                target_joints=final_target,
                timeout_sec=max(5.0, float(cumulative_sec) + 10.0),
            )

        return True

    # Mirrors UrScript.movel (urScript.py:142)
    # URBasic sends URScript movel command; here we solve IK locally then movej
    def movel(self, pose, a=1.2, v=0.25, t=0, r=0, wait=True):
        current_joints = self.get_actual_joint_positions()
        target_joints = self.get_inverse_kin(pose, qnear=current_joints)

        if target_joints is None:
            print("ERROR: movel failed — could not find inverse kinematics solution")
            return False

        if t > 0:
            duration = t
        else:
            current_tcp = self.get_actual_tcp_pose()
            dx = pose.x - current_tcp.x
            dy = pose.y - current_tcp.y
            dz = pose.z - current_tcp.z
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            duration = max(0.3, dist / v)

        return self.movej(target_joints, t=duration, wait=wait)

    # Mirrors UrScriptExt.movel_waypoints (urScriptExt.py:656)
    # Solves IK for each waypoint, then sends as joint trajectory to Gazebo
    def movel_waypoints(self, waypoints, wait=True):
        if not isinstance(waypoints, list):
            raise ValueError("waypoints must be a list of TCP6DDescriptor objects")
        for w in waypoints:
            if not isinstance(w, TCP6DDescriptor):
                raise ValueError(f"waypoints must be a list of TCP6DDescriptor objects — got {type(w)}")

        points = []
        cumulative_sec = 0
        prev_joints = self.get_actual_joint_positions()
        prev_tcp = self.get_actual_tcp_pose()

        for wp in waypoints:
            wp_dict = wp.getAsDict()
            pose = TCP6D.createFromMetersRadians(*wp_dict["pose"])
            v = wp_dict["v"]
            t_param = wp_dict["t"]

            target_joints = self.get_inverse_kin(pose, qnear=prev_joints)
            if target_joints is None:
                print(f"ERROR: movel_waypoints — IK failed for {pose}")
                return False

            if t_param > 0:
                duration = t_param
            else:
                dx = pose.x - prev_tcp.x
                dy = pose.y - prev_tcp.y
                dz = pose.z - prev_tcp.z
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                duration = max(0.3, dist / v)

            cumulative_sec += duration
            points.append({
                "positions": target_joints.toList(),
                "duration_sec": cumulative_sec,
            })

            prev_joints = target_joints
            prev_tcp = pose

        publish_trajectory(points)
        print(f"movel_waypoints sent ({len(points)} points, total={cumulative_sec}s)")

        if wait:
            final_target = Joint6D.createFromRadians(*points[-1]["positions"])
            return self._wait_until_motion_done(
                target_joints=final_target,
                timeout_sec=max(5.0, float(cumulative_sec) + 10.0),
            )

        return True

    # Mirrors UrScript.get_inverse_kin (urScript.py:892)
    # URBasic runs IK on the UR controller; here we use src.kinematics.analytical_ik
    # Based on Hawkins (2013) "Analytic Inverse Kinematics for the Universal Robots",
    # adapted from mc-capolei/python-Universal-robot-kinematics (see src/kinematics.py)
    def get_inverse_kin(self, pose, qnear=None):
        if qnear is not None:
            q0 = np.array(qnear.toList())
        else:
            q0 = np.zeros(6)

        T_desired = pose_to_matrix(pose)
        T_flange = T_desired @ np.linalg.inv(self._model_correction @ self._tcp_offset)
        solutions = analytical_ik(T_flange)

        if solutions:
            # Validate each solution with FK (applying tool offset) and keep only accurate ones
            valid = []
            target = np.array(pose.toList())
            for sol in solutions:
                T_check = forward_kinematics_matrix(sol.tolist()) @ self._model_correction @ self._tcp_offset
                tcp_check = matrix_to_tcp6d(T_check)
                err_pos = np.sum((np.array(tcp_check.toList()[:3]) - target[:3]) ** 2)
                if err_pos < 0.001:
                    valid.append(sol)

            best = select_closest_ik(valid if valid else solutions, q0)
            if best is not None:
                T_check = forward_kinematics_matrix(best.tolist()) @ self._model_correction @ self._tcp_offset
                tcp_check = matrix_to_tcp6d(T_check)
                err = np.sum((np.array(tcp_check.toList()[:3]) - np.array(pose.toList()[:3])) ** 2)
                if err < 0.001:
                    log.debug("IK OK for TCP=(%.4f, %.4f, %.4f), "
                              "%d/%d valid solutions",
                              pose.x, pose.y, pose.z, len(valid), len(solutions))
                    return Joint6D.createFromRadians(*best.tolist())
                log.debug("IK best solution has position error=%.6fm", np.sqrt(err))

        # Reachability diagnostic
        pos = np.array([pose.x, pose.y, pose.z])
        reach = np.linalg.norm(pos)
        n_raw = len(solutions) if solutions else 0
        flange_pos = T_flange[:3, 3]
        flange_reach = np.linalg.norm(flange_pos[:2])
        log.debug("IK failed for TCP=(%.4f, %.4f, %.4f), reach=%.4fm | "
                  "%d raw solutions | flange_r=%.4fm",
                  pose.x, pose.y, pose.z, reach, n_raw, flange_reach)

        return None

    # -- Internal helpers ----------------------------------------------------
    # These have no direct URBasic equivalent. URBasic uses waitRobotIdleOrStopFlag()
    # (urScript.py) which polls the controller. Here we poll Gazebo joint states instead.

    def _wait_until_motion_done(self, target_joints, timeout_sec=15.0, tolerance=0.05, poll_sec=0.1):
        deadline = time.time() + timeout_sec
        time.sleep(T_DELAY)

        while time.time() < deadline:
            if self.is_steady() and self._is_within_tolerance(target_joints, tolerance=tolerance):
                print("Movement OK — target reached")
                return True
            time.sleep(poll_sec)

        print(f"WARNING: Motion timeout after {timeout_sec:.1f}s")
        return self._verify_position(target_joints, tolerance=tolerance)

    def _is_within_tolerance(self, target_joints, tolerance=0.05):
        """Check target proximity without printing warnings."""
        actual = self.get_actual_joint_positions()
        target_list = target_joints.toList()
        actual_list = actual.toList()
        return all(abs(target_list[i] - actual_list[i]) <= tolerance for i in range(6))

    def _verify_position(self, target_joints, tolerance=0.05):
        """Check if the robot reached the target position.

        Args:
            target_joints: Joint6D with expected position.
            tolerance: max allowed error per joint in radians.

        Returns:
            True if all joints are within tolerance.
        """
        actual = self.get_actual_joint_positions()
        target_list = target_joints.toList()
        actual_list = actual.toList()

        all_ok = True
        for i in range(6):
            error = abs(target_list[i] - actual_list[i])
            if error > tolerance:
                print(f"WARNING: Joint {i+1} error = {math.degrees(error):.1f}° "
                      f"(target={target_list[i]:.4f}, actual={actual_list[i]:.4f})")
                all_ok = False

        if all_ok:
            print("Movement OK — target reached")
        else:
            print("Movement DONE — but target not fully reached (possible collision?)")

        return all_ok
