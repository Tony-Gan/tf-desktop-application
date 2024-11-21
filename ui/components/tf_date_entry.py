from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QDateEdit
from PyQt6.QtCore import QDate
from typing import Optional

from ui.components.tf_font import LABEL_FONT, TEXT_FONT


class TFDateEntry(QFrame):

    def __init__(
            self,
            label_text: str,
            label_size: Optional[int] = None,
            value_size: Optional[int] = None,
            height: int = 24,
            parent: Optional[QFrame] = None
    ):
        super().__init__(parent)
        self._setup_ui(
            label_text,
            label_size,
            value_size,
            height
        )

    def _setup_ui(
            self,
            label_text: str,
            label_size: Optional[int],
            value_size: Optional[int],
            height: int
    ) -> None:
        self.setFixedHeight(height)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(2)

        self.label = QLabel(label_text)
        self.label.setFont(LABEL_FONT)
        self.label.setFixedHeight(height - 4)
        if label_size:
            self.label.setFixedWidth(label_size)

        self.date_field = QDateEdit()
        self.date_field.setFont(TEXT_FONT)
        self.date_field.setFixedHeight(height - 4)
        self.date_field.setCalendarPopup(True)
        self.date_field.setDate(QDate.currentDate())
        self.date_field.setStyleSheet("QDateEdit { padding: 1px; }")
        if value_size:
            self.date_field.setFixedWidth(value_size)

        layout.addWidget(self.label)
        layout.addSpacing(-2)
        layout.addWidget(self.date_field)
        layout.addStretch()

    def get_value(self) -> str:
        return self.date_field.date().toString("yyyy-MM-dd")
