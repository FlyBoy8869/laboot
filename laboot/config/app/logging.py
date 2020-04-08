# logging.py
import logging

from PyQt5.QtCore import QSettings


def _get_logging_level_constant(level: str):
    level_constants = {"debug": logging.DEBUG,
                       "info": logging.INFO,
                       "warning": logging.WARNING,
                       "message": logging.ERROR,
                       "critical": logging.CRITICAL}

    return level_constants.get(level, logging.DEBUG)


def initialize():
    settings = QSettings()

    console_handler = logging.StreamHandler()  # defaults to sys.stderr
    console_handler.addFilter(lambda r: False if "selenium" in r.name else True)
    console_handler.addFilter(lambda r: False if "urllib3" in r.name else True)
    console_handler.addFilter(lambda r: False if "test log" in r.name else True)

    file_handler = logging.FileHandler('app.log', mode='w')
    file_handler.addFilter(lambda r: False if "selenium" in r.name else True)
    file_handler.addFilter(lambda r: False if "urllib3" in r.name else True)
    file_handler.addFilter(lambda r: False if "test log" in r.name else True)

    logging.basicConfig(level=_get_logging_level_constant(settings.value("main/debug_level")),
                        format="%(asctime)s : " +
                               "%(name)s : " +
                               "%(levelname)s : " +
                               "%(module)s." +
                               "%(funcName)s(), " +
                               "Line %(lineno)d - " +
                               "%(message)s",
                        datefmt="%d-%b-%y %H:%M:%S",
                        handlers=[console_handler, file_handler])
