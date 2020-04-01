# sensor.py
from typing import Optional


class Sensor:
    def __init__(self, line_position, serial_number, prior_failure: bool = False):
        self.test_position = line_position
        self.serial_number = serial_number
        self._prior_failure = prior_failure
        self.tested = False
        self.result = "Not Tested"

    @property
    def failure(self) -> bool:
        return self._prior_failure


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
        return self._find_sensor_by_serial_number(serial_number).tested

    def set_test_result(self, serial_number: str, result: str):
        sensor = self._find_sensor_by_serial_number(serial_number)
        sensor.result = result
        sensor.tested = True

    def _find_sensor_by_serial_number(self, serial_number) -> (Sensor, Optional):
        for sensor in self.log.values():
            if sensor.serial_number == serial_number:
                return sensor
        return None
