from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject

from ui.assets import AssetRegistry
from ui.calibration import CalibrationDialog
from ui.pen_calibration import PenCalibrationDialog
from ui.settings_manager import Settings, SettingsManager
from ui.transformation import TransformationDialog
from ui.utils import populate_combobox
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

        self.setup()

    def setup(self):
        populate_combobox(
            self.ui.robotModel, self.assets.list_models("stl"), self.assets.models_dir
        )
        populate_combobox(
            self.ui.robotTrace, self.assets.list_traces(), self.assets.output_dir
        )

        self.ui.robotNewTCPCalibration.clicked.connect(self.new_tcp_calibration)
        self.ui.robotNewTransformation.clicked.connect(self.new_transformation)
        self.ui.robotNewPenCalibration.clicked.connect(self.new_pen_calibration)

        self.ui.robotRun.clicked.connect(self.robot_run)

    def new_tcp_calibration(self):
        dialog = CalibrationDialog(self)
        dialog.exec()
        self.robot_check_ready()

    def new_transformation(self):
        dialog = TransformationDialog(self.assets.transformation_reference, parent=self)
        dialog.exec()
        self.robot_check_ready()

    def new_pen_calibration(self):
        dialog = PenCalibrationDialog(self)
        dialog.exec()
        self.robot_check_ready()

    def robot_check_ready(self):
        ready: bool = True
        self.ui.robotRun.setDisabled(not ready)

    def robot_run(self):
        model_path: Path = self.ui.robotModel.currentData()
        trace_path: Path = self.ui.robotTrace.currentData()
        filter_mode: str = (
            self.ui.robotFilter.currentData()
        )  # TODO: improve with enum ?

        tcp_calibration: str = self.ui.robotTCPCalibration.currentText()
        transformation: str = self.ui.robotTransformation.currentText()

        enable_gazebo: bool = self.ui.robotEnableGazebo.isChecked()

        settings: Settings = self.settings_manager.load()

        print("Running robot")
        print(f" - ip: {settings.robot.ip_address}")
        print(f" - model: {model_path}")
        print(f" - trace: {trace_path}")
        print(f" - filter: {filter_mode}")
        print(f" - TCP calibration: {tcp_calibration}")
        print(f" - transformation: {transformation}")
        print(f" - enable Gazebo: {enable_gazebo}")
