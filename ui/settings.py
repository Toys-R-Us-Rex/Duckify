import urllib.request
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QColorDialog, QDialog, QListWidgetItem

from ui.settings_manager import GenAISettings, Settings, TracingSettings
from ui.ui.settings_ui import Ui_Dialog
from ui.utils import ping


class SettingsDialog(QDialog, Ui_Dialog):
    def __init__(self, current_settings: Settings, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.set_settings(current_settings)

        self.genAITest.clicked.connect(self.test_genai_connection)
        self.tracingPalette.doubleClicked.connect(self.tracing_palette_edit)
        self.tracingPaletteAdd.clicked.connect(self.tracing_palette_prompt_add)
        self.tracingPaletteRemove.clicked.connect(self.tracing_palette_remove)
        self.robotTest.clicked.connect(self.test_robot_connection)

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
        colors: list[tuple[int, int, int]] = []
        for i in range(self.tracingPalette.count()):
            item: Optional[QListWidgetItem] = self.tracingPalette.item(i)
            if item is None:
                continue
            color: QColor = item.data(Qt.ItemDataRole.UserRole)
            colors.append(
                (
                    color.red(),
                    color.green(),
                    color.blue(),
                )
            )
        return colors

    def set_palette(self, palette: list[tuple[int, int, int]]):
        self.tracingPalette.clear()
        for r, g, b in palette:
            color: QColor = QColor(r, g, b)
            self.tracing_palette_add(color)

    def test_genai_connection(self):
        host: str = self.genAIHost.text()
        port: int = self.genAIPort.value()
        self.genAITestResult.setText("Testing connection...")
        try:
            urllib.request.urlopen(f"http://{host}:{port}").read()
            self.set_genai_connection_status("Connection successful")
        except:
            self.set_genai_connection_status("Connection failed")

    def set_genai_connection_status(self, status: str):
        self.genAITestResult.setText(status)

    def tracing_palette_prompt_add(self):
        dialog = QColorDialog(self)
        if not dialog.exec():
            return

        color: QColor = dialog.currentColor()
        self.tracing_palette_add(color)

    def tracing_palette_add(self, color: QColor):
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
    
    def test_robot_connection(self):
        host: str = self.robotIP.text()
        ports: list[int] = [29999, 30003, 30004]
        self.robotTestResult.setText("Testing connection...")
        for port in ports:
            if ping(host, port):
                self.robotTestResult.setText("Connection successful")
                break
        else:
            self.robotTestResult.setText("Connection failed")
