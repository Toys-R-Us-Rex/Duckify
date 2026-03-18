import shutil
import sys
from pathlib import Path
from typing import Optional

from PyQt6 import QtWidgets
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow

from tracing.color import Color
from tracing.config import TracerConfig
from tracing.stats import TracingStats
from tracing.tracer import Tracer
from ui.assets import AssetRegistry
from ui.calibration import CalibrationDialog
from ui.controllers.gen_ai import GenAIController
from ui.controllers.tracing import TracingController
from ui.mesh_visualizer import MeshVisualizer
from ui.pen_calibration import PenCalibrationDialog
from ui.settings import SettingsDialog
from ui.settings_manager import Settings, SettingsManager
from ui.transformation import TransformationDialog
from ui.ui.main_ui import Ui_MainWindow
from ui.utils import populate_combobox
from ui.workspace import WorkspaceManager

ROOT_DIR: Path = Path(__file__).parent.parent


class App(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.setWindowIcon(QIcon(str(ROOT_DIR / "assets" / "icon.png")))

        self.actionSettings.triggered.connect(self.open_settings)
        self.actionQuit.triggered.connect(QApplication.quit)

        self.settings_manager: SettingsManager = SettingsManager()
        self.apply_settings(self.settings_manager.load())

        self.assets: AssetRegistry = AssetRegistry(ROOT_DIR)
        self.workspace: WorkspaceManager = WorkspaceManager()

        self.gen_ai: GenAIController = GenAIController(
            self, self.assets, self.workspace, self.settings_manager
        )
        self.tracing: TracingController = TracingController(
            self, self.assets, self.workspace, self.settings_manager
        )
        self.setup_robot()

        self.genAIToTracing.clicked.connect(self.pass_texture_to_tracing)
        self.tracingToRobot.clicked.connect(self.pass_traces_to_robot)

    def closeEvent(self, event):  # pyright: ignore[reportIncompatibleMethodOverride]
        self.workspace.cleanup()
        super().closeEvent(event)

    def setup_robot(self):
        populate_combobox(
            self.robotModel, self.assets.list_models("stl"), self.assets.models_dir
        )
        populate_combobox(
            self.robotTrace, self.assets.list_traces(), self.assets.output_dir
        )

        self.robotNewTCPCalibration.clicked.connect(self.new_tcp_calibration)
        self.robotNewTransformation.clicked.connect(self.new_transformation)
        self.robotNewPenCalibration.clicked.connect(self.new_pen_calibration)

        self.robotRun.clicked.connect(self.robot_run)

    def apply_settings(self, settings: Settings):
        print(settings)
        # TODO

    def open_settings(self):
        dialog = SettingsDialog(self.settings_manager.load(), parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.settings_manager.save(dialog.get_settings())
            self.apply_settings(self.settings_manager.load())

    def pass_texture_to_tracing(self):
        model_path: Path = self.genAIModel.currentData()
        texture_path: Optional[Path] = self.gen_ai.get_selected()
        if texture_path is None:
            return

        model_name: str = str(model_path.relative_to(self.assets.models_dir))
        self.tracingModel.addItem(model_name, model_path)
        self.tracingModel.setCurrentIndex(self.tracingModel.count() - 1)

        self.tracingTexture.addItem("Generated texture", texture_path)
        self.tracingTexture.setCurrentIndex(self.tracingTexture.count() - 1)

        self.steps.setCurrentWidget(self.tabTracing)

    def pass_traces_to_robot(self):
        self.robotTrace.addItem("Generated traces", self.workspace.traces_path)
        self.robotTrace.setCurrentIndex(self.robotTrace.count() - 1)

        self.steps.setCurrentWidget(self.tabRobot)

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
        self.robotRun.setDisabled(not ready)

    def robot_run(self):
        model_path: Path = self.robotModel.currentData()
        trace_path: Path = self.robotTrace.currentData()
        filter_mode: str = self.robotFilter.currentData()  # TODO: improve with enum ?

        tcp_calibration: str = self.robotTCPCalibration.currentText()
        transformation: str = self.robotTransformation.currentText()

        enable_gazebo: bool = self.robotEnableGazebo.isChecked()

        settings: Settings = self.settings_manager.load()

        print("Running robot")
        print(f" - ip: {settings.robot.ip_address}")
        print(f" - model: {model_path}")
        print(f" - trace: {trace_path}")
        print(f" - filter: {filter_mode}")
        print(f" - TCP calibration: {tcp_calibration}")
        print(f" - transformation: {transformation}")
        print(f" - enable Gazebo: {enable_gazebo}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
