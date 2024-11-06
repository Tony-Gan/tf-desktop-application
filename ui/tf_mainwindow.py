from PyQt6.QtWidgets import QMainWindow, QScrollArea, QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from database.models import TFSystemState
from ui.tf_window_container import TFWindowContainer
from ui.tf_menubar import TFMenuBar
from ui.tf_application import TFApplication

class TFMainWindow(QMainWindow):
    """
    Main window class for the TF Desktop Application.
    
    This class provides the primary application window, managing the layout and coordination
    of various UI components including the menu bar, output panel, and window container.
    It handles window initialization, menu creation, and message/output management.

    Example:
        >>> # Creating the main window
        >>> main_window = TFMainWindow()
        >>> main_window.show()
        >>> 
        >>> # Displaying messages and output
        >>> main_window.show_message("Operation successful")
        >>> main_window.display_output("Processing results...")

    Attributes:
        app (TFApplication): Reference to the main application instance.
        window_container (TFWindowContainer): Container managing draggable sub-windows.
        menu_bar (TFMenuBar): Application's main menu bar.
    """
    def __init__(self):
        super().__init__()
        self.app = TFApplication.instance()
        self._init_ui()
        self._init_menubar()

    def _init_ui(self):
        """
        Initialize the main window's user interface.
        
        Sets up the window properties, creates the central widget, and organizes
        the layout including scroll areas, window container, and output panel.
        """
        self.setWindowTitle('TF Desktop Application')
        self.setWindowIcon(QIcon("static/images/icons/app.png"))

        with self.app.database.get_session() as session:
            system_state = session.query(TFSystemState).first()
            if system_state is not None:
                width = max(system_state.window_width, 600)
                height = max(system_state.window_height, 400)
                self.setGeometry(100, 100, width, height)
            else:
                self.setGeometry(100, 100, 1200, 960)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.window_container = TFWindowContainer(self)
        scroll_area.setWidget(self.window_container)

        self._splitter = QSplitter(Qt.Orientation.Vertical)
        self._splitter.addWidget(scroll_area)
        self.app.output_panel.setParent(self._splitter)
        self._splitter.addWidget(self.app.output_panel)
        self._splitter.setSizes([700, 260])
        
        main_layout.addWidget(self._splitter)
        self.setCentralWidget(central_widget)

    def _init_menubar(self):
        """
        Initialize the main window's menu bar.
        
        Creates and configures the main menu bar with file, theme, view, and language
        menus. Each menu is initialized through separate methods of the TFMenuBar class.
        """
        self.menu_bar = TFMenuBar(self)
        self.setMenuBar(self.menu_bar)

    def closeEvent(self, event):
        """
        Handle the window close event.
        
        Saves all window states and removes the translator before accepting
        the close event. Ensures proper cleanup of application resources.

        Args:
            event: Close event to be handled.
        """
        if hasattr(self, 'window_container'):
            self.window_container.save_all_window_states()

        self.app.removeTranslator(self.app.translator)
        
        event.accept()

    def resizeEvent(self, event):
        with self.app.database.get_session() as session:
            system_state = session.query(TFSystemState).first()
            if system_state is None:
                system_state = TFSystemState()
                session.add(system_state)

            system_state.window_width = self.width()
            system_state.window_height = self.height()
            session.commit()

        super().resizeEvent(event)
