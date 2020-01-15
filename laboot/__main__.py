# __main__.py
import logging
import sys

from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QFont, QBrush, QColor, QPixmap, QIcon, QCloseEvent
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                             QListWidget, QListWidgetItem, QLabel,
                             QHBoxLayout, QMessageBox, QAction, QStatusBar, QToolBar, QWidget)
from selenium import webdriver

from laboot import spreadsheet
from laboot.config.app import logging as lab_logging
from laboot.config.app import settings as lab_settings
from laboot.config.collector import collector
from laboot.five_amp_test_dialog import FiveAmpTestDialog
from laboot.sensor import Sensor, SensorLog
from laboot.setdialog import SetDialog
from laboot.signals import DropSignals
from laboot.strategies import FromWebSiteStrategy
from laboot.utilities import sound

lab_settings.load()
lab_logging.initialize()

snd_passed = QSound(r"laboot\resources\audio\cash_register.wav")
snd_failed = QSound(r"laboot\resources\audio\error_01.wav")


# version that shows in help dialog
def version():
    return '0.1.6'


def dialog_title():
    return "Low Amp Boot"


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.Window)

        self.logger = logging.getLogger(__name__)
        self.setAcceptDrops(True)
        self.signals = DropSignals()
        self.signals.dropped_filename.connect(self._process_file_drop)
        self.unsaved_test_results = False
        self.browser = None

        self.spreadsheet_path: str = ""
        self.sensor_log = SensorLog()
        self.test_results = []
        self.collector_configured = False

        self.logger.info("Application starting.")
        self._create_menus()
        self.setStatusBar(QStatusBar(self))

        self.set_dialog = SetDialog(self)
        self.set_dialog.signals.newSerialNumbers.connect(self._new_set_defined)
        self.set_dialog.finished.connect(self.on_set_dialog_finished)

        # self.frame = QFrame(self)
        self.frame = QWidget(self)
        self.frame_layout = QVBoxLayout(self.frame)

        self.left_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        font = QFont("Arial", 12)
        self.lbl_sensors = QLabel("Sensors:")
        self.lbl_sensors.setFont(font)

        font = QFont("Arial", 16)
        self.qlwSensors = QListWidget()
        self.qlwSensors.setFont(font)
        self.qlwSensors.itemDoubleClicked.connect(self.on_sensor_item_double_clicked)
        self.qlwSensors.itemClicked.connect(lambda i: self.start_five_amp_action.setEnabled(True))

        # add widgets to layout
        self.left_layout.addWidget(self.lbl_sensors, alignment=Qt.AlignLeft)
        self.left_layout.addWidget(self.qlwSensors)

        self.frame_layout.addLayout(self.left_layout)
        self.frame_layout.addLayout(self.button_layout)
        self.frame.setLayout(self.frame_layout)

        self.setWindowTitle(dialog_title())
        self.setCentralWidget(self.frame)
        self.setWindowIcon(QIcon(r"laboot/resources/images/app_128.png"))
        self.resize(500, 360)
        self.show()

    def closeEvent(self, event: QCloseEvent):
        settings = QSettings()
        header = "shutdown: "

        if self._discard_test_results():
            self.logger.info("shutdown in progress...")

            # save ui state
            self.logger.info(f"{header} saving ui state")
            self.logger.debug(header +
                              "saving ui/menus/options/autoconfigcollector=" +
                              f"{self.options_auto_config_collector_action.isChecked()}")

            settings.setValue("ui/menus/options/autoconfigcollector",
                              str(self.options_auto_config_collector_action.isChecked()))

            self.logger.info(f"{header} application terminated")
            logging.shutdown()

            event.accept()
        else:
            event.ignore()

    def _discard_test_results(self, clear_flag=True):
        if self.unsaved_test_results:
            result = QMessageBox.question(self, f"{dialog_title()} - Unsaved Test Results",
                                          "Discard results?\t\t\t\t",
                                          QMessageBox.Yes | QMessageBox.No,
                                          QMessageBox.No)

            if result == QMessageBox.No:
                return False

        if clear_flag:
            self.unsaved_test_results = False
        return True

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat("FileName"):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, event):
        self.logger.info("dropEvent occurred")
        self.signals.dropped_filename.emit(event.mimeData().urls()[0].toLocalFile())

    def on_save_test_results_action_triggered(self):
        spreadsheet.save_test_results(self.spreadsheet_path, self.sensor_log.get_test_results())
        QMessageBox.information(self, dialog_title(), "Test results saved.", QMessageBox.Ok)

    def on_configure_collector_action_triggered(self):
        if self.qlwSensors.count() != 0:
            a_collector = collector.CollectorConfigurator(self._get_browser())
            a_collector.signals.configured.connect(self._collector_configured)
            a_collector.signals.offline.connect(self._collector_config_error)

            self.logger.debug("Asking collector to configure serial numbers.")
            a_collector.configure_serial_numbers(self.sensor_log.get_serial_numbers())

    def on_define_set_action_triggered(self):
        if self._discard_test_results(clear_flag=False):
            self.logger.info("Menu option for manual entry of serial numbers selected.")
            self.set_dialog.exec_()

    def on_menu_help_about_action_triggered(self):
        text = "<center>" \
               f"<h1>{dialog_title()}</h1>" \
               "</center" \
               f"<p>Version {version()}<br/>" \
               "Author: Charles Cognato<br/>" \
               "Email: charlescognato@gmail.com</p>"
        QMessageBox.about(self, "About", text)

    def on_set_dialog_finished(self, result):
        if result:
            self.logger.info("Manual entry of serial numbers complete.")

            # serial_numbers = self.set_dialog.get_serial_numbers()
            # if any(map(lambda n: int(n), serial_numbers)):
            #     self._add_sensors_to_list(self.set_dialog.get_serial_numbers())
            #
            #     self.config_collector_action.setEnabled(True)
            #
            #     # auto configure the collector if applicable
            #     if self.set_dialog.configure_collector.isChecked():
            #         self.on_configure_collector_action_triggered()
            #
            # self.unsaved_test_results = False
        else:
            self.logger.info("Manual entry of serial numbers cancelled.")

        self.logger.debug(f"set_dialog configure collector: {self.set_dialog.configure_collector.isChecked()}")

    def on_save_action_triggered(self):
        if self.spreadsheet_path:
            spreadsheet.save_test_results(self.spreadsheet_path, self.sensor_log.get_test_results())
            self.unsaved_test_results = False

    def on_start_five_amp_test_action_triggered(self):
        self._submit_item_for_testing(self.qlwSensors.currentItem().text())

    def on_sensor_item_double_clicked(self, list_widget_item):
        self._submit_item_for_testing(list_widget_item.text())

    def on_test_dialog_finished(self, result):
        if result.result == "Pass":
            sound.play_sound(snd_passed)
            b = QBrush(QColor(0, 255, 0, 100))
        else:
            sound.play_sound(snd_failed)
            b = QBrush(QColor(255, 0, 0, 100))

        self.unsaved_test_results = True

        self.qlwSensors.currentItem().setBackground(b)
        self.test_results.append(result)

        self.save_results_action.setEnabled(True)

        self.sensor_log.set_test_result(result.serial_number, result.result)

    def _add_sensors_to_list(self, serial_numbers):
        self.logger.info("Adding sensors to lists.")
        self.logger.debug(f"Adding the following serial numbers: {serial_numbers}")

        self.qlwSensors.clear()  # start fresh
        self.sensor_log.clear()  # start fresh

        for index, serial_number in enumerate(serial_numbers):
            # make sure only sensors under test are added to list widget
            if serial_number != "0":
                item = QListWidgetItem(serial_number)
                self.qlwSensors.addItem(item)

            # but unused line positions must be added to the log in order to properly configure the collector
            self.sensor_log.append(Sensor(index, serial_number))

        self.logger.debug(f"sensor_log contains {self.sensor_log.count()} records.")

        self.qlwSensors.clearSelection()

    def _create_menus(self):
        settings = QSettings()

        self.logger.info("creating menus")

        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        # create top level menus
        self.menu = self.menuBar().addMenu("&Menu")
        self.menu_options = self.menuBar().addMenu("&Options")
        self.menu_help = self.menuBar().addMenu("&Help")

        # ----- create actions -----
        self.define_set_action = QAction(QIcon(r"laboot\resources\images\menu_icons\set-02_128.png"),
                                         "Define Set", self)
        self.config_collector_action = QAction(QIcon(r"laboot\resources\images\menu_icons\config-02_128.png"),
                                               "Configure Collector with  Serial Numbers", self)
        self.save_results_action = QAction(QIcon(r"laboot\resources\images\menu_icons\save-01_48.png"),
                                           "Save results", self)
        self.exit_action = QAction(QIcon(r"laboot\resources\images\menu_icons\exit-01_128.png"), "E&xit", self)

        # menu_tasks actions
        self.start_five_amp_action = QAction(QIcon(r"laboot\resources\images\menu_icons\bolt-01_48.png"),
                                             "Start 5amp test...", self)

        # menu_options actions
        self.options_auto_config_collector_action = QAction("Auto Configure Collector", self)
        self.options_successive_testing_action = QAction("Successive testing", self)
        self.options_headless_action = QAction("Headless mode", self)

        self.help_about_action = QAction(QIcon(r"laboot\resources\images\menu_icons\info-01_32.png"), "&About", self)

        # ----- configure options -----

        # menu
        self.define_set_action.setStatusTip("Manually enter serial numbers.")
        self.config_collector_action.setEnabled(True)
        self.start_five_amp_action.setEnabled(False)
        self.save_results_action.setEnabled(False)
        self.exit_action.setStatusTip("Exit the application.")

        # menu_options
        self.options_auto_config_collector_action.setCheckable(True)
        if settings.value("ui/menus/options/autoconfigcollector", "False") == "True":
            self.options_auto_config_collector_action.setChecked(True)
        self.options_auto_config_collector_action.setStatusTip(
            "Automatically configures collector on serial number import.")

        self.options_successive_testing_action.setCheckable(True)
        self.options_successive_testing_action.setChecked(False)
        self.options_successive_testing_action.setStatusTip("Test units one after the other pausing in between.")
        self.options_successive_testing_action.setEnabled(False)

        self.options_headless_action.setCheckable(True)
        self.options_headless_action.setChecked(False)
        self.options_headless_action.setStatusTip("In headless mode, the browser window will not appear.")
        settings.setValue("ui/menus/options/headless", False)

        # menu_help
        self.help_about_action.setStatusTip("Information about Low Amperage Boot.")

        # ----- configure triggers -----
        self.define_set_action.triggered.connect(self.on_define_set_action_triggered)
        self.config_collector_action.triggered.connect(self.on_configure_collector_action_triggered)
        self.start_five_amp_action.triggered.connect(self.on_start_five_amp_test_action_triggered)
        self.save_results_action.triggered.connect(self.on_save_action_triggered)
        self.exit_action.triggered.connect(self.close)

        self.options_headless_action.toggled.connect(lambda s: settings.setValue("ui/menus/options/headless", s))

        self.help_about_action.triggered.connect(self.on_menu_help_about_action_triggered)

        # ----- add to menu -----

        # menu
        self.menu.addSeparator()
        self.menu.addAction(self.exit_action)

        # menu_optons
        self.menu_options.addAction(self.options_auto_config_collector_action)
        self.menu_options.addAction(self.options_successive_testing_action)
        self.menu_options.addAction(self.options_headless_action)

        # menu_help
        self.menu_help.addAction(self.help_about_action)

        # set up toolbar
        toolbar.addAction(self.define_set_action)
        toolbar.addAction(self.config_collector_action)
        toolbar.addSeparator()
        toolbar.addAction(self.start_five_amp_action)
        toolbar.addSeparator()
        toolbar.addAction(self.save_results_action)
        toolbar.addAction(self.exit_action)

    def _close_browser(self):
        if self.browser:
            self.browser.quit()

    def _collector_configured(self):
        self.config_collector_action.setEnabled(False)
        self.collector_configured = True

        self._close_browser()

        icon = QPixmap(r"laboot\resources\images\info_72.png")
        msgbox = QMessageBox(QMessageBox.NoIcon,
                             f"{dialog_title()} - Info",
                             "Serial numbers sent to collector.",
                             QMessageBox.Ok, self)
        msgbox.setIconPixmap(icon)
        msgbox.exec_()

    def _collector_config_error(self, message):
        self.config_collector_action.setEnabled(True)

        self._close_browser()
        msg_box = QMessageBox(QMessageBox.Information, "Low Amp Boot", message, QMessageBox.Ok)
        msg_box.exec_()

    def _get_browser(self):
        settings = QSettings()

        if self.browser is None:
            self.browser = webdriver.Chrome(executable_path=settings.value('drivers/chromedriver'))

        return self.browser

    def _import_serial_numbers_from_spreadsheet(self, filename) -> tuple:
        print(f"importing from dropped_filename: {filename}")
        return spreadsheet.get_serial_numbers(filename)

    def _new_set_defined(self, serial_numbers):
        if all(map(lambda n: not n.isalpha(), serial_numbers)):
            if all(map(lambda n: n.isdigit(), serial_numbers)):
                self._add_sensors_to_list(serial_numbers)

                self.config_collector_action.setEnabled(True)

                # auto configure the collector if applicable
                if self.set_dialog.configure_collector.isChecked():
                    self.on_configure_collector_action_triggered()

                self.unsaved_test_results = False

    def _process_file_drop(self, filename: str):
        if self._discard_test_results():
            self.logger.debug(f"dropped spreadsheet: {filename}")
            self.spreadsheet_path = filename

            serial_numbers = self._import_serial_numbers_from_spreadsheet(filename)
            self._add_sensors_to_list(serial_numbers)

            if self.options_auto_config_collector_action.isChecked():
                QTimer(self).singleShot(1000, self.on_configure_collector_action_triggered)
                self.logger.info("Automatically configured collector.")

    def _submit_item_for_testing(self, serial_number):
        settings = QSettings()

        self.logger.info("-" * 10 + f" Start of test run for {serial_number} " + "-" * 10)

        if self.collector_configured:
            if not self.sensor_log.is_tested(serial_number):
                self.logger.debug(f"Using url to check link status: {settings.value('pages/modem_status')}")
                td = FiveAmpTestDialog(serial_number,
                                       FromWebSiteStrategy(serial_number, settings.value("pages/modem_status")),
                                       parent=self)
                td.signals.testPassed.connect(self.on_test_dialog_finished)
                td.signals.testFailed.connect(self.on_test_dialog_finished)
                td.exec_()
            else:
                message = f"Sensor {serial_number} has already been tested."
                self.logger.info(message)
                QMessageBox.information(self, dialog_title(), message, QMessageBox.Ok)
        else:
            message = "The collector must be configured before running any tests."
            self.logger.info(message)
            QMessageBox.information(self, dialog_title(), message, QMessageBox.Ok)

        self.logger.info("-" * 10 + f" End of test run for {serial_number} " + "-" * 10)


def main(args):
    app = QApplication(args)
    main_window = MainWindow()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv)
