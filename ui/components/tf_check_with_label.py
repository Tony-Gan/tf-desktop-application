from typing import Optional

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QFrame, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.components.if_state_controll import IStateController
from ui.components.tf_font import TEXT_FONT
from ui.components.tf_tooltip import TFTooltip


class TFCheckWithLabel(QFrame, IStateController):
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
        QFrame.__init__(self, parent)
        IStateController.__init__(self)

        self.show_tooltip = show_tooltip

        self.label_text = label_text
        self.label_font = label_font
        self.label_alignment = label_alignment

        self.height = height
        self.spacing = spacing

        self.checked = checked

        self.show_tooltip = show_tooltip
        self.tooltip_text = tooltip_text

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(self.height)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(self.spacing)

        self.check = QCheckBox()
        self.check.setChecked(self.checked)
        self.check.stateChanged.connect(lambda state: self.value_changed.emit(bool(state)))

        self.label = QLabel(self.label_text)
        self.label.setFont(self.label_font)
        self.label.setAlignment(self.label_alignment)
        self.label.mousePressEvent = self._on_label_clicked

        layout.addWidget(self.check)
        layout.addWidget(self.label)

        if self.show_tooltip and self.tooltip_text:
            icon_size = self.height - 4
            self.tooltip_icon = TFTooltip(icon_size, self.tooltip_text)
            layout.addWidget(self.tooltip_icon)
            layout.addSpacing(2)

        layout.addStretch()

    def _on_label_clicked(self, event) -> None:
        self.check.setChecked(not self.check.isChecked())

    def get_value(self) -> bool:
        return self.check.isChecked()
    
    def set_checked(self, checked) -> None:
        self.check.setChecked(checked)

    def update_tooltip(self, text: str) -> None:
        if self.show_tooltip:
            self.tooltip_icon.update_tooltip(text)

    def set_enabled(self, enable, check_only=True):
        self.check.setEnabled(enable)
        if not check_only:
            self.label.setEnabled(enable)
