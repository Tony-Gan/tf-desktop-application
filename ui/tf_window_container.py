from PyQt6.QtWidgets import QWidget

from .tf_draggable_window import TFDraggableWindow
from tools.tf_message_bar import TFMessageBar
from settings.general import MAX_WIDTH, MAX_HEIGHT

from typing import List, Type

class TFWindowContainer(QWidget):
    
    def __init__(self, parent=None, message_bar: TFMessageBar =None):
        super().__init__(parent)
        self.parent = parent
        self.message_bar = message_bar
        self.windows: List[TFDraggableWindow] = []
        self.setMinimumSize(MAX_WIDTH, MAX_HEIGHT)
        
    def add_window(self, window_class: Type[TFDraggableWindow]) -> None:
        current_count = sum(1 for win in self.windows if isinstance(win, window_class))
        temp_window = window_class(parent=self)
        if current_count >= temp_window.max_count:
            message = f"Cannot add more '{temp_window.display_title}'. Maximum count of {temp_window.max_count} reached."
            self.message_bar.show_message(message, 3000, 'green')
            return

        window = window_class(parent=self, message_bar=self.message_bar)
        window.mouse_released.connect(self.arrange_windows)
        window.closed.connect(self.remove_specific_window)
        size = window.size

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

    def arrange_windows(self):
        if not self.windows:
            return
            
        current_window = max(self.windows, key=lambda w: w.last_moved_time)
        if current_window.last_moved_time == 0:
            return
                
        windows_info = [(w, w.x(), w.y()) for w in self.windows if w != current_window]
        windows_info.sort(key=lambda x: (x[2], x[1]))
        
        rows, row_positions = self._group_windows_into_rows(windows_info)
        
        current_x = current_window.x()
        current_y = current_window.y()
        insert_row_index = -1
        insert_position = -1
        original_row_index = self._find_original_row_index(rows, current_y)
            
        insert_row_index, target_y, create_new_row, insert_position = self._find_insert_position(
            current_window, current_x, current_y, rows, row_positions)
        
        self._handle_original_row(original_row_index, insert_row_index, rows, row_positions, current_window, current_x)
        
        self._handle_target_row(create_new_row, insert_row_index, target_y, rows, current_window, insert_position)
        
        self._adjust_all_rows_position(rows)
        
        self.resize_container()

    def _group_windows_into_rows(self, windows_info):
        rows = []
        current_row = []
        current_y = windows_info[0][2] if windows_info else 0
        
        for window, x, y in windows_info:
            if abs(y - current_y) < 5:
                current_row.append((window, x))
            else:
                if current_row:
                    rows.append(sorted(current_row, key=lambda x: x[1]))
                current_row = [(window, x)]
                current_y = y
        if current_row:
            rows.append(sorted(current_row, key=lambda x: x[1]))
                
        row_positions = []
        current_y = 0
        for row in rows:
            if row:
                height = row[0][0].height()
                row_positions.append((current_y, height))
                current_y += height
                
        return rows, row_positions

    def _find_original_row_index(self, rows, current_y):
        for i, row in enumerate(rows):
            for j, (window, x) in enumerate(row):
                if abs(window.y() - current_y) < 5:
                    return i
        return -1

    def _find_insert_position(self, current_window, current_x, current_y, rows, row_positions):
        create_new_row = True
        target_y = current_y
        
        closest_row_index = -1
        min_distance = float('inf')
        for i, (row_y, height) in enumerate(row_positions):
            distance = abs(current_y - row_y)
            if distance < min_distance:
                min_distance = distance
                closest_row_index = i
        
        if min_distance < 200:
            create_new_row = False
            insert_row_index = closest_row_index
            target_y = row_positions[closest_row_index][0]
            
            target_row = rows[insert_row_index]
            insert_position = self._find_row_insert_position(target_row, current_x)
        else:
            insert_row_index, target_y = self._find_new_row_position(current_window, current_y, row_positions)
            insert_position = 0
            rows.insert(insert_row_index, [])
            row_positions.insert(insert_row_index, (target_y, current_window.height()))
        
        return insert_row_index, target_y, create_new_row, insert_position

    def _find_row_insert_position(self, target_row, current_x):
        for j, (window, x) in enumerate(target_row):
            if current_x < x:
                return j
        return len(target_row)

    def _find_new_row_position(self, current_window, current_y, row_positions):
        insert_row_index = -1
        target_y = current_y
        
        for i, (row_y, height) in enumerate(row_positions):
            if current_y < row_y:
                insert_row_index = i
                target_y = row_y - height
                break
        
        if insert_row_index == -1:
            insert_row_index = len(row_positions)
            if row_positions:
                target_y = row_positions[-1][0] + row_positions[-1][1]
            else:
                target_y = 0
                
        return insert_row_index, target_y

    def _handle_original_row(self, original_row_index, insert_row_index, rows, row_positions, current_window, current_x):
        if original_row_index != -1 and original_row_index != insert_row_index:
            original_row = rows[original_row_index]
            updated_row = []
            original_y = original_row[0][0].y() if original_row else 0
            
            remaining_windows = [(window, x) for window, x in original_row if window != current_window]
            remaining_windows.sort(key=lambda x: x[1])
            
            current_x = 0
            for window, _ in remaining_windows:
                window.move(current_x, original_y)
                current_x += window.width()
                updated_row.append((window, current_x))
            
            if remaining_windows:
                rows[original_row_index] = updated_row
            else:
                rows.pop(original_row_index)
                row_positions.pop(original_row_index)
                for i in range(original_row_index, len(rows)):
                    row_y = row_positions[i][0]
                    for window, _ in rows[i]:
                        window.move(window.x(), row_y)

    def _handle_target_row(self, create_new_row, insert_row_index, target_y, rows, current_window, insert_position):
        if not create_new_row:
            target_row = rows[insert_row_index]
            new_positions = []
            current_x = 0
            
            for i in range(insert_position):
                window, _ = target_row[i]
                new_positions.append((window, current_x))
                current_x += window.width()
            
            new_positions.append((current_window, current_x))
            current_x += current_window.width()
            
            for i in range(insert_position, len(target_row)):
                window, _ = target_row[i]
                new_positions.append((window, current_x))
                current_x += window.width()
            
            for window, x in new_positions:
                window.move(x, target_y)
        else:
            current_window.move(0, target_y)

    def _adjust_all_rows_position(self, rows):
        current_y = 0
        for row in rows:
            if row:
                row_height = row[0][0].height()
                for window, _ in row:
                    window.move(window.x(), current_y)
                current_y += row_height
        
    def remove_window(self) -> None:
        if self.windows:
            window = self.windows.pop()
            window.close()
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
