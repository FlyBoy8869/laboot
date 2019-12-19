# collector.py
import logging
from collections import namedtuple
from typing import Tuple

from PyQt5.QtCore import QSettings
from selenium import webdriver

from laboot.config.dom.constants import (_serial_number_elements, _correction_angle_elements,
                                         _voltage_ride_through,
                                         _password_element, _save_config_element)

ConfigurationResult = namedtuple("ConfigurationResult", "result exc message")


class Configurator:
    def __init__(self):
        settings = QSettings()

        self.browser = self._get_browser()
        self.config_password = settings.value("main/config_password")
        self.admin_user = settings.value("main/admin_user")
        self.admin_password = settings.value("main/admin_password")

    def close_browser(self):
        self.browser.quit()

    def configure(self):
        pass

    def _disable_voltage_ride_through(self):
        logger = logging.getLogger(__name__)
        logger.info("disabling Voltage Ride Through")
        vrt = self._find_voltage_ride_through_element()
        logger.debug(f"Voltage Ride Through checked state: {vrt.is_selected()}")
        if vrt.is_selected():
            vrt.click()

    def _select_60_hz(self):
        logger = logging.getLogger(__name__)
        logger.info("selecting 60Hz")
        self.browser.find_element_by_xpath("//input[@name='frequency'][@value='60']").click()

    def _find_serial_input_elements(self):
        return self._find_elements_by_name(_serial_number_elements)

    def _find_angle_elements(self):
        return self._find_elements_by_name(_correction_angle_elements)

    def _find_password_element(self):
        return self.browser.find_element_by_name(_password_element)

    def _find_save_config_button(self):
        return self.browser.find_element_by_id(_save_config_element)

    def _find_voltage_ride_through_element(self):
        return self.browser.find_element_by_id(_voltage_ride_through)

    def _find_elements_by_name(self, elements: Tuple):
        """Finds elements by name."""
        return [self.browser.find_element_by_name(element) for element in elements]

    def _enter_password(self):
        self._find_password_element().send_keys(self.config_password)

    def _get_browser(self):
        # TODO: add exception handling
        settings = QSettings()

        driver_executable = settings.value("drivers/chromedriver")
        service_log_path = r"laboot\resources\logs\chromewebdriver.log"
        browser = webdriver.Chrome(executable_path=driver_executable,
                                   service_log_path=service_log_path)

        return browser

    def _handle_admin_login(self):
        pass

    def _save_changes(self):
        self._find_save_config_button().click()

    def _submit_changes(self):
        logger = logging.getLogger(__name__)
        logger.info("Saving changes to the collector.")
        self._enter_password()
        self._save_changes()

# TODO: Will have to account for the times when the administration pages rears it's head
# TODO: Need to implement exception handling
#       - program crashes with a url that can't be reached, found, etc. in configure()
#           - Fixed: now check browser.page_source for presence of "offline", if present return
