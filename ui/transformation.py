from PyQt6.QtWidgets import QDialog

from ui.transformation_ui import Ui_Dialog

class TransformationDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
