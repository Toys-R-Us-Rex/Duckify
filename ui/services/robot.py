from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from robot.src.calibration import get_tcp_offset
from robot.src.logger import DataStore
from robot.urbasic.URBasic.devices.robotiq_two_fingers_gripper import (
    RobotiqTwoFingersGripper,
)
from robot.urbasic.URBasic.iscoin import ISCoin
from robot.urbasic.URBasic.urScriptExt import UrScriptExt
from robot.urbasic.URBasic.waypoint6d import TCP6D
from ui.models import TCPPoint


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


class RobotService:
    def __init__(self, ip_address: str, base_dir: Path) -> None:
        self.ip_address: str = ip_address
        self._robot: Optional[ISCoin] = None
        base_dir.mkdir(parents=True, exist_ok=True)
        self.ds: DataStore = DataStore(base_dir)

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

    def deactivate_gripper(self):
        self.gripper.deactivate()

    def is_gripper_activated(self) -> bool:
        return self.gripper.isActivated()
