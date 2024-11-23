from time import time
from PyQt6.QtWidgets import QFrame, QLabel, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QMouseEvent, QFont
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from ui.components.tf_animated_button import TFAnimatedButton
from utils.registry.tf_tool_matadata import TFToolMetadata
from ui.tf_application import TFApplication
from ui.components.tf_settings_widget import TFCloseButton, TFMenuButton, TFIconButton
from utils.helper import resource_path
from ui.components.tf_font import Merriweather

CONTENT_PADDING_LEFT = 10
CONTENT_PADDING_TOP = 30
CONTENT_PADDING_RIGHT = 10
CONTENT_PADDING_BOTTOM = 10

SNAP_THRESHOLD = 10

class TFDraggableWindow(QFrame):
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
        self.setFixedSize(*self.metadata.window_size)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self._create_title_bar(main_layout)

        self._content_container = QWidget(self)
        self._content_container.setObjectName("contentContainer")
        main_layout.addWidget(self._content_container)

        self.initialize_window()

    def _create_title_bar(self, main_layout):
        title_bar = QWidget(self)
        title_bar.setFixedHeight(40)
        title_bar.setObjectName("titleBar")

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 12, 15, 5)
        title_layout.setSpacing(0)

        self._title_label = QLabel(self.metadata.window_title, title_bar)
        self._title_label.setFont(Merriweather)
        self._title_label.setObjectName("titleLabel")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        title_layout.addWidget(self._title_label, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        title_layout.addStretch()

        self._init_buttons(title_layout)

        main_layout.addWidget(title_bar)

    def _init_buttons(self, layout):
        self._close_button = TFAnimatedButton(
            icon_name="close",
            tooltip="Close window",
            size=20 ,
            parent=self
        )
        self._close_button.clicked_signal.connect(self.close_window)
        layout.addWidget(self._close_button, alignment=Qt.AlignmentFlag.AlignVCenter)

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

    def close_window(self):
        self.closed.emit(self)
