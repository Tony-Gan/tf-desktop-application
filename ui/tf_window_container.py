from typing import List, Type, Dict

from PyQt6.QtWidgets import QWidget

from ui.tf_draggable_window import TFDraggableWindow
from ui.tf_frames_impl.tf_calculator import TFCalculator
from ui.tf_frames_impl.tf_scientific_calculator import TFScientificCalculator
from ui.tf_frames_impl.tf_currency_converter import TFCurrencyConverter
from tools.tf_message_bar import TFMessageBar
from database.tf_database import TFDatabase
from database.models import TFWindowState
from settings.general import MAX_WIDTH, MAX_HEIGHT

class TFWindowContainer(QWidget):
    
    def __init__(self, parent=None, message_bar: TFMessageBar=None, database: TFDatabase=None):
        super().__init__(parent)
        self.parent = parent
        self.message_bar = message_bar
        self.database = database
        self.windows: List[TFDraggableWindow] = []
        self.setMinimumSize(MAX_WIDTH, MAX_HEIGHT)

        if self.database:
            self.restore_windows()

    def save_window_state(self, window: TFDraggableWindow):
        if not self.database:
            return
        
        with self.database.get_session() as session:
            window_state = TFWindowState(
                window_class=window.__class__.__name__,
                title=window.display_title,
                x_position=window.x(),
                y_position=window.y()
            )
            session.add(window_state)
            session.commit()

    def restore_windows(self):
        if not self.database:
            return

        window_classes = self.get_window_classes()

        with self.database.get_session() as session:
            saved_states = session.query(TFWindowState).all()
            
            for state in saved_states:
                if state.window_class in window_classes:
                    window_class = window_classes[state.window_class]
                    
                    window = window_class(parent=self, message_bar=self.message_bar)
                    window.closed.connect(self.remove_specific_window)
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

    def save_all_window_states(self):
        if not self.database:
            return
        
        with self.database.get_session() as session:
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
        current_count = sum(1 for win in self.windows if isinstance(win, window_class))
        temp_window = window_class(parent=self)
        if current_count >= temp_window.max_count:
            message = f"Cannot add more '{temp_window.display_title}'. Maximum count of {temp_window.max_count} reached."
            self.message_bar.show_message(message, 3000, 'green')
            return

        window = window_class(parent=self, message_bar=self.message_bar, database=self.database)
        window.closed.connect(self.remove_specific_window)
        size = window.size

        window.bring_to_front.connect(lambda w: w.raise_())
        window.send_to_back.connect(lambda w: w.lower())
        window.raise_level.connect(lambda w: w.raise_())
        window.lower_level.connect(lambda w: w.lower())

        x, y = 0, 0
        while self.is_position_occupied(x, y, size):
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

        self.append_window(window)

        window.show()

        window.moved.connect(self.resize_container)
        self.resize_container()

    def remove_specific_window(self, window: TFDraggableWindow) -> None:
        if window in self.windows:
            self.windows.remove(window)
            window.deleteLater()
            self.resize_container()

    def append_window(self, window: TFDraggableWindow):
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

    def resize_container(self) -> None:
        max_width = max((window.x() + window.width() for window in self.windows), default=MAX_WIDTH)
        max_height = max((window.y() + window.height() for window in self.windows), default=MAX_HEIGHT)

        self.setMinimumSize(max(max_width, MAX_WIDTH), max(max_height, MAX_HEIGHT))

    def is_position_occupied(self, x, y, size) -> bool:
        for win in self.windows:
            if (win.x() < x + size[0] and x < win.x() + win.width()) and \
               (win.y() < y + size[1] and y < win.y() + win.height()):
                return True
        return False
    
    def bring_window_to_front(self, window: TFDraggableWindow) -> None:
        if window in self.windows:
            window.raise_()

    def get_window_classes(self) -> Dict[str, Type[TFDraggableWindow]]:
        return {
            'TFCalculator': TFCalculator,
            'TFScientificCalculator': TFScientificCalculator,
            'TFCurrencyConverter': TFCurrencyConverter
        }
    
