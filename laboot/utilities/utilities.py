# utilities/utilities.py
import sys
import traceback


def print_exception_info():
    for line in traceback.format_exception(*sys.exc_info()):
        print(line.strip())


def to_bool(value) -> bool:
    """Converts any variation the strings 'true' and 'false' to boolean values."""

    # explicit cast is for protection
    if str(value).lower() == "true":
        return True
    else:
        return False

