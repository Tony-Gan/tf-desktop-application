from PyQt6.QtWidgets import QMainWindow, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from .tf_window_container import TFWindowContainer
from .tf_menubar import TFMenuBar
from tools.tf_message_bar import TFMessageBar

class TFMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_menubar()

    def init_ui(self):
        self.setWindowTitle('TF Desktop Application')
        self.setWindowIcon(QIcon("static/images/icons/app.png"))
        self.setGeometry(100, 100, 1200, 960)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.message_bar = TFMessageBar(self)
        self.window_container = TFWindowContainer(self, self.message_bar)
        
        scroll_area.setWidget(self.window_container)
        
        self.setCentralWidget(scroll_area)

    def init_menubar(self):
        self.menu_bar = TFMenuBar(self)
        self.menu_bar.init_file_menu()
        self.menu_bar.init_theme_menu()
        self.setMenuBar(self.menu_bar)

    def show_message(self, message: str, display_time=2000, colour='green'):
        self.message_bar.show_message(message, display_time, colour)
