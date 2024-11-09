from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget, QLineEdit, QDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.components.tf_number_receiver import TFNumberReceiver

class TFValueEntry(QWidget):
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

    def __init__(self, label_text="", value_text="", label_size=80, value_size=36, height=24,
                custom_label_font=None, custom_edit_font=None, 
                alignment=Qt.AlignmentFlag.AlignCenter,
                label_alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                object_name=None, 
                number_only=False,
                allow_decimal=True,
                allow_negative=False,
                special_edit=None,
                parent=None):
        super().__init__(parent)

        self.special_edit = special_edit
        self._setup_ui(label_text, value_text, label_size, value_size, height,
                     custom_label_font, custom_edit_font, alignment, label_alignment,
                     object_name, number_only, allow_decimal, allow_negative)

    def _setup_ui(self, label_text, value_text, label_size, value_size, height,
                 custom_label_font, custom_edit_font, alignment, label_alignment,
                 object_name, number_only, allow_decimal, allow_negative):
        self.setFixedHeight(height)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 0, 2, 0)
        self.layout.setSpacing(2)

        self.label = QLabel(label_text)
        self.label.setFont(custom_label_font if custom_label_font else self.label_font)
        self.label.setFixedWidth(label_size)
        self.label.setAlignment(label_alignment)

        if number_only:
            self.value_field = TFNumberReceiver(
                text=str(value_text),
                alignment=alignment,
                font=custom_edit_font if custom_edit_font else self.edit_font,
                allow_decimal=allow_decimal,
                allow_negative=allow_negative,
                parent=self
            )
        else:
            self.value_field = QLineEdit()
            self.value_field.setFont(custom_edit_font if custom_edit_font else self.edit_font)
            self.value_field.setAlignment(alignment)
            self.value_field.setText(str(value_text))

        if object_name:
            self.value_field.setObjectName(object_name)
        self.value_field.setFixedWidth(value_size)
        self.value_field.setEnabled(False)
        self.value_field.setStyleSheet("QLineEdit { padding: 1px; }")
        
        self.value_field.textChanged.connect(self._on_value_changed)
        if self.special_edit:
            self.value_field.mousePressEvent = self._handle_special_edit

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value_field)
        self.layout.addStretch()

    def _handle_special_edit(self, event):
        if self.value_field.isEnabled() and self.special_edit:
            result = self.special_edit()
            if result is not None:
                self.value_field.setText(str(result))
        elif hasattr(self.value_field, 'mousePressEvent'):
            super(type(self.value_field), self.value_field).mousePressEvent(event)

    def _on_value_changed(self, text):
        self.value_changed.emit(text)

    def get_value(self):
        return self.value_field.text()

    def set_value(self, value):
        self.value_field.setText(str(value))

    def set_label(self, text):
        self.label.setText(text)

    def set_label_font(self, font):
        self.label.setFont(font)

    def set_edit_font(self, font):
        self.value_field.setFont(font)

    def set_special_edit(self, callback):
        self.special_edit = callback
        if callback:
            self.value_field.mousePressEvent = self._handle_special_edit
        else:
            self.value_field.mousePressEvent = super(type(self.value_field), self.value_field).mousePressEvent
