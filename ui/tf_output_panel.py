from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from tools.tf_application import TFApplication

class TFOutputPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_enable = False
        self.app = TFApplication.instance()
        self.init_ui()
        self.hide()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setMinimumHeight(100)
        self.text_display.setMaximumHeight(self.parent().height() // 2)
        layout.addWidget(self.text_display)

    def display_output(self, text):
        self.text_display.append(text)
        scrollbar = self.text_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_output(self):
        self.text_display.clear()

    def toggle_panel(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def resizeEvent(self, event):
        if self.parent():
            self.setFixedWidth(self.parent().width())
            self.text_display.setMaximumHeight(self.parent().height() // 2)
        super().resizeEvent(event)
        