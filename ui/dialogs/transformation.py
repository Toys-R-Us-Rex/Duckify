import json
from pathlib import Path
from typing import Callable, Optional

from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtGui import QColor, QIcon, QPixmap, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QDialog, QPushButton

from ui.ui.transformation_ui import Ui_Dialog

TCPPoint = tuple[float, float, float, float, float, float]
TCPReader = Callable[[], TCPPoint]


class TransformationDialog(QDialog, Ui_Dialog):
    REF_ROLE = Qt.ItemDataRole.UserRole
    MEASURE_ROLE = Qt.ItemDataRole.UserRole + 1
    MISSING_COLOR = QColor(163, 53, 33)
    RECORDED_COLOR = QColor(78, 149, 88)

    def __init__(self, pos_path: Path, read_tcp: TCPReader, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.pos_path: Path = pos_path
        self.read_tcp: TCPReader = read_tcp
        self.point_model: QStandardItemModel = QStandardItemModel(self.pointsList)

        missing_pixmap: QPixmap = QPixmap(16, 16)
        missing_pixmap.fill(self.MISSING_COLOR)
        self.missing_icon: QIcon = QIcon(missing_pixmap)

        recorded_pixmap: QPixmap = QPixmap(16, 16)
        recorded_pixmap.fill(self.RECORDED_COLOR)
        self.recorded_icon: QIcon = QIcon(recorded_pixmap)

        self.load_points()

        self.positions: list[tuple[float, float, float]] = []

        self.recordBtn.clicked.connect(self.record_point)
        self.point_model.dataChanged.connect(lambda _: self.update_save_btn())
        self.update_save_btn()

    def update_save_btn(self):
        save_btn: Optional[QPushButton] = self.buttonBox.button(
            self.buttonBox.StandardButton.Save
        )
        if save_btn is not None:
            save_btn.setDisabled(not self.is_complete())

    def is_complete(self) -> bool:
        for i in range(self.point_model.rowCount()):
            item: Optional[QStandardItem] = self.point_model.item(i)
            if item is not None and item.data(self.MEASURE_ROLE) is None:
                return False
        return True

    def load_points(self):
        with open(self.pos_path, "r") as f:
            data: list[dict] = json.load(f)["calibration"]

        for pt in data:
            item: QStandardItem = QStandardItem(pt["label"])
            item.setIcon(self.missing_icon)
            item.setData(pt["pos"], self.REF_ROLE)
            item.setEditable(False)
            self.point_model.appendRow(item)
        self.pointsList.setModel(self.point_model)

    def record_point(self):
        tcp_point: TCPPoint = self.read_tcp()
        idx: QModelIndex = self.pointsList.currentIndex()
        row: int = idx.row()
        column: int = idx.column()
        item: Optional[QStandardItem] = self.point_model.item(row)
        if item is None:
            return
        item.setData(tcp_point, self.MEASURE_ROLE)
        item.setIcon(self.recorded_icon)
        new_idx: QModelIndex = self.point_model.createIndex(row + 1, column)
        self.pointsList.setCurrentIndex(new_idx)

    def get_points(self) -> list[TCPPoint]:
        points: list[TCPPoint] = []
        for i in range(self.point_model.rowCount()):
            item: Optional[QStandardItem] = self.point_model.item(i)
            if item is None:
                continue
            points.append(item.data(self.MEASURE_ROLE))
        return points
