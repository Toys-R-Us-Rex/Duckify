from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QComboBox, QFileDialog, QMessageBox, QWidget
from URBasic.waypoint6d import TCP6D

from robot.src.conversion import convert_segments
from robot.src.filter import filter_traces
from robot.src.segment import SideType
from robot.src.utils import AtoB
from ui.assets import AssetRegistry
from ui.dialogs.calibration import CalibrationDialog
from ui.dialogs.pen_calibration import PenCalibrationDialog
from ui.dialogs.transformation import TransformationDialog
from ui.models import Point3D, TCPPoint
from ui.services.robot import (
    RobotRequest,
    RobotResult,
    RobotService,
    tcp6d_to_tcppoint,
    tcppoint_to_tcp6d,
)
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
            ip_address=settings.robot.ip_address,
            base_dir=self.workspace.datastore_path,
            assets=self.assets,
            log_func=self.log,
        )
        self.widgets_needing_robot: list[QWidget] = []

        self.setup()

    def setup(self):
        self.settings_manager.changed.connect(self.on_settings_changed)
        self.widgets_needing_robot = [
            w
            for w in self.ui.findChildren(QWidget)
            if w.property("requireRobot") is True
        ]

        self.ui.actionReloadAssets.triggered.connect(self.populate_comboboxes)
        self.populate_comboboxes()

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

        self.loaded_tcp_calibration: bool = False
        self.loaded_transformation: bool = False
        self.ui.robotLoadTCPCalibration.clicked.connect(self.load_tcp_calibration)
        self.ui.robotLoadTransformation.clicked.connect(self.load_transformation)
        self.ui.robotNewTCPCalibration.clicked.connect(self.new_tcp_calibration)
        self.ui.robotNewTransformation.clicked.connect(self.new_transformation)
        self.ui.robotNewPenCalibration.clicked.connect(self.new_pen_calibration)

        self.ui.robotLoadTraces.clicked.connect(self.load_traces)

        self.ui.robotPathfind.clicked.connect(self.run_pathfind)

        self.ui.robotShowPlanAnim.clicked.connect(self.show_plan_animation)

        self.ui.robotRun.clicked.connect(self.robot_run)

        self.connect_change()

    def on_settings_changed(self, settings: Settings):
        self.service.change_ip(settings.robot.ip_address)

    def populate_comboboxes(self):
        self.ui.robotTrace.clear()
        populate_combobox(
            self.ui.robotTrace, self.assets.list_traces(), self.assets.output_dir
        )

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

        if connected:
            self.check_gripper_activation()

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

    def load_tcp_calibration(self):
        path_str, _ = QFileDialog.getOpenFileName(
            self.ui,
            "Open TCP calibration",
            str(self.assets.root_dir),
            "Calibrations (*.pkl *.json)",
        )
        if path_str.strip() == "":
            return
        path: Path = Path(path_str)
        box: QComboBox = self.ui.robotTCPCalibration
        idx: int = box.findText("Loaded")
        if idx == -1:
            add_and_select_item(box, "Loaded", path)
            self.loaded_tcp_calibration = True
        else:
            box.setItemData(idx, path)
            box.setCurrentIndex(idx)

    def load_transformation(self):
        path_str, _ = QFileDialog.getOpenFileName(
            self.ui,
            "Open transformation",
            str(self.assets.root_dir),
            "Transformations (*.pkl *.json)",
        )
        if path_str.strip() == "":
            return
        path: Path = Path(path_str)
        box: QComboBox = self.ui.robotTransformation
        idx: int = box.findText("Loaded")
        if idx == -1:
            add_and_select_item(box, "Loaded", path)
            self.loaded_transformation = True
        else:
            box.setItemData(idx, path)
            box.setCurrentIndex(idx)

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
        self.ui.statusbar.showMessage("TCP calibration successful")

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
        self.ui.statusbar.showMessage("Transformation recording successful")

    def new_pen_calibration(self):
        dialog = PenCalibrationDialog(parent=self.ui)
        if dialog.exec():
            origin: TCP6D = tcppoint_to_tcp6d(self.service.read_tcp())
            self.service.ds.save_pen_calibration(
                origin, origin, self.workspace.pen_origin_path
            )
        self.robot_check_ready()
        self.ui.statusbar.showMessage("Pen calibration successful")

    def load_traces(self):
        traces_path: Path = self.ui.robotTrace.currentData()
        side: SideType = SideType.RIGHT
        if self.ui.robotFilter.currentIndex() == 1:
            side = SideType.LEFT
        segments: dict = filter_traces(traces_path, False, side)
        self.service.ds.save_trace_segments(
            segments, self.workspace.trace_segments_path
        )

        transformation: AtoB = self.get_transformation()
        tcp_segments: dict = convert_segments(transformation, segments)
        self.service.ds.save_tcp_segments(
            tcp_segments, self.workspace.tcp_segments_path
        )
        self.ui.robotStepPlanning.setDisabled(False)
        self.ui.statusbar.showMessage("Traces loaded, filtered and converted")

    def run_pathfind(self):
        tcp_segments: dict = self.service.ds.load_tcp_segments(
            self.workspace.tcp_segments_path
        )
        joint_segments: dict = self.service.plan_paths(
            obj2robot=self.get_transformation(),
            data=tcp_segments,
            tcp_offset=self.get_tcp_calibration(),
        )
        self.service.ds.save_joint_segments(joint_segments, self.workspace.joint_segments_path)  # type: ignore
        self.ui.statusbar.showMessage("Pathfind successful")

        self.ui.robotStepValidation.setDisabled(False)
        self.ui.robotStepExecution.setDisabled(False)

    def robot_check_ready(self):
        ready: bool = True
        self.ui.robotRun.setDisabled(not ready)

    def show_plan_animation(self):
        obj2robot = self.get_transformation()
        tcp_offset = self.get_tcp_calibration()
        joint_segments: dict = self.service.ds.load_joint_segments(self.workspace.joint_segments_path)  # type: ignore
        self.service.show_plan_animation(obj2robot, tcp_offset, joint_segments)

    def robot_run(self):
        joint_segments: dict = self.service.ds.load_joint_segments(self.workspace.joint_segments_path)  # type: ignore
        pen_origins: Optional[tuple[TCPPoint, TCPPoint]] = None
        if self.workspace.pen_origin_path.exists():
            p1, p2 = self.service.ds.load_pen_calibration(
                self.workspace.pen_origin_path
            )
            pen_origins = (
                tcp6d_to_tcppoint(p1),
                tcp6d_to_tcppoint(p2),
            )

        request: RobotRequest = RobotRequest(
            tcp_offset=self.get_tcp_calibration(),
            joint_segments=joint_segments,
            pen_origins=pen_origins,
        )

        ans = QMessageBox.question(
            self.ui,
            "Confirm execution",
            "Do you want to run the trajectory on the REAL robot ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if ans != QMessageBox.StandardButton.Yes:
            return

        result: RobotResult = self.service.run(
            request, on_progress=self.update_execution_progress
        )
        if result.error is not None:
            QMessageBox.critical(
                self.ui, "Error", f"The following error occurred:\n{result.error}"
            )

    @property
    def tcp_calibration_path(self) -> Path:
        path: Optional[Path] = self.ui.robotTCPCalibration.currentData()
        if path is None:
            return self.assets.default_tcp_calibration_path
        return path

    @property
    def transformation_path(self) -> Path:
        path: Optional[Path] = self.ui.robotTransformation.currentData()
        if path is None:
            return self.assets.test_transformation_path
        return path

    def get_tcp_calibration(self) -> TCPPoint:
        path: Path = self.tcp_calibration_path
        _, offset = self.service.ds.load_calibration(
            path, use_pickle=path.suffix == ".pkl"
        )
        return tcp6d_to_tcppoint(offset)

    def get_transformation(self) -> AtoB:
        path: Path = self.transformation_path
        obj2robot: AtoB = self.service.ds.load_transformation(
            path, use_pickle=path.suffix == ".pkl"
        )
        return obj2robot

    def update_execution_progress(self, current: int, maximum: int):
        self.ui.robotProgress.setMaximum(maximum)
        self.ui.robotProgress.setValue(current)

    def log(self, message: str):
        self.ui.robotLogs.addItem(message)
