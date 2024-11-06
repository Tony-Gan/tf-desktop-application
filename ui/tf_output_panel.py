# tf_output_panel.py
from PyQt6.QtWidgets import QTextEdit, QApplication, QMainWindow
from PyQt6.QtCore import pyqtSignal, Qt, QRect

from ui.tf_widgets.tf_settings_widget import TFCloseButton, TFMenuButton
from settings.general import ICON_BUTTON_SIZE

class TFOutputPanel(QTextEdit):
    """
    A floating output panel that stays at the bottom of the main window.
    Allows vertical resizing only and maintains width equal to parent window.
    """
    closed = pyqtSignal()
    visibility_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_enable = False
        self.resize_area_height = 5
        self.dragging = False
        self.drag_start_y = 0
        self.initial_height = 0
        
        self._init_ui()
        self._init_buttons()
        self.hide()

    def _init_ui(self):
        self.setObjectName("output_panel")
        self.setReadOnly(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        
        self.setMinimumHeight(100)
        screen = QApplication.primaryScreen()
        if screen:
            self.setMaximumHeight(screen.size().height() // 2)
        
        self.setFixedHeight(200)
        
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        self.setContentsMargins(5, 5, 5, 5)

    def _init_buttons(self):
        self._close_button = TFCloseButton(parent=self, position=(0, 0))
        self._menu_button = TFMenuButton(parent=self, position=(0, 0), skip_default=True)
        self._update_button_positions()

    def _update_button_positions(self):
        width = self.width()
        margin = 5
        spacing = 5
        button_size = ICON_BUTTON_SIZE[0]

        close_btn_x = width - margin - button_size
        menu_btn_x = close_btn_x - spacing - button_size
        btn_y = margin

        self._close_button.move(close_btn_x, btn_y)
        self._menu_button.move(menu_btn_x, btn_y)

    def update_position(self):
        pass

    def showEvent(self, event):
        super().showEvent(event)
        self.update_position()
        self.visibility_changed.emit(True)
        
    def hideEvent(self, event):
        super().hideEvent(event)
        self.visibility_changed.emit(False)

    def display_output(self, text):
        self.append(text)
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_output(self):
        self.clear()

    def toggle_panel(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()

    def showEvent(self, event):
        super().showEvent(event)
        self.update_position()
        self.visibility_changed.emit(True)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.visibility_changed.emit(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_button_positions()
    