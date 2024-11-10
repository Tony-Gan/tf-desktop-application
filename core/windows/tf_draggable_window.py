from time import time
from PyQt6.QtWidgets import QFrame, QLabel, QWidget
from PyQt6.QtGui import QMouseEvent, QFont
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from utils.registry.tf_tool_matadata import TFToolMetadata
from ui.tf_application import TFApplication
from ui.components.tf_settings_widget import TFCloseButton, TFMenuButton, TFIconButton
from utils.helper import resource_path

# Window appearance constants
TITLE_FONT_FAMILY = "Open Sans"
TITLE_FONT_SIZE = 11
TITLE_X_OFFSET = 10
TITLE_Y_OFFSET = 5

# Content layout constants
CONTENT_PADDING_LEFT = 10
CONTENT_PADDING_TOP = 30
CONTENT_PADDING_RIGHT = 10
CONTENT_PADDING_BOTTOM = 10

# Window snapping constant
SNAP_THRESHOLD = 10

class TFDraggableWindow(QFrame):
    """A draggable window frame that can be moved within its parent container.

    This base class provides draggable window functionality with snapping to edges,
    window management signals, and basic window controls. It serves as the base for
    all draggable tool windows in the application.

    Class Attributes:
        metadata (Optional[TFToolMetadata]): 
            Required tool metadata that must be defined by subclasses. Contains window 
            configuration like size and title.

    Signals:
        moved: 
            Emitted when the window is moved.
        mouse_released: 
            Emitted when the mouse button is released.
        closed:  
            Emitted when the window is closed. Passes window object.
        bring_to_front: 
            Emitted to request window be brought to front. Passes window object.
        send_to_back: 
            Emitted to request window be sent to back. Passes window object.
        raise_level: 
            Emitted to request window be raised one level. Passes window object.
        lower_level: 
            Emitted to request window be lowered one level. Passes window object.

    Args:
        parent (QWidget): Parent widget containing this window.

    Raises:
        ValueError: If the subclass has not defined the required metadata attribute.

    Attributes:
        app (TFApplication): Reference to the main application instance.
        title_label (QLabel): Label displaying the window title.
        close_button (TFCloseButton): Button to close the window.
        menu_button (TFMenuButton): Button for accessing the window menu.
        last_moved_time (float): Timestamp of the last window movement.

    Implementation Notes:
        For customized developer - Inheritance this class for developing, you don't need to
        modify other part of the project.

    Example:
        >>> class MyToolWindow(TFDraggableWindow):
        ...     metadata = TFToolMetadata(
        ...         window_title="My Tool",
        ...         window_size=(400, 300)
        ...     )
        ...     
        ...     def initialize_window(self):
        ...         # Add custom widgets and layout
        ...         pass
        ... 

    Note:
        All tool windows must define a class-level `metadata` attribute of type
        `TFToolMetadata` that specifies the window configuration. Tool classes are
        automatically registered with the `TFToolRegistry` when defined.
    """

    moved = pyqtSignal()
    mouse_released = pyqtSignal()
    closed = pyqtSignal(object)

    metadata: TFToolMetadata

    def __init__(self, parent):
        if self.metadata is None:
            raise ValueError(f"Tool class {self.__class__.__name__} must define metadata")

        super().__init__(parent)

        # Initialize member variables
        self._dragging = False
        self._offset = QPoint()
        self._is_focused = False
        self.setProperty("focused", False)
        self.last_moved_time = 0
        self.app = TFApplication.instance()

        # Setup window frame
        self.setObjectName("TFDraggableWindow")
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setFixedSize(*self.metadata.window_size)

        # Create title label
        self._title_label = QLabel(self.metadata.window_title, self)
        self._title_label.move(TITLE_X_OFFSET, TITLE_Y_OFFSET)
        self._title_label.setFixedWidth(self.width())
        font = QFont(TITLE_FONT_FAMILY, TITLE_FONT_SIZE)
        self._title_label.setFont(font)

        # Initialize buttons
        self._init_buttons()

        # Create content container
        self._content_container = QWidget(self)
        container_width = (self.metadata.window_size[0] - CONTENT_PADDING_LEFT - CONTENT_PADDING_RIGHT)
        container_height = (self.metadata.window_size[1] - CONTENT_PADDING_TOP - CONTENT_PADDING_BOTTOM)
        self._content_container.setGeometry(
            CONTENT_PADDING_LEFT,
            CONTENT_PADDING_TOP,
            container_width,
            container_height
        )

        # Initialize window content
        self.initialize_window()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.metadata is not None:
            from utils.registry.tf_tool_registry import TFToolRegistry
            TFToolRegistry.register(cls)

    @property
    def content_container(self) -> QWidget:
        return self._content_container

    @property
    def close_button(self) -> TFCloseButton:
        return self._close_button

    @property
    def menu_button(self) -> TFMenuButton:
        return self._menu_button

    @property
    def is_dragging(self) -> bool:
        return self._dragging

    @property
    def title(self) -> str:
        return self._title_label.text()

    @title.setter
    def title(self, value: str) -> None:
        self._title_label.setText(value)

    @property
    def focused(self) -> bool:
        return self._focused

    @focused.setter
    def focused(self, value: bool):
        self._focused = value
        self.setProperty("focused", value)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

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
        width = self.metadata.window_size[0]
        hover_style = """
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }
        """
        self._close_button = TFCloseButton(
            parent=self,
            position=(width - 25, TITLE_Y_OFFSET),
            tooltip="Close window",
            hover_style=hover_style
        )
        
        self._menu_button = TFMenuButton(
            parent=self,
            position=(width - 50, TITLE_Y_OFFSET),
            tooltip="Open menu",
            hover_style=hover_style
        )
        
        self._tooltip_button = TFIconButton(
            parent=self,
            icon_path=resource_path('resources/images/icons/tooltips.png'),
            position=(width - 75, TITLE_Y_OFFSET),
            tooltip=self.get_tooltip_hover_text(),
            hover_style=hover_style
        )

    def get_tooltip_hover_text(self) -> str:
        return "You forgot to override this method"

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press events for window dragging.
        
        Initiates dragging on left button press and brings window to front.

        Args:
            event (QMouseEvent): Mouse event object.
        """
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            self.parent().set_focused_window(self)
            
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
                        if abs(new_y - window.y()) < SNAP_THRESHOLD:
                            new_y = window.y()
                        elif abs((new_y + self.height()) - window.y()) < SNAP_THRESHOLD:
                            new_y = window.y() - self.height()
                        elif abs(new_y - (window.y() + window.height())) < SNAP_THRESHOLD:
                            new_y = window.y() + window.height()

                        if (new_y < window.y() + window.height() and
                                new_y + self.height() > window.y()):
                            if abs(new_x - (window.x() + window.width())) < SNAP_THRESHOLD:
                                new_x = window.x() + window.width()
                            elif abs((new_x + self.width()) - window.x()) < SNAP_THRESHOLD:
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
