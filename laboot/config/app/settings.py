# settings.py
from PyQt5.QtCore import QSettings, QCoreApplication


org_name = "Medium Voltage Sensors"
app_name = "laboot"

QCoreApplication.setOrganizationName(org_name)
QCoreApplication.setApplicationName(app_name)


def load():
    with open(r"laboot/resources/data/config.txt") as in_f:
        settings = QSettings()
        for setting in in_f.readlines():
            if not setting.strip() or setting.startswith("#"):
                continue
            setting = setting.strip().split("=", 1)
            print(f"creating setting: {setting}")
            settings.setValue(setting[0], setting[1])
