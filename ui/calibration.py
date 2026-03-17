import time
from typing import Optional

from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QDialog, QPushButton

from ui.calibration_ui import Ui_Dialog


class CalibrationDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.point_model: QStandardItemModel = QStandardItemModel(self.pointsList)
        self.pointsList.setModel(self.point_model)

        self.addBtn.clicked.connect(self.add_point)
        self.removeBtn.clicked.connect(self.remove_point)

        self._next_id: int = 0

        self.set_count(0)

    def set_count(self, count: int):
        self.progressBar.setMaximum(max(6, count))
        self.progressBar.setValue(count)

        save_btn: Optional[QPushButton] = self.buttonBox.button(
            self.buttonBox.StandardButton.Save
        )
        if save_btn is not None:
            save_btn.setDisabled(count < 6)

    def add_point(self):
        timestamp: str = time.strftime("%H:%M:%S")
        id: int = self._next_id
        self._next_id += 1
        item: QStandardItem = QStandardItem(f"Point {id} ({timestamp})")
        self.point_model.appendRow(item)
        self.set_count(self.point_model.rowCount())

    def remove_point(self):
        row: int = self.pointsList.currentIndex().row()
        self.point_model.takeRow(row)
        self.set_count(self.point_model.rowCount())
