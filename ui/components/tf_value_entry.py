from typing import Optional
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QFrame, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal

from ui.components.tf_expanding_input import TFExpandingInput
from ui.components.tf_font import LABEL_FONT, TEXT_FONT
from ui.components.tf_number_receiver import TFNumberReceiver


class TFValueEntry(QFrame):
    value_changed = pyqtSignal(str)

    def __init__(
            self,
            label_text: str = "",
            value_text: str = "",
            label_size: int = 80,
            value_size: int = 36,
            height: int = 24,
            alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
            label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            number_only: bool = False,
            allow_decimal: bool = True,
            allow_negative: bool = False,
            expanding: bool = False,
            expanding_text_width: int = 300,
            expanding_text_height: int = 100,
            parent: Optional[QFrame] = None
    ) -> None:
        super().__init__(parent)

        self._setup_ui(
            label_text, value_text, label_size, value_size, height,
            alignment, label_alignment, number_only, allow_decimal, allow_negative,
            expanding, expanding_text_width, expanding_text_height
        )

    def _setup_ui(
            self,
            label_text: str,
            value_text: str,
            label_size: int,
            value_size: int,
            height: int,
            alignment: Qt.AlignmentFlag,
            label_alignment: Qt.AlignmentFlag,
            number_only: bool,
            allow_decimal: bool,
            allow_negative: bool,
            expanding: bool,
            expanding_text_width: int,
            expanding_text_height: int
    ) -> None:
        self.setFixedHeight(height)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(2)

        self.label = QLabel(label_text)
        self.label.setFont(LABEL_FONT)
        self.label.setFixedWidth(label_size)
        self.label.setAlignment(label_alignment)

        if number_only:
            self.value_field = TFNumberReceiver(
                text=str(value_text),
                alignment=alignment,
                font=TEXT_FONT,
                allow_decimal=allow_decimal,
                allow_negative=allow_negative,
                parent=self
            )
        elif expanding:
            self.value_field = TFExpandingInput(
                line_width=value_size,
                line_height=height,
                text_width=expanding_text_width,
                text_height=expanding_text_height,
                font=TEXT_FONT,
                parent=self
            )
            self.value_field.setText(str(value_text))
        else:
            self.value_field = QLineEdit()
            self.value_field.setFont(TEXT_FONT)
            self.value_field.setAlignment(alignment)
            self.value_field.setText(str(value_text))

        self.value_field.setFixedWidth(value_size)
        self.value_field.setStyleSheet("QLineEdit { padding: 1px; }")

        self.value_field.textChanged.connect(self.value_changed.emit)

        layout.addWidget(self.label)
        layout.addWidget(self.value_field)
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
