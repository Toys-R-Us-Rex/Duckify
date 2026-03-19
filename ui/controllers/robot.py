from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject

from ui.assets import AssetRegistry
from ui.dialogs.calibration import CalibrationDialog
from ui.dialogs.pen_calibration import PenCalibrationDialog
from ui.dialogs.transformation import TransformationDialog
from ui.services.robot import RobotRequest, RobotResult, RobotService
from ui.settings_manager import Settings, SettingsManager
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

        settings: Settings = self.settings_manager.load()
        self.service: RobotService = RobotService(ip_address=settings.robot.ip_address)

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
        dialog = CalibrationDialog(self.service.read_tcp, parent=self.ui)
        if dialog.exec():
            calibration: list = dialog.get_points()
            print(f"Calibration: {calibration}")
        self.robot_check_ready()

    def new_transformation(self):
        dialog = TransformationDialog(
            self.assets.transformation_reference, self.service.read_tcp, parent=self.ui
        )
        if dialog.exec():
            points: list = dialog.get_points()
            print(f"Reference points: {points}")
        self.robot_check_ready()

    def new_pen_calibration(self):
        dialog = PenCalibrationDialog(parent=self.ui)
        if dialog.exec():
            calibration: tuple = self.service.read_tcp()
            print(f"Pen 0 position: {calibration}")
        self.robot_check_ready()

    def robot_check_ready(self):
        ready: bool = True
        self.ui.robotRun.setDisabled(not ready)

    def robot_run(self):
        request: RobotRequest = RobotRequest(
            model_path=self.ui.robotModel.currentData(),
            trace_path=self.ui.robotTrace.currentData(),
            filter_mode=self.ui.robotFilter.currentData(),  # TODO: improve with enum ?
            tcp_calibration=self.ui.robotTCPCalibration.currentText(),
            transformation=self.ui.robotTransformation.currentText(),
            enable_gazebo=self.ui.robotEnableGazebo.isChecked(),
        )
        result: RobotResult = self.service.run(request)
