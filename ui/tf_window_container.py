from typing import List, Type

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget, QScrollArea

from ui.tf_draggable_window import TFDraggableWindow
from ui.tf_application import TFApplication
from tools.tf_tool_registry import TFToolRegistry
from database.models import TFWindowState
from settings.general import MAX_WIDTH, MAX_HEIGHT

class TFWindowContainer(QWidget):
    """
    A container widget managing multiple draggable windows within the application.
    
    This class handles the creation, positioning, and state management of draggable
    windows. It provides functionality for window placement, state persistence,
    and window organization within the container area.

    Args:
        parent (QWidget): Parent widget. Should be set as the main window.

    Example:
        >>> # Creating a window container
        >>> container = TFWindowContainer(parent_widget)
        >>> 
        >>> # Adding a new calculator window
        >>> container.add_window(TFCalculator)
        >>> 
        >>> # Saving window states
        >>> container.save_all_window_states()

    Attributes:
        windows (List[TFDraggableWindow]): List of managed draggable windows.
        app (TFApplication): Reference to the main application instance.
        parent (QWidget): Parent widget reference.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.app = TFApplication.instance()
        self.windows: List[TFDraggableWindow] = []
        
        # Set initial size to ensure scrolling works properly
        self.setMinimumSize(MAX_WIDTH, MAX_HEIGHT)
        
        self._restore_windows()

    def save_all_window_states(self):
        """
        Save the states of all current windows to the database.
        
        Clears existing window states and saves the current state of all windows,
        including their positions and titles.
        """
        with self.app.database.get_session() as session:
            session.query(TFWindowState).delete()
            
            for window in self.windows:
                window_state = TFWindowState(
                    window_class=window.__class__.__name__,
                    title=window.metadata.window_title,
                    x_position=window.x(),
                    y_position=window.y()
                )
                session.add(window_state)
            
            session.commit()

    def add_window(self, window_class: Type[TFDraggableWindow]) -> None:
        """
        Add a new window of the specified class to the container.
        
        Creates and positions a new window instance, ensuring it doesn't exceed
        maximum count limits and doesn't overlap with existing windows.
        Automatically connects necessary signals and handles window positioning.

        Args:
            window_class (Type[TFDraggableWindow]): Class of the window to create.
        """
        current_count = sum(1 for win in self.windows if isinstance(win, window_class))
        if current_count >= window_class.metadata.max_instances:
            message = (f"Cannot add more '{window_class.metadata.window_title}'. "
                      f"Maximum count of {window_class.metadata.max_instances} reached.")
            self.app.show_message(message, 3000, 'green')
            return

        window = window_class(parent=self)
        window.closed.connect(self._remove_specific_window)
        window_size = window.metadata.window_size

        window.bring_to_front.connect(lambda w: w.raise_())
        window.send_to_back.connect(lambda w: w.lower())
        window.raise_level.connect(lambda w: w.raise_())
        window.lower_level.connect(lambda w: w.lower())

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
        """
        Resize the container to accommodate all windows, considering both width and height.
        Ensures proper scrolling in both directions.
        """
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
        """
        Bring a specific window to the front of the stack.
        
        Raises the specified window above other windows in the container.

        Args:
            window (TFDraggableWindow): Window to bring to front.
        """
        if window in self.windows:
            window.raise_()

    def _restore_windows(self):
        window_classes = {
            cls.__name__: cls 
            for cls in TFToolRegistry.get_tools().values()
        }

        with self.app.database.get_session() as session:
            saved_states = session.query(TFWindowState).all()
            
            for state in saved_states:
                if state.window_class in window_classes:
                    window_class = window_classes[state.window_class]
                    
                    window = window_class(parent=self)
                    window.closed.connect(self._remove_specific_window)
                    window.moved.connect(self.resize_container)
                    
                    window.bring_to_front.connect(lambda w: w.raise_())
                    window.send_to_back.connect(lambda w: w.lower())
                    window.raise_level.connect(lambda w: w.raise_())
                    window.lower_level.connect(lambda w: w.lower())
                    
                    window.move(state.x_position, state.y_position)
                    
                    if state.title != window.metadata.window_title:
                        window.title = state.title
                    
                    self.windows.append(window)
                    window.show()

    def _remove_specific_window(self, window: TFDraggableWindow) -> None:
        if window in self.windows:
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
    
    def sizeHint(self) -> QSize:
        return self.minimumSizeHint()
    
    def minimumSizeHint(self) -> QSize:
        max_right = max((window.x() + window.width() for window in self.windows), default=0)
        max_bottom = max((window.y() + window.height() for window in self.windows), default=0)
        
        padding = 50
        width = max(max_right + padding, MAX_WIDTH)
        height = max(max_bottom + padding, MAX_HEIGHT)
        
        return QSize(width, height)
