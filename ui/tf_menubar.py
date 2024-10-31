from PyQt6.QtWidgets import QMenuBar, QMenu, QMainWindow, QScrollArea
from PyQt6.QtGui import QAction

from ui.tf_frames_impl.tf_calculator import TFCalculator
from ui.tf_frames_impl.tf_scientific_calculator import TFScientificCalculator
from ui.tf_frames_impl.tf_currency_converter import TFCurrencyConverter
from utils.helper import resource_path
from .tf_window_container import TFWindowContainer

class TFMenuBar(QMenuBar):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.main_window = parent
        self.current_mode = 'light'

        scroll_area = self.main_window.centralWidget()
        if isinstance(scroll_area, QScrollArea):
            self.window_container = scroll_area.widget()
        
    def init_file_menu(self):
        file_menu = QMenu("File", self)
        
        add_calc_action = file_menu.addAction("Add Calculator")
        add_calc_action.triggered.connect(self._add_calc_window)
        
        add_adv_calc_action = file_menu.addAction("Add Advanced Calculator")
        add_adv_calc_action.triggered.connect(self._add_adv_calc_window)

        add_currency_converter = file_menu.addAction("Add Currency Converter")
        add_currency_converter.triggered.connect(self._add_currency_converter)
        
        self.addMenu(file_menu)

    def init_theme_menu(self):
        theme_menu = QMenu("Theme", self)
        toggle_theme_action = QAction("Toggle Light/Dark Mode", self)
        toggle_theme_action.triggered.connect(self._toggle_theme)
        theme_menu.addAction(toggle_theme_action)
        self.addMenu(theme_menu)

    def _toggle_theme(self):
        self.current_mode = 'dark' if self.current_mode == 'light' else 'light'
        self._apply_stylesheet()
    
    def _apply_stylesheet(self):
        style_file = "styles/styles_light.qss" if self.current_mode == 'light' else "styles/styles_dark.qss"
        with open(resource_path(style_file), "r") as f:
            self.main_window.setStyleSheet(f.read())
        
    def _add_calc_window(self):
        if isinstance(self.window_container, TFWindowContainer):
            self.window_container.add_window(window_class=TFCalculator)
        
    def _add_adv_calc_window(self):
        if isinstance(self.window_container, TFWindowContainer):
            self.window_container.add_window(window_class=TFScientificCalculator)

    def _add_currency_converter(self):
        if isinstance(self.window_container, TFWindowContainer):
            self.window_container.add_window(window_class=TFCurrencyConverter)
