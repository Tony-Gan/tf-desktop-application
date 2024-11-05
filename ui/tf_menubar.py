from PyQt6.QtWidgets import QMenuBar, QMenu, QMainWindow, QScrollArea, QWidget, QSplitter
from PyQt6.QtGui import QAction, QIcon

from ui.tf_application import TFApplication
from tools.tf_tool_registry import TFToolRegistry
from database.models import TFSystemState
from utils.helper import resource_path
from settings.general import THEME_COLOURS

class TFMenuBar(QMenuBar):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.parent = parent
        self.app = TFApplication.instance()
        self.window_container = None
        self._menus = {}
        
        central_widget = self.parent.centralWidget()
        if isinstance(central_widget, QWidget):
            splitter = central_widget.findChild(QSplitter)
            if splitter:
                scroll_area = splitter.widget(0)
                if isinstance(scroll_area, QScrollArea):
                    self.window_container = scroll_area.widget()
        
        # Load saved preferences
        self.current_mode = 'dark' if self._get_system_state('dark_mode', False) else 'light'
        self.current_language = self._get_system_state('language', 'en')
        
        # Apply saved language
        qm_file = 'zh_CN.qm' if self.current_language == 'zh' else 'en_US.qm'
        self.app.translator.load(resource_path(f"translations/{qm_file}"))
        self.app.installTranslator(self.app.translator)
        
        self._apply_stylesheet()

        self.init_menus()
        
    def init_menus(self):
        self._create_tool_menus()

        view_menu = self.get_or_create_menu("View")
        view_menu.addAction(
            self._create_action(
                "Toggle Output Panel",
                self.app.output_panel.toggle_panel
            )
        )

        theme_menu = self.get_or_create_menu("Theme")
        self.toggle_theme_action = self._create_action(
            "Toggle Light/Dark Mode",
            self._toggle_theme,
            checkable=True,
            checked=(self.current_mode == 'dark')
        )
        theme_menu.addAction(self.toggle_theme_action)

        language_menu = self.get_or_create_menu("Language")
        languages = {
            self.tr("English"): "en_US.qm",
            self.tr("Chinese"): "zh_CN.qm"
        }
        for language_name, qm_file in languages.items():
            language_menu.addAction(
                self._create_action(
                    language_name,
                    lambda q=qm_file: self._switch_language(q)
                )
            )

    def get_or_create_menu(self, menu_path: str) -> QMenu:
        path_parts = menu_path.split('/')
        current_menu = self
        current_path = ""
        
        for part in path_parts:
            current_path = f"{current_path}/{part}" if current_path else part
            if current_path not in self._menus:
                if isinstance(current_menu, QMenuBar):
                    new_menu = QMenu(self.tr(part), self)
                    current_menu.addMenu(new_menu)
                else:
                    new_menu = current_menu.addMenu(self.tr(part))
                self._menus[current_path] = new_menu
            current_menu = self._menus[current_path]
        
        return current_menu
    
    def _create_tool_menus(self):
        for tool_class in TFToolRegistry.get_tools().values():
            menu = self.get_or_create_menu(tool_class.metadata.menu_path)
            action = self._create_action(
                tool_class.metadata.menu_title,
                lambda checked=False, tc=tool_class: 
                    self.window_container.add_window(window_class=tc),
                tooltip=tool_class.metadata.description,
                icon_path=tool_class.metadata.icon_path
            )
            menu.addAction(action)

    def _create_action(self, text: str, slot, tooltip: str = None, icon_path: str = None, checkable: bool = False, checked: bool = False) -> QAction:
        action = QAction(self.tr(text), self)
        action.triggered.connect(slot)
        
        if tooltip:
            action.setStatusTip(tooltip)
        if icon_path:
            action.setIcon(QIcon(icon_path))
        if checkable:
            action.setCheckable(True)
            action.setChecked(checked)
            
        return action

    def _switch_language(self, qm_file):
        self.current_language = 'zh' if qm_file == 'zh_CN.qm' else 'en'
        self._set_system_state('language', self.current_language)
        
        self.app.translator.load(resource_path(f"translations/{qm_file}"))
        self.app.installTranslator(self.app.translator)
        
        self.clear()
        self._menus.clear()
        self.init_menus()

    def _toggle_theme(self):
        self.current_mode = 'dark' if self.current_mode == 'light' else 'light'
        self._set_system_state('dark_mode', self.current_mode == 'dark')
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

    def _get_system_state(self, attribute, default_value=None):
        with self.app.database.get_session() as session:
            system_state = session.query(TFSystemState).first()
            return getattr(system_state, attribute) if system_state else default_value

    def _set_system_state(self, attribute, value):
        with self.app.database.get_session() as session:
            system_state = session.query(TFSystemState).first()
            if system_state:
                setattr(system_state, attribute, value)
            else:
                system_state = TFSystemState()
                setattr(system_state, attribute, value)
                session.add(system_state)
            session.commit()
