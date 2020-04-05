# utilities/time.py
from datetime import datetime


def format_seconds_to_minutes_seconds(seconds):
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


class TestTimeRecord:
    def __init__(self, test_time: int, current_time: datetime):
        self.test_time = test_time
        self.current_time = current_time

    @property
    def remaining_time(self):
        return self.test_time - (datetime.now() - self.current_time).seconds
