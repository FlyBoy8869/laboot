import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from laboot.config.app import logging as lab_logging
from laboot.config.app import settings as lab_settings

lab_settings.load_from_config_file(r"laboot/resources/data/config.txt", QSettings())
lab_settings.load_from_command_line(sys.argv, QSettings())
lab_logging.initialize()


def main(args):
    app = QApplication(args)

    from laboot.mainwindow import MainWindow
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv)
