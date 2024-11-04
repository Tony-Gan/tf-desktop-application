from PyQt6.QtWidgets import QMenuBar, QMenu, QMainWindow, QScrollArea, QWidget, QSplitter
from PyQt6.QtGui import QAction

from ui.tf_frames_impl.tf_calculator import TFCalculator
from ui.tf_frames_impl.tf_scientific_calculator import TFScientificCalculator
from ui.tf_frames_impl.tf_currency_converter import TFCurrencyConverter
from ui.tf_frames_impl.tf_coin_fliper import TFCoinFliper
from ui.tf_window_container import TFWindowContainer
from tools.tf_application import TFApplication
from database.models import TFSystemState
from utils.helper import resource_path
from settings.general import THEME_COLOURS

class TFMenuBar(QMenuBar):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.parent = parent
        self.app = TFApplication.instance()
        self.window_container = None
        
        central_widget = self.parent.centralWidget()
        if isinstance(central_widget, QWidget):
            splitter = central_widget.findChild(QSplitter)
            if splitter:
                scroll_area = splitter.widget(0)
                if isinstance(scroll_area, QScrollArea):
                    self.window_container = scroll_area.widget()
        
        self.current_mode = 'dark' if self.get_theme_mode() else 'light'
        
        self._apply_stylesheet()
        
    def init_file_menu(self):
        file_menu = QMenu(self.tr("File"), self)
        
        add_calc_action = file_menu.addAction(self.tr("Add Calculator"))
        add_calc_action.triggered.connect(self._add_calc_window)
        
        add_adv_calc_action = file_menu.addAction(self.tr("Add Advanced Calculator"))
        add_adv_calc_action.triggered.connect(self._add_adv_calc_window)

        add_currency_converter = file_menu.addAction(self.tr("Add Currency Converter"))
        add_currency_converter.triggered.connect(self._add_currency_converter)

        add_coin_flipper = file_menu.addAction(self.tr("Add Coin Flipper"))
        add_coin_flipper.triggered.connect(self._add_coin_flipper)
        
        self.addMenu(file_menu)

    def init_view_menu(self):
        view_menu = QMenu(self.tr("View"), self)
        
        toggle_output_action = view_menu.addAction(self.tr("Toggle Output Panel"))
        toggle_output_action.triggered.connect(self.parent.toggle_output_panel)
        
        self.addMenu(view_menu)    

    def init_theme_menu(self):
        theme_menu = QMenu(self.tr("Theme"), self)
        self.toggle_theme_action = QAction(self.tr("Toggle Light/Dark Mode"), self)
        self.toggle_theme_action.triggered.connect(self._toggle_theme)
        
        self.toggle_theme_action.setCheckable(True)
        self.toggle_theme_action.setChecked(self.current_mode == 'dark')
        
        theme_menu.addAction(self.toggle_theme_action)
        self.addMenu(theme_menu)

    def init_language_menu(self):
        language_menu = QMenu(self.tr("Language"), self)
        
        languages = {
            self.tr("English"): "en_US.qm",
            self.tr("Chinese"): "zh_CN.qm"
        }

        for language_name, qm_file in languages.items():
            action = QAction(language_name, self)
            action.triggered.connect(lambda _, q=qm_file: self._switch_language(q))
            language_menu.addAction(action)
        
        self.addMenu(language_menu)

    def _switch_language(self, qm_file):
        self.app.translator.load(resource_path(f"translations/{qm_file}"))
        self.app.installTranslator(self.app.translator)

        self.clear()
        self.init_file_menu()
        self.init_view_menu()
        self.init_theme_menu()
        self.init_language_menu()

    def _toggle_theme(self):
        self.current_mode = 'dark' if self.current_mode == 'light' else 'light'
        self.set_theme_mode(self.current_mode == 'dark')
        self._apply_stylesheet()
        self.toggle_theme_action.setChecked(self.current_mode == 'dark')
    
    def _apply_stylesheet(self):
        with open(resource_path("styles/styles.qss"), "r", encoding='utf-8') as f:
            base_stylesheet = f.read()
        
        colours = THEME_COLOURS[self.current_mode]
        
        replacements = {
            'background-color: white;': f'background-color: {colours["background-primary"]};',
            'background-color: #f0f0f0;': f'background-color: {colours["background-secondary"]};',
            'background-color: #e0e0e0;': f'background-color: {colours["background-secondary-hover"]};',
            'border: 1px solid #ccc;': f'border: 1px solid {colours["border-color-dark"]};',
            'border: 1px solid #ddd;': f'border: 1px solid {colours["border-color"]};',
            'color: black;': f'color: {colours["text-primary"]};',
            'color: gray;': f'color: {colours["text-secondary"]};',
            'background-color: #ffd700;': f'background-color: {colours["button-operator"]};',
            'background-color: #ffcd00;': f'background-color: {colours["button-operator-hover"]};',
            'border: 1px solid #daa520;': f'border: 1px solid {colours["button-operator-border"]};',
            'background-color: #ff6b6b;': f'background-color: {colours["button-special"]};',
            'background-color: #ff5252;': f'background-color: {colours["button-special-hover"]};',
            'border: 1px solid #ff5252;': f'border: 1px solid {colours["button-special-border"]};',
            'background-color: #4CAF50;': f'background-color: {colours["button-equal"]};',
            'background-color: #45a049;': f'background-color: {colours["button-equal-hover"]};',
            'border: 1px solid #45a049;': f'border: 1px solid {colours["button-equal-border"]};',
            'background-color: green;': f'background-color: {colours["message-success"]};',
        }

        stylesheet = base_stylesheet
        for old, new in replacements.items():
            stylesheet = stylesheet.replace(old, new)

        self.parent.setStyleSheet(stylesheet)
        
        self.parent.style().unpolish(self.parent)
        self.parent.style().polish(self.parent)
        
        for widget in self.parent.findChildren(QWidget):
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
        with self.app.database.get_session() as session:
            system_state = session.query(TFSystemState).first()
            return system_state.dark_mode if system_state else False
        
    def set_theme_mode(self, is_dark_mode: bool) -> None:
        with self.app.database.get_session() as session:
            system_state = session.query(TFSystemState).first()
            if system_state:
                system_state.dark_mode = is_dark_mode
            else:
                system_state = TFSystemState(dark_mode=is_dark_mode)
                session.add(system_state)
            session.commit()
