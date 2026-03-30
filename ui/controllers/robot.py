from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QWidget

from robot.src.conversion import convert_segments
from robot.src.filter import filter_traces
from robot.src.segment import SideType
from robot.src.utils import AtoB
from ui.assets import AssetRegistry
from ui.dialogs.calibration import CalibrationDialog
from ui.dialogs.pen_calibration import PenCalibrationDialog
from ui.dialogs.transformation import TransformationDialog
from ui.models import Point3D, TCPPoint
from ui.services.robot import RobotRequest, RobotResult, RobotService
from ui.settings_manager import Settings, SettingsManager
from ui.utils.misc import populate_combobox, add_and_select_item
from ui.workspace import WorkspaceManager

if TYPE_CHECKING:
    from ui.main import App


class RobotController(QObject):
    def __init__(
        self,
        ui: App,
        assets: AssetRegistry,
        workspace: WorkspaceManager,
        settings_manager: SettingsManager,
    ):
        super().__init__()
        self.ui: App = ui
        self.assets: AssetRegistry = assets
        self.workspace: WorkspaceManager = workspace
        self.settings_manager: SettingsManager = settings_manager

        settings: Settings = self.settings_manager.load()
        self.service: RobotService = RobotService(
            ip_address=settings.robot.ip_address, base_dir=self.workspace.datastore_path
        )
        self.widgets_needing_robot: list[QWidget] = []

        self.setup()

    def setup(self):
        self.widgets_needing_robot = [
            w
            for w in self.ui.findChildren(QWidget)
            if w.property("requireRobot") is True
        ]

        populate_combobox(
            self.ui.robotTrace, self.assets.list_traces(), self.assets.output_dir
        )

        self.ui.robotConnect.toggled.connect(self.connect_change)

        self.ui.robotFreedriveDisable.clicked.connect(
            lambda _: self.service.set_freedrive(False)
        )
        self.ui.robotFreedriveEnable.clicked.connect(
            lambda _: self.service.set_freedrive(True)
        )

        self.ui.robotGripperDeactivate.clicked.connect(
            lambda _: self.set_gripper_activation(False)
        )
        self.ui.robotGripperActivate.clicked.connect(
            lambda _: self.set_gripper_activation(True)
        )
        self.ui.robotGripperClose.clicked.connect(
            lambda _: self.service.set_gripper_state(False)
        )
        self.ui.robotGripperOpen.clicked.connect(
            lambda _: self.service.set_gripper_state(True)
        )

        self.ui.robotNewTCPCalibration.clicked.connect(self.new_tcp_calibration)
        self.ui.robotNewTransformation.clicked.connect(self.new_transformation)
        self.ui.robotNewPenCalibration.clicked.connect(self.new_pen_calibration)

        self.ui.robotLoadTraces.clicked.connect(self.load_traces)

        self.ui.robotRun.clicked.connect(self.robot_run)

        self.connect_change()

    def connect_change(self):
        connected: bool = self.ui.robotConnect.isChecked()
        if connected:
            if not self.service.connect():
                self.ui.robotConnect.setChecked(False)
                connected = False
        else:
            self.service.disconnect()

        tooltip: Optional[str] = None
        if not connected:
            tooltip = "Must be connected to robot"
        for w in self.widgets_needing_robot:
            w.setDisabled(not connected)
            w.setToolTip(tooltip)

    def set_gripper_activation(self, activated: bool):
        if activated:
            self.service.activate_gripper()
        else:
            self.service.deactivate_gripper()
        self.check_gripper_activation()

    def check_gripper_activation(self):
        activated: bool = self.service.is_gripper_activated()
        self.ui.robotGripperClose.setDisabled(not activated)
        self.ui.robotGripperOpen.setDisabled(not activated)

    def new_tcp_calibration(self):
        dialog = CalibrationDialog(self.service, parent=self.ui)
        if dialog.exec():
            tcps: list[TCPPoint] = dialog.get_tcps()
            tcp_offset: TCPPoint = self.service.compute_tcp_offset(tcps)
            path: Path = self.workspace.calibration_path
            exists: bool = path.exists()
            self.service.ds.save_calibration(tcps, tcp_offset, path, use_pickle=False)  # type: ignore

            if not exists:
                add_and_select_item(self.ui.robotTCPCalibration, "Custom", path)
        self.robot_check_ready()

    def new_transformation(self):
        dialog = TransformationDialog(
            self.assets.transformation_reference, self.service, parent=self.ui
        )
        if dialog.exec():
            points: list[tuple[Point3D, TCPPoint]] = dialog.get_pairs()
            path: Path = self.workspace.transformation_path
            exists: bool = path.exists()
            transformation: AtoB = self.service.compute_transformation(points)
            self.service.ds.save_transformation(transformation, path, use_pickle=False)

            if not exists:
                add_and_select_item(self.ui.robotTransformation, "Custom", path)
        self.robot_check_ready()

    def new_pen_calibration(self):
        dialog = PenCalibrationDialog(parent=self.ui)
        if dialog.exec():
            calibration: tuple = self.service.read_tcp()
            print(f"Pen 0 position: {calibration}")
        self.robot_check_ready()
    
    def load_traces(self):
        traces_path: Path = self.ui.robotTrace.currentData()
        side: SideType = SideType.RIGHT
        if self.ui.robotFilter.currentIndex() == 1:
            side = SideType.LEFT
        segments: dict = filter_traces(traces_path, True, side)
        self.service.ds.save_trace_segments(segments, self.workspace.trace_segments_path)

        transformation_path: Path = self.ui.robotTransformation.currentData()
        transformation: AtoB = self.service.ds.load_transformation(transformation_path, use_pickle=False)
        tcp_segments: dict = convert_segments(transformation, segments)
        self.service.ds.save_tcp_segments(tcp_segments, self.workspace.tcp_segments_path)

    def robot_check_ready(self):
        ready: bool = True
        self.ui.robotRun.setDisabled(not ready)

    def robot_run(self):
        request: RobotRequest = RobotRequest(
            trace_path=self.ui.robotTrace.currentData(),
            filter_mode=self.ui.robotFilter.currentData(),  # TODO: improve with enum ?
            tcp_calibration=self.ui.robotTCPCalibration.currentText(),
            transformation=self.ui.robotTransformation.currentText(),
        )
        result: RobotResult = self.service.run(request)
