from typing import Optional

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QFrame, QRadioButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.components.if_state_controll import IStateController
from ui.components.tf_font import TEXT_FONT
from ui.components.tf_tooltip import TFTooltip


class TFRadioWithLabel(QFrame, IStateController):
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

        self.setObjectName("tfRadioWithLabel")

        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        self.setStyleSheet("""
            #tfRadioWithLabel {
                border-radius: 4px; 
                background-color: transparent;
            }
            #tfRadioWithLabel:hover {
                background-color: rgba(200, 200, 200, 0.2);
            }
        """)

        self.show_tooltip = show_tooltip

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
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(spacing)

        self.radio = QRadioButton()
        self.radio.setChecked(checked)

        self.radio.toggled.connect(self._on_toggled)

        self.label = QLabel(label_text)
        self.label.setFont(label_font)
        self.label.setAlignment(label_alignment)

        layout.addWidget(self.radio)
        layout.addWidget(self.label)

        if show_tooltip and tooltip_text:
            icon_size = height - 4
            self.tooltip_icon = TFTooltip(icon_size, tooltip_text)
            layout.addWidget(self.tooltip_icon)
            layout.addSpacing(2)

        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.radio.setChecked(True)
            self.value_changed.emit(self.radio.isChecked())
        super().mousePressEvent(event)

    def _on_label_clicked(self, event) -> None:
        self.radio.setChecked(True)

    def _on_toggled(self, checked: bool) -> None:
        self.value_changed.emit(checked)

    def get_value(self) -> bool:
        return self.radio.isChecked()
    
    def set_checked(self, checked: bool) -> None:
        self.radio.setChecked(checked)
        
    def get_text(self) -> str:
        return self.label.text()
    
    def is_checked(self) -> bool:
        return self.radio.isChecked()

    def update_tooltip(self, text: str) -> None:
        if self.show_tooltip:
            self.tooltip_icon.update_tooltip(text)
