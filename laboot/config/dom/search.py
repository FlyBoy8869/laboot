# search.py
from laboot.config.dom.constants import *


class SearchDom:
    @staticmethod
    def for_serial_input_elements(webdriver):
        return SearchDom._find_elements_by_name(webdriver, serial_number_elements)

    @staticmethod
    def for_angle_input_elements(webdriver):
        return SearchDom._find_elements_by_name(webdriver, correction_angle_elements)

    @staticmethod
    def for_password_input_element(webdriver):
        return webdriver.find_element_by_name(password_element)

    @staticmethod
    def for_save_config_button(webdriver):
        return webdriver.find_element_by_id(save_config_element)

    @staticmethod
    def for_voltage_ride_through_radio_button_element(webdriver):
        return webdriver.find_element_by_id(voltage_ride_through)

    @staticmethod
    def for_sixty_hz_radio_button_element(webdriver):
        return webdriver.find_element_by_xpath(sixty_hertz)

    @staticmethod
    def _find_elements_by_name(webdriver, elements):
        """Finds elements by name."""
        return [webdriver.find_element_by_name(element) for element in elements]
