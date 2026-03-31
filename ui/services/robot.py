import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pybullet as pb
from URBasic.devices.robotiq_two_fingers_gripper import RobotiqTwoFingersGripper
from URBasic.iscoin import ISCoin
from URBasic.urScriptExt import UrScriptExt
from URBasic.waypoint6d import TCP6D, Joint6D

from robot.src.calibration import get_tcp_offset
from robot.src.computation import (
    assemble_segments,
    hotfix_j6_correction,
    plan_travels,
    plot_joint_plan,
    plot_normal_diff,
    smoothing,
)
from robot.src.kinematics import pose_to_matrix
from robot.src.logger import DataStore
from robot.src.pybullet_helpers import (
    find_hovers,
    split_into_runs,
    validate_surface_points,
)
from robot.src.safety import setup_checker
from robot.src.transformation import create_transformation, extract_pybullet_pose
from robot.src.utils import AtoB
from ui.assets import AssetRegistry
from ui.models import Point3D, TCPPoint


@dataclass
class RobotRequest:
    trace_path: Path
    filter_mode: str
    tcp_calibration: str
    transformation: str


@dataclass
class RobotResult:
    pass


class NotConnectedError(RuntimeError):
    def __init__(self, msg: str = "Not connected to the robot") -> None:
        super().__init__(msg)


def tcp6d_to_tcppoint(tcp6d: TCP6D) -> TCPPoint:
    tcp: list[float] = tcp6d.toList()
    return (
        tcp[0],
        tcp[1],
        tcp[2],
        tcp[3],
        tcp[4],
        tcp[5],
    )


def tcppoint_to_tcp6d(tcppoint: TCPPoint) -> TCP6D:
    return TCP6D.createFromMetersRadians(*tcppoint)


class RobotService:
    def __init__(self, ip_address: str, base_dir: Path, assets: AssetRegistry) -> None:
        self.ip_address: str = ip_address
        self._robot: Optional[ISCoin] = None
        base_dir.mkdir(parents=True, exist_ok=True)
        self.ds: DataStore = DataStore(base_dir)

        self.homej: Joint6D = Joint6D.createFromRadians(
            1.8859, -1.4452, 1.2389, -1.3639, -1.5693, -0.3849
        )
        self.obstacles: list[dict] = [
            {
                "path": assets.root_dir / "assets" / "models" / "duck_uv_low_poly.stl",
                "scale": [0.001, 0.001, 0.001],
            },
            {
                "path": assets.root_dir / "assets" / "models" / "workspace.stl",
                "scale": [1, 1, 1],
                "position": [0, 0, 0],
                "orientation": [0, 0, 0, 1],
                "exclude_links": [1, 2, 3, 4],
            },
            {
                "path": assets.root_dir / "assets" / "models" / "support_duck_simulation.stl",
                "scale": [0.001, 0.001, 0.001],
            },
        ]

    @property
    def robot(self) -> ISCoin:
        if self._robot is None:
            raise NotConnectedError
        return self._robot

    @property
    def ctrl(self) -> UrScriptExt:
        robot: ISCoin = self.robot
        if robot.robot_control is None:
            raise RuntimeError("Connected to robot but robot_control is None")
        return robot.robot_control

    @property
    def gripper(self) -> RobotiqTwoFingersGripper:
        robot: ISCoin = self.robot
        if robot.gripper is None:
            raise RuntimeError("Connected to robot but gripper is None")
        return robot.gripper

    def connect(self) -> bool:
        if self._robot is not None:
            return True
        try:
            self._robot = ISCoin(
                host=self.ip_address,
                opened_gripper_size_mm=40,  # TODO: put this in settings
            )
            return True
        except:
            self._robot = None
            return False

    def disconnect(self):
        if self._robot is None:
            return
        self._robot.close()
        self._robot = None

    def run(self, request: RobotRequest) -> RobotResult:
        print("Running robot")
        print(f" - ip: {self.ip_address}")
        print(f" - trace: {request.trace_path}")
        print(f" - filter: {request.filter_mode}")
        print(f" - TCP calibration: {request.tcp_calibration}")
        print(f" - transformation: {request.transformation}")
        return RobotResult()

    def read_tcp(self) -> TCPPoint:
        tcp: TCP6D = self.ctrl.get_actual_tcp_pose()
        return tcp6d_to_tcppoint(tcp)

    def compute_tcp_offset(self, tcps: list[TCPPoint]) -> TCPPoint:
        offset: TCP6D = get_tcp_offset(list(map(list, tcps)))
        return tcp6d_to_tcppoint(offset)

    def compute_transformation(self, points: list[tuple[Point3D, TCPPoint]]) -> AtoB:
        world: list[Point3D] = []
        tcps: list[TCPPoint] = []
        for w, t in points:
            world.append(w)
            tcps.append(t)
        return create_transformation(np.array(world), np.array(tcps))

    def set_freedrive(self, enabled: bool):
        if enabled:
            self.ctrl.freedrive_mode()
        else:
            self.ctrl.end_freedrive_mode()

    def set_gripper_state(self, open: bool):
        if open:
            self.gripper.open()
        else:
            self.gripper.close()

    def activate_gripper(self):
        self.gripper.activate()
        while not self.is_gripper_activated():
            time.sleep(0.2)

    def deactivate_gripper(self):
        self.gripper.deactivate()
        while self.is_gripper_activated():
            time.sleep(0.2)

    def is_gripper_activated(self) -> bool:
        return self.gripper.isActivated()

    def plan_paths(
        self,
        obj2robot: AtoB,
        data: dict,
        tcp_offset: TCPPoint,
        draw_sides: Optional[tuple[str]] = None,
    ) -> dict:
        tcp6d_offset: TCP6D = tcppoint_to_tcp6d(tcp_offset)
        tcp_offset_mat = pose_to_matrix(tcp6d_offset)

        position, quat, scale = extract_pybullet_pose(obj2robot)
        checker = setup_checker(
            self.obstacles, obj_position=position, obj_orientation=quat, gui=False
        )
        checker.set_joint_angles(self.homej.toList())

        joint_data = {}
        is_flipped = False

        for side, colors in data.items():
            if draw_sides is not None and side not in draw_sides:
                continue

            pb.removeAllUserDebugItems(physicsClientId=checker.cid)

            workspace_id = (
                checker.obstacle_ids[1] if len(checker.obstacle_ids) > 1 else None
            )
            exclude = {workspace_id} if workspace_id else None
            if side == "right" and not is_flipped:
                checker.flip_obstacles_z(exclude_ids=exclude)
                is_flipped = True
            elif side == "left" and is_flipped:
                checker.flip_obstacles_z(exclude_ids=exclude)
                is_flipped = False

            joint_data[side] = {}
            for color, traces in colors.items():

                self.ds.log(f"Processing {side} - {color}")
                trace_waypoints = [t.waypoints for t in traces]
                default_normals = [t.default_normals for t in traces]

                valid_masks, surface_joints = validate_surface_points(
                    checker,
                    tcp_offset_mat,
                    trace_waypoints,
                    self.homej,
                )

                runs_per_trace = split_into_runs(valid_masks)
                validated_runs = find_hovers(
                    checker,
                    tcp_offset_mat,
                    trace_waypoints,
                    runs_per_trace,
                    surface_joints,
                    home=self.homej,
                )

                segments = assemble_segments(
                    tcp_offset_mat,
                    checker,
                    validated_runs,
                    surface_joints,
                    self.homej,
                    trace_waypoints,
                    default_normals,
                )

                smoothing(tcp_offset_mat, checker, segments, self.homej)

                normal_plot_index = 0
                while (
                    self.ds.data_path / f"normal_diff_{normal_plot_index}.png"
                ).exists():
                    normal_plot_index += 1
                plot_normal_diff(
                    segments,
                    self.ds.data_path / f"normal_diff_{normal_plot_index}.png",
                    tcp_offset=tcp_offset_mat,
                )

                plan_travels(checker, segments)

                segments = hotfix_j6_correction(segments)

                joint_data[side][color] = segments
                plot_index = 0
                while (self.ds.data_path / f"joint_plan_{plot_index}.png").exists():
                    plot_index += 1
                plot_joint_plan(
                    segments, self.ds.data_path / f"joint_plan_{plot_index}.png"
                )

        if pb.isConnected(checker.cid):
            pb.disconnect(checker.cid)
            print("PyBullet disconnected")

        return joint_data
