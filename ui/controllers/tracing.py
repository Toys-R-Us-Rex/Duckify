from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QFileDialog

from tracing.stats import TracingStats
from ui.assets import AssetRegistry
from ui.mesh_visualizer import MeshVisualizer
from ui.services.tracing import TracingRequest, TracingResult, TracingService
from ui.settings_manager import Settings, SettingsManager
from ui.utils.misc import populate_combobox
from ui.workspace import WorkspaceManager

if TYPE_CHECKING:
    from ui.main import App


class TracingController(QObject):
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

        self.service: TracingService = TracingService(
            traces_path=self.workspace.traces_path,
            paletted_texture_path=self.workspace.paletted_texture_path,
        )

        self.setup()

    def setup(self):
        self.ui.actionReloadAssets.triggered.connect(self.populate_comboboxes)
        self.populate_comboboxes()

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

    def populate_comboboxes(self):
        self.ui.tracingModel.clear()
        self.ui.tracingMask.clear()
        self.ui.tracingTexture.clear()
        populate_combobox(
            self.ui.tracingModel,
            self.assets.list_models("obj"),
            self.assets.models_dir,
        )
        populate_combobox(
            self.ui.tracingMask,
            self.assets.list_masks(),
            self.assets.masks_dir,
        )
        populate_combobox(
            self.ui.tracingTexture,
            self.assets.list_textures(),
            self.assets.textures_dir,
        )

    def start_tracing(self):
        print("Starting tracing")

        settings: Settings = self.settings_manager.load()

        request: TracingRequest = TracingRequest(
            model_path=self.ui.tracingModel.currentData(),
            mask_path=self.ui.tracingMask.currentData(),
            texture_path=self.ui.tracingTexture.currentData(),
            palette=settings.tracing.palette,
            enable_fill_slicing=self.ui.tracingEnableFill.isChecked(),
        )

        result: TracingResult = self.service.run(
            request, on_progress=self.update_progress
        )
        self.show_result(request, result)

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
        request: TracingRequest,
        result: TracingResult,
    ):
        self.set_stats(result.stats)
        self.visualizer.load_model(request.model_path)
        self.visualizer.clear_textures()
        self.visualizer.add_texture(request.texture_path)
        if result.paletted_texture_path is not None:
            self.visualizer.add_texture(result.paletted_texture_path)
        self.visualizer.load_traces(result.traces_path)

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
