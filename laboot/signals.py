from PyQt5.QtCore import QObject, pyqtSignal


class TestSignals(QObject):
    data = pyqtSignal(str)
    testFinished = pyqtSignal()
    testPassed = pyqtSignal(tuple)
    testFailed = pyqtSignal(tuple)
    testCanceled = pyqtSignal()
    linkCheckResult = pyqtSignal()


class DropSignals(QObject):
    dropped_filename = pyqtSignal(str)


class CollectorSignals(QObject):
    offline = pyqtSignal(str)
    configured = pyqtSignal()


class DefineSetSignals(QObject):
    newSerialNumbers = pyqtSignal(tuple)