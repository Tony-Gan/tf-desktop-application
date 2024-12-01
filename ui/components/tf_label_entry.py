from typing import Optional

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

from ui.components.tf_font import NotoSerifNormal
from ui.components.tf_tooltip import TFTooltip


class TFLabelWithTip(QFrame):
    def __init__(
            self,
            text: str = "",
            font: QFont = NotoSerifNormal,
            tooltip_text: str = "",
            height: int = 24,
            label_size: Optional[int] = None,
            alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            parent: Optional[QFrame] = None
    ) -> None:
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        self.label = QLabel(text)
        self.label.setFont(font)
        self.label.setAlignment(alignment)
        if label_size:
            self.label.setFixedWidth(label_size)
        self.label.setFixedHeight(height)
        
        self.tooltip = TFTooltip(height - 4, tooltip_text)
        
        layout.addWidget(self.label)
        layout.addWidget(self.tooltip, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.tooltip)
        layout.addStretch()
        
    def setText(self, text: str) -> None:
        self.label.setText(text)
        
    def text(self) -> str:
        return self.label.text()