from typing import List, Type, Optional

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget, QScrollArea

from core.windows.tf_draggable_window import TFDraggableWindow
from ui.tf_application import TFApplication
from settings.general import MAX_WIDTH, MAX_HEIGHT

class TFWindowContainer(QWidget):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.app = TFApplication.instance()
        self.windows: List[TFDraggableWindow] = []
        self.focused_window: Optional[TFDraggableWindow] = None

        self.setObjectName("windowContainer")
        self.setStyleSheet("""
            QWidget#windowContainer {
                background-color: #181C26;
            }
        """)
        
        self.setMinimumSize(MAX_WIDTH, MAX_HEIGHT)

    def add_window(self, window_class: Type[TFDraggableWindow]) -> None:
        current_count = sum(1 for win in self.windows if isinstance(win, window_class))
        if current_count >= window_class.metadata.max_instances:
            message = (f"Cannot add more '{window_class.metadata.window_title}'. "
                      f"Maximum count of {window_class.metadata.max_instances} reached.")
            self.app.show_message(message, 3000, 'green')
            return

        window = window_class(parent=self)
        window.closed.connect(self._remove_specific_window)
        window_size = window.metadata.window_size
        
        x, y = 0, 0
        while self._is_position_occupied(x, y, window_size):
            x += window_size[0]
            if x + window_size[0] > self.width():
                x = 0
                y += window_size[1]
            if y + window_size[1] > self.height():
                break
        
        if y + window_size[1] > self.height():
            if self.windows:
                rightmost_window = max(self.windows, key=lambda w: w.x() + w.width())
                x = rightmost_window.x() + rightmost_window.width()
                y = rightmost_window.y()
            else:
                x, y = 0, 0

        window.move(x, y)
        self._append_window(window)
        window.show()
        window.moved.connect(self.resize_container)
        self.resize_container()

    def resize_container(self) -> None:
        max_right = max((window.x() + window.width() for window in self.windows), default=0)
        max_bottom = max((window.y() + window.height() for window in self.windows), default=0)
        
        padding = 20
        new_width = max(max_right + padding, MAX_WIDTH)
        new_height = max(max_bottom + padding, MAX_HEIGHT)
        
        self.setMinimumWidth(new_width)
        self.setMinimumHeight(new_height)
        self.resize(new_width, new_height)
        
        scroll_area = self._find_parent_scroll_area()
        if scroll_area:
            scroll_area.updateGeometry()

    def _find_parent_scroll_area(self) -> QScrollArea:
        widget = self
        while widget:
            if isinstance(widget.parentWidget(), QScrollArea):
                return widget.parentWidget()
            widget = widget.parentWidget()
        return None
    
    def bring_window_to_front(self, window: TFDraggableWindow) -> None:
        if window in self.windows:
            window.raise_()

    def _remove_specific_window(self, window: TFDraggableWindow) -> None:
        if window in self.windows:
            if self.focused_window is window:
                self.focused_window = None
            self.windows.remove(window)
            window.deleteLater()
            self.resize_container()

    def _append_window(self, window: TFDraggableWindow):
        count = 0
        max_number = 0
        base_title = window.metadata.window_title
        
        for w in self.windows:
            if isinstance(w, type(window)):
                count += 1
                try:
                    current_title = w.title
                    if current_title != base_title:
                        number = int(current_title.split(" ")[-1])
                        max_number = max(max_number, number)
                except (ValueError, IndexError):
                    continue

        if count > 0:
            new_title = f"{base_title} {max_number + 1}"
            window.title = new_title
        else:
            window.title = base_title

        self.windows.append(window)

    def _is_position_occupied(self, x, y, size) -> bool:
        for win in self.windows:
            if (win.x() < x + size[0] and x < win.x() + win.width()) and \
               (win.y() < y + size[1] and y < win.y() + win.height()):
                return True
        return False
    
    def set_focused_window(self, window: TFDraggableWindow):
        if self.focused_window is window:
            return
        if self.focused_window is not None:
            self.focused_window.focused = False
        self.focused_window = window
        if self.focused_window is not None:
            self.focused_window.focused = True
    
    def sizeHint(self) -> QSize:
        return self.minimumSizeHint()
    
    def minimumSizeHint(self) -> QSize:
        max_right = max((window.x() + window.width() for window in self.windows), default=0)
        max_bottom = max((window.y() + window.height() for window in self.windows), default=0)
        
        padding = 50
        width = max(max_right + padding, MAX_WIDTH)
        height = max(max_bottom + padding, MAX_HEIGHT)
        
        return QSize(width, height)
