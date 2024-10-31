from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QFontMetrics

class TFMessageBar(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("message_label")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)

        font = QFont("Open Sans", 11)
        self.setFont(font)

        self.hide()

    def show_message(self, message: str, display_time=2000, colour='green') -> None:
        self.setText(message)
        self.setStyleSheet(f"background-color: {colour};")

        if self.parent():
            self.setFixedWidth(self.parent().width())

        font_metrics = QFontMetrics(self.font())
        line_spacing = font_metrics.lineSpacing()
        lines = message.split('\n')
        height = line_spacing * len(lines) + 10
        self.setFixedHeight(height)
        
        self.move(0, 20)

        self.show()
        QTimer.singleShot(display_time, self.hide)
