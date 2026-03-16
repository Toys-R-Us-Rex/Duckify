import urllib.request

from PyQt6 import QtWidgets
from settings_manager import GenAISettings, Settings, TracingSettings
from settings_ui import Ui_Dialog


class SettingsDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, current_settings: Settings, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.set_settings(current_settings)

        self.genAITest.clicked.connect(self.test_genai_connection)

    def get_settings(self) -> Settings:
        return Settings(
            genAI=GenAISettings(
                host=self.genAIHost.text(),
                port=self.genAIPort.value(),
            ),
            tracing=TracingSettings(palette=self.get_palette()),
        )

    def set_settings(self, settings: Settings):
        self.genAIHost.setText(settings.genAI.host)
        self.genAIPort.setValue(settings.genAI.port)
        self.set_palette(settings.tracing.palette)

    def get_palette(self) -> list[tuple[int, int, int]]:
        # TODO
        return []

    def set_palette(self, palette: list[tuple[int, int, int]]):
        # TODO
        pass

    def test_genai_connection(self):
        host: str = self.genAIHost.text()
        port: int = self.genAIPort.value()
        try:
            urllib.request.urlopen(f"http://{host}:{port}").read()
            self.set_genai_connection_status("Connection successful")
        except:
            self.set_genai_connection_status("Connection failed")

    def set_genai_connection_status(self, status: str):
        self.genAITestResult.setText(status)
