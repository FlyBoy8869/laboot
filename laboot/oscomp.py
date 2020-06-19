import enum
import platform

from PyQt5.QtCore import QSettings


class OSType(enum.Enum):
    LINUX = "Linux"
    MAC = "Darwin"
    WINDOWS = "Windows"


_os_map = {"Darwin": OSType.MAC, "Linux": OSType.LINUX, "Windows": OSType.WINDOWS}
os_type = _os_map[platform.system()]


class QSettingsAdapter:
    """This class hides the type differences between Windows and macOS."""

    @staticmethod
    def value(key):
        """Returns a lower cased string of the 'key' contents."""
        return str(QSettings().value(key, None)).lower()

    @staticmethod
    def set_value(key, value):
        QSettings().setValue(key, value)
