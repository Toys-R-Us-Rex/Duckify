from PyQt6.QtWidgets import QDialog

from ui.ui.pen_calibration_ui import Ui_Dialog

class PenCalibrationDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
