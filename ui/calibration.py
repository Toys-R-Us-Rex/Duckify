from PyQt6.QtWidgets import QDialog

from ui.calibration_ui import Ui_Dialog

class CalibrationDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
