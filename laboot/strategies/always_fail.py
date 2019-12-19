# always_fail.py
from laboot.strategies.strategy import BaseStrategy, STATUS_ITEM_NOT_CONNECTED, RequestResults


class AlwaysFailStrategy(BaseStrategy):
    def __init__(self, serial_number):
        super().__init__(serial_number)

    def check_link_status(self):
        return self.always_fail(self.serial_number)

    @staticmethod
    def always_fail(serial_number):
        return RequestResults(status=STATUS_ITEM_NOT_CONNECTED, message=None)
