from PyQt6.QtWidgets import QMainWindow, QScrollArea, QWidget, QVBoxLayout, QSplitter, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from ui.tf_window_container import TFWindowContainer
from ui.tf_menubar import TFMenuBar
from ui.tf_output_panel import TFOutputPanel
from tools.tf_application import TFApplication

class TFMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = TFApplication.instance()
        self.init_ui()
        self.init_menubar()

    def init_ui(self):
        self.setWindowTitle('TF Desktop Application')
        self.setWindowIcon(QIcon("static/images/icons/app.png"))
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

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.addWidget(scroll_area)

        self.output_panel = TFOutputPanel(self)
        self.splitter.addWidget(self.output_panel)
        self.splitter.setSizes([700, 260])
        
        main_layout.addWidget(self.splitter)
        self.setCentralWidget(central_widget)

    def init_menubar(self):
        self.menu_bar = TFMenuBar(self, self.database, self.translator)
        self.menu_bar.init_file_menu()
        self.menu_bar.init_theme_menu()
        self.menu_bar.init_view_menu()
        self.menu_bar.init_language_menu()
        self.setMenuBar(self.menu_bar)

    def show_message(self, message: str, display_time=2000, colour='green'):
        self.app.show_message(message, display_time, colour)

    def display_output(self, text: str):
        if not self.output_panel.isVisible():
            self.output_panel.show()
        self.output_panel.display_output(text)

    def clear_output(self):
        self.output_panel.clear_output()

    def toggle_output_panel(self):
        self.output_panel.toggle_panel()

    def closeEvent(self, event):
        if hasattr(self, 'window_container'):
            self.window_container.save_all_window_states()

        QApplication.instance().removeTranslator(self.translator)
        
        event.accept()
