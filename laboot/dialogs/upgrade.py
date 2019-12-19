from PyQt5.QtWidgets import QDialog


class Upgrade(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.resize(600, 600)
