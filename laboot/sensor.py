# sensor.py
from typing import Optional

from laboot import constants
from laboot.utilities.time import TestTimeRecord


class Sensor:
    def __init__(self, line_position, serial_number, test_time_record: TestTimeRecord, prior_failure: bool = False):
        self.test_position = line_position
        self.serial_number = serial_number
        self._prior_failure = prior_failure
        # self.test_time = test_time
        self.tested = False
        self.result = "Not Tested"
        self.test_time_record = test_time_record

    @property
    def failure(self) -> bool:
        return self._prior_failure

    @property
    def remaining_time(self):
        return self.test_time_record.remaining_time

    def set_test_time(self, test_time_record: TestTimeRecord):
        self.test_time_record = test_time_record


class SensorLog:
    def __init__(self):
        self.log = dict()

    def append(self, sensor: Sensor):
        self.log[(sensor.test_position, sensor.serial_number)] = sensor

    def clear(self):
        self.log.clear()

    def count(self):
        return len(self.log)

    def get_sensor(self, serial_number: str):
        return self._find_sensor_by_serial_number(serial_number)

    def get_serial_numbers(self) -> tuple:
        return tuple([sensor.serial_number for sensor in self.log.values()])

    def get_line_position(self, serial_number: str) -> int:
        return self._find_sensor_by_serial_number(serial_number).test_position

    def get_test_results(self) -> tuple:
        return tuple([sensor.result for sensor in self.log.values()])

    def is_tested(self, serial_number: str) -> bool:
        return self._find_sensor_by_serial_number(serial_number).is_tested()

    def set_test_time(self, serial_number: str, test_time_record: TestTimeRecord):
        self._find_sensor_by_serial_number(serial_number).set_test_time(test_time_record)

    def set_test_result(self, serial_number: str, result: str):
        sensor = self._find_sensor_by_serial_number(serial_number)
        sensor.result = result
        sensor.tested = True

    def _find_sensor_by_serial_number(self, serial_number) -> (Sensor, Optional):
        for sensor in self.log.values():
            if sensor.serial_number == serial_number:
                return sensor
        return None


class TestTime:
    def __init__(self):
        self.test_time_remaining = 1500
