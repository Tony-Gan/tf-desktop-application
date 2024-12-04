from typing import Optional, List

from PyQt6.QtWidgets import QFrame, QButtonGroup, QVBoxLayout
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from ui.components.if_state_controll import IStateController
from ui.components.tf_font import TEXT_FONT
from ui.components.tf_radio_with_label import TFRadioWithLabel


class TFRadioGroup(QFrame, IStateController):
    value_changed = pyqtSignal(str)

    def __init__(
            self,
            options: List[str],
            current_value: Optional[str] = None,
            label_font: QFont = TEXT_FONT,
            layout_type: type = QVBoxLayout,
            height: int = 24,
            spacing: int = 6,
            show_tooltip: bool = False,
            tooltip_text: str = "",
            parent: Optional[QFrame] = None
    ) -> None:
        QFrame.__init__(self, parent)
        IStateController.__init__(self)
        
        self.options = options
        self.current_value = current_value
        self.radio_buttons = []
        
        self._setup_ui(
            label_font,
            layout_type,
            height,
            spacing,
            show_tooltip,
            tooltip_text
        )

    def _setup_ui(
            self,
            label_font: QFont,
            layout_type: type,
            height: int,
            spacing: int,
            show_tooltip: bool,
            tooltip_text: str
    ) -> None:
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        self.main_layout = layout_type(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(spacing)
        
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        for option in self.options:
            radio = TFRadioWithLabel(
                label_text=option,
                label_font=label_font,
                checked=(option == self.current_value),
                height=height,
                show_tooltip=show_tooltip,
                tooltip_text=tooltip_text
            )
            self.radio_buttons.append(radio)
            self.button_group.addButton(radio.radio)
            self.main_layout.addWidget(radio)
            radio.value_changed.connect(lambda checked, r=radio: self._on_radio_toggled(checked, r))

    def _on_radio_toggled(self, checked: bool, radio: TFRadioWithLabel) -> None:
        if checked:
            self.value_changed.emit(radio.get_text())

    def get_value(self) -> Optional[str]:
        """Returns the text of selected option, or None if nothing selected"""
        for radio in self.radio_buttons:
            if radio.get_value():
                return radio.get_text()
        return None

    def set_value(self, value: str) -> None:
        """Sets the radio button with matching text as checked"""
        for radio in self.radio_buttons:
            if radio.get_text() == value:
                radio.set_checked(True)
                break