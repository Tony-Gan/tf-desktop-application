from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor

class TFActionLabel(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("""
            QLabel {
                color: #B4B4B4;
                padding: 5px;
                margin: 2px 0;
            }
            QLabel:hover {
                color: #FFFFFF;
            }
        """)
        font = QFont()
        font.setPointSize(9)
        self.setFont(font)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
