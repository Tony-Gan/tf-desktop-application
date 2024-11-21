from PyQt6.QtWidgets import QFrame


class TFStandardFrame(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent