import time
from typing import Optional

from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QDialog, QPushButton

from ui.models import TCPPoint
from ui.services.robot import RobotService
from ui.ui.calibration_ui import Ui_Dialog


class CalibrationDialog(QDialog, Ui_Dialog):
    def __init__(self, service: RobotService, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.service: RobotService = service
        self.point_model: QStandardItemModel = QStandardItemModel(self.pointsList)
        self.pointsList.setModel(self.point_model)

        self.point_model.rowsInserted.connect(self.update_count)
        self.point_model.rowsRemoved.connect(self.update_count)
        self.addBtn.clicked.connect(self.add_point)
        self.removeBtn.clicked.connect(self.remove_point)

        self._next_id: int = 0

        self.set_count(0)

        self.finished.connect(lambda: self.service.set_freedrive(False))

    def exec(self) -> int:
        self.service.set_freedrive(True)
        return super().exec()

    def update_count(self, *args):
        self.set_count(self.point_model.rowCount())

    def set_count(self, count: int):
        self.progressBar.setMaximum(max(6, count))
        self.progressBar.setValue(count)

        save_btn: Optional[QPushButton] = self.buttonBox.button(
            self.buttonBox.StandardButton.Save
        )
        if save_btn is not None:
            save_btn.setDisabled(count < 6)

    def add_point(self):
        tcp_point: TCPPoint = self.service.read_tcp()
        timestamp: str = time.strftime("%H:%M:%S")
        id: int = self._next_id
        self._next_id += 1
        item: QStandardItem = QStandardItem(f"Point {id} ({timestamp})")
        item.setData(tcp_point)

        self.point_model.appendRow(item)

    def remove_point(self):
        row: int = self.pointsList.currentIndex().row()
        self.point_model.takeRow(row)

    def get_tcps(self) -> list[TCPPoint]:
        tcps: list[TCPPoint] = []
        for i in range(self.point_model.rowCount()):
            item: Optional[QStandardItem] = self.point_model.item(i)
            if item is None:
                continue
            tcps.append(item.data())
        return tcps
