# five_amp_test_dialog.py
import re
from collections import namedtuple
from datetime import datetime

import requests
from PyQt5.QtCore import QTimer, QEvent, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QLineEdit, QDialogButtonBox

from laboot import constants
from laboot.sensor import Sensor
from laboot.signals import TestSignals
from laboot.utilities import time as utilities_time

TestResult = namedtuple("TestResult", "serial_number result")

link_pattern = re.compile(r"\s*\d{7}\s*\d{7}\s*\d{7}\s*-?\d{1,2}")
serial_pattern = re.compile(r"\s*\d{7}")


class FiveAmpTestDialog(QDialog):
    def __init__(self, parent, sensor: Sensor):
        super().__init__(parent)

        self._sensor = sensor
        self.serial_number = sensor.serial_number
        self.signals = TestSignals()

        self.link_timer_interval = constants.LINK_CHECK_TIME
        self.link_timer_count_down = self.link_timer_interval
        self.test_timer_interval = sensor.test_time_record.remaining_time
        self.test_time_remaining = self.test_timer_interval

        self.dialog_layout = QVBoxLayout()

        # time labels
        font = QFont("Arial", 10)
        self.lbl_remaining_time_header = QLabel(
            f"Test Time Remaining: {utilities_time.format_seconds_to_minutes_seconds(self.test_time_remaining)}\t\t\t")
        self.lbl_remaining_time_header.setFont(font)

        self.pb_test_time = QProgressBar(self)
        self.pb_test_time.installEventFilter(self)
        self.pb_test_time.setTextVisible(False)
        self.pb_test_time.setRange(0, self.test_timer_interval)
        self.pb_test_time.setMinimum(0)
        self.pb_test_time.setMaximum(self.test_timer_interval)
        self.pb_test_time.setValue(self.test_timer_interval)

        # link interval visual status indicator
        font = QFont("Arial", 10)
        self.lbl_link_check = QLabel(
            f"Link check in {utilities_time.format_seconds_to_minutes_seconds(self.link_timer_count_down)}")
        self.lbl_link_check.setFont(font)

        self.pb_link_check = QProgressBar(self)
        self.pb_link_check.installEventFilter(self)
        self.pb_link_check.setTextVisible(False)
        self.pb_link_check.setRange(0, self.link_timer_interval)
        self.pb_link_check.setMinimum(0)
        self.pb_link_check.setMaximum(self.link_timer_interval)
        self.pb_link_check.setValue(self.link_timer_interval)

        self.output = QLineEdit()
        self.output.setAlignment(Qt.AlignCenter)

        buttons = QDialogButtonBox()
        buttons.setStandardButtons(QDialogButtonBox.Cancel)
        buttons.rejected.connect(self.reject)

        self.dialog_layout.addWidget(self.lbl_remaining_time_header, alignment=Qt.AlignLeft)
        self.dialog_layout.addWidget(self.pb_test_time)
        self.dialog_layout.addWidget(self.lbl_link_check, alignment=Qt.AlignLeft)
        self.dialog_layout.addWidget(self.pb_link_check)
        self.dialog_layout.addWidget(self.output)
        self.dialog_layout.addWidget(buttons)

        self.setLayout(self.dialog_layout)
        self.setWindowTitle(f"Testing Sensor: {sensor.serial_number}")

        # update status every second
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.on_status_timer_timeout)
        self.status_timer.start(1000)

        self.resize(300, 50)

    def done(self, status):
        if status == QDialog.Rejected:
            self._sensor.test_time_record.set_test_interruption_time(self.test_time_remaining, datetime.now())

        self._kill_timers()
        super().done(status)

    def eventFilter(self, obj, event) -> bool:
        if obj is self.pb_test_time or obj is self.pb_link_check:
            if event.type() == QEvent.Resize:
                self.pb_test_time.setFixedHeight(10)
                self.pb_link_check.setFixedHeight(10)
                return True
            else:
                return False

        # the I don't care about other widgets response :)
        return super().eventFilter(obj, event)

    def on_status_timer_timeout(self):
        self._process_link_timer()
        self._process_test_timer()

    def _kill_timers(self):
        if self.status_timer.isActive():
            self.status_timer.stop()

    def _test_time_has_run_out(self):
        self.signals.testFailed.emit(TestResult(self.serial_number, "Fail"))
        self.done(constants.TEST_TIMED_OUT)

    def _process_link_timer(self):
        self.link_timer_count_down -= 1
        self.lbl_link_check.setText(
            f"Link check in {utilities_time.format_seconds_to_minutes_seconds(self.link_timer_count_down)}")

        self.pb_link_check.setValue(self.link_timer_count_down)

        if self._is_time_to_check_link_status():
            self.lbl_link_check.setText("Checking for link...")
            self.output.clear()

            if self._check_for_link():
                self.signals.testPassed.emit(TestResult(self.serial_number, "Pass"))
                self.done(QDialog.Accepted)

            QTimer(self).singleShot(1000, lambda: self.output.setText("no connection detected"))
            self.link_timer_count_down = self.link_timer_interval

    def _process_test_timer(self):
        self.test_time_remaining -= 1

        self.pb_test_time.setValue(self.test_time_remaining)
        self.pb_test_time.update()  # update visuals immediately

        if self.test_time_remaining <= 0:
            self._test_time_has_run_out()

        self.lbl_remaining_time_header.setText(
            f"Test time remaining: {utilities_time.format_seconds_to_minutes_seconds(self.test_time_remaining)}\t\t\t"
        )

    def _is_time_to_check_link_status(self) -> bool:
        return self.link_timer_count_down <= 0

    def _check_for_link(self):
        for line in [line for line in requests.get(constants.URL_MODEM_STATUS).text.split('\n')
                     if serial_pattern.match(line)]:
            if (match := link_pattern.match(line)) and match[0].split()[0] == self.serial_number:
                return True

        return False
