from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTextEdit

from ui.components.tf_group_box import TFGroupBox
from ui.components.tf_font import LABEL_FONT


class TFTextGroupBox(TFGroupBox):
    def __init__(self, title, place_holder_text=None, parent=None):
        self.place_holder_text = place_holder_text
        super().__init__(title, parent=parent)

    def _setup_content(self):
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont(LABEL_FONT))
        self.text_edit.setStyleSheet("background-color: transparent;")
        self.text_edit.setPlaceholderText(self.place_holder_text)

        self.layout.addWidget(self.text_edit)

    def get_text(self) -> str:
        return self.text_edit.toPlainText().strip()

    def set_text(self, text: str):
        self.text_edit.setText(text)

    def reset(self):
        self.text_edit.clear()
