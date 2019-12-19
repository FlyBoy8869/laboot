# collector.py
import logging
from typing import List, Callable, Any

from PyQt5.QtCore import QSettings

from laboot.config.dom.search import SearchDom
from laboot.signals import CollectorSignals


class CollectorConfigurator:
    def __init__(self, browser):
        settings = QSettings()
        self.logger = logging.getLogger(__name__)
        self.signals = CollectorSignals()
        self.browser = browser

        self.configuration_url = settings.value("pages/configuration")
        self.config_password = settings.value("main/config_password")

    def configure_serial_numbers(self, serial_numbers: tuple):
        self.logger.info("Configuring serial numbers.")
        self.logger.debug(f"Using serial numbers: {serial_numbers}")

        self._configure_collector(serial_numbers, self.configuration_url, self._configure_serial_numbers)

    def _configure_collector(self, data: Any, url: str, func: Callable):
        # TODO: see if better type hint than Any for dropped_filename
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
        """

        # BUG: app will probably shit the bed if the user login page is displayed
        self.browser.get(url)

        if "offline" in self.browser.page_source:
            self.signals.offline.emit("The collector appears to be offline.")
            return

        # TODO: some how, some day verify this will work; see LWTest codebase for solution
        # TODO: add code to handle login page

        func(data)

        self._select_60_hz()
        self._disable_voltage_ride_through()

        self._submit_changes()

        self.signals.configured.emit()

    def _configure_serial_numbers(self, serial_numbers: List[str]):
        """Must receive a list of 6 strings representing numeric values."""
        serial_elements = SearchDom.for_serial_input_elements(self.browser)

        for index, element in enumerate(serial_elements[:len(serial_numbers)]):
            element.clear()
            element.send_keys(serial_numbers[index])

        self.logger.debug(f"Collector configured with serial numbers: {serial_numbers}")

    def _disable_voltage_ride_through(self):
        self.logger.info("Disabling Voltage Ride Through.")

        vrt = SearchDom.for_voltage_ride_through_radio_button_element(self.browser)
        if vrt.is_selected():
            vrt.click()

    def _select_60_hz(self):
        self.logger.info("Selecting 60Hz")
        SearchDom.for_sixty_hz_radio_button_element(self.browser).click()

    def _handle_admin_login(self):
        pass

    def _submit_changes(self):
        self.logger.info("Saving changes to the collector.")

        SearchDom.for_password_input_element(self.browser).send_keys(self.config_password)
        SearchDom.for_save_config_button(self.browser).click()

        self.logger.info("Changes saved.")
