# spreadsheet.py
import sys
from typing import Optional, Tuple
import logging

from PyQt5.QtCore import QSettings
from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook as openpyxlWorkbook, Worksheet as openpyxlWorksheet

from laboot.utilities import utilities


def get_serial_numbers(filename: str) -> Tuple[str]:
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
        # read_only=False, keep_vba=True prevent Excel from thinking the spreadsheet has been corrupted
        workbook = load_workbook(filename=filename, read_only=False, keep_vba=True)
    except FileNotFoundError:
        logger.debug("spreadsheet not found")
        # utilities.print_exception_info()
        sys.exit(1)
    except Exception:
        utilities.print_exception_info()
        raise Exception

    return workbook


def _get_worksheet(workbook: openpyxlWorkbook, worksheet_name: str) -> openpyxlWorksheet:
    logger = logging.getLogger(__name__)
    try:
        worksheet = workbook[worksheet_name]
        logger.info(f"retrieved worksheet '{worksheet_name}' from workbook")
        return worksheet
    except KeyError:
        logger.debug(f"Worksheet '{worksheet_name}' does not exist. Check the spelling in config.txt.")
        sys.exit(1)


def _extract_serial_numbers_from_worksheet(filename: str) -> Tuple[str]:
    logger = logging.getLogger(__name__)
    settings = QSettings()

    workbook = _get_workbook(filename)
    worksheet = _get_worksheet(workbook, settings.value("spreadsheet/worksheet"))

    logger.debug(f"Opened worksheet_name {settings.value('spreadsheet/worksheet')} from workbook {filename}")

    serial_locations = settings.value('spreadsheet/serial_locations').split(' ')
    serial_numbers = []
    for serial_location in serial_locations:
        serial_numbers.append(str(worksheet[serial_location].value))

    workbook.close()

    serial_numbers = [serial_number if serial_number != 'None' else "0" for serial_number in serial_numbers]

    logger.debug(f"Extracted serial numbers from spreadsheet: {serial_numbers}")

    return tuple(serial_numbers)
