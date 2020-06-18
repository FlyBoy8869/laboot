# spreadsheet.py

from functools import partial
from typing import Tuple, List

from PyQt5.QtCore import QSettings
from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook as openpyxlWorkbook, Worksheet as openpyxlWorksheet

import laboot.constants as constants
from laboot.utilities import utilities
from laboot.utilities.returns import Result


class SerialNumberInfo:
    def __init__(self, serial_number: str, position: int, failure: bool):
        self.serial_number = serial_number
        self.position = position
        self.failure = failure

    def __repr__(self):
        return f"SerialNumberResult('{self.serial_number}', {self.failure})"


def get_serial_numbers(file_name: str) -> Result:
    """Loads serial numbers from a spreadsheet.

    Parameters
    ----------

    file_name: str
        path to spreadsheet

    Returns
    -------
        Result
            A class representing success or failure, a value if successful or None if not,
            a message if an error occurred, and the exception if one is thrown.

            For example,

                Result(True, [9800001, 9800002, 9800003], message=None, exception=None)

                or

                Result(False, None, message="Error retrieving serial numbers.", exception=FileNotFoundError())
    """

    return _get_serial_numbers_from_worksheet(file_name)


def save_test_results(file_name: str, results: Tuple[str]) -> Result:
    """Save results of MV Sensor 5 Amp test to spreadsheet.

    Parameters
    ----------

    file_name: str
        path to spreadsheet

    results: tuple[str]
        For example, ("Pass", "Fail", "Pass", "Fail", "Pass", "Fail").
    """
    settings = QSettings()

    save_locations = settings.value('spreadsheet/result_locations').split(' ')

    if not (work_book_result := _get_workbook(file_name)):
        return work_book_result

    if not (work_sheet_result := _get_worksheet(work_book_result(), settings.value("spreadsheet/worksheet"))):
        return work_sheet_result

    for result, location in zip(results, save_locations):
        work_sheet_result()[location].value = str(result)

    work_book_result().save(file_name)
    work_book_result().close()

    return Result(True, results, message="Data successfully saved.")


def _get_workbook(file_name: str) -> Result:
    try:
        # read_only=False, keep_vba=True prevents Excel from thinking the spreadsheet has been corrupted
        # data_only=True returns the result of a formula instead of the actual formula in the cell
        work_book: openpyxlWorkbook = load_workbook(filename=file_name, read_only=False, keep_vba=True, data_only=True)
    except Exception as e:
        utilities.print_exception_info()
        return Result(False, None, message="Unable to load the workbook.", exception=e)

    return Result(True, work_book)


def _get_worksheet(work_book: openpyxlWorkbook, worksheet_name: str) -> Result:
    try:
        work_sheet = work_book[worksheet_name]
    except KeyError as e:
        message = f"Unable to locate worksheet '{worksheet_name}' in the spreadsheet."
        return Result(False, None, message=message, exception=e)
    except Exception as e:
        return Result(False, None, message=str(e), exception=e)

    return Result(True, work_sheet)


def _get_serial_numbers_from_worksheet(file_name: str) -> Result:
    settings = QSettings()

    if not (work_book_result := _get_workbook(file_name)):
        return work_book_result

    if not (work_sheet_result := _get_worksheet(work_book_result(), settings.value("spreadsheet/worksheet"))):
        return work_sheet_result

    serial_locations = settings.value('spreadsheet/serial_locations').split(' ')
    serial_numbers = []
    for serial_location in serial_locations:
        serial_numbers.append(str(work_sheet_result()[serial_location].value))

    serial_numbers = [serial_number if serial_number != 'None' else "0" for serial_number in serial_numbers]
    serial_numbers_with_failures_identified: Tuple[SerialNumberInfo] = _identify_failures(work_sheet_result(),
                                                                                          serial_numbers)

    work_book_result().close()

    return Result(True, serial_numbers_with_failures_identified)


def _get_cell_contents(work_sheet: openpyxlWorksheet, cell: str) -> str:
    return str(work_sheet[cell].value)


def _is_failure(work_sheet: openpyxlWorksheet, position: int) -> bool:
    gcc = partial(_get_cell_contents, work_sheet)

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


def _identify_failures(work_sheet: openpyxlWorksheet, serial_numbers) -> Tuple[SerialNumberInfo]:
    results: List[SerialNumberInfo] = []

    for index, serial_number in enumerate(serial_numbers):
        fails = True if _is_failure(work_sheet, index) else False
        results.append(SerialNumberInfo(serial_number, index, fails))

    return tuple(results)
