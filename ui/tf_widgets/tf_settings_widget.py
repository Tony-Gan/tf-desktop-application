from enum import Enum
from typing import Optional, Callable, Tuple, List, Dict

from PyQt6.QtWidgets import QPushButton, QMenu
from PyQt6.QtGui import QIcon, QAction

class TFIconButton(QPushButton):
    DEFAULT_SIZE = (20, 20)

    def __init__(
        self,
        parent,
        icon_path: str,
        position: Tuple[int, int],
        on_click: Optional[Callable],
        size: Optional[Tuple[int, int]] = None,
    ):
        super().__init__(parent)

        self.setFixedSize(*(size or self.DEFAULT_SIZE))
        self.move(*position)
        self.setIcon(QIcon(icon_path))
        self.clicked.connect(on_click)

class TFCloseButton(TFIconButton):
    def __init__(
        self,
        parent,
        position: Tuple[int, int] = None
    ):
        super().__init__(
            parent=parent,
            icon_path="static/images/icons/close.png",
            position=position,
            on_click=self.on_click
        )
        self.parent = parent
        self.setObjectName("close_button")

    def on_click(self):
        self.parent.closed.emit(self.parent)
        self.parent.hide()

class MenuSection(Enum):
    WINDOW_CONTROL = 1
    CUSTOM = 2
    WINDOW_MANAGEMENT = 3

class TFMenuButton(TFIconButton):
    def __init__(
        self,
        parent,
        position: Tuple[int, int] = None
    ):
        super().__init__(
            parent=parent,
            icon_path="static/images/icons/settings.png",
            position=position,
            on_click=self.on_click
        )
        self.parent = parent
        self.setObjectName("menu_button")
        self.menu = QMenu(self.parent)

        self.actions: Dict[MenuSection, List[QAction]] = {
            section: [] for section in MenuSection
        }
        
        self.init_default_actions()
        self.rebuild_menu()

    def on_click(self):
        self.rebuild_menu()
        self.menu.exec(self.mapToGlobal(self.rect().bottomLeft()))

    def init_default_actions(self):
        window_controls = [
            ("Bring to Front", lambda: self.parent.bring_to_front.emit(self.parent)),
            ("Raise One Level", lambda: self.parent.raise_level.emit(self.parent)),
            ("Lower One Level", lambda: self.parent.lower_level.emit(self.parent)),
            ("Send to Back", lambda: self.parent.send_to_back.emit(self.parent))
        ]
        
        window_management = [
            ("Close Window", self.on_closed_click)
        ]

        for text, callback in window_controls:
            self.add_action(text, callback, MenuSection.WINDOW_CONTROL)

        for text, callback in window_management:
            self.add_action(text, callback, MenuSection.WINDOW_MANAGEMENT)

    def add_action(self, 
                  text: str, 
                  callback: Callable, 
                  section: MenuSection = MenuSection.CUSTOM,
                  index: int = -1):
        action = QAction(text, self.parent)
        action.triggered.connect(callback)
        
        if index == -1 or index >= len(self.actions[section]):
            self.actions[section].append(action)
        else:
            self.actions[section].insert(index, action)
            
        self.rebuild_menu()

    def remove_action(self, text: str, section: Optional[MenuSection] = None):
        sections = [section] if section else list(MenuSection)
        
        for sect in sections:
            for action in self.actions[sect]:
                if action.text() == text:
                    self.actions[sect].remove(action)
                    self.rebuild_menu()
                    return
                
    def clear_section(self, section: MenuSection):
        self.actions[section].clear()
        self.rebuild_menu()

    def move_action(self, 
                   text: str, 
                   new_section: MenuSection, 
                   new_index: int = -1):
        action_to_move = None
        for section in MenuSection:
            for action in self.actions[section]:
                if action.text() == text:
                    action_to_move = action
                    self.actions[section].remove(action)
                    break
            if action_to_move:
                break

        if action_to_move:
            if new_index == -1 or new_index >= len(self.actions[new_section]):
                self.actions[new_section].append(action_to_move)
            else:
                self.actions[new_section].insert(new_index, action_to_move)
            self.rebuild_menu()

    def rebuild_menu(self):
        self.menu.clear()
        
        for action in self.actions[MenuSection.WINDOW_CONTROL]:
            self.menu.addAction(action)
            
        if self.actions[MenuSection.CUSTOM]:
            self.menu.addSeparator()
            
        for action in self.actions[MenuSection.CUSTOM]:
            self.menu.addAction(action)
            
        if self.actions[MenuSection.WINDOW_MANAGEMENT]:
            self.menu.addSeparator()
            
        for action in self.actions[MenuSection.WINDOW_MANAGEMENT]:
            self.menu.addAction(action)

    def on_closed_click(self):
        self.parent.closed.emit(self.parent)
        self.parent.hide()
