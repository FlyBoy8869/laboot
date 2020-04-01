# spreadsheet.py

import sys
from typing import Optional, Tuple, List
import logging
from functools import partial

from PyQt5.QtCore import QSettings
from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook as openpyxlWorkbook, Worksheet as openpyxlWorksheet

from laboot.utilities import utilities
import laboot.constants as constants


class SerialNumberInfo:
    def __init__(self, serial_number: str, position: int, failure: bool):
        self.serial_number = serial_number
        self.position = position
        self.failure = failure

    def __repr__(self):
        return f"SerialNumberResult('{self.serial_number}', {self.failure})"


def get_serial_numbers(filename: str) -> Tuple[SerialNumberInfo]:  # Tuple[str]:
    """Loads serial numbers from a spreadsheet.

    Parameters
    ----------

    filename: str
        path to spreadsheet

    Returns
    -------
        tuple[str]
            a tuple of strings representing sensor serial numbers
    """

    print("spreadsheet.get_serial_numbers() called...")
    return _extract_serial_numbers_from_worksheet(filename)


def save_test_results(filename: str, results: Tuple[str]):
    """Save results of MV Sensor 5 Amp test to spreadsheet.

    Parameters
    ----------

    filename: str
        path to spreadsheet

    results: tuple[str]
        For example, ("Pass", "Fail", "Pass", "Fail", "Pass", "Fail").
    """
    settings = QSettings()
    logger = logging.getLogger(__name__)

    logger.info(f"saving test results to spreadsheet: {results}")
    logger.info(f"using file: {filename}")

    save_locations = settings.value('spreadsheet/result_locations').split(' ')

    workbook = _get_workbook(filename)
    worksheet = _get_worksheet(workbook, settings.value('spreadsheet/worksheet'))
    logger.info(f"saving to worksheet {worksheet}")

    for result, location in zip(results, save_locations):
        logger.debug(f"saving '{result}' to location '{location}'")
        worksheet[location].value = str(result)

    workbook.save(filename)
    workbook.close()


def _get_workbook(filename: str) -> (openpyxlWorkbook, Optional):
    logger = logging.getLogger(__name__)
    try:
        # read_only=False, keep_vba=True prevents Excel from thinking the spreadsheet has been corrupted
        # data_only=True returns the result of a formula instead of the actual formula in the cell
        workbook = load_workbook(filename=filename, read_only=False, keep_vba=True, data_only=True)
    except FileNotFoundError:
        logger.debug("spreadsheet not found")
        # utilities.print_exception_info()
        sys.exit(1)
    except Exception:
        utilities.print_exception_info()
        raise Exception

    return workbook


def _get_worksheet(workbook: openpyxlWorkbook, worksheet_name: str) -> openpyxlWorksheet:
    try:
        worksheet = workbook[worksheet_name]
        return worksheet
    except KeyError:
        print(f"An error occurred retrieving worksheet '{worksheet_name}' from the spreadsheet.")
        sys.exit(1)


def _extract_serial_numbers_from_worksheet(filename: str) -> Tuple[SerialNumberInfo]:  # Tuple[str]
    logger = logging.getLogger(__name__)
    settings = QSettings()

    workbook = _get_workbook(filename)
    worksheet = _get_worksheet(workbook, settings.value("spreadsheet/worksheet"))

    logger.debug(f"Opened worksheet_name {settings.value('spreadsheet/worksheet')} from workbook {filename}")

    serial_locations = settings.value('spreadsheet/serial_locations').split(' ')
    serial_numbers = []
    for serial_location in serial_locations:
        serial_numbers.append(str(worksheet[serial_location].value))

    serial_numbers = tuple([serial_number if serial_number != 'None' else "0" for serial_number in serial_numbers])

    logger.debug(f"Extracted serial numbers from spreadsheet: {serial_numbers}")

    # return tuple(serial_numbers)
    results = _identify_failures(worksheet, serial_numbers)

    workbook.close()

    return results


def _get_cell_contents(worksheet: openpyxlWorksheet, cell: str) -> str:
    return str(worksheet[cell].value)


def _is_failure(worksheet: openpyxlWorksheet, position: int) -> bool:
    gcc = partial(_get_cell_contents, worksheet)

    if gcc(constants.RAW_CONFIG_RESULTS[position]).lower() != 'pass' or \
       gcc(constants.LOW_VOLTAGE_RESULTS[position]).lower() != 'pass' or \
       gcc(constants.HIGH_VOLTAGE_RESULTS[position]).lower() != 'pass' or \
       gcc(constants.PERSISTENCE_RESULTS[position]).lower() != 'pass' or \
       gcc(constants.REPORTING_RESULTS[position]).lower() != 'pass' or \
       gcc(constants.CALIBRATIONS_RESULTS[position]).lower() != 'pass' or \
       gcc(constants.FAULT_CURRENT_RESULTS[position]).lower() != 'pass':

        return True

    if int(gcc(constants.RSSI_RESULTS[position])) <= -75 or \
       abs(float(gcc(constants.TEMPERATURE_REFERENCE)) - float(gcc(constants.TEMPERATURE_RESULTS[position]))) > 15:

        return True

    return False


def _identify_failures(worksheet: openpyxlWorksheet, serial_numbers: Tuple[str]) -> Tuple[SerialNumberInfo]:
    results: List[SerialNumberInfo] = []

    for index, serial_number in enumerate(serial_numbers):
        fails = True if _is_failure(worksheet, index) else False
        results.append(SerialNumberInfo(serial_number, index, fails))

    return tuple(results)


if __name__ == '__main__':
    # filename = r"C:\Users\charles\Desktop\ATR-PRD#-SN9802386-SN9802165-SN9802316-SN9802334-SN9802310-SN9802193.xlsm"
    filename = r"C:\Users\charles\Desktop\MVSS Test Results\01-06-2020\Set 2\ATR-PRD#-SN9802603-SN9802600-SN9802506-SN9802457.xlsm"
    workbook = _get_workbook(filename)
    worksheet = _get_worksheet(workbook, 'Sensor(s)')

    sensor_resutls = []

    for p, serial_number in enumerate(['9800001', '9800002', '9800003', '9800004', '9800005', '9800006']):
        if _is_failure(worksheet, p):
            sensor_resutls.append(SerialNumberInfo(serial_number, p, True))

    print(sensor_resutls)

    workbook.close()
