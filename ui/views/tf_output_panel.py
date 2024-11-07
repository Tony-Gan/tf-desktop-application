from PyQt6.QtWidgets import QTextEdit, QApplication
from PyQt6.QtCore import pyqtSignal, Qt

from ui.components.tf_settings_widget import TFCloseButton, TFMenuButton
from settings.general import ICON_BUTTON_SIZE

class TFOutputPanel(QTextEdit):
    """
    A floating output panel that stays at the bottom of the main window.
    Allows vertical resizing only and maintains width equal to parent window.
    """
    closed = pyqtSignal(object)

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

        self.setMouseTracking(True)

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
        self._close_button = TFCloseButton(self, (0, 0))
        self._menu_button = TFMenuButton(self, (0, 0), skip_default=True)

    def update_button_positions(self):
        margin = 5
        spacing = 5
        button_size = ICON_BUTTON_SIZE[0]

        close_btn_x = self.width() - margin - button_size
        menu_btn_x = close_btn_x - spacing - button_size
        btn_y = margin

        self._close_button.move(close_btn_x, btn_y)
        self._menu_button.move(menu_btn_x, btn_y)

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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and 0 <= event.position().y() <= self.resize_area_height:
            self.dragging = True
            self.drag_start_y = event.globalPosition().y()
            self.initial_height = self.height()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        pass
        # 世纪难题：为什么缩放没用

    def resizeEvent(self, event):
        super().resizeEvent(event)
