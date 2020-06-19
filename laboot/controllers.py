from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QListWidgetItem

from laboot import constants, oscomp
from laboot.oscomp import OSType
from laboot.utilities import sound
from laboot.widgets import LabootListWidget


_snd_passed = QSound(r"laboot/resources/audio/cash_register.wav")
_snd_failed = QSound(r"laboot/resources/audio/error_01.wav")

_green_brush = QBrush(QColor(0, 255, 0, 100))
_red_brush = QBrush(QColor(255, 0, 0, 100))

_yellow_brush = QBrush(QColor(Qt.yellow))
_black_brush = QBrush(QColor(Qt.black))


class SerialNumberViewController:
    def __init__(self, view: LabootListWidget):
        self._view = view

    def populate_from_sensor_log(self, sensor_log):
        self._populate(sensor_log.get_serial_numbers_as_tuple())
        self._highlight_failures(sensor_log.get_failed_serial_numbers())

    def indicate_test_result(self, result):
        sound.play_sound(self._get_sound_for_test_result(result))
        self._view.currentItem().setBackground(self._get_brush_for_test_result(result))

    def _populate(self, serial_numbers):
        self._add_serial_numbers_to_view(serial_numbers)

    def _highlight_failures(self, failures):
        for item in self._get_failures(failures):
            self._set_item_background_to_yellow(item)
            if oscomp.os_type == OSType.MAC:
                self._set_item_text_color_to_black(item)

    def _add_serial_numbers_to_view(self, serial_numbers):
        self._view.clear()
        for serial_number in [serial_number for serial_number in serial_numbers
                              if serial_number is not constants.BLANK_SERIAL_NUMBER]:
            item = self._create_item_with_serial_number(serial_number)
            self._view.addItem(item)

    def _get_failures(self, serial_numbers):
        return [results[0] for serial_number in serial_numbers
                if (results := self._view.findItems(serial_number, Qt.MatchExactly))]

    @staticmethod
    def _set_item_background_to_yellow(item):
        item.setBackground(_yellow_brush)

    @staticmethod
    def _set_item_text_color_to_black(item):
        item.setForeground(_black_brush)

    @staticmethod
    def _create_item_with_serial_number(serial_number):
        return QListWidgetItem(serial_number)

    @staticmethod
    def _get_sound_for_test_result(result):
        return _snd_passed if result.result == "Pass" else _snd_failed

    @staticmethod
    def _get_brush_for_test_result(result):
        return _green_brush if result.result == "Pass" else _red_brush
