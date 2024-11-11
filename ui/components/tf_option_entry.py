from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QMouseEvent
from typing import Optional, Callable, List, Union, Any

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

    def __init__(self, label_text: str = "", options: List[str] = None, current_value: str = "", 
                 label_size: int = 80, value_size: int = 36, height: int = 24,
                 custom_label_font: Optional[QFont] = None, custom_edit_font: Optional[QFont] = None,
                 alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
                 label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                 object_name: Optional[str] = None,
                 special_edit: Optional[Callable[[], Optional[str]]] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self.special_edit = special_edit
        self._setup_ui(label_text, options or [], current_value, label_size, value_size, height,
                      custom_label_font, custom_edit_font, alignment, label_alignment, object_name)

    def _setup_ui(self, label_text: str, options: List[str], current_value: str,
                 label_size: int, value_size: int, height: int,
                 custom_label_font: Optional[QFont], custom_edit_font: Optional[QFont],
                 alignment: Qt.AlignmentFlag, label_alignment: Qt.AlignmentFlag,
                 object_name: Optional[str]) -> None:
        self.setFixedHeight(height)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 0, 2, 0)
        self.layout.setSpacing(2)

        self.label = QLabel(label_text)
        self.label.setFont(custom_label_font if custom_label_font else self.label_font)
        self.label.setFixedWidth(label_size)
        self.label.setAlignment(label_alignment)

        self.value_field = QComboBox()
        self.value_field.setFont(custom_edit_font if custom_edit_font else self.edit_font)
        if object_name:
            self.value_field.setObjectName(object_name)
        self.value_field.setFixedWidth(value_size)
        self.value_field.addItems(options)
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

    def get_value(self) -> str:
        return self.value_field.currentText()

    def set_value(self, value: str) -> None:
        index = self.value_field.findText(str(value))
        if index >= 0:
            self.value_field.setCurrentIndex(index)

    def set_options(self, options: List[str], current_value: Optional[str] = None) -> None:
        self.value_field.clear()
        self.value_field.addItems(options)
        if current_value and current_value in options:
            self.value_field.setCurrentText(current_value)

    def set_label(self, text: str) -> None:
        self.label.setText(text)

    def set_label_font(self, font: QFont) -> None:
        self.label.setFont(font)

    def set_edit_font(self, font: QFont) -> None:
        self.value_field.setFont(font)
