from PyQt6.QtWidgets import QMenuBar, QMenu, QMainWindow, QScrollArea, QWidget
from PyQt6.QtGui import QAction

from ui.tf_frames_impl.tf_calculator import TFCalculator
from ui.tf_frames_impl.tf_scientific_calculator import TFScientificCalculator
from ui.tf_frames_impl.tf_currency_converter import TFCurrencyConverter
from ui.tf_frames_impl.tf_coin_fliper import TFCoinFliper
from database.tf_database import TFDatabase
from database.models import TFSystemState
from utils.helper import resource_path
from .tf_window_container import TFWindowContainer

class TFMenuBar(QMenuBar):
    def __init__(self, parent: QMainWindow, database: TFDatabase):
        super().__init__(parent)
        self.main_window = parent
        self.database = database
        
        scroll_area = self.main_window.centralWidget()
        if isinstance(scroll_area, QScrollArea):
            self.window_container = scroll_area.widget()
        
        self.current_mode = 'dark' if self.get_theme_mode() else 'light'
        
        self._apply_stylesheet()
        
    def init_file_menu(self):
        file_menu = QMenu("File", self)
        
        add_calc_action = file_menu.addAction("Add Calculator")
        add_calc_action.triggered.connect(self._add_calc_window)
        
        add_adv_calc_action = file_menu.addAction("Add Advanced Calculator")
        add_adv_calc_action.triggered.connect(self._add_adv_calc_window)

        add_currency_converter = file_menu.addAction("Add Currency Converter")
        add_currency_converter.triggered.connect(self._add_currency_converter)

        add_coin_flipper = file_menu.addAction("Add Coin Flipper")
        add_coin_flipper.triggered.connect(self._add_coin_flipper)
        
        self.addMenu(file_menu)

    def init_theme_menu(self):
        theme_menu = QMenu("Theme", self)
        self.toggle_theme_action = QAction("Toggle Light/Dark Mode", self)
        self.toggle_theme_action.triggered.connect(self._toggle_theme)
        
        self.toggle_theme_action.setCheckable(True)
        self.toggle_theme_action.setChecked(self.current_mode == 'dark')
        
        theme_menu.addAction(self.toggle_theme_action)
        self.addMenu(theme_menu)

    def _toggle_theme(self):
        self.current_mode = 'dark' if self.current_mode == 'light' else 'light'
        self.set_theme_mode(self.current_mode == 'dark')
        self._apply_stylesheet()
        self.toggle_theme_action.setChecked(self.current_mode == 'dark')
    
    def _apply_stylesheet(self):
        style_file = "styles/styles_dark.qss" if self.current_mode == 'dark' else "styles/styles_light.qss"
        with open(resource_path(style_file), "r") as f:
            stylesheet = f.read()

        self.main_window.setStyleSheet(stylesheet)

        self.main_window.style().unpolish(self.main_window)
        self.main_window.style().polish(self.main_window)

        for widget in self.main_window.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()
        
    def _add_calc_window(self):
        if isinstance(self.window_container, TFWindowContainer):
            self.window_container.add_window(window_class=TFCalculator)
        
    def _add_adv_calc_window(self):
        if isinstance(self.window_container, TFWindowContainer):
            self.window_container.add_window(window_class=TFScientificCalculator)

    def _add_currency_converter(self):
        if isinstance(self.window_container, TFWindowContainer):
            self.window_container.add_window(window_class=TFCurrencyConverter)

    def _add_coin_flipper(self):
        if isinstance(self.window_container, TFWindowContainer):
            self.window_container.add_window(window_class=TFCoinFliper)

    def get_theme_mode(self) -> bool:
        with self.database.get_session() as session:
            system_state = session.query(TFSystemState).first()
            return system_state.dark_mode if system_state else False
        
    def set_theme_mode(self, is_dark_mode: bool) -> None:
        with self.database.get_session() as session:
            system_state = session.query(TFSystemState).first()
            if system_state:
                system_state.dark_mode = is_dark_mode
            else:
                system_state = TFSystemState(dark_mode=is_dark_mode)
                session.add(system_state)
            session.commit()
