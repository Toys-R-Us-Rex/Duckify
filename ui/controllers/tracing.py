from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtWidgets import QFileDialog

from tracing.color import Color
from tracing.config import TracerConfig
from tracing.stats import TracingStats
from tracing.tracer import Tracer
from ui.assets import AssetRegistry
from ui.mesh_visualizer import MeshVisualizer
from ui.settings_manager import Settings, SettingsManager
from ui.utils import populate_combobox
from ui.workspace import WorkspaceManager

if TYPE_CHECKING:
    from ui.main import App


class TracingController(QObject):
    IGNORED_COLOR: Color = (0, 0, 0)

    to_robot: pyqtSignal = pyqtSignal(Path, Path)

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
            self.ui.tracingModel, self.assets.list_models("obj"), self.assets.models_dir
        )
        populate_combobox(
            self.ui.tracingTexture,
            self.assets.list_textures(),
            self.assets.textures_dir,
        )

        self.ui.tracingTrace.clicked.connect(self.start_tracing)

        self.visualizer: MeshVisualizer = MeshVisualizer(self.ui)
        self.ui.tracingVisual.parentWidget().layout().replaceWidget(self.ui.tracingVisual, self.visualizer)  # type: ignore
        self.ui.tracingVisual.deleteLater()
        self.ui.tracingVisual = self.visualizer
        self.ui.tracingVisualAltitude.valueChanged.connect(self.visualizer.set_altitude)
        self.ui.tracingVisualAzimuth.valueChanged.connect(self.visualizer.set_azimuth)
        self.ui.tracingVisualLayerMesh.toggled.connect(self.update_visual_layer)
        self.ui.tracingVisualLayerTexture.toggled.connect(self.update_visual_layer)
        self.ui.tracingVisualLayerPalettized.toggled.connect(self.update_visual_layer)

        self.ui.tracingSaveAs.clicked.connect(self.prompt_save)

    def start_tracing(self):
        print("Starting tracing")

        settings: Settings = self.settings_manager.load()

        model_path: Path = self.ui.tracingModel.currentData()
        texture_path: Path = self.ui.tracingTexture.currentData()
        traces_path: Path = self.workspace.traces_path
        paletted_path: Path = self.workspace.paletted_texture_path

        config: TracerConfig = TracerConfig(
            enable_fill_slicing=self.ui.tracingEnableFill.isChecked()
        )

        palette: list[Color] = settings.tracing.palette

        tracer: Tracer = Tracer(
            config, texture_path, model_path, tuple(palette), self.IGNORED_COLOR
        )
        stats: TracingStats = tracer.compute_traces(
            progress_callback=self.update_progress
        )

        tracer.export_traces(traces_path, force=True)
        if tracer.paletted_texture is not None:
            tracer.paletted_texture.save(paletted_path)

        self.set_stats(stats)
        self.show_result(model_path, texture_path, traces_path, paletted_path)

    def update_progress(self, current: int, maximum: int, label: str):
        self.ui.tracingProgressLabel.setText(label)
        self.ui.tracingProgress.setMaximum(maximum)
        self.ui.tracingProgress.setValue(current)

    def set_stats(self, stats: TracingStats):
        self.ui.tracingStatIslands.setText(str(stats.n_islands))
        self.ui.tracingStat2DTraces.setText(str(stats.n_2d_traces))
        self.ui.tracingStat3DTraces.setText(str(stats.n_3d_traces))
        self.ui.tracingStatPoints.setText(str(stats.n_points))

    def show_result(
        self,
        model_path: Path,
        texture_path: Path,
        traces_path: Path,
        paletted_texture_path: Path,
    ):
        self.visualizer.load_model(model_path)
        self.visualizer.clear_textures()
        self.visualizer.add_texture(texture_path)
        self.visualizer.add_texture(paletted_texture_path)
        self.visualizer.load_traces(traces_path)

        self.update_visual_layer()

    def update_visual_layer(self):
        if self.ui.tracingVisualLayerMesh.isChecked():
            self.visualizer.show_texture(None)
        elif self.ui.tracingVisualLayerTexture.isChecked():
            self.visualizer.show_texture(0)
        elif self.ui.tracingVisualLayerPalettized.isChecked():
            self.visualizer.show_texture(1)

    def prompt_save(self):
        save_path, _ = QFileDialog.getSaveFileName(
            self.ui, "Save traces", str(self.assets.output_dir), "Traces (*.json)"
        )
        if save_path.strip() == "":
            return
        shutil.copy(self.workspace.traces_path, save_path)
