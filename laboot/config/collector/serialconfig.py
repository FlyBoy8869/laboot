# collector.py
import logging
from collections import namedtuple
from typing import List, Callable, Tuple

from PyQt5.QtCore import QSettings

from laboot.config.collector.configurator import Configurator

ConfigurationResult = namedtuple("ConfigurationResult", "result exc message")


class SerialConfigurator(Configurator):
    def __init__(self, url, serial_numbers):
        super().__init__()

        settings = QSettings()

        self.url = url
        self.serial_numbers = serial_numbers

    def configure(self):
        self._configure_collector(self.serial_numbers, self.url, self._configure_collector)

    def _configure_collector(self, data: Tuple[str], url: str, func: Callable) -> ConfigurationResult:
        # TODO: figure out some sort of exception handling
        """Configures the collector with values for test.

        Parameters
        ----------
        data: (str, list)
            the values to enter into the collector

        url: str
            the url where the dropped_filename will be entered

        func: Callable
            this function will be called with 'dropped_filename' and is responsible
            for performing the task of configuring the collector i.e., func(dropped_filename)

        Returns
        -------
            True if the collector was successfully configured.
            False if an error occurred."""
        logger = logging.getLogger(__name__)

        self.browser.get(url)

        if "offline" in self.browser.page_source:
            print("There appears to be a network issue. The browser reports 'No internet'.")
            return ConfigurationResult(False, None, "Browser reports 'offline'")

        # TODO: some how, some day verify this will work
        if "trigger text" in self.browser.current_url:
            self._handle_admin_login()
            self.browser.get(url)

        func(data)

        self._select_60_hz()
        self._disable_voltage_ride_through()

        self._submit_changes()

        return ConfigurationResult(True, None, None)

    def _configure_serial_numbers(self, serial_numbers: List[str]):
        logger = logging.getLogger(__name__)
        serial_inputs = self._find_serial_input_elements()
        for index, serial_input in enumerate(serial_inputs):
            print(f"configuring {serial_input} with {serial_numbers[index]}")
            serial_input.clear()
            serial_input.send_keys(serial_numbers[index])
        logger.debug(f"Collector configured with serial numbers: {serial_numbers}")
