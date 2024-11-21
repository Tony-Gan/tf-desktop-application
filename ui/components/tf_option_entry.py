from typing import Optional, List
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QFrame, QComboBox, QCompleter, QListView
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from ui.components.tf_font import LABEL_FONT, TEXT_FONT

class TFOptionEntry(QFrame):
    value_changed = pyqtSignal(str)

    def __init__(
            self,
            label_text: str = "",
            options: List[str] = None,
            current_value: str = "",
            label_size: int = 80,
            value_size: int = 36,
            height: int = 24,
            extra_value_width: Optional[int] = None,
            enable_filter: bool = False,
            parent: Optional[QFrame] = None
    ) -> None:
        super().__init__(parent)

        self.extra_value_width = extra_value_width
        self._setup_ui(
            label_text, options or [], current_value,
            label_size, value_size, height, enable_filter
        )

    def _setup_ui(
            self,
            label_text: str,
            options: List[str],
            current_value: str,
            label_size: int,
            value_size: int,
            height: int,
            enable_filter: bool
    ) -> None:
        self.setFixedHeight(height)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(2)

        self.label = QLabel(label_text)
        self.label.setFont(LABEL_FONT)
        self.label.setFixedWidth(label_size)
        self.label.setFixedHeight(height - 4)

        self.value_field = QComboBox()
        self.value_field.setFont(TEXT_FONT)
        self.value_field.view().setFont(TEXT_FONT)
        self.value_field.setFixedHeight(height - 4)
        self.value_field.setFixedWidth(value_size)
        self.value_field.setEditable(True)
        self.value_field.lineEdit().setFont(TEXT_FONT)

        if self.extra_value_width:
            self.value_field.view().setMinimumWidth(value_size + self.extra_value_width)

        self.value_field.setStyleSheet("""
            QComboBox { 
                padding: 2px 5px;
                min-height: 18px;
            }
        """)

        self.value_field.addItems(options)
        if current_value and current_value in options:
            self.value_field.setCurrentText(current_value)

        if enable_filter:
            self._setup_filter()

        self.value_field.currentTextChanged.connect(self.value_changed.emit)

        layout.addWidget(self.label)
        layout.addSpacing(-2)
        layout.addWidget(self.value_field)
        layout.addStretch()

    def _setup_filter(self) -> None:
        completer = QCompleter(self.value_field.model(), self.value_field)
        completer.setCompletionRole(Qt.ItemDataRole.DisplayRole)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        popup = QListView()
        popup.setIconSize(QSize(24, 24))
        popup.setUniformItemSizes(True)
        completer.setPopup(popup)

        self.value_field.setCompleter(completer)

    def get_value(self) -> str:
        return self.value_field.currentText()