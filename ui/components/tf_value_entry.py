from typing import Optional

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QFrame, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.components.if_state_controll import IStateController
from ui.components.tf_expanding_input import TFExpandingInput
from ui.components.tf_font import LABEL_FONT, TEXT_FONT
from ui.components.tf_number_receiver import TFNumberReceiver
from ui.components.tf_tooltip import TFTooltip


class TFValueEntry(QFrame, IStateController):
    value_changed = pyqtSignal(str)

    def __init__(
            self,
            label_text: str = "",
            value_text: str = "",
            label_size: int = 80,
            value_size: int = 36,
            label_font: QFont = LABEL_FONT,
            value_font: QFont = TEXT_FONT,
            enable: bool = True,
            height: int = 24,
            alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
            label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            number_only: bool = False,
            allow_decimal: bool = False,
            allow_negative: bool = False,
            max_digits: Optional[int] = None,
            expanding: bool = False,
            expanding_text_width: int = 300,
            expanding_text_height: int = 100,
            show_tooltip: bool = False,
            tooltip_text: str = "",
            parent: Optional[QFrame] = None
    ) -> None:
        QFrame.__init__(self, parent)
        IStateController.__init__(self)

        self.label_text = label_text
        self.label_size = label_size
        self.label_font = label_font
        self.value_text = value_text
        self.value_size = value_size
        self.value_font = value_font

        self.enable = enable

        self.height = height
        self.label_alignment = label_alignment
        self.value_alignment = alignment

        self.number_only = number_only
        self.allow_decimal = allow_decimal
        self.allow_negative = allow_negative
        self.max_digits = max_digits

        self.expanding = expanding
        self.expanding_text_width = expanding_text_width
        self.expanding_text_height = expanding_text_height

        self.show_tooltip = show_tooltip
        self.tooltip_text = tooltip_text

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(self.height)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.label = QLabel(self.label_text)
        self.label.setFont(self.label_font)
        self.label.setFixedWidth(self.label_size)
        self.label.setFixedHeight(self.height)
        self.label.setAlignment(self.label_alignment)

        if self.number_only:
            self.value_field = TFNumberReceiver(
                text=str(self.value_text),
                alignment=self.value_alignment,
                font=self.value_font,
                allow_decimal=self.allow_decimal,
                allow_negative=self.allow_negative,
                max_digits=self.max_digits,
                parent=self
            )
        elif self.expanding:
            self.value_field = TFExpandingInput(
                line_width=self.value_size,
                line_height=self.height,
                text_width=self.expanding_text_width,
                text_height=self.expanding_text_height,
                font=self.value_font,
                parent=self
            )
            self.value_field.setText(str(self.value_text))
        else:
            self.value_field = QLineEdit()
            self.value_field.setFont(self.value_font)
            self.value_field.setFixedHeight(self.height)
            self.value_field.setAlignment(self.value_alignment)
            self.value_field.setText(str(self.value_text))

        self.value_field.setFixedWidth(self.value_size)
        self.value_field.textChanged.connect(self.value_changed.emit)

        layout.addWidget(self.label)
        layout.addWidget(self.value_field)

        if self.show_tooltip and self.tooltip_text:
            icon_size = self.height - 4
            self.tooltip_icon = TFTooltip(icon_size, self.tooltip_text)
            layout.addSpacing(5)
            layout.addWidget(self.tooltip_icon)
            layout.addSpacing(2)
        layout.addStretch()

        self.value_field.setEnabled(self.enable)

    def get_value(self) -> str:
        if isinstance(self.value_field, TFExpandingInput):
            return self.value_field.text_edit.toPlainText()
        else:
            return self.value_field.text()

    def set_value(self, value: str) -> None:
        if isinstance(self.value_field, TFExpandingInput):
            self.value_field.text_edit.setPlainText(str(value))
        else:
            self.value_field.setText(str(value))

    def set_enabled(self, enable: bool, entry_only: bool=True) -> None:
        self.value_field.setEnabled(enable)
        if not entry_only:
            self.label.setEnabled(enable)

    def update_tooltip(self, text: str) -> None:
        if self.show_tooltip:
            self.tooltip_icon.update_tooltip(text)
