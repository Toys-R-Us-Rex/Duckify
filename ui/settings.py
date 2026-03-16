from typing import Optional
import urllib.request

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QColorDialog, QDialog, QListWidgetItem
from settings_manager import GenAISettings, Settings, TracingSettings
from settings_ui import Ui_Dialog


class SettingsDialog(QDialog, Ui_Dialog):
    def __init__(self, current_settings: Settings, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.set_settings(current_settings)

        self.genAITest.clicked.connect(self.test_genai_connection)
        self.tracingPalette.doubleClicked.connect(self.tracing_palette_edit)
        self.tracingPaletteAdd.clicked.connect(self.tracing_palette_add)
        self.tracingPaletteRemove.clicked.connect(self.tracing_palette_remove)

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

    def tracing_palette_add(self):
        dialog = QColorDialog(self)
        if not dialog.exec():
            return

        color: QColor = dialog.currentColor()
        pixmap = QPixmap(16, 16)
        pixmap.fill(color)
        item = QListWidgetItem(QIcon(pixmap), color.name())
        item.setData(Qt.ItemDataRole.UserRole, color)
        self.tracingPalette.addItem(item)

    def tracing_palette_remove(self):
        current: Optional[QListWidgetItem] = self.tracingPalette.currentItem()
        if current is not None:
            row: int = self.tracingPalette.row(current)
            self.tracingPalette.takeItem(row)
    
    def tracing_palette_edit(self):
        current: Optional[QListWidgetItem] = self.tracingPalette.currentItem()
        if current is None:
            return
        color: QColor = current.data(Qt.ItemDataRole.UserRole)
        
        dialog = QColorDialog(self)
        dialog.setCurrentColor(color)
        if not dialog.exec():
            return

        color = dialog.currentColor()
        pixmap = QPixmap(16, 16)
        pixmap.fill(color)
        current.setData(Qt.ItemDataRole.UserRole, color)
        current.setText(color.name())
        current.setIcon(QIcon(pixmap))
