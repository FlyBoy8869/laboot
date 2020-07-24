from PyQt5 import QtGui
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem


class Signals(QObject):
    item_right_clicked = pyqtSignal(QListWidgetItem)


class LabootListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        item = self.itemAt(event.pos())

        if event.button() == Qt.RightButton:
            if item is not None:
                self.signals.item_right_clicked.emit(item)
            event.accept()
        elif event.button() == Qt.LeftButton:
            if item is None:
                self.clearSelection()
            event.accept()
        else:
            event.ignore()
