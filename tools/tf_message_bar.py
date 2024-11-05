from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QFontMetrics

class TFMessageBar(QLabel):
    """
    A temporary message display widget for notifications.

    This class extends QLabel to create a temporary notification bar that appears
    at the top of the parent widget and automatically hides after a specified duration.

    Args:
        parent (QWidget, optional): The parent widget. Defaults to None.

    Attributes:
        font (QFont): Font used for message text, set to "Open Sans" 11pt.
        objectName (str): Set to "message_label" for styling purposes.

    Example:
        >>> message_bar = TFMessageBar(parent=main_window)
        >>> message_bar.show_message("Operation successful!", 3000, "green")
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        self.setObjectName("message_label")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)

        font = QFont("Open Sans", 11)
        self.setFont(font)

        self.hide()

    def show_message(self, message: str, display_time=2000, colour='green') -> None:
        """Display a temporary notification message.

        Shows a colored message bar at the top of the parent widget that automatically
        hides after the specified duration.

        Args:
            message (str): The message text to display. Can include line breaks.
            display_time (int, optional): Duration in milliseconds to show the message.
                Defaults to 2000ms (2 seconds).
            colour (str, optional): Background color of the message bar.
                Can be any valid CSS color value. Defaults to 'green'.

        Note:
            - The message bar width automatically adjusts to parent widget width
            - Height automatically adjusts based on message text length and line breaks
            - Position is fixed at 20 pixels from the top of the parent widget
            - Message is centered and can wrap to multiple lines
        """
        self.setText(message)
        if colour == 'yellow':
            self.setStyleSheet(f"background-color: {colour}; color: black;")
        else:
            self.setStyleSheet(f"background-color: {colour};")

        if self.parent:
            self.setFixedWidth(self.parent.width())

        font_metrics = QFontMetrics(self.font())
        line_spacing = font_metrics.lineSpacing()
        lines = message.split('\n')
        height = line_spacing * len(lines) + 10
        self.setFixedHeight(height)
        
        self.move(0, 30)

        self.show()
        self.raise_()
        QTimer.singleShot(display_time, self.hide)
