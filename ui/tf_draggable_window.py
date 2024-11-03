from PyQt6.QtWidgets import QFrame, QPushButton, QMenu, QLabel
from PyQt6.QtGui import QMouseEvent, QAction, QIcon, QFont
from PyQt6.QtCore import Qt, QPoint, pyqtSignal

from time import time

from tools.tf_message_bar import TFMessageBar
from database.tf_database import TFDatabase

class TFDraggableWindow(QFrame):
    """
    An abstract base class for creating draggable window widgets with title bar, close button, and customizable menu.

    This class provides the base implementation for draggable window frames that can be moved around their parent widget.
    It includes a title bar, close button, and a customizable menu system. This class should not be instantiated directly;
    instead, create a subclass to implement specific window functionality.

    Args:
        parent (QWidget, optional): The parent widget. Defaults to None.
        size (tuple[int, int], optional): Window size as (width, height). Defaults to (200, 150).
        title (str, optional): Window title text. Defaults to "Default Window".
        max_count (int, optional): Maximum number of instances allowed. Defaults to 1.
        message_bar (TFMessageBar, optional): Message bar for displaying temporary notifications. Defaults to None.

    Signals:
        moved: Emitted when the window is moved.\n
        mouse_released: Emitted when the mouse button is released after dragging.\n
        closed: Emitted when the window is closed, passes the window instance.\n
        bring_to_front: Emit when the window is asking bring it to front.\n
        send_to_back: Emit when the window is asking send it to back.\n
        raise_level: Emit when the window is asking raising level.\n
        lower_level: Emit when the window is asking lowering level.\n

    Example:
        >>> class MyCustomWindow(TFDraggableWindow):
        ...     def __init__(self, parent=None):
        ...         super().__init__(parent, size=(300, 200), title="My Custom Window")
        ...         # Add custom widgets and functionality
        ...         self.add_menu_action("Custom Action", self.my_custom_action)
        ...     
        ...     def my_custom_action(self):
        ...         # Implement custom functionality
        ...         pass
        ...
        >>> custom_window = MyCustomWindow(parent=main_window)
        >>> custom_window.show()

    Attributes:
        size (tuple[int, int]): Current window size.
        display_title (str): Current window title.
        max_count (int): Maximum allowed instances.
        message_bar (TFMessageBar): Associated message bar for temporary notifications.
        last_moved_time (float): Timestamp of last movement.
    """

    moved = pyqtSignal()
    mouse_released = pyqtSignal()
    closed = pyqtSignal(object)
    bring_to_front = pyqtSignal(object)
    send_to_back = pyqtSignal(object)
    raise_level = pyqtSignal(object)
    lower_level = pyqtSignal(object)

    def __init__(self, parent=None, size=(200, 150), title="Default Window", max_count=1, message_bar: TFMessageBar=None, database: TFDatabase=None):
        super().__init__(parent)

        self.setObjectName("TFDraggableWindow")
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setFixedSize(*size)
        self.size = size
        self.display_title = title
        self.max_count = max_count
        self.message_bar = message_bar
        self.database = database
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
    
        self.initialize_window()

        self.dragging = False
        self.offset = QPoint()

    def initialize_window(self):
        """
        Initialize the window content and setup.
        
        This method must be implemented by subclasses to set up their specific
        window content, widgets, and any additional initialization.
        
        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement initialize_window()")

    def init_default_actions(self):
        bring_to_front_action = QAction("Bring to Front", self)
        bring_to_front_action.triggered.connect(lambda: self.bring_to_front.emit(self))
        
        raise_one_level_action = QAction("Raise One Level", self)
        raise_one_level_action.triggered.connect(lambda: self.raise_level.emit(self))
        
        lower_one_level_action = QAction("Lower One Level", self)
        lower_one_level_action.triggered.connect(lambda: self.lower_level.emit(self))
        
        send_to_back_action = QAction("Send to Back", self)
        send_to_back_action.triggered.connect(lambda: self.send_to_back.emit(self))
        
        close_action = QAction("Close Window", self)
        close_action.triggered.connect(self.request_close)
        
        self.menu.addAction(bring_to_front_action)
        self.menu.addAction(raise_one_level_action)
        self.menu.addAction(lower_one_level_action)
        self.menu.addAction(send_to_back_action)
        self.menu.addSeparator()
        self.menu.addAction(close_action)
        
        self.menu_button.clicked.connect(self.show_menu)

    def add_menu_action(self, text, callback):
        """
        Add a custom action to the window's menu.

        Args:
            text (str): Display text for the menu item.
            callback (callable): Function to be called when the menu item is selected.
        """
        action = QAction(text, self)
        action.triggered.connect(callback)
        self.menu.addAction(action)

    def show_menu(self):
        """Display the window's menu at the current menu button position."""
        self.menu.exec(self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft()))

    def request_close(self):
        """
        Handle window close request.

        Emits the closed signal and hides the window.
        """
        self.closed.emit(self)
        self.hide()


    def rename(self, name: str) -> None:
        """
        Rename the window.

        Args:
            name (str): New title for the window.
        """
        self.display_title = name

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press events for initiating window dragging.

        This method is called when a mouse button is pressed on the window. It initiates
        the dragging operation when the left mouse button is pressed by recording the
        initial click position relative to the window.

        Args:
            event (QMouseEvent): The mouse event containing button and position information.
                            Only left button clicks are processed for dragging.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.position().toPoint()
            
            self.parent().bring_window_to_front(self)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse move events for window dragging.

        This method is called when the mouse is moved while a button is pressed. If dragging
        is active (initiated by mousePressEvent), it calculates the new window position based
        on the mouse movement delta and updates the window position. The window movement is
        constrained to stay within the parent widget's boundaries.

        Args:
            event (QMouseEvent): The mouse event containing the current cursor position.
                            Used to calculate movement delta from the initial press position.
        
        Note:
            The window position is constrained to prevent moving outside the parent widget's
            boundaries by enforcing minimum x and y coordinates of 0.
        """
        if self.dragging:
            current_pos = event.position().toPoint()
            delta = current_pos - self.offset
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
        """Handle mouse release events for completing window dragging.

        This method is called when a mouse button is released. If it was a left button release
        during an active drag operation, it finalizes the drag operation, updates the last
        moved timestamp, and emits the mouse_released signal.

        Args:
            event (QMouseEvent): The mouse event containing button information.
                            Only left button releases are processed.

        Note:
            Updates last_moved_time with the current timestamp which can be used to track
            the most recent window movement.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.last_moved_time = time()
            self.mouse_released.emit()

