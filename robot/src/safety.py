import math
import numpy as np
import pybullet as p
import pybullet_data
from pybullet_planning import pairwise_link_collision
from scipy.spatial.transform import Rotation
from pathlib import Path
from URBasic import TCP6D

from URBasic import Joint6D

from src.config import *
from src.kinematics import get_all_ik_solutions


def snap_joints_to_qnear(candidates, previous_joints):
    if previous_joints is None:
        return candidates
    snapped = []
    for q in candidates:
        joints = np.array(q.toList())
        for j in range(len(joints)):
            while joints[j] - previous_joints[j] > np.pi:
                joints[j] -= 2 * np.pi
            while joints[j] - previous_joints[j] < -np.pi:
                joints[j] += 2 * np.pi
        snapped.append(Joint6D.createFromRadians(*joints.tolist()))
    return snapped


def wrapped_joint_distance(joints_a, joints_b):
    diff = joints_a - joints_b
    diff = (diff + np.pi) % (2 * np.pi) - np.pi
    return np.sum(diff ** 2)

class CollisionChecker:

    def __init__(self, obstacle_stls=None, gui=False):
        self.cid = p.connect(p.GUI if gui else p.DIRECT)

        # Load robot (pi rotation around Z to match real-robot frame )
        self.robot_id = p.loadURDF(
            str(URDF_PATH),
            basePosition=[0, 0, 0],
            baseOrientation=p.getQuaternionFromEuler([0, 0, np.pi]),
            useFixedBase=True,
            physicsClientId=self.cid,
        )

        # read all joints from URDF
        num_joints = p.getNumJoints(self.robot_id, physicsClientId=self.cid)
        self.joint_indices = []
        for i in range(num_joints):
            info = p.getJointInfo(self.robot_id, i, physicsClientId=self.cid)
            if info[2] in (p.JOINT_REVOLUTE, p.JOINT_PRISMATIC):
                self.joint_indices.append(i)
        self.link_indices = list(range(num_joints))

        self.self_pairs = [
            (self.robot_id, a, self.robot_id, b) for a, b in SELF_COLLISION_PAIRS
        ]

        # Load obstacles
        self.obstacle_ids = []
        self.obstacle_exclude_links = {}
        for obs in (obstacle_stls or []):
            col_shape = p.createCollisionShape(
                p.GEOM_MESH,
                fileName=str(obs['path']),
                meshScale=obs.get('scale', [1, 1, 1]),
                physicsClientId=self.cid,
                flags=p.GEOM_FORCE_CONCAVE_TRIMESH
            )
            vis_shape = -1
            if gui:
                vis_shape = p.createVisualShape(
                    p.GEOM_MESH,
                    fileName=str(obs['path']),
                    meshScale=obs.get('scale', [1, 1, 1]),
                    rgbaColor=[0.6, 0.6, 0.8, 0.7],
                    physicsClientId=self.cid,
                )
            oid = p.createMultiBody(
                baseMass=0,
                baseCollisionShapeIndex=col_shape,
                baseVisualShapeIndex=vis_shape,
                basePosition=obs.get('position', [0, 0, 0]),
                baseOrientation=obs.get('orientation', [0, 0, 0, 1]),
                physicsClientId=self.cid,
            )
            self.obstacle_ids.append(oid)
            self.obstacle_exclude_links[oid] = set(obs.get('exclude_links', []))

        self.obstacle_pairs = []
        for oid in self.obstacle_ids:
            excluded = self.obstacle_exclude_links.get(oid, set())
            for link in self.link_indices:
                if link not in excluded:
                    self.obstacle_pairs.append((self.robot_id, link, oid, -1))

    # -------------------------------------------------------------------------

    def flip_obstacles_z(self, exclude_ids=None):
        rz_180 = [0, 0, 1, 0]
        for oid in self.obstacle_ids:
            if exclude_ids and oid in exclude_ids:
                continue
            pos, orn = p.getBasePositionAndOrientation(oid, physicsClientId=self.cid)
            new_orn = p.multiplyTransforms([0, 0, 0], rz_180, [0, 0, 0], orn)[1]
            p.resetBasePositionAndOrientation(oid, pos, new_orn, physicsClientId=self.cid)

    def set_joint_angles(self, q):
        for idx, angle in zip(self.joint_indices, q):
            p.resetJointState(self.robot_id, idx, float(angle), physicsClientId=self.cid)


    def in_self_collision(self, margin=SELF_COLLISION_MARGIN):
        for b1, l1, b2, l2 in self.self_pairs:
            if pairwise_link_collision(b1, l1, b2, l2, max_distance=margin):
                return True
        return False

    def in_obstacle_collision(self, margin=COLLISION_MARGIN):
        for b1, l1, b2, l2 in self.obstacle_pairs:
            if pairwise_link_collision(b1, l1, b2, l2, max_distance=margin):
                return True
        return False

    def check_workspace_bounds(self, tcp):
        x, y, z = tcp.x, tcp.y, tcp.z
        if y > TCP_Y_MAX:
            return False, f"TCP Y={y:.4f} > {TCP_Y_MAX}"
        if z < TCP_Z_MIN:
            return False, f"TCP Z={z:.4f} < {TCP_Z_MIN}"
        if z > TCP_Z_MAX:
            return False, f"TCP Z={z:.4f} > {TCP_Z_MAX}"
        if UR3E_MAX_REACH and math.sqrt(x*x + y*y + z*z) > UR3E_MAX_REACH:
            return False, f"TCP reach > {UR3E_MAX_REACH}"
        return True, ""

    # not being used at the mment
    def check_joint_limits(self, q):
        q_list = q.toList() if hasattr(q, 'toList') else list(q)
        for i, (angle, limit) in enumerate(zip(q_list, JOINT_LIMITS)):
            if limit is None:
                continue
            lo, hi = limit
            if not (lo <= angle <= hi):
                return False, f"Joint {i} = {angle:.4f} outside [{lo}, {hi}]"
        return True, ""

    # -------------------------------------------------------------------------

    def _is_safe(self, q, margin, check_obstacle):
        ok, reason = self.check_joint_limits(q)
        if not ok:
            return False, reason

        self.set_joint_angles(q.toList())

        for link_idx, z_min in (LINK_Z_MIN or {}).items():
            link_z = p.getAABB(self.robot_id, link_idx, physicsClientId=self.cid)[0][2]
            if link_z < z_min:
                info = p.getJointInfo(self.robot_id, link_idx, physicsClientId=self.cid)
                return False, f"Link {info[12].decode()} Z={link_z:.4f} < {z_min}"

        if self.in_self_collision():
            return False, "Self-collision"

        if check_obstacle and self.in_obstacle_collision(margin):
            return False, "Obstacle collision"

        return True, ""

    def _cone_orientations(self, tcp, max_cone_angle, tilt_step, azimuth_step):
        yield tcp

        tcp_xyz = np.array([tcp.x, tcp.y, tcp.z])
        original_rot = Rotation.from_rotvec([tcp.rx, tcp.ry, tcp.rz])

        tilt = tilt_step
        while tilt <= max_cone_angle + 1e-9:
            n_azimuth = max(int(np.ceil(2 * math.pi / azimuth_step)), 1)
            for az_i in range(n_azimuth):
                azimuth = az_i * (2 * math.pi / n_azimuth)
                axis = np.array([math.sin(azimuth), math.cos(azimuth), 0.0])
                rv = (original_rot * Rotation.from_rotvec(axis * tilt)).as_rotvec()
                yield TCP6D.createFromMetersRadians(
                    *tcp_xyz.tolist(), float(rv[0]), float(rv[1]), float(rv[2])
                )
            tilt += tilt_step

    # -------------------------------------------------------------------------

    def validate_tcp(self, tcp_offset, tcp, qnear=None, margin=COLLISION_MARGIN,
                     check_obstacle=True, orientation_search=False,
                     max_cone_angle=math.radians(DRAWING_ANGLE),
                     tilt_step=math.radians(CONE_TILT_STEP),
                     azimuth_step=math.radians(CONE_AZIMUTH_STEP),
                     search_mode=0, check_joint_jump=False, min_rings=0):
        ok, reason = self.check_workspace_bounds(tcp)
        if not ok:
            return False, None, reason, tcp, []

        if search_mode in (1, 2) and orientation_search:
            early_stop = (search_mode == 1)
            best_joint, best_tcp, all_solutions_by_step = self._find_all_valid(
                tcp_offset, tcp, qnear, margin, check_obstacle, max_cone_angle,
                tilt_step, azimuth_step, early_stop=early_stop,
                check_joint_jump=check_joint_jump, min_rings=min_rings,
            )
            if best_joint is not None:
                return True, best_joint, "", best_tcp, all_solutions_by_step
            return False, None, "No valid solution in cone", tcp, all_solutions_by_step

        ok, best_joint, reason, valid = self._try_ik_and_collision(
            tcp_offset, tcp, qnear, margin, check_obstacle, check_joint_jump,
        )
        if ok:
            return True, best_joint, "", tcp, [valid]

        if orientation_search:
            all_solutions_by_step = [valid]
            for candidate_tcp in self._cone_orientations(tcp, max_cone_angle, tilt_step, azimuth_step):
                if candidate_tcp is tcp:
                    continue
                ok, cone_joint, cone_reason, cone_valid = self._try_ik_and_collision(
                    tcp_offset, candidate_tcp, qnear, margin, check_obstacle, check_joint_jump,
                )
                all_solutions_by_step.append(cone_valid)
                if ok:
                    return True, cone_joint, "", candidate_tcp, all_solutions_by_step
            return False, None, reason, tcp, all_solutions_by_step

        return False, None, reason, tcp, [valid]

    def _try_ik_and_collision(self, tcp_offset, tcp, qnear, margin, check_obstacle, check_joint_jump=False):
        candidates = get_all_ik_solutions(tcp, tcp_offset, fixed_theta6=FIXED_THETA6)

        all_with_reasons = []

        if not candidates:
            return False, None, "IK has no solution", all_with_reasons

        if qnear is not None:
            previous_joints = np.array(qnear.toList())
            distances = []
            for c in candidates:
                distances.append(wrapped_joint_distance(np.array(c.toList()), previous_joints))
            candidates = [c for unused, c in sorted(zip(distances, candidates), key=lambda t: t[0])]

        best_joint = None
        first_reason = None
        for joint in candidates:
            if check_joint_jump and qnear is not None:
                candidate_joints = np.array(joint.toList())
                diff = (candidate_joints - previous_joints + np.pi) % (2 * np.pi) - np.pi
                max_diff = np.max(np.abs(diff))
                if max_diff > MAX_JOINT_JUMP:
                    reason = f"Joint jump {max_diff:.2f} rad > {MAX_JOINT_JUMP}"
                    all_with_reasons.append((joint, reason))
                    if first_reason is None:
                        first_reason = reason
                    continue

            ok, reason = self._is_safe(joint, margin, check_obstacle)
            all_with_reasons.append((joint, reason))
            if not ok:
                if first_reason is None:
                    first_reason = reason
                continue

            if best_joint is None:
                best_joint = joint

        if best_joint is not None:
            return True, best_joint, "", all_with_reasons

        return False, None, first_reason or "IK has no solution", all_with_reasons

    def _find_all_valid(self, tcp_offset, tcp, qnear, margin, check_obstacle, max_cone_angle, tilt_step, azimuth_step, early_stop=False, check_joint_jump=False, min_rings=0):
        previous_joints = np.array(qnear.toList()) if qnear is not None else None
        all_solutions_by_step = []

        candidates = get_all_ik_solutions(tcp, tcp_offset, fixed_theta6=FIXED_THETA6)
        best, all_with_reasons = self._pick_best_safe(candidates, previous_joints, margin, check_obstacle, check_joint_jump)
        all_solutions_by_step.append(all_with_reasons)

        overall_best = None
        overall_best_cost = float('inf')
        overall_best_tcp = tcp

        if best is not None:
            overall_best = best
            overall_best_cost = wrapped_joint_distance(np.array(best.toList()), previous_joints) if previous_joints is not None else 0.0
            overall_best_tcp = tcp
            if early_stop and min_rings <= 0:
                return overall_best, overall_best_tcp, all_solutions_by_step

        tcp_xyz = np.array([tcp.x, tcp.y, tcp.z])
        original_rot = Rotation.from_rotvec([tcp.rx, tcp.ry, tcp.rz])

        ring_number = 0
        tilt = tilt_step
        while tilt <= max_cone_angle + 1e-9:
            ring_number += 1
            ring_best_joint = None
            ring_best_cost = float('inf')
            ring_best_tcp = None

            n_azimuth = max(int(np.ceil(2 * math.pi / azimuth_step)), 1)
            for az_i in range(n_azimuth):
                azimuth = az_i * (2 * math.pi / n_azimuth)
                axis = np.array([math.sin(azimuth), math.cos(azimuth), 0.0])
                rv = (original_rot * Rotation.from_rotvec(axis * tilt)).as_rotvec()
                candidate_tcp = TCP6D.createFromMetersRadians(
                    *tcp_xyz.tolist(), float(rv[0]), float(rv[1]), float(rv[2])
                )

                candidates = get_all_ik_solutions(candidate_tcp, tcp_offset, fixed_theta6=FIXED_THETA6)
                azimuth_best, all_with_reasons = self._pick_best_safe(candidates, previous_joints, margin, check_obstacle, check_joint_jump)
                all_solutions_by_step.append(all_with_reasons)

                if azimuth_best is not None:
                    cost = wrapped_joint_distance(np.array(azimuth_best.toList()), previous_joints) if previous_joints is not None else 0.0
                    if cost < ring_best_cost:
                        ring_best_cost = cost
                        ring_best_joint = azimuth_best
                        ring_best_tcp = candidate_tcp

            if ring_best_joint is not None and ring_best_cost < overall_best_cost:
                overall_best_cost = ring_best_cost
                overall_best = ring_best_joint
                overall_best_tcp = ring_best_tcp

            if early_stop and overall_best is not None and ring_number >= min_rings:
                return overall_best, overall_best_tcp, all_solutions_by_step

            tilt += tilt_step

        return overall_best, overall_best_tcp, all_solutions_by_step

    def _pick_best_safe(self, candidates, previous_joints, margin, check_obstacle, check_joint_jump=False):
        if not candidates:
            return None, []

        all_with_reasons = []
        best = None
        best_cost = float('inf')

        for joint in candidates:
            if check_joint_jump and previous_joints is not None:
                candidate_joints = np.array(joint.toList())
                diff = (candidate_joints - previous_joints + np.pi) % (2 * np.pi) - np.pi
                max_diff = np.max(np.abs(diff))
                if max_diff > MAX_JOINT_JUMP:
                    all_with_reasons.append((joint, f"Joint jump {max_diff:.2f} rad > {MAX_JOINT_JUMP}"))
                    continue

            ok, reason = self._is_safe(joint, margin, check_obstacle)
            all_with_reasons.append((joint, reason))
            if not ok:
                continue

            cost = wrapped_joint_distance(np.array(joint.toList()), previous_joints) if previous_joints is not None else 0.0
            if cost < best_cost:
                best_cost = cost
                best = joint

        return best, all_with_reasons

    # -------------------------------------------------------------------------


    def validate_path(self, tcp_offset, waypoints_tcp, margin=COLLISION_MARGIN,
                      qnear=None, check_obstacle=True, orientation_search=False):
        joint_trajectory = []

        for i, tcp in enumerate(waypoints_tcp):
            ok, joint, reason, used_tcp, solutions = self.validate_tcp(
                tcp_offset, tcp, qnear=qnear, margin=margin,
                check_obstacle=check_obstacle,
                orientation_search=orientation_search,
            )
            if not ok:
                return False, i, reason, joint_trajectory
            joint_trajectory.append(joint)
            qnear = joint

        return True, -1, "", joint_trajectory



def setup_checker(obstacle_stls, obj_position=None, obj_orientation=None, gui=True):
    for obs in (obstacle_stls or []):
        if 'position' not in obs and obj_position is not None:
            obs['position'] = obj_position
            obs['orientation'] = obj_orientation

    checker = CollisionChecker(obstacle_stls=obstacle_stls, gui=gui)

    print(f"PyBullet GUI running (cid={checker.cid})")
    print(f"Robot body id: {checker.robot_id}")
    print(f"Obstacle ids:  {checker.obstacle_ids}")

    for oid in checker.obstacle_ids:
        pos_ob, orn = p.getBasePositionAndOrientation(oid, physicsClientId=checker.cid)
        aabb_min, aabb_max = p.getAABB(oid, physicsClientId=checker.cid)
        print(f"\nObstacle {oid}:")
        print(f"  Position:    {pos_ob}")
        print(f"  Orientation: {orn}")
        print(f"  AABB min:    {[f'{v:.4f}' for v in aabb_min]}")
        print(f"  AABB max:    {[f'{v:.4f}' for v in aabb_max]}")
        size = (aabb_max[0]-aabb_min[0], aabb_max[1]-aabb_min[1], aabb_max[2]-aabb_min[2])
        print(f"  Size (m):    ({size[0]:.4f}, {size[1]:.4f}, {size[2]:.4f})")

    if gui and obj_position is not None:
        p.resetDebugVisualizerCamera(
            cameraDistance=0.6, cameraYaw=45, cameraPitch=-30,
            cameraTargetPosition=obj_position, physicsClientId=checker.cid,
        )

    return checker