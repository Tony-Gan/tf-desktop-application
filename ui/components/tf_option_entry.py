from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget, QComboBox, QCompleter, QListView
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QMouseEvent, QStandardItemModel, QStandardItem
from typing import Dict, Optional, Callable, List, Union

class TFOptionEntry(QWidget):
    value_changed = pyqtSignal(str)
    
    @property
    def label_font(self):
        font = QFont("Inconsolata", 10)
        font.setWeight(QFont.Weight.DemiBold)
        return font

    @property
    def edit_font(self):
        font = QFont("Inconsolata", 10)
        font.setWeight(QFont.Weight.Normal)
        return font

    def __init__(self, label_text: str = "", options: Union[List[str], Dict[str, List[str]]] = None,
                current_value: str = "", label_size: int = 80, value_size: int = 36, height: int = 24,
                custom_label_font: Optional[QFont] = None, custom_edit_font: Optional[QFont] = None,
                label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                object_name: Optional[str] = None, special_edit: Optional[Callable[[], Optional[str]]] = None,
                extra_value_width: int = None, filter: bool = False, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.special_edit = special_edit
        self.extra_value_width = extra_value_width
        self.filter_enabled = filter
        self._setup_ui(label_text, options or [], current_value, label_size, value_size, height,
                    custom_label_font, custom_edit_font, label_alignment, object_name)

    def _setup_ui(self, label_text: str, options: List[str], current_value: str,
                 label_size: int, value_size: int, height: int,
                 custom_label_font: Optional[QFont], custom_edit_font: Optional[QFont], label_alignment: Qt.AlignmentFlag,
                 object_name: Optional[str]) -> None:
        self.setFixedHeight(height)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 0, 2, 0)
        self.layout.setSpacing(2)

        self.label = QLabel(label_text)
        self.label.setFont(custom_label_font if custom_label_font else self.label_font)
        self.label.setFixedWidth(label_size)
        self.label.setAlignment(label_alignment)
        self.label.setFixedHeight(height - 4)

        self.value_field = QComboBox()
        self.value_field.setFixedHeight(height - 4)
        if self.extra_value_width:
            self.value_field.view().setMinimumWidth(value_size + self.extra_value_width)
        self.value_field.setFont(custom_edit_font if custom_edit_font else self.edit_font)
        self.value_field.view().setFont(custom_edit_font if custom_edit_font else self.edit_font)
        self.value_field.setEditable(True)
        self.value_field.lineEdit().setFont(custom_edit_font if custom_edit_font else self.edit_font)

        if object_name:
            self.value_field.setObjectName(object_name)
        self.value_field.setFixedWidth(value_size)
        self._set_grouped_options(options)
        self.value_field.setStyleSheet("""
            QComboBox { 
                padding: 2px 5px;
                min-height: 18px;
            }
        """)
        
        if current_value and current_value in options:
            self.value_field.setCurrentText(current_value)
            
        self.value_field.currentTextChanged.connect(self._on_value_changed)
        if self.special_edit:
            self.value_field.mousePressEvent = self._handle_special_edit

        self.layout.addWidget(self.label)
        self.layout.addSpacing(-2)
        self.layout.addWidget(self.value_field)
        self.layout.addStretch()

        if self.filter_enabled:
            self._enable_filter()

    def _set_grouped_options(self, options: Union[List[str], Dict[str, List[str]]]) -> None:
        model = QStandardItemModel(self.value_field)
        item_font = self.value_field.font()

        if isinstance(options, dict):
            for group_name, items in options.items():
                group_item = QStandardItem(group_name)
                group_item.setFlags(Qt.ItemFlag.NoItemFlags)
                model.appendRow(group_item)

                group_item.setData("color: #555555;", Qt.ItemDataRole.ToolTipRole)

                for item in items:
                    option_item = QStandardItem(item)
                    option_item.setFont(item_font)
                    model.appendRow(option_item)
        else:
            for item in options:
                option_item = QStandardItem(item)
                option_item.setFont(item_font)
                model.appendRow(option_item)

        self.value_field.setModel(model)

    def _handle_special_edit(self, event: QMouseEvent) -> None:
        if self.special_edit:
            result = self.special_edit()
            if result is not None:
                index = self.value_field.findText(str(result))
                if index >= 0:
                    self.value_field.setCurrentIndex(index)
        elif hasattr(self.value_field, 'mousePressEvent'):
            super(type(self.value_field), self.value_field).mousePressEvent(event)

    def _on_value_changed(self, text: str) -> None:
        self.value_changed.emit(text)

    def _enable_filter(self) -> None:
        model = self.value_field.model()

        completer = QCompleter(model, self.value_field)
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

    def set_value(self, value: str) -> None:
        index = self.value_field.findText(str(value))
        if index >= 0:
            self.value_field.setCurrentIndex(index)

    def set_options(self, options: Union[List[str], Dict[str, List[str]]], current_value: Optional[str] = None) -> None:
        self._set_grouped_options(options)
        if current_value:
            self.set_value(current_value)

    def set_label(self, text: str) -> None:
        self.label.setText(text)

    def set_label_font(self, font: QFont) -> None:
        self.label.setFont(font)

    def set_edit_font(self, font: QFont) -> None:
        self.value_field.setFont(font)
