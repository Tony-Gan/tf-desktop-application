from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QDateEdit
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

class TFDateEntry(QWidget):
    def __init__(self, 
                 label_text: str,
                 label_size: int = None,
                 value_size: int = None,
                 alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
                 parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(0)

        self.setFixedHeight(24)
        font = QFont("Inconsolata", 10)
        font.setWeight(QFont.Weight.DemiBold)
        
        self.label = QLabel(label_text)
        self.label.setFont(font)
        self.label.setFixedHeight(24)
        if label_size:
            self.label.setFixedWidth(label_size)
        self.label.setAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
        
        self.date_field = QDateEdit()
        self.date_field.setStyleSheet("QLineEdit { padding: 1px; }")
        self.date_field.setFixedHeight(24)
        self.date_field.setCalendarPopup(True)
        self.date_field.setDate(QDate.currentDate())
        if value_size:
            self.date_field.setFixedWidth(value_size)
            
        layout.addWidget(self.label)
        layout.addWidget(self.date_field)
        
        if alignment == Qt.AlignmentFlag.AlignLeft:
            layout.addStretch()
            
    def get_value(self) -> str:
        return self.date_field.date().toString("yyyy-MM-dd")
        
    def set_value(self, date_str: str):
        try:
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            if date.isValid():
                self.date_field.setDate(date)
        except:
            pass
            
    def set_enabled(self, enabled: bool):
        self.date_field.setEnabled(enabled)
