# setdialog.py
from typing import Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFormLayout, QVBoxLayout, QLineEdit, QCheckBox, QDialogButtonBox, QDialog

from laboot.signals import DefineSetSignals
import laboot.spreadsheet as spreadsheet


class SetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.Window)
        self.signals = DefineSetSignals()

        self.setWindowTitle("Define Set")
        self.dialog_layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        names = ["Sensor 1:", "Sensor 2:", "Sensor 3",
                 "Sensor 4:", "Sensor 5:", "Sensor 6"]
        self.line_edits = []

        font = QFont("Arial", 16)
        for i in range(6):
            le = QLineEdit()
            le.setFont(font)
            self.line_edits.append(le)
            self.form_layout.addRow(names[i], le)

        self.configure_collector = QCheckBox("Configure Collector")

        btns = QDialogButtonBox()
        btns.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        self.dialog_layout.addLayout(self.form_layout)
        self.dialog_layout.addWidget(self.configure_collector)
        self.dialog_layout.addWidget(btns)

        self.setLayout(self.dialog_layout)

    def accept(self):
        super().accept()
        self.signals.newSerialNumbers.emit(self._get_serial_numbers())

    def showEvent(self, QShowEvent):
        super().showEvent(QShowEvent)
        for line_edit in self.line_edits:
            line_edit.clear()

        # make sure carrot is in first sensor field
        self.line_edits[0].setFocus()

    def _get_serial_numbers(self) -> Tuple[spreadsheet.SerialNumberInfo]:
        """Returns sensor serial numbers.

        Returns
        -------
        tuple
            a tuple of strings representing sensor serial numbers
        """

        serial_numbers = [spreadsheet.SerialNumberInfo(line_edit.text(), index, False)
                          if line_edit.text() else spreadsheet.SerialNumberInfo("0", index, False)
                          for index, line_edit in enumerate(self.line_edits)]
        print(f"SetDialog.get_serial_numbers() returning: {serial_numbers}")

        return tuple(serial_numbers)
