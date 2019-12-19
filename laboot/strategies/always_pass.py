from laboot.strategies.strategy import BaseStrategy, RequestResults, STATUS_ITEM_CONNECTED


class AlwaysPassStrategy(BaseStrategy):
    def __init__(self, serial_number):
        super().__init__(serial_number)

    def check_link_status(self):
        return self.always_pass(self.serial_number)

    @staticmethod
    def always_pass(serial_number):
        return RequestResults(status=STATUS_ITEM_CONNECTED, message=None)
