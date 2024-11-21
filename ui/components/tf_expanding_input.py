from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLineEdit, QTextEdit

from ui.tf_application import TFApplication
from ui.components.tf_font import TEXT_FONT

class TFExpandingInput(QLineEdit):
    def __init__(
            self,
            place_holder: str = None,
            line_width: int = 100,
            line_height: int = 30,
            text_width: int = 300,
            text_height: int = 100,
            font: QFont = TEXT_FONT,
            parent=None
    ):
        super().__init__(parent)
        if place_holder:
            self.setPlaceholderText(place_holder)
        self.setFixedWidth(line_width)
        self.setFixedHeight(line_height)
        self.setFont(font)

        self.text_edit = QTextEdit()
        self.text_edit.setFixedWidth(text_width)
        self.text_edit.setFixedHeight(text_height)
        self.text_edit.setFont(font)
        self.text_edit.hide()

        self.text_edit.setWindowFlag(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)

        self.textChanged.connect(self._sync_text_to)
        self.text_edit.textChanged.connect(self._sync_text_from)

        TFApplication.instance().installEventFilter(self)

    def mousePressEvent(self, event):
        self._expand()
        super().mousePressEvent(event)

    def _sync_text_to(self, text):
        self.text_edit.blockSignals(True)
        self.text_edit.setPlainText(text)
        self.text_edit.blockSignals(False)

    def _sync_text_from(self):
        text = self.text_edit.toPlainText()
        self.blockSignals(True)
        self.setText(text)
        self.blockSignals(False)

    def _expand(self):
        global_pos = self.mapToGlobal(self.rect().topLeft())
        self.text_edit.move(global_pos)
        self.text_edit.show()
        self.text_edit.raise_()
        self.text_edit.activateWindow()
        self.text_edit.setFocus()

    def _collapse(self):
        self.text_edit.hide()
        self.setFocus()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if self.text_edit.isVisible():
                click_pos = event.globalPosition().toPoint()
                if not self.text_edit.geometry().contains(click_pos):
                    self._collapse()
        return super().eventFilter(obj, event)
