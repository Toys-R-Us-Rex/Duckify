from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QColorDialog, QDialog, QFileDialog, QLabel, QListWidgetItem

from genai.client import GenAIClient
from ui.settings_manager import GenAISettings, RobotSettings, Settings, TracingSettings
from ui.ui.settings_ui import Ui_Dialog
from ui.utils import ping


class SettingsDialog(QDialog, Ui_Dialog):
    def __init__(self, current_settings: Settings, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.set_settings(current_settings)

        self.genAISSHKeyBrowse.clicked.connect(self.browse_ssh_key)
        self.genAISSHTest.clicked.connect(self.test_genai_ssh_connection)
        self.genAITest.clicked.connect(self.test_genai_server_connection)
        self.tracingPalette.doubleClicked.connect(self.tracing_palette_edit)
        self.tracingPaletteAdd.clicked.connect(self.tracing_palette_prompt_add)
        self.tracingPaletteRemove.clicked.connect(self.tracing_palette_remove)
        self.robotTest.clicked.connect(self.test_robot_connection)

    def get_settings(self) -> Settings:
        return Settings(
            genAI=GenAISettings(
                ssh_host=self.genAISSHHost.text(),
                ssh_port=self.genAISSHPort.value(),
                ssh_user=self.genAISSHUser.text(),
                ssh_key=self.genAISSHKey.text(),
                host=self.genAIHost.text(),
                port=self.genAIPort.value(),
                hf_token=self.genAIHFToken.text(),
                negative_prompt=self.genAINegativePrompt.toPlainText(),
                prompt_wrapper=self.genAIPromptWrapper.toPlainText(),
                steps=self.genAISteps.value(),
                guidance=self.genAIGuidance.value(),
            ),
            tracing=TracingSettings(palette=self.get_palette()),
            robot=RobotSettings(ip_address=self.robotIP.text()),
        )

    def set_settings(self, settings: Settings):
        self.genAISSHHost.setText(settings.genAI.ssh_host)
        self.genAISSHPort.setValue(settings.genAI.ssh_port)
        self.genAISSHUser.setText(settings.genAI.ssh_user)
        self.genAISSHKey.setText(settings.genAI.ssh_key)
        self.genAIHost.setText(settings.genAI.host)
        self.genAIPort.setValue(settings.genAI.port)
        self.genAIHFToken.setText(settings.genAI.hf_token)
        self.genAINegativePrompt.setText(settings.genAI.negative_prompt)
        self.genAIPromptWrapper.setText(settings.genAI.prompt_wrapper)
        self.genAISteps.setValue(settings.genAI.steps)
        self.genAIGuidance.setValue(settings.genAI.guidance)
        self.set_palette(settings.tracing.palette)
        self.robotIP.setText(settings.robot.ip_address)

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

    def browse_ssh_key(self):
        key_path, _ = QFileDialog.getOpenFileName(
            self, "Select an SSH key", str(Path.home() / ".ssh")
        )
        if key_path.strip() == "":
            return
        self.genAISSHKey.setText(key_path)

    def make_test_genai_client(self) -> GenAIClient:
        ssh_host: str = self.genAISSHHost.text()
        ssh_port: int = self.genAISSHPort.value()
        ssh_user: str = self.genAISSHUser.text()
        ssh_key_path: Path = Path(self.genAISSHKey.text())
        remote_host: str = self.genAIHost.text()
        remote_port: int = self.genAIPort.value()

        return GenAIClient(
            ssh_host=ssh_host,
            ssh_port=ssh_port,
            ssh_user=ssh_user,
            ssh_key_path=ssh_key_path,
            remote_host=remote_host,
            remote_port=remote_port,
        )

    def test_genai_ssh_connection(self):
        client: GenAIClient = self.make_test_genai_client()
        result: QLabel = self.genAISSHTestResult
        result.setText("Testing connection...")
        result.setToolTip(None)
        try:
            ok: bool = client.test_ssh_connection()
            if ok:
                result.setText("Connection successful")
            else:
                result.setText("Connection failed")
        except Exception as e:
            result.setText("Connection failed")
            result.setToolTip(f"Connection failed: {e}")

    def test_genai_server_connection(self):
        client: GenAIClient = self.make_test_genai_client()
        result: QLabel = self.genAITestResult
        result.setText("Testing connection...")
        result.setToolTip(None)
        try:
            ok: bool = client.test_api_connection()
            if ok:
                result.setText("Connection successful")
            else:
                result.setText("Connection failed")
        except Exception as e:
            result.setText("Connection failed")
            result.setToolTip(f"Connection failed: {e}")

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
