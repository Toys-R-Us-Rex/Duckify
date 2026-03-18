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
    IGNORED_COLOR: Color = (0, 0, 0)

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

        self.setup_tracing()
        self.setup_robot()

        self.genAIToTracing.clicked.connect(self.pass_texture_to_tracing)

    def closeEvent(self, event):  # pyright: ignore[reportIncompatibleMethodOverride]
        self.workspace.cleanup()
        super().closeEvent(event)

    def setup_tracing(self):
        populate_combobox(
            self.tracingModel, self.assets.list_models("obj"), self.assets.models_dir
        )
        populate_combobox(
            self.tracingTexture, self.assets.list_textures(), self.assets.textures_dir
        )

        self.tracingTrace.clicked.connect(self.start_tracing)

        traces_visualizer: MeshVisualizer = MeshVisualizer(self)
        self.tracingVisual.parentWidget().layout().replaceWidget(self.tracingVisual, traces_visualizer)  # type: ignore
        self.tracingVisual.deleteLater()
        self.tracingVisual = traces_visualizer
        self.tracingVisualAltitude.valueChanged.connect(traces_visualizer.set_altitude)
        self.tracingVisualAzimuth.valueChanged.connect(traces_visualizer.set_azimuth)
        self.tracingVisualLayerMesh.toggled.connect(self.update_tracing_visual_layer)
        self.tracingVisualLayerTexture.toggled.connect(self.update_tracing_visual_layer)
        self.tracingVisualLayerPalettized.toggled.connect(
            self.update_tracing_visual_layer
        )

        self.tracingSaveAs.clicked.connect(self.prompt_save_traces)
        self.tracingToRobot.clicked.connect(self.pass_traces_to_robot)

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

    def start_tracing(self):
        print("Starting tracing")

        settings: Settings = self.settings_manager.load()

        model_path: Path = self.tracingModel.currentData()
        texture_path: Path = self.tracingTexture.currentData()
        traces_path: Path = self.workspace.traces_path
        paletted_path: Path = self.workspace.paletted_texture_path

        config: TracerConfig = TracerConfig(
            enable_fill_slicing=self.tracingEnableFill.isChecked()
        )

        palette: list[Color] = settings.tracing.palette

        tracer: Tracer = Tracer(
            config, texture_path, model_path, tuple(palette), self.IGNORED_COLOR
        )
        stats: TracingStats = tracer.compute_traces(
            progress_callback=self.update_tracing_progress
        )

        tracer.export_traces(traces_path, force=True)
        if tracer.paletted_texture is not None:
            tracer.paletted_texture.save(paletted_path)

        self.set_tracing_stats(stats)
        self.show_tracing_result(model_path, texture_path, traces_path, paletted_path)

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

    def update_tracing_progress(self, current: int, maximum: int, label: str):
        self.tracingProgressLabel.setText(label)
        self.tracingProgress.setMaximum(maximum)
        self.tracingProgress.setValue(current)

    def set_tracing_stats(self, stats: TracingStats):
        self.tracingStatIslands.setText(str(stats.n_islands))
        self.tracingStat2DTraces.setText(str(stats.n_2d_traces))
        self.tracingStat3DTraces.setText(str(stats.n_3d_traces))
        self.tracingStatPoints.setText(str(stats.n_points))

    def show_tracing_result(
        self,
        model_path: Path,
        texture_path: Path,
        traces_path: Path,
        paletted_texture_path: Path,
    ):
        self.tracingVisual.load_model(model_path)
        self.tracingVisual.clear_textures()
        self.tracingVisual.add_texture(texture_path)
        self.tracingVisual.add_texture(paletted_texture_path)
        self.tracingVisual.load_traces(traces_path)

        self.update_tracing_visual_layer()

    def update_tracing_visual_layer(self):
        if self.tracingVisualLayerMesh.isChecked():
            self.tracingVisual.show_texture(None)
        elif self.tracingVisualLayerTexture.isChecked():
            self.tracingVisual.show_texture(0)
        elif self.tracingVisualLayerPalettized.isChecked():
            self.tracingVisual.show_texture(1)

    def prompt_save_traces(self):
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save traces", str(self.assets.output_dir), "Traces (*.json)"
        )
        if save_path.strip() == "":
            return
        shutil.copy(self.workspace.traces_path, save_path)

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
