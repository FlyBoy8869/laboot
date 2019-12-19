# strategies/strategy.py
from collections import namedtuple

STATUS_ITEM_CONNECTED: int = 0
STATUS_ITEM_NOT_CONNECTED: int = 1
STATUS_ITEM_NOT_PRESENT: int = 2
STATUS_REQUEST_TIMED_OUT: int = 3

STATUS_NOT_JOINED_NOT_LINKED: int = 4
STATUS_JOINED_NOT_LINKED: int = 5
STATUS_JOINED_AND_LINKED: int = 6

RequestResults = namedtuple("RequestResults", "status message")


class BaseStrategy:
    def __init__(self, serial_number):
        self.serial_number = serial_number

    def check_link_status(self):
        raise NotImplementedError
