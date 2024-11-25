from typing import Optional

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QFrame, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.components.if_state_controll import IStateContoller
from ui.components.tf_expanding_input import TFExpandingInput
from ui.components.tf_font import LABEL_FONT, TEXT_FONT
from ui.components.tf_number_receiver import TFNumberReceiver
from ui.components.tf_tooltip import TFTooltip


class TFValueEntry(QFrame, IStateContoller):
    value_changed = pyqtSignal(str)

    def __init__(
            self,
            label_text: str = "",
            value_text: str = "",
            label_size: int = 80,
            value_size: int = 36,
            label_font: QFont = LABEL_FONT,
            value_font: QFont = TEXT_FONT,
            height: int = 24,
            alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
            label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            number_only: bool = False,
            allow_decimal: bool = True,
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
        IStateContoller.__init__(self)

        self._setup_ui(
            label_text, value_text, label_size, value_size, label_font, value_font,
            height, alignment, label_alignment, number_only, allow_decimal, allow_negative,
            max_digits, expanding, expanding_text_width, expanding_text_height,
            show_tooltip, tooltip_text
        )

    def _setup_ui(
            self,
            label_text: str,
            value_text: str,
            label_size: int,
            value_size: int,
            label_font: QFont,
            value_font: QFont,
            height: int,
            alignment: Qt.AlignmentFlag,
            label_alignment: Qt.AlignmentFlag,
            number_only: bool,
            allow_decimal: bool,
            allow_negative: bool,
            max_digits: Optional[int],
            expanding: bool,
            expanding_text_width: int,
            expanding_text_height: int,
            show_tooltip: bool,
            tooltip_text: str 
    ) -> None:
        self.setFixedHeight(height)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.label = QLabel(label_text)
        self.label.setFont(label_font)
        self.label.setFixedWidth(label_size)
        self.label.setFixedHeight(height)
        self.label.setAlignment(label_alignment)

        if number_only:
            self.value_field = TFNumberReceiver(
                text=str(value_text),
                alignment=alignment,
                font=value_font,
                allow_decimal=allow_decimal,
                allow_negative=allow_negative,
                max_digits=max_digits,
                parent=self
            )
        elif expanding:
            self.value_field = TFExpandingInput(
                line_width=value_size,
                line_height=height,
                text_width=expanding_text_width,
                text_height=expanding_text_height,
                font=value_font,
                parent=self
            )
            self.value_field.setText(str(value_text))
        else:
            self.value_field = QLineEdit()
            self.value_field.setFont(value_font)
            self.value_field.setFixedHeight(height)
            self.value_field.setAlignment(alignment)
            self.value_field.setText(str(value_text))

        self.value_field.setFixedWidth(value_size)

        self.value_field.textChanged.connect(self.value_changed.emit)

        layout.addWidget(self.label)
        layout.addWidget(self.value_field)

        if show_tooltip and tooltip_text:
            icon_size = height - 4
            self.tooltip_icon = TFTooltip(icon_size, tooltip_text)
            layout.addSpacing(5)
            layout.addWidget(self.tooltip_icon)
            layout.addSpacing(2)
        layout.addStretch()

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

    def set_enable(self, enable: bool) -> None:
        self.label.setEnabled(enable)
        self.value_field.setEnabled(enable)
