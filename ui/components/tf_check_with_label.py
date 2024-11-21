from PyQt6.QtWidgets import QHBoxLayout, QLabel, QFrame, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional

from ui.components.tf_font import TEXT_FONT


class TFCheckWithLabel(QFrame):
    value_changed = pyqtSignal(bool)

    def __init__(
            self,
            label_text: str = "",
            checked: bool = False,
            height: int = 24,
            spacing: int = 6,
            label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            parent: Optional[QFrame] = None
    ) -> None:
        super().__init__(parent)
        self._setup_ui(
            label_text,
            checked,
            height,
            spacing,
            label_alignment
        )

    def _setup_ui(
            self,
            label_text: str,
            checked: bool,
            height: int,
            spacing: int,
            label_alignment: Qt.AlignmentFlag
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
        font = TEXT_FONT
        self.label.setFont(font)
        self.label.setAlignment(label_alignment)
        self.label.mousePressEvent = self._on_label_clicked

        layout.addWidget(self.check)
        layout.addWidget(self.label)
        layout.addStretch()

    def _on_label_clicked(self, event) -> None:
        self.check.setChecked(not self.check.isChecked())

    def get_value(self) -> bool:
        return self.check.isChecked()
