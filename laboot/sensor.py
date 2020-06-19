# sensor.py
from typing import Optional

from laboot import constants
from laboot.utilities.time import TestTimeRecord


class Sensor:
    def __init__(self, line_position, serial_number, prior_failure: bool = False):
        self.position = line_position
        self.serial_number = serial_number
        self._prior_failure = prior_failure
        self.tested = False
        self.result = "Not Tested"
        self.test_time_record = TestTimeRecord(constants.TEST_TIME)

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

    def __len__(self):
        return len(self.log)

    def __iter__(self):
        return iter(self.log.values())

    def append(self, sensor: Sensor):
        self.log[(sensor.position, sensor.serial_number, sensor.failure)] = sensor

    def append_all(self, sensors):
        self.clear()
        for sensor in sensors:
            self.append(Sensor(sensor.position, sensor.serial_number, sensor.failure))

    def clear(self):
        self.log.clear()

    def count(self):
        return len(self.log)

    def get_failed_serial_numbers(self):
        return [sensor.serial_number for sensor in self.log.values() if sensor.failure]

    def get_sensor(self, serial_number: str):
        return self._find_sensor_by_serial_number(serial_number)

    def get_serial_numbers_as_tuple(self) -> tuple:
        return tuple([sensor.serial_number for sensor in self.log.values()])

    def get_line_position(self, serial_number: str) -> int:
        return self._find_sensor_by_serial_number(serial_number).position

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

    def _find_sensor_by_serial_number(self, serial_number) -> Optional[Sensor]:
        for sensor in self.log.values():
            if sensor.serial_number == serial_number:
                return sensor
        return None
