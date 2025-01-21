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

        self.enable_filter = enable_filter
        self.extra_value_width = extra_value_width
        self.options = options or []
        self.show_tooltip = show_tooltip

        self.label_text = label_text
        self.current_value = current_value
        self.label_size = label_size
        self.value_size = value_size
        self.label_font = label_font
        self.value_font = value_font
        self.height_ = height
        self.enable = enable
        self.tooltip_text = tooltip_text

        self.completer = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(self.height_)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label = QLabel(self.label_text, self)
        self.label.setFont(self.label_font)
        self.label.setFixedWidth(self.label_size)
        self.label.setFixedHeight(self.height_)

        self.combo_box = TFComboBox(self)
        self.combo_box.setFont(self.value_font)
        self.combo_box.setFixedHeight(self.height_)

        if self.extra_value_width:
            total_width = self.value_size + self.extra_value_width
        else:
            total_width = max(self.value_size, 100)

        self.combo_box.setFixedWidth(total_width)

        self.combo_box.addItems(self.options)

        if self.current_value:
            index = self.combo_box.findText(self.current_value)
            if index >= 0:
                self.combo_box.setCurrentIndex(index)
            else:
                if self.enable_filter:
                    self.combo_box.setEditText(self.current_value)

        self.combo_box.currentTextChanged.connect(self.on_option_selected)

        if self.enable_filter:
            self._setup_filter()

        self.combo_box.setEnabled(self.enable)

        layout.addWidget(self.label)
        layout.addSpacing(2)
        layout.addWidget(self.combo_box)

        if self.show_tooltip and self.tooltip_text:
            icon_size = self.height_ - 4
            self.tooltip_icon = TFTooltip(icon_size, self.tooltip_text, self)
            layout.addSpacing(2)
            layout.addWidget(self.tooltip_icon)

        layout.addStretch()

    def on_option_selected(self, value: str) -> None:
        self.value_changed.emit(value)

    def _setup_filter(self) -> None:
        self.combo_box.setEditable(True)
        self.completer = QCompleter(self.options, self.combo_box)
        self.completer.setCompletionRole(Qt.ItemDataRole.DisplayRole)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.combo_box.setCompleter(self.completer)
        if self.combo_box.isEditable():
            line_edit = self.combo_box.lineEdit()
            if line_edit:
                line_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
                line_edit.setStyleSheet("QLineEdit { padding-left: 0px; margin: 0px; }")

    def update_options(self, options: List[str]) -> None:
        self.options = options
        self.combo_box.clear()
        self.combo_box.addItems(options)

        if self.enable_filter and self.completer is not None:
            self.completer.model().setStringList(options)

    def get_value(self) -> str:
        return self.combo_box.currentText()

    def set_value(self, value: str) -> None:
        index = self.combo_box.findText(value)
        if index >= 0:
            self.combo_box.setCurrentIndex(index)
        else:
            if self.enable_filter:
                self.combo_box.setEditText(value)

    def update_tooltip(self, text: str) -> None:
        if self.show_tooltip and hasattr(self, 'tooltip_icon'):
            self.tooltip_icon.update_tooltip(text)


class TFComboBox(QComboBox):
    def showPopup(self):
        super().showPopup()
        popup = self.view().window()
        popup.move(popup.x(), popup.y() + 3)
