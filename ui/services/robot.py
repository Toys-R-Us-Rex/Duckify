from dataclasses import dataclass
from pathlib import Path


@dataclass
class RobotRequest:
    model_path: Path
    trace_path: Path
    filter_mode: str
    tcp_calibration: str
    transformation: str
    enable_gazebo: bool


@dataclass
class RobotResult:
    pass


class RobotService:
    def __init__(self, ip_address: str) -> None:
        self.ip_address: str = ip_address
    
    def run(self, request: RobotRequest) -> RobotResult:
        print("Running robot")
        print(f" - ip: {self.ip_address}")
        print(f" - model: {request.model_path}")
        print(f" - trace: {request.trace_path}")
        print(f" - filter: {request.filter_mode}")
        print(f" - TCP calibration: {request.tcp_calibration}")
        print(f" - transformation: {request.transformation}")
        print(f" - enable Gazebo: {request.enable_gazebo}")
        return RobotResult()
