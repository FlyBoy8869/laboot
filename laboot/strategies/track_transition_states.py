# laboot/strategies/track_transition_states.py
from laboot.strategies.strategy import BaseStrategy


class TrackTransitionStatesStrategy(BaseStrategy):
    def __init__(self, serial_number):
        super().__init__(serial_number)

    def check_link_status(self):
        return self.always_pass(self.serial_number)

    @staticmethod
    def always_pass(serial_number):
        status_strings = [f"{serial_number} -1 -1",
                          f"{serial_number} -1 -1",
                          f"{serial_number} -1 -1",
                          f"{serial_number} {serial_number} -1",
                          f"{serial_number} {serial_number} -1",
                          f"{serial_number} {serial_number} -1",
                          f"{serial_number} {serial_number} {serial_number} -69 dB"]

        for status in status_strings:
            yield status
