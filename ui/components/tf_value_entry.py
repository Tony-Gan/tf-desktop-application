from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.components.tf_number_receiver import TFNumberReceiver

class TFValueEntry(QWidget):
    
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
                parent=None):
        super().__init__(parent)

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

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value_field)
        self.layout.addStretch()

    def get_value(self):
        return self.value_field.text()

    def set_value(self, value):
        self.value_field.setText(str(value))

    def set_label(self, text):
        self.label.setText(text)

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