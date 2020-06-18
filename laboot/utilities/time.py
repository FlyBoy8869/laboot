# utilities/time.py
from datetime import datetime

from laboot import constants


def format_seconds_to_minutes_seconds(seconds):
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


class TestTimeRecord:
    def __init__(self, test_time: int):
        self.test_time = test_time
        self.interruption_time = None

    @property
    def remaining_time(self):
        if self.interruption_time:
            if (test_time := self.test_time - (datetime.now() - self.interruption_time).seconds) <= 0:
                return 0
            return test_time

        return self.test_time

    def reset(self):
        self.test_time = constants.TEST_TIME
        self.interruption_time = None

    def set_test_interruption_time(self, remaining_test_time: int, interrupt_time: datetime):
        self.interruption_time = interrupt_time
        self.test_time = remaining_test_time
