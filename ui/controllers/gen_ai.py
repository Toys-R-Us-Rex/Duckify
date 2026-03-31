from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PyQt6.QtCore import QModelIndex, QObject, QThreadPool, pyqtSignal
from PyQt6.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from ui.assets import AssetRegistry
from ui.mesh_visualizer import MeshVisualizer
from ui.services.gen_ai import GenAIRequest, GenAIResult, GenAIService
from ui.settings_manager import Settings, SettingsManager
from ui.utils.misc import populate_combobox
from ui.utils.worker import Worker
from ui.workspace import WorkspaceManager

if TYPE_CHECKING:
    from ui.main import App


class GenAIController(QObject):
    to_tracing: pyqtSignal = pyqtSignal(Path, Path)

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

        self.result_model: QStandardItemModel = QStandardItemModel(self.ui.genAIResults)
        settings: Settings = self.settings_manager.load()
        self.service: GenAIService = GenAIService(
            ssh_host=settings.genAI.ssh_host,
            ssh_port=settings.genAI.ssh_port,
            ssh_user=settings.genAI.ssh_user,
            ssh_key_path=Path(settings.genAI.ssh_key),
            host=settings.genAI.host,
            port=settings.genAI.port,
            hf_token=settings.genAI.hf_token
        )

        self.setup()

    def setup(self):
        self.settings_manager.changed.connect(self.on_settings_changed)

        self.ui.actionReloadAssets.triggered.connect(self.populate_comboboxes)
        self.populate_comboboxes()

        # Result visualizer
        self.visualizer: MeshVisualizer = MeshVisualizer(self.ui)
        self.ui.genAIVisualizerGroup.layout().replaceWidget(self.ui.genAIVisual, self.visualizer)  # type: ignore
        self.ui.genAIVisual.deleteLater()
        self.ui.genAIVisual = self.visualizer
        self.ui.genAIVisualAltitude.valueChanged.connect(self.visualizer.set_altitude)
        self.ui.genAIVisualAzimuth.valueChanged.connect(self.visualizer.set_azimuth)

        self.ui.genAIGenerate.clicked.connect(self.generate_texture)
        self.ui.genAIResults.clicked.connect(self.select_result)
        self.ui.genAIResults.setModel(self.result_model)

        self.ui.genAISaveAs.clicked.connect(self.prompt_save)
    
    def on_settings_changed(self, settings: Settings):
        self.service.host = settings.genAI.host
        self.service.port = settings.genAI.port
    
    def populate_comboboxes(self):
        self.ui.genAIModel.clear()
        populate_combobox(
            self.ui.genAIModel, self.assets.list_models("obj"), self.assets.models_dir
        )

        self.visualizer.load_model(self.ui.genAIModel.currentData())
        self.ui.genAIModel.currentIndexChanged.connect(self.reload_model)

    def reload_model(self):
        self.visualizer.load_model(self.ui.genAIModel.currentData())

    def generate_texture(self):
        settings: Settings = self.settings_manager.load()
        request: GenAIRequest = GenAIRequest(
            model_path=self.ui.genAIModel.currentData(),
            prompt=self.ui.genAIPrompt.toPlainText(),
            negative_prompt=settings.genAI.negative_prompt,
            prompt_wrapper=settings.genAI.prompt_wrapper,
            steps=settings.genAI.steps,
            guidance=settings.genAI.guidance,
            output_dir=self.assets.output_dir,
        )
        worker = Worker(self.service.run, request)
        self.ui.genAIGenerate.setDisabled(True)
        self.ui.genAIProgress.setRange(0, 0)
        worker.signals.finished.connect(self.on_done)
        worker.signals.error.connect(self.on_error)
        QThreadPool.globalInstance().start(worker)  # type: ignore

    def on_done(self, result: GenAIResult):
        if result.texture_path is None:
            self.on_error(result.error)
            return
        self.add_result(result.texture_path)
        self.ui.genAIGenerate.setDisabled(False)
        self.ui.genAIProgress.setRange(0, 1)
        self.ui.genAIProgress.setValue(1)
    
    def on_error(self, err):
        self.ui.genAIGenerate.setDisabled(False)
        self.ui.genAIProgress.setRange(0, 1)
        self.ui.genAIProgress.setValue(0)
        QMessageBox.critical(
            self.ui,
            "Error",
            f"The following error occured:\n{err}",
        )

    def set_results(self, results: list[Path]):
        for result in results:
            self.add_result(result)

    def add_result(self, result: Path):
        item = QStandardItem(
            QIcon(str(result)), str(result.name)
        )
        item.setData(result)
        item.setEditable(False)
        self.result_model.appendRow(item)

    def get_selected(self) -> Optional[Path]:
        index: QModelIndex = self.ui.genAIResults.currentIndex()
        item: Optional[QStandardItem] = self.result_model.itemFromIndex(index)
        if item is None:
            return None
        return item.data()

    def select_result(self):
        path: Optional[Path] = self.get_selected()
        if path is None:
            return
        print(f"Selected {path}")
        self.visualizer.clear_textures()
        self.visualizer.add_texture(path)
        self.visualizer.show_texture(0)

    def prompt_save(self):
        texture_path: Optional[Path] = self.get_selected()
        if texture_path is None:
            return
        save_path, _ = QFileDialog.getSaveFileName(
            self.ui,
            "Save generated texture",
            str(self.assets.textures_dir),
            "Images (*.png *.jpg)",
        )
        if save_path.strip() == "":
            return
        shutil.copy(texture_path, save_path)
