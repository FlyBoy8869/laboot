# strategies/from_web_site.py
import logging

import requests
from PyQt5.QtCore import QSettings

from laboot import constants
from laboot.strategies.strategy import BaseStrategy, RequestResults
from laboot.strategies.strategy import STATUS_ITEM_CONNECTED, STATUS_ITEM_NOT_CONNECTED, STATUS_ITEM_NOT_PRESENT, \
    STATUS_REQUEST_TIMED_OUT

link_map = {(True, False, False): "not joined, not linked",
            (True, True, False): "joined, not linked",
            (True, True, True): "joined and linked"}


class FromWebSiteStrategy(BaseStrategy):
    def __init__(self, serial_number, url):
        super().__init__(serial_number)
        self.url = url
        # used when requests.exceptions.Timeout occurs
        self.request_timed_out = False
        self.exc = None

        self.logger = logging.getLogger(__name__)

    def check_link_status(self) -> RequestResults:
        self.logger.info("Checking for a link.")
        return self._process_lines(self.serial_number, self.url)

    def _request_lines(self, serial_number, url):
        # Note: this method is structured this way due to the fact
        # that Qt does not propagate exceptions up the call stack,
        # but instead chooses to "eat" them.
        #
        # Change with caution, if at all.

        try:
            r = requests.get(url, timeout=constants.REQUEST_TIMEOUT)
            for line in r.text.split("\n"):
                # TODO: figure out how to handle special characters like TM or Trade Mark
                # self.logger.debug(f"Retrieved line from website: {line}")
                if serial_number in line:
                    yield line
        except (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout) as e:
            self.request_timed_out = True
            self.exc = e

        return []

    def _process_lines(self, serial_number, url):
        for line in self._request_lines(serial_number, url):
            self.logger.debug(f"processing input: {line}")
            line = line.split(" ")
            self.logger.debug(f"Line after split: {line}")
            line = tuple([piece.strip() for piece in line if piece])
            self.logger.debug(f"Line after further processing: {line}")
            status = tuple([True if piece and piece != "-1" else False
                            for piece in line])

            self.logger.info("Evaluating input.")
            result = link_map[status[0:3]]

            if result == "joined and linked":
                self.logger.info("Returning successful results.")
                return RequestResults(status=STATUS_ITEM_CONNECTED, message=None)

            self.logger.info("Returning unsuccessful results: no join, no link")
            return RequestResults(status=STATUS_ITEM_NOT_CONNECTED, message=None)

        # Need to pass info about the timeout up the stack manually since Qt "eats" exceptions.
        if self.request_timed_out:
            self.logger.info("Request timed out.")
            return RequestResults(status=STATUS_REQUEST_TIMED_OUT,
                                  message="Request timed out while querying the collector.\n\n" +
                                  "Items to check:\n" +
                                  "\t- collector powered on and booted\n" +
                                  "\t- url in config.txt is correct\n" +
                                  "_____________________________________________________\n\n" +
                                  f"{self.exc}")

        self.logger.info("Collector has not refreshed its serial numbers.")
        return RequestResults(status=STATUS_ITEM_NOT_PRESENT, message=None)
