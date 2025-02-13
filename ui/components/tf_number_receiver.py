from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QFont

from ui.components.tf_font import NotoSerifNormal

class TFNumberReceiver(QLineEdit):
    def __init__(self, 
                 text="0", 
                 alignment: Qt.AlignmentFlag=Qt.AlignmentFlag.AlignLeft, 
                 font: QFont=NotoSerifNormal,
                 allow_decimal=True,
                 allow_negative=False,
                 width=50,
                 height=24,
                 max_digits=None,
                 parent=None):
        super().__init__(text, parent)
        self.setAlignment(alignment)
        self.setFont(font)
        self.allow_decimal = allow_decimal
        self.allow_negative = allow_negative
        self.max_digits = max_digits
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)

    def keyPressEvent(self, event: QKeyEvent | None):
        if self.max_digits is not None:
            current_digits = self._count_digits(self.text())
            is_digit = event.text().isdigit()
            
            if (current_digits >= self.max_digits and is_digit and 
                event.key() not in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete)):
                if not self.hasSelectedText():
                    event.ignore()
                    return

        if self.text() == "0" and event.text().isdigit():
            self.setText(event.text())
            return
        
        if event.text() == "-" and self.allow_negative:
            if self.text() == "" or self.cursorPosition() == 0:
                super().keyPressEvent(event)
            return
        
        if event.text() == "." and self.allow_decimal:
            if "." not in self.text():
                super().keyPressEvent(event)
            return
        
        if (event.text().isdigit() or 
            event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete, 
                          Qt.Key.Key_Left, Qt.Key.Key_Right)):
            super().keyPressEvent(event)
        else:
            event.ignore()


    def _count_digits(self, text: str) -> int:
        digits = ''.join(c for c in text if c.isdigit())
        return len(digits)
