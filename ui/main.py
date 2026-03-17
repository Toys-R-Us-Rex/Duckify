import shutil
import sys
import tempfile
from pathlib import Path
from typing import Optional

from PyQt6 import QtWidgets
from PyQt6.QtCore import QModelIndex
from PyQt6.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QFileDialog

from tracing.color import Color
from tracing.config import TracerConfig
from tracing.stats import TracingStats
from tracing.tracer import Tracer
from ui.calibration import CalibrationDialog
from ui.main_ui import Ui_MainWindow
from ui.mesh_visualizer import MeshVisualizer
from ui.pen_calibration import PenCalibrationDialog
from ui.settings import SettingsDialog
from ui.settings_manager import Settings, SettingsManager
from ui.transformation import TransformationDialog

ROOT_DIR: Path = Path(__file__).parent.parent


class App(QtWidgets.QMainWindow, Ui_MainWindow):
    MODELS_DIR: Path = ROOT_DIR / "assets" / "models"
    TEXTURES_DIR: Path = ROOT_DIR / "assets" / "textures"
    OUTPUT_DIR: Path = ROOT_DIR / "output"
    IGNORED_COLOR: Color = (0, 0, 0)

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.actionSettings.triggered.connect(self.open_settings)
        self.actionQuit.triggered.connect(QApplication.quit)

        self.settings_manager: SettingsManager = SettingsManager()
        self.apply_settings(self.settings_manager.load())

        self.gen_ai_result_model: QStandardItemModel = QStandardItemModel(
            self.genAIResults
        )
        working_dir = tempfile.TemporaryDirectory(prefix="duckify_")
        self.working_dir: Path = Path(working_dir.name)

        self.setup_gen_ai()
        self.setup_tracing()
        self.setup_robot()

    @property
    def texture_path(self) -> Path:
        return self.working_dir / "texture.png"

    @property
    def traces_path(self) -> Path:
        return self.working_dir / "traces.json"

    def setup_gen_ai(self):
        for model_path in self.list_models("obj"):
            name: str = str(model_path.relative_to(self.MODELS_DIR))
            self.genAIModel.addItem(name, model_path)

        # Result visualizer
        result_visualizer: MeshVisualizer = MeshVisualizer(self)
        self.genAIVisualizerGroup.layout().replaceWidget(self.genAIVisual, result_visualizer)  # type: ignore
        self.genAIVisual.deleteLater()
        self.genAIVisual = result_visualizer
        self.genAIVisualAltitude.valueChanged.connect(result_visualizer.set_altitude)
        self.genAIVisualAzimuth.valueChanged.connect(result_visualizer.set_azimuth)

        self.genAIGenerate.clicked.connect(self.generate_texture)
        self.genAIResults.clicked.connect(self.select_gen_ai_result)

        self.genAISaveAs.clicked.connect(self.prompt_save_texture)
        self.genAIToTracing.clicked.connect(self.pass_texture_to_tracing)

    def setup_tracing(self):
        for model_path in self.list_models("obj"):
            name: str = str(model_path.relative_to(self.MODELS_DIR))
            self.tracingModel.addItem(name, model_path)

        for texture_path in self.list_textures():
            name: str = str(texture_path.relative_to(self.TEXTURES_DIR))
            self.tracingTexture.addItem(name, texture_path)

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
        for model_path in self.list_models("stl"):
            name: str = str(model_path.relative_to(self.MODELS_DIR))
            self.robotModel.addItem(name, model_path)

        for trace_path in self.list_traces():
            name: str = str(trace_path.relative_to(self.OUTPUT_DIR))
            self.robotTrace.addItem(name, trace_path)

        self.robotNewTCPCalibration.clicked.connect(self.new_tcp_calibration)
        self.robotNewTransformation.clicked.connect(self.new_transformation)
        self.robotNewPenCalibration.clicked.connect(self.new_pen_calibration)

    def list_models(self, extension: str) -> list[Path]:
        return list(self.MODELS_DIR.glob(f"*.{extension}"))

    def list_textures(self) -> list[Path]:
        return list(self.TEXTURES_DIR.iterdir())

    def list_traces(self) -> list[Path]:
        return list(self.OUTPUT_DIR.glob("*-trace.json"))

    def apply_settings(self, settings: Settings):
        print(settings)
        # TODO

    def open_settings(self):
        dialog = SettingsDialog(self.settings_manager.load(), parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.settings_manager.save(dialog.get_settings())
            self.apply_settings(self.settings_manager.load())

    def generate_texture(self):
        model_path: Path = self.genAIModel.currentData()
        prompt: str = self.genAIPrompt.toPlainText()
        # TODO: Call GenAI endpoint
        print("Generating texture")
        self.set_texture_results(list(self.TEXTURES_DIR.iterdir()))

    def start_tracing(self):
        print("Starting tracing")

        settings: Settings = self.settings_manager.load()

        model_path: Path = self.tracingModel.currentData()
        texture_path: Path = self.tracingTexture.currentData()

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
        tracer.export_traces(self.traces_path, force=True)
        paletted_texture_path: Path = self.working_dir / "paletted.png"
        if tracer.paletted_texture is not None:
            tracer.paletted_texture.save(paletted_texture_path)

        self.set_tracing_stats(stats)
        self.show_tracing_result(
            model_path, texture_path, self.traces_path, paletted_texture_path
        )

    def set_texture_results(self, results: list[Path]):
        model: QStandardItemModel = self.gen_ai_result_model
        for result in results:
            item = QStandardItem(
                QIcon(str(result)), str(result.relative_to(self.TEXTURES_DIR))
            )
            item.setData(result)
            item.setEditable(False)
            model.appendRow(item)

        self.genAIResults.setModel(model)
        self.genAIVisual.load_model(self.genAIModel.currentData())

    def get_selected_genai_texture(self) -> Optional[Path]:
        index: QModelIndex = self.genAIResults.currentIndex()
        item: Optional[QStandardItem] = self.gen_ai_result_model.itemFromIndex(index)
        if item is None:
            return None
        return item.data()

    def select_gen_ai_result(self):
        path: Optional[Path] = self.get_selected_genai_texture()
        if path is None:
            return
        print(f"Selected {path}")
        self.genAIVisual.clear_textures()
        self.genAIVisual.add_texture(path)
        self.genAIVisual.show_texture(0)

    def prompt_save_texture(self):
        texture_path: Optional[Path] = self.get_selected_genai_texture()
        if texture_path is None:
            return
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save generated texture",
            str(self.TEXTURES_DIR),
            "Images (*.png *.jpg)",
        )
        if save_path.strip() == "":
            return
        shutil.copy(texture_path, save_path)

    def pass_texture_to_tracing(self):
        model_path: Path = self.genAIModel.currentData()
        texture_path: Optional[Path] = self.get_selected_genai_texture()
        if texture_path is None:
            return

        model_name: str = str(model_path.relative_to(self.MODELS_DIR))
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
            self, "Save traces", str(self.OUTPUT_DIR), "Traces (*.json)"
        )
        if save_path.strip() == "":
            return
        shutil.copy(self.traces_path, save_path)

    def pass_traces_to_robot(self):
        pass

    def new_tcp_calibration(self):
        dialog = CalibrationDialog(self)
        dialog.exec()

    def new_transformation(self):
        dialog = TransformationDialog(self)
        dialog.exec()

    def new_pen_calibration(self):
        dialog = PenCalibrationDialog(self)
        dialog.exec()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
