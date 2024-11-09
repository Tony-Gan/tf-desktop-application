from PyQt6.QtWidgets import QMainWindow, QScrollArea, QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from core.database.models import TFSystemState
from ui.views.tf_window_container import TFWindowContainer
from ui.views.tf_menubar import TFMenuBar
from ui.tf_application import TFApplication
from utils.helper import resource_path

class TFMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = TFApplication.instance()
        
        self._create_central_widget()
        self._create_window_container()
        self._create_scroll_area()
        self._setup_layout()
        self._init_menubar()
        self._setup_window_properties()
        self._setup_output_panel()
    
    def _create_central_widget(self):
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)
        
    def _create_window_container(self):
        self.window_container = TFWindowContainer(self)
    
    def _create_scroll_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setMinimumSize(200, 200)
        
        self.scroll_area.setWidget(self.window_container)
        self.window_container.setParent(self.scroll_area)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def _setup_layout(self):
        self.main_layout.addWidget(self.scroll_area)

    def _init_menubar(self):
        self.menu_bar = TFMenuBar(self, self.window_container)
        self.setMenuBar(self.menu_bar)

    def _setup_window_properties(self):
        self.setWindowTitle('TF Desktop Application')
        self.setWindowIcon(QIcon(resource_path("resources/images/icons/app.png")))
        with self.app.database.get_session() as session:
            system_state = session.query(TFSystemState).first()
            if system_state is not None:
                width = max(system_state.window_width, 600)
                height = max(system_state.window_height, 400)
                self.setGeometry(100, 100, width, height)
            else:
                self.setGeometry(100, 100, 1200, 960)

    def _setup_output_panel(self):
        self.app.output_panel.setParent(self)
        self.app.output_panel.setFixedWidth(self.width())
        self.app.output_panel.move(0, self.height() - self.app.output_panel.height())
        self.app.output_panel.update_button_positions()

    def resizeEvent(self, event):
        self.app.output_panel.setFixedWidth(self.width())
        self.app.output_panel.move(0, self.height() - self.app.output_panel.height())
        self.app.output_panel.update_button_positions()

    def closeEvent(self, event):
        if hasattr(self, 'window_container'):
            self.window_container.save_all_window_states()

        with self.app.database.get_session() as session:
            state = session.query(TFSystemState).first()
            state.window_width = self.width()
            state.window_height = self.height()
            session.commit()
            
        self.app.removeTranslator(self.app.translator)
        event.accept()
