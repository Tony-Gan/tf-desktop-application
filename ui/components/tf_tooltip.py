from PyQt6.QtWidgets import QPushButton, QToolTip
from PyQt6.QtCore import QSize, QPoint
from PyQt6.QtGui import QIcon

from utils.helper import resource_path

class TFTooltip(QPushButton):
    def __init__(self, tooltip_text, parent=None):
        super().__init__(parent)
        self.tooltip_text = tooltip_text
        self.setFixedSize(24, 24)
        self.setIcon(QIcon(resource_path('resources/images/icons/tooltips.png')))
        self.setIconSize(QSize(24, 24))
        
    def enterEvent(self, event):
        pos = self.mapToGlobal(QPoint(self.width(), 0))
        QToolTip.showText(pos, self.tooltip_text)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        QToolTip.hideText()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event) -> None:
        super().mouseMoveEvent(event)
        if self._tooltip and QToolTip.isVisible():
            pos = self.mapToGlobal(QPoint(0, self.height()))
            QToolTip.showText(pos, self._tooltip)
