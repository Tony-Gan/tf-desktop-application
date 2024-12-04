from typing import Optional, List

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QComboBox, QLabel, QHBoxLayout, QFrame, QCompleter

from ui.components.if_state_controll import IStateController
from ui.components.tf_font import LABEL_FONT, TEXT_FONT
from ui.components.tf_tooltip import TFTooltip


class TFOptionEntry(QFrame, IStateController):
    value_changed = pyqtSignal(str)

    def __init__(
            self,
            label_text: str = "",
            options: List[str] = None,
            current_value: str = "",
            label_size: int = 80,
            value_size: int = 36,
            label_font: QFont = LABEL_FONT,
            value_font: QFont = TEXT_FONT,
            height: int = 24,
            enable: bool = True,
            extra_value_width: Optional[int] = None,
            enable_filter: bool = False,
            show_tooltip: bool = False,
            tooltip_text: str = "",
            parent: Optional[QFrame] = None
    ) -> None:
        QFrame.__init__(self, parent)
        IStateController.__init__(self)

        self.extra_value_width = extra_value_width
        self.options = options or []
        self.show_tooltip = show_tooltip
        self._setup_ui(
            label_text, current_value,
            label_size, value_size, label_font, value_font,
            height, enable, enable_filter,
            show_tooltip, tooltip_text
        )

    def _setup_ui(
            self,
            label_text: str,
            current_value: str,
            label_size: int,
            value_size: int,
            label_font: QFont,
            value_font: QFont,
            height: int,
            enable: bool,
            enable_filter: bool,
            show_tooltip: bool,
            tooltip_text: str
    ) -> None:
        self.setFixedHeight(height)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label = QLabel(label_text)
        self.label.setFont(label_font)
        self.label.setFixedWidth(label_size)
        self.label.setFixedHeight(height)

        self.combo_box = TFComboBox()
        self.combo_box.setFont(value_font)
        self.combo_box.setFixedHeight(height)
        if self.extra_value_width:
            self.combo_box.setFixedWidth(value_size + self.extra_value_width)
        else:
            self.combo_box.setFixedWidth(value_size)
        self.combo_box.addItems(self.options)
        if current_value:
            index = self.combo_box.findText(current_value)
            if index >= 0:
                self.combo_box.setCurrentIndex(index)
        self.combo_box.currentTextChanged.connect(self.on_option_selected)

        if enable_filter:
            self._setup_filter()

        self.combo_box.setEnabled(enable)

        layout.addWidget(self.label)
        layout.addSpacing(2)
        layout.addWidget(self.combo_box)

        if show_tooltip and tooltip_text:
            icon_size = height - 4
            self.tooltip_icon = TFTooltip(icon_size, tooltip_text)
            layout.addSpacing(2)
            layout.addWidget(self.tooltip_icon)

        layout.addStretch()

    def on_option_selected(self, value: str) -> None:
        self.value_changed.emit(value)

    def _setup_filter(self) -> None:
        completer = QCompleter(self.options, self.combo_box)
        completer.setCompletionRole(Qt.ItemDataRole.DisplayRole)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.combo_box.setCompleter(completer)

    def update_options(self, options: List[str]) -> None:
        self.options = options
        self.combo_box.clear()
        self.combo_box.addItems(options)

    def get_value(self) -> str:
        return self.combo_box.currentText()

    def set_value(self, value: str) -> None:
        index = self.combo_box.findText(value)
        if index >= 0:
            self.combo_box.setCurrentIndex(index)

    def update_tooltip(self, text: str) -> None:
        if self.show_tooltip:
            self.tooltip_icon.update_tooltip(text)


class TFComboBox(QComboBox):
    def showPopup(self):
        super().showPopup()
        popup = self.view().window()
        popup.move(popup.x(), popup.y() + 3)

