from typing import List, Type, Dict

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTranslator

from ui.tf_draggable_window import TFDraggableWindow
from ui.tf_frames_impl.tf_calculator import TFCalculator
from ui.tf_frames_impl.tf_scientific_calculator import TFScientificCalculator
from ui.tf_frames_impl.tf_currency_converter import TFCurrencyConverter
from ui.tf_application import TFApplication
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
                    title=window.display_title,
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
        temp_window = window_class(parent=self)
        if current_count >= temp_window.max_count:
            message = f"Cannot add more '{temp_window.display_title}'. Maximum count of {temp_window.max_count} reached."
            self.app.show_message(message, 3000, 'green')
            return

        window = window_class(parent=self)
        window.closed.connect(self._remove_specific_window)
        size = window.size

        window.bring_to_front.connect(lambda w: w.raise_())
        window.send_to_back.connect(lambda w: w.lower())
        window.raise_level.connect(lambda w: w.raise_())
        window.lower_level.connect(lambda w: w.lower())

        x, y = 0, 0
        while self._is_position_occupied(x, y, size):
            x += size[0]
            if x + size[0] > self.width():
                x = 0
                y += size[1]
            if y + size[1] > self.height():
                break
        
        if y + size[1] > self.height():
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
        Resize the container to accommodate all windows.
        
        Adjusts the container size based on the position and size of all
        contained windows, ensuring minimum dimensions are maintained.
        Uses MAX_WIDTH and MAX_HEIGHT as minimum constraints.
        """
        max_width = max((window.x() + window.width() for window in self.windows), default=MAX_WIDTH)
        max_height = max((window.y() + window.height() for window in self.windows), default=MAX_HEIGHT)

        self.setMinimumSize(max(max_width, MAX_WIDTH), max(max_height, MAX_HEIGHT))
    
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
        window_classes = self._get_window_classes()

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
                    
                    if window.display_title != state.title:
                        window.rename(state.title)
                        window.title_label.setText(state.title)
                    
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
        for w in self.windows:
            if w.__class__ == window.__class__:
                count += 1
                try:
                    max_number = int(w.display_title.split(" ")[-1])
                except ValueError:
                    max_number = 0
        if count != 0:
            window.rename(window.display_title + f' {max_number + 1}')
        self.windows.append(window)
        window.title_label.setText(window.display_title)

    def _is_position_occupied(self, x, y, size) -> bool:
        for win in self.windows:
            if (win.x() < x + size[0] and x < win.x() + win.width()) and \
               (win.y() < y + size[1] and y < win.y() + win.height()):
                return True
        return False

    def _get_window_classes(self) -> Dict[str, Type[TFDraggableWindow]]:
        return {
            'TFCalculator': TFCalculator,
            'TFScientificCalculator': TFScientificCalculator,
            'TFCurrencyConverter': TFCurrencyConverter
        }
    
