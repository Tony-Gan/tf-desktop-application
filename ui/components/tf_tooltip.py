from PyQt6.QtWidgets import QLabel, QToolTip
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from utils.helper import resource_path

class TFTooltip(QLabel):
    def __init__(self, size: int, tooltip_text: str):
        super().__init__()
        self.normal_icon = QPixmap(resource_path("resources/images/icons/tooltips.png")).scaled(
            size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.hover_icon = QPixmap(resource_path("resources/images/icons/tooltips_hover.png")).scaled(
            size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(self.normal_icon)

        self.setToolTip(tooltip_text)
        self.setCursor(Qt.CursorShape.WhatsThisCursor)

    def enterEvent(self, event):
        self.setPixmap(self.hover_icon)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setPixmap(self.normal_icon)
        super().leaveEvent(event)