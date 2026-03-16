from PyQt6 import QtWidgets

from settings_ui import Ui_Dialog


class SettingsDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
