from PyQt6.QtWidgets import QComboBox
from PyQt6.QtGui import QFont

from ui.tf_draggable_window import TFDraggableWindow

class UnitTypeSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("unit_type_selector")
        font = QFont("Nunito", 10)
        font.setStyleName("Condensed")
        self.setFont(font)

class UnitSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("unit_selector")
        font = QFont("Nunito", 10)
        font.setStyleName("Condensed")
        self.setFont(font)
        self.setEnabled(False)

class TFUnitConverter(TFDraggableWindow):
    def __init__(self, parent=None):
        super().__init__(parent, (300, 500), "Unit Converter", 1)