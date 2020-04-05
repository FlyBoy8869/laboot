# settings.py

from PyQt5.QtCore import QSettings, QCoreApplication


org_name = "Medium Voltage Sensors"
app_name = "laboot"

QCoreApplication.setOrganizationName(org_name)
QCoreApplication.setApplicationName(app_name)


def load_from_config_file(config_file: str, settings_repo: QSettings):
    with open(config_file) as in_f:
        for setting in in_f.readlines():
            if not setting.strip() or setting.startswith("#"):
                continue
            setting = setting.strip().split("=", 1)
            print(f"creating setting: {setting}")
            settings_repo.setValue(setting[0], setting[1])


def load_from_command_line(args: list, settings_repo: QSettings):
    debug = True if 'DEBUG' in args else False
    settings_repo.setValue('DEBUG', debug)
