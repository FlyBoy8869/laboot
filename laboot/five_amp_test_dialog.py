# five_amp_test_dialog.py
import logging
from collections import namedtuple

from PyQt5.QtCore import QSettings, QTimer, QEvent, Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QLineEdit, QDialogButtonBox, QMessageBox

import laboot.strategies.strategy
from laboot import strategies
from laboot.config.collector.support import WaitForTextOnPage
from laboot.signals import TestSignals
from laboot.utilities import time as utilities_time
from laboot.utilities.time import format_seconds_to_minutes_seconds

TestResult = namedtuple("TestResult", "serial_number result")


class FiveAmpTestDialog(QDialog):
    def __init__(self, serial_number, strategy, parent=None):
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)
        settings = QSettings()

        self.serial_number = serial_number
        self.strategy = strategy
        self.signals = TestSignals()

        self.collector_configured = True
        self.verification_running = False

        self.link_timer_interval = int(settings.value("main/link_check_time"))
        self.link_timer_count_down = self.link_timer_interval
        self.test_timer_interval = int(settings.value("main/test_time"))
        self.test_time_remaining = self.test_timer_interval
        self.wait = WaitForTextOnPage(self,
                                      settings.value("pages/modem_status"),
                                      self.serial_number,
                                      wait_time=10,
                                      monitor=True)
        self.wait_time = self.wait.wait_time

        self.dialog_layout = QVBoxLayout()

        # time labels
        font = QFont("Arial", 10)
        self.lbl_remaining_time_header = QLabel(f"Test Time Remaining:\t\t\t\t")
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
        self.lbl_link_check = QLabel("Link Check Pending...")
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

        btns = QDialogButtonBox()
        btns.setStandardButtons(QDialogButtonBox.Cancel)
        btns.rejected.connect(self.reject)

        self.dialog_layout.addWidget(self.lbl_remaining_time_header, alignment=Qt.AlignLeft)
        # self.dialog_layout.addWidget(self.lbl_remaining_time, alignment=Qt.AlignCenter)
        self.dialog_layout.addWidget(self.pb_test_time)
        self.dialog_layout.addWidget(self.lbl_link_check, alignment=Qt.AlignLeft)
        self.dialog_layout.addWidget(self.pb_link_check)
        self.dialog_layout.addWidget(self.output)
        self.dialog_layout.addWidget(btns)

        self.setLayout(self.dialog_layout)
        self.setWindowTitle(f"Testing Sensor: {serial_number}")

        # update status every second
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.onStatusTimerTimeout)
        self.status_timer.start(1000)

        self.resize(300, 50)

    def _check_link_status(self):
        self.output.setText("checking for connection...")

        result = self.strategy.check_link_status()
        if result.status == laboot.strategies.strategy.STATUS_ITEM_CONNECTED:
            self.logger.info("Sensor connected to collector.")
            self.signals.testPassed.emit(TestResult(self.serial_number, "Pass"))
            self.done(QDialog.Accepted)
        elif result.status == laboot.strategies.strategy.STATUS_REQUEST_TIMED_OUT:
            QMessageBox.warning(self, "Low Amperage Boot", result.message, QMessageBox.Ok)
            self.done(QDialog.Rejected)
        elif result.status == laboot.strategies.strategy.STATUS_ITEM_NOT_PRESENT and not self.verification_running:
            self._start_verification()
        self.logger.debug("Link check complete.")

        QTimer(self).singleShot(1000, lambda: self.output.setText("no connection detected..."))

        # return result

    def _test_time_has_run_out(self):
        self.logger.info("Test time has expired. No connection detected.")
        self.signals.testFailed.emit(TestResult(self.serial_number, "Fail"))
        self.done(QDialog.Rejected)

    def onStatusTimerTimeout(self):
        self.logger.debug("Status timer has timed out.")

        # This check must be here for the message box to appear
        # as soon as possible and not have to wait for the link_timer_count_down
        # to elapse which causes a weird visual.
        if self.verification_running:
            self._check_verification_status()

        if self.link_timer_count_down <= 0:
            self.logger.debug("It's time for a link check.")
            self.logger.debug("Test time remaining: " +
                              f"{utilities_time.format_seconds_to_minutes_seconds(self.test_time_remaining)}")
            self.lbl_link_check.setText("Checking for link...")
            self.output.clear()
            self.link_timer_count_down = self.link_timer_interval + 1

            self._check_link_status()

            # if result.status == strategies.STATUS_ITEM_NOT_PRESENT \
            #    and not self.verification_running:
            #     self._start_verification()
            # self.logger.debug("Link check complete.")

            # Take a second before changing text so that the previous message can be seen.
            QTimer(self).singleShot(1000, lambda: self.lbl_link_check.setText("Link Check Pending..."))

        self.test_time_remaining -= 1
        self.pb_test_time.setValue(self.test_time_remaining)
        self.pb_test_time.update()  # update visuals immediately

        self.link_timer_count_down -= 1
        self.pb_link_check.setValue(self.link_timer_count_down)
        self.pb_link_check.update()

        if self.test_time_remaining <= 0:
            self._test_time_has_run_out()

    def _kill_timers(self):
        if self.status_timer.isActive():
            self.status_timer.stop()

    def _start_verification(self):
        if not self.wait.is_running:
            self.wait.start()
            self.verification_running = True

    def _check_verification_status(self):
        if self.wait.result() == WaitForTextOnPage.WAIT_TIME_EXPIRED:
            self.status_timer.stop()

            (minutes, seconds) = format_seconds_to_minutes_seconds(self.wait_time).split(":")

            msgbox = QMessageBox(QMessageBox.NoIcon,
                                 "Low Amperage Boot",
                                 f"Serial number {self.serial_number} not found.\n" +
                                 "Terminating test run.\n\n" +
                                 "See details below.",
                                 QMessageBox.NoButton,
                                 self)
            msgbox.addButton("Continue", QMessageBox.AcceptRole)
            msgbox.setDetailedText("The collector has not updated its serial number list " +
                                   f"for {minutes} minutes and {seconds} seconds. " +
                                   "Typically, this happens within 60 to 90 seconds.\n\n" +
                                   "Please, make sure it is operating correctly.")
            icon = QPixmap(r"laboot\resources\images\stop_256.png")
            msgbox.setIconPixmap(icon.scaled(96, 96))
            msgbox.exec_()

            self.done(QDialog.Rejected)

    def eventFilter(self, obj, event) -> bool:
        if obj is self.pb_test_time or obj is self.pb_link_check:
            if event.type() == QEvent.Resize:
                self.pb_test_time.setFixedHeight(10)
                self.pb_link_check.setFixedHeight(10)
                return True
            else:
                return False

        # the I don't care about other widgets response :)
        return QDialog.eventFilter(obj, event)

    def done(self, status):
        if status == QDialog.Rejected:
            self.logger.info("Test run cancelled.")

        self._kill_timers()
        super().done(status)
