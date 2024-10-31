from PyQt6.QtWidgets import QFrame, QPushButton, QMenu, QLabel
from PyQt6.QtGui import QMouseEvent, QAction, QIcon, QFont
from PyQt6.QtCore import Qt, QPoint, pyqtSignal

from time import time

from tools.tf_message_bar import TFMessageBar

class TFDraggableWindow(QFrame):
    moved = pyqtSignal()
    mouse_released = pyqtSignal()
    closed = pyqtSignal(object)

    def __init__(self, parent=None, size=(200, 150), title="Default Window", max_count=1, message_bar: TFMessageBar=None):
        super().__init__(parent)

        self.setObjectName("TFDraggableWindow")
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setFixedSize(*size)
        self.size = size
        self.display_title = title
        self.max_count = max_count
        self.message_bar = message_bar
        self.last_moved_time = 0

        self.title_label = QLabel(self.display_title, self)
        self.title_label.move(10, 5)
        font = QFont("Open Sans", 11)
        self.title_label.setFont(font)

        self.close_button = QPushButton(self)
        self.close_button.setObjectName("close_button")
        self.close_button.setIcon(QIcon("static/images/icons/close.png"))
        self.close_button.setFixedSize(20, 20)
        self.close_button.move(size[0] - 25, 5)
        self.close_button.clicked.connect(self.request_close)

        self.menu_button = QPushButton(self)
        self.menu_button.setObjectName("menu_button")
        self.menu_button.setIcon(QIcon("static/images/icons/settings.png"))
        self.menu_button.setFixedSize(20, 20)
        self.menu_button.move(size[0] - 50, 5)

        self.menu = QMenu(self)
        self.init_default_actions()

        self.dragging = False
        self.offset = QPoint()

    def init_default_actions(self):
        close_action = QAction("Close the window", self)
        close_action.triggered.connect(self.request_close)
        self.menu.addAction(close_action)
        self.menu_button.clicked.connect(self.show_menu)

    def add_menu_action(self, text, callback):
        action = QAction(text, self)
        action.triggered.connect(callback)
        self.menu.addAction(action)

    def show_menu(self):
        self.menu.exec(self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft()))

    def request_close(self):
        self.closed.emit(self)
        self.hide()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.dragging:
            current_pos = event.position().toPoint()
            delta = current_pos - self.offset
            new_pos = self.pos() + delta

            if self.parent():
                new_x = max(0, new_pos.x())
                new_y = max(0, new_pos.y())
                
                self.move(new_x, new_y)
                self.moved.emit()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.last_moved_time = time()
            self.mouse_released.emit()

    def rename(self, name: str) -> None:
        self.display_title = name
