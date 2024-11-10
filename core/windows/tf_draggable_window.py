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
    """
    A draggable window frame that can be moved within its parent container with snapping capabilities.

    This base class provides draggable window functionality with edge snapping, window management,
    focus handling, tooltips and window controls including close and menu buttons. It serves as the base for
    all draggable tool windows in the application and automatically registers tool implementations
    with the TFToolRegistry.

    Class Attributes:
        metadata (Optional[TFToolMetadata]): 
            Required tool metadata that must be defined by subclasses. Contains window 
            configuration like size and title.

    Signals:
        moved: 
            Emitted when the window is moved within its container.
        mouse_released: 
            Emitted when the mouse button is released after dragging.
        closed:  
            Emitted when the window is closed via the close button. Passes window object reference.

    Args:
        parent (QWidget): Parent widget containing this window.

    Raises:
        ValueError: If the subclass has not defined the required metadata attribute.

    Attributes:
        app (TFApplication): Reference to the main application instance.
        content_container (QWidget): Container widget for the window's content area.
        title (str): The window's title text, can be get/set.
        focused (bool): Window focus state, affects visual appearance when true.
        close_button (TFCloseButton): Button to close the window.
        menu_button (TFMenuButton): Button for accessing window options menu.
        is_dragging (bool): True when window is being dragged.
        last_moved_time (float): Timestamp of the last window movement.
    
    Implementation Notes:
        For customized developer - Inherit this class for developing new tool windows. You only need to:
        1. Define the required metadata class attribute
        2. Implement the initialize_window() method
        3. Override get_tooltip_hover_text() if needed

    Example:
        >>> class MyToolWindow(TFDraggableWindow):
        ...     metadata = TFToolMetadata(
        ...         window_title="My Tool",
        ...         window_size=(400, 300)
        ...     )
        ...     
        ...     def initialize_window(self):
        ...         # Add custom widgets and layout
        ...         layout = QVBoxLayout(self.content_container)
        ...         layout.addWidget(QLabel("My Tool Content"))
        ...     
        ...     def get_tooltip_hover_text(self):
        ...         return "This is my custom tool's tooltip"
        ... 

    Note:
        All tool windows must define a class-level `metadata` attribute of type
        `TFToolMetadata` that specifies the window configuration. Tool classes are
        automatically registered with the `TFToolRegistry` when defined.
        The window implements edge snapping behavior when dragged near other windows
        and constrains movement within the parent container bounds.
    """

    moved = pyqtSignal()
    mouse_released = pyqtSignal()
    closed = pyqtSignal(object)

    metadata: TFToolMetadata

    def __init__(self, parent):
        if self.metadata is None:
            raise ValueError(f"Tool class {self.__class__.__name__} must define metadata")

        super().__init__(parent)

        self._dragging = False
        self._offset = QPoint()
        self._is_focused = False
        self.setProperty("focused", False)
        self.last_moved_time = 0
        self.app = TFApplication.instance()

        self.setObjectName("TFDraggableWindow")
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setFixedSize(*self.metadata.window_size)

        self._title_label = QLabel(self.metadata.window_title, self)
        self._title_label.move(TITLE_X_OFFSET, TITLE_Y_OFFSET)
        self._title_label.setFixedWidth(self.width())
        font = QFont(TITLE_FONT_FAMILY, TITLE_FONT_SIZE)
        self._title_label.setFont(font)

        self._init_buttons()

        self._content_container = QWidget(self)
        container_width = (self.metadata.window_size[0] - CONTENT_PADDING_LEFT - CONTENT_PADDING_RIGHT)
        container_height = (self.metadata.window_size[1] - CONTENT_PADDING_TOP - CONTENT_PADDING_BOTTOM)
        self._content_container.setGeometry(
            CONTENT_PADDING_LEFT,
            CONTENT_PADDING_TOP,
            container_width,
            container_height
        )

        self.initialize_window()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.metadata is not None:
            from utils.registry.tf_tool_registry import TFToolRegistry
            TFToolRegistry.register(cls)

    @property
    def content_container(self) -> QWidget:
        """
        Get the container widget for window content.

        Returns:
            QWidget: The container widget where subclasses should add their content.
        """
        return self._content_container

    @property
    def close_button(self) -> TFCloseButton:
        """
        Get the window's close button.

        Returns:
            TFCloseButton: Button that emits closed signal when clicked.
        """
        return self._close_button

    @property
    def menu_button(self) -> TFMenuButton:
        """
        Get the window's menu button.

        Returns:
            TFMenuButton: Button that shows window options menu when clicked.
        """
        return self._menu_button

    @property
    def is_dragging(self) -> bool:
        """
        Check if window is currently being dragged.

        Returns:
            bool: True if window is being dragged, False otherwise.
        """
        return self._dragging

    @property
    def title(self) -> str:
        """
        Get window title text.

        Returns:
            str: Current window title.
        """
        return self._title_label.text()

    @title.setter
    def title(self, value: str) -> None:
        """
        Set window title text.

        Args:
            value (str): New window title to display.
        """
        self._title_label.setText(value)

    @property
    def focused(self) -> bool:
        """
        Get window focus state.

        Returns:
            bool: True if window has focus, False otherwise.
        """
        return self._focused

    @focused.setter
    def focused(self, value: bool):
        """
        Set window focus state.

        Updates visual style to indicate focus state.

        Args:
            value (bool): True to set window as focused, False otherwise.
        """
        self._focused = value
        self.setProperty("focused", value)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def initialize_window(self):
        """
        Initialize window content and layout.
        
        This method must be implemented by subclasses to set up their specific
        window content and layout. Content should be added to the content_container.

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
        """
        Get tooltip text shown when hovering over the tooltip button.
        
        Override this method in subclasses to provide custom tooltip text.

        Returns:
            str: Tooltip text to display.
        """
        return "You forgot to override this method"

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press events for window dragging and focus management.
        
        When left button is pressed, initiates window dragging and brings window to front.
        When either left or right button is pressed, sets this window as the focused window.

        Args:
            event (QMouseEvent): Mouse event object containing button and position information.

        Implementation Notes:
            - Left click: Initiates dragging and brings window to front
            - Right/Left click: Sets window focus
            - Dragging offset is calculated from click position
        """
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            self.parent().set_focused_window(self)
            
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._offset = event.position().toPoint()
            self.parent().bring_window_to_front(self)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse move events for window dragging with edge snapping.
        
        Manages window movement within parent container bounds and implements snapping
        behavior when dragged near other windows' edges. The window will snap to:
        - Vertical edges of other windows
        - Horizontal edges of other windows
        - Window tops and bottoms
        
        Args:
            event (QMouseEvent): Mouse event object containing the new cursor position.

        Implementation Notes:
            - Movement is constrained within parent container
            - Snapping occurs when within SNAP_THRESHOLD pixels of another window's edge
            - Both vertical and horizontal snapping can occur simultaneously
            - Emits moved signal when window position changes
            - Triggers parent container resize after movement
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
        Handle mouse release events for ending drag operations.
        
        Ends the dragging operation when left button is released and updates the
        timestamp of the last movement. Emits mouse_released signal.

        Args:
            event (QMouseEvent): Mouse event object containing the released button information.

        Notes:
            The last_moved_time is updated even if the window position didn't actually
            change during the drag operation.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.last_moved_time = time()
            self.mouse_released.emit()
