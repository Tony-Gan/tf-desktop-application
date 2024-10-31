from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QFont

class TFNumberReceiver(QLineEdit):
    def __init__(self, 
                 text="0", 
                 alignment: Qt.AlignmentFlag=Qt.AlignmentFlag.AlignLeft, 
                 font: QFont=QFont("Montserrat", 12),
                 parent=None):
        super().__init__(text, parent)
        self.setAlignment(alignment)
        self.setFont(font)

    def keyPressEvent(self, event: QKeyEvent | None):
        if self.text() == "0" and event.text().isdigit():
            self.setText(event.text())
            return
        
        if event.text().isdigit() or event.text() == "." or event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            if event.text() == "." and "." in self.text():
                event.ignore()
                return
            super().keyPressEvent(event)
        else:
            event.ignore()