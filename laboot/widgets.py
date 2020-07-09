from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QListWidget, QListWidgetItem


class Signals(QObject):
    item_right_clicked = pyqtSignal(QListWidgetItem)


class LabootListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton:
            item = self.itemAt(event.pos())

            if item is not None:
                self.signals.item_right_clicked.emit(item)

            event.accept()
        else:
            event.ignore()
