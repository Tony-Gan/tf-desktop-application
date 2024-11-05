from time import time
from PyQt6.QtWidgets import QFrame, QLabel
from PyQt6.QtGui import QMouseEvent, QFont
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from ui.tf_application import TFApplication
from ui.tf_widgets.tf_settings_widget import TFCloseButton, TFMenuButton

class TFDraggableWindow(QFrame):
    """
    A draggable window frame that can be moved within its parent container.

    This base class provides draggable window functionality with snapping to edges,
    window management signals, and basic window controls. It serves as the base for
    all draggable windows in the application.

    Args:
        parent (QWidget): Parent widget containing this window.
        size (tuple): Window size as (width, height).
        title (str): Window title text.
        max_count (int, optional): Maximum number of instances allowed. Defaults to 1.

    Example:
        >>> # Creating a custom draggable window
        >>> class MyWindow(TFDraggableWindow):
        ...     def initialize_window(self):
        ...         # Add custom widgets and layout
        ...         pass
        >>> 
        >>> window = MyWindow(
        ...     parent=container,
        ...     size=(400, 300),
        ...     title="My Window"
        ... )

    Attributes:
        display_title (str): Window's display title.
        size (tuple): Window dimensions (width, height).
        max_count (int): Maximum allowed instances.
        title_label (QLabel): Label displaying window title.
        close_button (TFCloseButton): Button to close window.
        menu_button (TFMenuButton): Button for window menu.
        last_moved_time (float): Timestamp of last window movement.

    Signals: \n
        moved: Emitted when window is moved. \n
        mouse_released: Emitted when mouse button is released. \n
        closed: Emitted when window is closed, passes window object. \n
        bring_to_front: Emitted to request window be brought to front. \n
        send_to_back: Emitted to request window be sent to back. \n
        raise_level: Emitted to request window be raised one level. \n
        lower_level: Emitted to request window be lowered one level. \n
    """

    moved = pyqtSignal()
    mouse_released = pyqtSignal()
    closed = pyqtSignal(object)
    bring_to_front = pyqtSignal(object)
    send_to_back = pyqtSignal(object)
    raise_level = pyqtSignal(object)
    lower_level = pyqtSignal(object)

    def __init__(self, parent, size, title, max_count=1):
        super().__init__(parent)
        self.app = TFApplication.instance()

        self.setObjectName("TFDraggableWindow")
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setFixedSize(*size)
        self.size = size
        self.display_title = title
        self.max_count = max_count
        self.last_moved_time = 0

        self.title_label = QLabel(self.display_title, self)
        self.title_label.move(10, 5)
        font = QFont("Open Sans", 11)
        self.title_label.setFont(font)

        self._init_buttons()
    
        self.initialize_window()

        self._dragging = False
        self._offset = QPoint()

    def initialize_window(self):
        """
        Initialize window content and layout.
        
        This method must be implemented by subclasses to set up their specific
        window content and layout.

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
        """
        raise NotImplementedError("Subclasses must implement initialize_window()")

    def _init_buttons(self):
        self.close_button = TFCloseButton(parent=self, position=(self.size[0] - 25, 5))
        self.menu_button = TFMenuButton(parent=self, position=(self.size[0] - 50, 5))

    def rename(self, name: str) -> None:
        self.display_title = name

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press events for window dragging.
        
        Initiates dragging on left button press and brings window to front.

        Args:
            event (QMouseEvent): Mouse event object.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._offset = event.position().toPoint()
            self.parent().bring_window_to_front(self)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse move events for window dragging.
        
        Manages window movement with edge snapping to other windows.
        Constrains movement within parent container bounds.

        Args:
            event (QMouseEvent): Mouse event object.
        """
        if self._dragging:
            current_pos = event.position().toPoint()
            delta = current_pos - self._offset
            new_pos = self.pos() + delta

            container = self.parent()
            if container:
                min_x = 0
                min_y = 0
                
                new_x = max(min_x, new_pos.x())
                new_y = max(min_y, new_pos.y())
                
                for window in container.windows:
                    if window != self:
                        if abs(new_y - window.y()) < 10:
                            new_y = window.y()
                        elif abs((new_y + self.height()) - window.y()) < 10:
                            new_y = window.y() - self.height()
                        elif abs(new_y - (window.y() + window.height())) < 10:
                            new_y = window.y() + window.height()
                            
                        if (new_y < window.y() + window.height() and 
                            new_y + self.height() > window.y()):
                            if abs(new_x - (window.x() + window.width())) < 10:
                                new_x = window.x() + window.width()
                            elif abs((new_x + self.width()) - window.x()) < 10:
                                new_x = window.x() - self.width()
                
                self.move(new_x, new_y)
                self.moved.emit()
                
                container.resize_container()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse release events.
        
        Ends dragging operation and records movement timestamp.

        Args:
            event (QMouseEvent): Mouse event object.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.last_moved_time = time()
            self.mouse_released.emit()
