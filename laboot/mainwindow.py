import logging
from time import sleep
from typing import Tuple, Callable, Optional

from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QFont, QBrush, QColor, QPixmap, QIcon, QCloseEvent, QCursor
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout,
                             QListWidgetItem, QLabel,
                             QHBoxLayout, QMessageBox, QAction, QStatusBar, QToolBar, QWidget, QMenu)
from selenium import webdriver

from laboot import spreadsheet, constants
from laboot.config.collector import collector
from laboot.five_amp_test_dialog import FiveAmpTestDialog
from laboot.sensor import Sensor, SensorLog
from laboot.setdialog import SetDialog
from laboot.signals import DropSignals
from laboot.strategies import FromWebSiteStrategy
from laboot.utilities import sound, time as util_time
from laboot.utilities.returns import Result
from laboot.widgets import LabootListWidget


# version that shows in help dialog
def version():
    return '0.1.17'


def dialog_title():
    return "Low Amp Boot"


class MainWindow(QMainWindow):
    snd_passed = QSound(r"laboot/resources/audio/cash_register.wav")
    snd_failed = QSound(r"laboot/resources/audio/error_01.wav")

    green_brush = QBrush(QColor(0, 255, 0, 100))
    red_brush = QBrush(QColor(255, 0, 0, 100))
    yellow_brush = QBrush(QColor(Qt.yellow))
    black_brush = QBrush(QColor(Qt.black))

    PAUSE_FOR_WEB_SERVER_BROWSER_COMMUNICATION = 5

    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.Window)

        self.logger = logging.getLogger(__name__)
        self.setAcceptDrops(True)
        self.signals = DropSignals()
        self.signals.dropped_filename.connect(self._process_file_drop)
        self.need_to_save = False
        self.browser = None

        self.spreadsheet_path: str = ""
        self._sensor_log = SensorLog()
        self.collector_configured = False

        self.logger.info("Application starting.")
        self._create_menus()
        self.setStatusBar(QStatusBar(self))

        self.set_dialog = SetDialog(self)
        self.set_dialog.signals.newSerialNumbers.connect(self._new_set_defined)

        self.frame = QWidget(self)
        self.frame_layout = QVBoxLayout(self.frame)

        self.left_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        font = QFont("Arial", 12)
        self.lbl_sensors = QLabel("Sensors:")
        self.lbl_sensors.setFont(font)

        font = QFont("Arial", 16)
        self._sensor_view = LabootListWidget()
        self._sensor_view.setFont(font)
        self._sensor_view.itemDoubleClicked.connect(self.on_sensor_item_double_clicked)
        self._sensor_view.signals.item_right_clicked.connect(
            lambda list_widget_item: self.on_sensor_item_right_clicked(
                self._sensor_log.get_sensor(list_widget_item.text())
            )
        )

        # add widgets to layout
        self.left_layout.addWidget(self.lbl_sensors, alignment=Qt.AlignLeft)
        self.left_layout.addWidget(self._sensor_view)

        self.frame_layout.addLayout(self.left_layout)
        self.frame_layout.addLayout(self.button_layout)
        self.frame.setLayout(self.frame_layout)

        self.setWindowTitle(dialog_title())
        self.setCentralWidget(self.frame)
        self.setWindowIcon(QIcon(r"laboot/resources/images/app_128.png"))
        self.resize(500, 550)
        self.show()

    def closeEvent(self, event: QCloseEvent):
        if self._ok_to_discard_test_results():
            self._save_ui_state(QSettings())
            logging.shutdown()
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            self.signals.dropped_filename.emit(event.mimeData().urls()[0].toLocalFile())
        else:
            event.ignore()

    def on_save_test_results_action_triggered(self):
        spreadsheet.save_test_results(self.spreadsheet_path, self._sensor_log.get_test_results())
        QMessageBox.information(self, dialog_title(), "Test results saved.", QMessageBox.Ok)

    def on_configure_collector_action_triggered(self, serial_numbers, password, config_url, get_driver: Callable):
        if serial_numbers:
            a_collector = collector.CollectorConfigurator(get_driver(), config_url, password)
            a_collector.signals.configured.connect(self._collector_configured)
            a_collector.signals.offline.connect(self._handle_serial_number_configuration_error)
            a_collector.configure_serial_numbers(serial_numbers)

    def on_define_set_action_triggered(self):
        if self._ok_to_discard_test_results(clear_flag=False):
            self.set_dialog.exec_()

    def on_menu_help_about_action_triggered(self):
        text = "<center>" \
               f"<h1>{dialog_title()}</h1>" \
               "</center" \
               f"<p><h4>Version</h4>{version()}" \
               "<h4>Author:</h4>Charles Cognato" \
               "<h4>Email:</h4>charlescognato@gmail.com</p>"
        QMessageBox.about(self, "About", text)

    def on_save_action_triggered(self):
        if result := spreadsheet.save_test_results(self.spreadsheet_path, self._sensor_log.get_test_results()):
            self.need_to_save = False

        QMessageBox.information(self, "LWTest - Save Data", result.message, QMessageBox.Ok)

    def on_start_five_amp_test_action_triggered(self):
        self._sensor_selected_for_testing(self._sensor_view.currentItem())

    def on_sensor_item_double_clicked(self, list_widget_item: QListWidgetItem):
        self._sensor_selected_for_testing(list_widget_item)

    def on_sensor_item_right_clicked(self, sensor: Sensor):
        if (action := self._get_sensor_context_menu_choice(sensor.remaining_time)) and "reset" in action.text():
            sensor.test_time_record.reset()

    def _get_sensor_context_menu_choice(self, remaining_time) -> Optional[QAction]:
        return self._make_sensor_context_menu(remaining_time).exec(QCursor.pos())

    def _make_sensor_context_menu(self, remaining_time):
        menu = QMenu(self)
        menu.addAction(
            QIcon("laboot/resources/images/menu_icons/refresh.png"),
            f"reset [remaining time {util_time.format_seconds_to_minutes_seconds(remaining_time)}]"
        )
        return menu

    def on_test_dialog_finished(self, result):
        self._record_sensor_test_result(result)
        self._indicate_test_result(result)

        self._flag_unsaved_test_results()
        self._enable_save_action()

    def _record_sensor_test_result(self, result):
        self._sensor_log.set_test_result(result.serial_number, result.result)

    def _indicate_test_result(self, result):
        sound.play_sound(self._get_sound_for_test_result(result))
        self._sensor_view.currentItem().setBackground(self._get_brush_for_test_result(result))

    def _get_sound_for_test_result(self, result):
        return self.snd_passed if result.result == "Pass" else self.snd_failed

    def _get_brush_for_test_result(self, result):
        return self.green_brush if result.result == "Pass" else self.red_brush

    def _flag_unsaved_test_results(self):
        self.need_to_save = True

    def _enable_save_action(self):
        self.save_results_action.setEnabled(True)

    def _add_sensors_to_log(self, serial_numbers: Tuple[spreadsheet.SerialNumberInfo]):
        self._sensor_log.clear()

        for serial_info in serial_numbers:
            self._sensor_log.append(Sensor(serial_info.position, serial_info.serial_number, serial_info.failure))

        self._initialize_list_view_from_sensor_log()

    def _set_item_background_to_yellow_if_failure(self, item, failure):
        if failure:
            item.setBackground(self.yellow_brush)
            item.setForeground(Qt.black)

    def _create_list_widget_item_from_serial_number(self, serial_number):
        return QListWidgetItem(serial_number)

    def _is_valid_serial_number(self, serial_number):
        return serial_number != "0"

    def _add_serial_number_to_view(self, serial_number, failure):
        if self._is_valid_serial_number(serial_number):
            item = self._create_list_widget_item_from_serial_number(serial_number)
            self._set_item_background_to_yellow_if_failure(item, failure)
            self._sensor_view.addItem(item)

    def _initialize_list_view(self, sensor_log):
        for sensor in sensor_log:
            self._add_serial_number_to_view(sensor.serial_number, sensor.failure)

    def _initialize_list_view_from_sensor_log(self):
        self._sensor_view.clear()
        self._initialize_list_view(self._sensor_log)

    def _collector_configured(self):
        self._close_browser()
        self._show_information_message("Serial numbers sent to collector.")

        self.collector_configured = True
        self.start_five_amp_action.setEnabled(True)

    def _handle_serial_number_configuration_error(self, message):
        self._close_browser()
        self._show_information_message(message)
        self.collector_configuration_action.setEnabled(True)

    def _ask_to_discard_test_results(self, clear_flag):
        if self._ask_yes_no_question("Discard results?\t\t\t\t") == QMessageBox.No:
            return False

        self.need_to_save = not clear_flag

        return True

    def _ok_to_discard_test_results(self, clear_flag=True):
        return not self.need_to_save or self._ask_to_discard_test_results(clear_flag)

    def _close_browser(self):
        if self.browser:
            self.browser.minimize_window()
            sleep(self.PAUSE_FOR_WEB_SERVER_BROWSER_COMMUNICATION)
            self.browser.quit()
            self.browser = None

    def _get_browser(self, driver_location: str):
        if self.browser is None:
            self.browser = webdriver.Chrome(executable_path=driver_location)

        return self.browser

    def _get_serial_numbers_from_spreadsheet(self, filename) -> Result:
        print(f"importing from dropped_filename: {filename}")

        return spreadsheet.get_serial_numbers(filename)

    def _new_set_defined(self, serial_numbers):
        if all(map(lambda n: not n.serial_number.isalpha(), serial_numbers)) and \
         all(map(lambda n: n.serial_number.isdigit(), serial_numbers)):

            self._add_sensors_to_log(serial_numbers)
            self.collector_configuration_action.setEnabled(True)

            # auto configure the collector if applicable
            if self.set_dialog.configure_collector.isChecked():
                self.collector_configuration_action.trigger()
                self.collector_configured = True

            self.need_to_save = False

    def _process_file_drop(self, filename: str):
        if self._ok_to_discard_test_results():
            self.spreadsheet_path = filename

            if not (result_serial_numbers := self._get_serial_numbers_from_spreadsheet(filename)):
                QMessageBox.information(self, dialog_title(), result_serial_numbers.message, QMessageBox.Ok)
                return

            self._add_sensors_to_log(result_serial_numbers())
            self.collector_configuration_action.setEnabled(True)

            if self.options_auto_collector_configuration_action.isChecked():
                QTimer(self).singleShot(1000, self.collector_configuration_action.trigger)
                self.collector_configured = True
                return

            self.collector_configured = False

    def _test_sensor(self, sensor):
        if not sensor.tested:
            if sensor.failure and not self._ask_yes_no_question("Sensor failed previous sections of testing.\n" +
                                                                "Do you want to continue?"):
                return

            td = FiveAmpTestDialog(sensor,
                                   FromWebSiteStrategy(
                                       sensor.serial_number,
                                       constants.URL_MODEM_STATUS
                                   ),
                                   parent=self
                                   )
            td.signals.testPassed.connect(self.on_test_dialog_finished)
            td.signals.testFailed.connect(self.on_test_dialog_finished)
            td.exec_()

    def _check_collector_is_configured(self):
        if not self.collector_configured:
            self._show_information_message("The collector must be configured before running any tests.")

    def _sensor_selected_for_testing(self, item: QListWidgetItem):
        if self.collector_configured:
            serial_number: str = item.text()
            sensor: Sensor = self._sensor_log.get_sensor(serial_number)
            self._test_sensor(sensor)
        else:
            message = "The collector must be configured before running any tests."
            QMessageBox.information(self, dialog_title(), message, QMessageBox.Ok)

    def _create_menus(self):
        settings = QSettings()

        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        # create top level menus
        self.menu_options = self.menuBar().addMenu("&Options")
        self.menu_help = self.menuBar().addMenu("&Help")

        # ----- create actions -----
        self.define_set_action = QAction(QIcon(r"laboot/resources/images/menu_icons/set-02_128.png"),
                                         "", self)
        self.collector_configuration_action = QAction(QIcon(r"laboot/resources/images/menu_icons/config-02_128.png"),
                                               "", self)
        self.save_results_action = QAction(QIcon(r"laboot/resources/images/menu_icons/save-01_48.png"),
                                           "", self)
        self.exit_action = QAction(QIcon(r"laboot/resources/images/menu_icons/exit-01_128.png"), "", self)

        # menu_tasks actions
        self.start_five_amp_action = QAction(QIcon(r"laboot/resources/images/menu_icons/bolt-01_48.png"),
                                             "", self)

        # menu_options actions
        self.options_auto_collector_configuration_action = QAction("Auto Configure Collector", self)
        self.options_successive_testing_action = QAction("Successive testing", self)
        self.options_headless_action = QAction("Headless mode", self)

        self.help_about_action = QAction(QIcon(r"laboot/resources/images/menu_icons/info-01_32.png"), "&About", self)

        # ----- configure options -----

        # menu
        self.define_set_action.setStatusTip("Manually enter serial numbers.")

        self.collector_configuration_action.setEnabled(True)
        self.collector_configuration_action.setStatusTip("Configures collector with serial numbers.")

        self.start_five_amp_action.setEnabled(False)
        self.start_five_amp_action.setStatusTip("Start 5 Amp test.")

        self.save_results_action.setEnabled(False)
        self.save_results_action.setStatusTip("Save test results.")

        self.exit_action.setStatusTip("Exit the application.")

        # menu_options
        self.options_auto_collector_configuration_action.setCheckable(True)
        if settings.value("ui/menus/options/autoconfigcollector", "False") == "True":
            self.options_auto_collector_configuration_action.setChecked(True)
        self.options_auto_collector_configuration_action.setStatusTip(
            "Automatically configures collector on serial number import.")

        self.options_successive_testing_action.setCheckable(True)
        self.options_successive_testing_action.setChecked(False)
        self.options_successive_testing_action.setStatusTip("Test units one after the other pausing in between.")
        self.options_successive_testing_action.setEnabled(False)

        self.options_headless_action.setCheckable(True)
        self.options_headless_action.setChecked(False)
        self.options_headless_action.setStatusTip("In headless mode, the get_driver window will not appear.")
        settings.setValue("ui/menus/options/headless", False)

        # menu_help
        self.help_about_action.setStatusTip("Information about Low Amperage Boot.")

        # ----- configure triggers -----
        self.define_set_action.triggered.connect(self.on_define_set_action_triggered)

        self.collector_configuration_action.triggered.connect(
            lambda: self.on_configure_collector_action_triggered(self._sensor_log.get_serial_numbers(),
                                                                 QSettings().value('main/config_password'),
                                                                 constants.URL_CONFIGURATION,
                                                                 lambda: self._get_browser(
                                                                     constants.CHROMEDRIVER_PATH
                                                                 ))
        )

        self.start_five_amp_action.triggered.connect(self.on_start_five_amp_test_action_triggered)
        self.save_results_action.triggered.connect(self.on_save_action_triggered)
        self.exit_action.triggered.connect(self.close)

        self.options_headless_action.toggled.connect(lambda s: settings.setValue("ui/menus/options/headless", s))

        self.help_about_action.triggered.connect(self.on_menu_help_about_action_triggered)

        # ----- add to menus -----

        # menu_options
        self.menu_options.addAction(self.options_auto_collector_configuration_action)
        self.menu_options.addAction(self.options_successive_testing_action)
        self.menu_options.addAction(self.options_headless_action)

        # menu_help
        self.menu_help.addAction(self.help_about_action)

        # set up toolbar
        toolbar.addAction(self.define_set_action)
        toolbar.addAction(self.collector_configuration_action)
        toolbar.addSeparator()
        toolbar.addAction(self.start_five_amp_action)
        toolbar.addSeparator()
        toolbar.addAction(self.save_results_action)
        toolbar.addAction(self.exit_action)

    # PRIVATE INTERFACE METHODS

    def _show_information_message(self, message):
        icon = QPixmap(r"laboot/resources/images/info_72.png")
        msg_box = QMessageBox(QMessageBox.NoIcon,
                              f"{dialog_title()} - Info",
                              message,
                              QMessageBox.Ok, self)
        msg_box.setIconPixmap(icon)
        msg_box.exec_()

    def _ask_yes_no_question(self, message) -> bool:
        return QMessageBox.question(self, f"{dialog_title()}",
                                    message,
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No) == QMessageBox.Yes

    def _save_ui_state(self, settings_repository):
        settings_repository.setValue("ui/menus/options/autoconfigcollector",
                                     str(self.options_auto_collector_configuration_action.isChecked())
                                     )
