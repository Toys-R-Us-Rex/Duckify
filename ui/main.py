import sys
from pathlib import Path
from typing import Optional

from PyQt6 import QtWidgets
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow

from ui.assets import AssetRegistry
from ui.controllers.gen_ai import GenAIController
from ui.controllers.robot import RobotController
from ui.controllers.tracing import TracingController
from ui.dialogs.settings import SettingsDialog
from ui.settings_manager import Settings, SettingsManager
from ui.ui.main_ui import Ui_MainWindow
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
        self.robot: RobotController = RobotController(
            self, self.assets, self.workspace, self.settings_manager
        )

        self.genAIToTracing.clicked.connect(self.pass_texture_to_tracing)
        self.tracingToRobot.clicked.connect(self.pass_traces_to_robot)

    def closeEvent(self, event):  # pyright: ignore[reportIncompatibleMethodOverride]
        self.workspace.cleanup()
        super().closeEvent(event)

    def apply_settings(self, settings: Settings):
        # TODO
        pass

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


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
