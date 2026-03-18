import json
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QModelIndex
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QDialog

from ui.ui.transformation_ui import Ui_Dialog


class TransformationDialog(QDialog, Ui_Dialog):
    def __init__(self, pos_path: Path, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.pos_path: Path = pos_path
        self.point_model: QStandardItemModel = QStandardItemModel(self.pointsList)
        self.load_points()

        self.positions: list[tuple[float, float, float]] = []

        self.recordBtn.clicked.connect(self.record_point)

    def load_points(self):
        with open(self.pos_path, "r") as f:
            data: list[dict] = json.load(f)["calibration"]

        for pt in data:
            item: QStandardItem = QStandardItem(pt["label"])
            item.setData(pt["pos"])
            item.setEditable(False)
            self.point_model.appendRow(item)
        self.pointsList.setModel(self.point_model)
    
    def record_point(self):
        idx: QModelIndex = self.pointsList.currentIndex()
        row: int = idx.row()
        column: int = idx.column()
        item: Optional[QStandardItem] = self.point_model.item(row)
        if item is None:
            return
        new_idx: QModelIndex = self.point_model.createIndex(row + 1, column)
        self.pointsList.setCurrentIndex(new_idx)
