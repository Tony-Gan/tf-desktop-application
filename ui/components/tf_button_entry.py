from typing import Callable, Optional

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.components.if_state_controll import IStateController
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_font import NotoSerifLight
from ui.components.tf_tooltip import TFTooltip

class TFButtonEntry(QFrame, IStateController):
    text_changed = pyqtSignal(str)
    button_clicked = pyqtSignal()

    def __init__(
        self,
        label_text: str = "",
        label_font: QFont = NotoSerifLight,
        label_size: int = 100,
        label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        button_text: str = "Confirm",
        entry_text: str = "",
        entry_size: int = 100,
        button_size: int = 100,
        entry_font: QFont = NotoSerifLight,
        height: int = 24,
        placeholder_text: str = "",
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        button_enabled: bool = True,
        button_space: int = 10,
        button_tooltip: str = "",
        button_callback: Optional[Callable] = None,
        show_tooltip: bool = False,
        tooltip_text: str = "",
        border_radius: int = 5,
        icon_path: str = None,
        parent: Optional[QFrame] = None
    ):
        QFrame.__init__(self, parent)
        IStateController.__init__(self)

        self.show_tooltip = show_tooltip

        self._setup_ui(
            label_text, label_font, label_size, label_alignment,
            button_text, entry_text, entry_size, button_size,
            entry_font, height, placeholder_text, 
            alignment, button_enabled, button_tooltip, button_space, 
            button_callback, show_tooltip, tooltip_text, border_radius, icon_path
        )

    def _setup_ui(
            self,
            label_text: str,
            label_font: QFont,
            label_size: int,
            label_alignment: Qt.AlignmentFlag,
            button_text: str,
            entry_text: str,
            entry_size: int,
            button_size: int,
            entry_font: QFont,
            height: int,
            placeholder_text: str,
            alignment: Qt.AlignmentFlag,
            button_enabled: bool,
            button_tooltip: str,
            button_space: int,
            button_callback: Optional[Callable],
            show_tooltip: bool,
            tooltip_text: str,
            border_radius: int,
            icon_path: str
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
        
        self.entry_field = QLineEdit()
        self.entry_field.setFont(entry_font)
        self.entry_field.setFixedHeight(height)
        self.entry_field.setFixedWidth(entry_size)
        self.entry_field.setAlignment(alignment)
        self.entry_field.setText(entry_text)
        if placeholder_text:
            self.entry_field.setPlaceholderText(placeholder_text)
        
        self.button = TFBaseButton(
            text=button_text,
            width=button_size,
            height=height,
            font_size=10,
            enabled=button_enabled,
            tooltip=button_tooltip,
            border_radius=border_radius,
            on_clicked=button_callback,
            icon_path=icon_path,
            parent=self
        )
        
        self.entry_field.textChanged.connect(self.text_changed.emit)
        if not button_callback:
            self.button.clicked.connect(self.button_clicked.emit)
        
        layout.addWidget(self.label)
        layout.addWidget(self.entry_field)
        layout.addSpacing(button_space)
        layout.addWidget(self.button)
        
        if show_tooltip and tooltip_text:
            icon_size = height - 4
            self.tooltip_icon = TFTooltip(icon_size, tooltip_text)
            layout.addSpacing(5)
            layout.addWidget(self.tooltip_icon)
            layout.addSpacing(2)
            
        layout.addStretch()

    def get_text(self) -> str:
        return self.entry_field.text()
    
    def set_text(self, text: str) -> None:
        self.entry_field.setText(str(text))
        
    def clear_text(self) -> None:
        self.entry_field.clear()
        
    def set_button_enabled(self, enabled: bool) -> None:
        self.button.setEnabled(enabled)
        
    def set_entry_enabled(self, enabled: bool) -> None:
        self.entry_field.setEnabled(enabled)
        
    def set_enable(self, enable: bool) -> None:
        self.entry_field.setEnabled(enable)
        self.button.setEnabled(enable)
        
    def set_placeholder(self, text: str) -> None:
        self.entry_field.setPlaceholderText(text)
        
    def set_button_text(self, text: str) -> None:
        self.button.setText(text)

    def update_tooltip(self, text: str) -> None:
        if self.show_tooltip:
            self.tooltip_icon.update_tooltip(text)
