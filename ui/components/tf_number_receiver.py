from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QFont

class TFNumberReceiver(QLineEdit):
    """
    A specialized line edit widget that only accepts numeric input including decimals.
    
    This widget extends QLineEdit to create a number-only input field that handles
    decimal points and prevents invalid characters. Leading zeros are automatically
    handled.

    Args:
        text (str, optional): Initial text value. Defaults to "0".
        alignment (Qt.AlignmentFlag, optional): Text alignment. Defaults to AlignLeft.
        font (QFont, optional): Font settings. Defaults to Montserrat 12pt.
        parent (QWidget, optional): Parent widget. Defaults to None.

    Example:
        >>> # Create a right-aligned number input
        >>> number_input = TFNumberReceiver(
        ...     text="0",
        ...     alignment=Qt.AlignmentFlag.AlignRight,
        ...     font=QFont("Arial", 14)
        ... )
        >>> 
        >>> # Create default number input
        >>> basic_input = TFNumberReceiver()
    """
    def __init__(self, 
                 text="0", 
                 alignment: Qt.AlignmentFlag=Qt.AlignmentFlag.AlignLeft, 
                 font: QFont=QFont("Montserrat", 12),
                 allow_decimal=True,
                 allow_negative=False,
                 width=50,
                 height=24,
                 parent=None):
        super().__init__(text, parent)
        self.setAlignment(alignment)
        self.setFont(font)
        self.allow_decimal = allow_decimal
        self.allow_negative = allow_negative
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)

    def keyPressEvent(self, event: QKeyEvent | None):
        """
        Handle key press events to enforce numeric input rules.
        
        Controls input to allow only:
        - Numeric digits (0-9)
        - Single decimal point
        - Backspace and delete keys
        Automatically handles leading zeros by replacing them with pressed digit.

        Args:
            event (QKeyEvent): The key event to handle.
        """
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