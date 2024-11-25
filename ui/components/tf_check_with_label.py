from typing import Optional

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QFrame, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.components.tf_font import TEXT_FONT
from ui.components.tf_tooltip import TFTooltip


class TFCheckWithLabel(QFrame):
    value_changed = pyqtSignal(bool)

    def __init__(
            self,
            label_text: str = "",
            label_font: QFont = TEXT_FONT,
            checked: bool = False,
            height: int = 24,
            spacing: int = 6,
            label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            show_tooltip: bool = False,
            tooltip_text: str = "",
            parent: Optional[QFrame] = None
    ) -> None:
        super().__init__(parent)
        self._setup_ui(
            label_text,
            label_font,
            checked,
            height,
            spacing,
            label_alignment,
            show_tooltip,
            tooltip_text
        )

    def _setup_ui(
            self,
            label_text: str,
            label_font: QFont,
            checked: bool,
            height: int,
            spacing: int,
            label_alignment: Qt.AlignmentFlag,
            show_tooltip: bool,
            tooltip_text: str
    ) -> None:
        self.setFixedHeight(height)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(spacing)

        self.check = QCheckBox()
        self.check.setChecked(checked)
        self.check.stateChanged.connect(lambda state: self.value_changed.emit(bool(state)))

        self.label = QLabel(label_text)
        self.label.setFont(label_font)
        self.label.setAlignment(label_alignment)
        self.label.mousePressEvent = self._on_label_clicked

        layout.addWidget(self.check)
        layout.addWidget(self.label)

        if show_tooltip and tooltip_text:
            icon_size = height - 4
            self.tooltip_icon = TFTooltip(icon_size, tooltip_text)
            layout.addWidget(self.tooltip_icon)
            layout.addSpacing(2)

        layout.addStretch()

    def _on_label_clicked(self, event) -> None:
        self.check.setChecked(not self.check.isChecked())

    def get_value(self) -> bool:
        return self.check.isChecked()
