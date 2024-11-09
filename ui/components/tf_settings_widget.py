from enum import Enum
from typing import Optional, Callable, Tuple, List, Dict

from PyQt6.QtWidgets import QPushButton, QMenu
from PyQt6.QtGui import QIcon, QAction

from settings.general import ICON_BUTTON_SIZE

class TFIconButton(QPushButton):
    """
    A base class for icon-based buttons with fixed size and position.

    Args:
        parent (QWidget): Parent widget.
        icon_path (str): Path to the icon image.
        position (Tuple[int, int]): Button position (x, y).
        on_click (Optional[Callable]): Callback function for click event.
        size (Optional[Tuple[int, int]], optional): Button size (width, height). 
            Defaults to ICON_BUTTON_SIZE (20, 20).
    """
    def __init__(
        self,
        parent,
        icon_path: str,
        position: Tuple[int, int],
        on_click: Optional[Callable],
        size: Optional[Tuple[int, int]] = None,
    ):
        super().__init__(parent)

        self.setFixedSize(*(size or ICON_BUTTON_SIZE))
        self.move(*position)
        self.setIcon(QIcon(icon_path))
        self.clicked.connect(on_click)

class TFCloseButton(TFIconButton):
    """
    A specialized button for closing windows or panels.

    Args:
        parent (QWidget): Parent widget to be closed.
        position (Tuple[int, int], optional): Button position (x, y).

    Example:
        >>> close_btn = TFCloseButton(
        ...     parent=window,
        ...     position=(380, 5)
        ... )
    """
    def __init__(
        self,
        parent,
        position: Tuple[int, int] = None
    ):
        super().__init__(
            parent=parent,
            icon_path="resources/images/icons/close.png",
            position=position,
            on_click=self.on_click
        )
        self.parent = parent
        self.setObjectName("close_button")

    def on_click(self):
        self.parent.close()

class MenuSection(Enum):
    """
    Enumeration of menu sections for organizing actions.

    Attributes:
        WINDOW_CONTROL: Section for window positioning controls.
        CUSTOM: Section for custom user-added actions.
        WINDOW_MANAGEMENT: Section for window management actions like close.
    """
    WINDOW_CONTROL = 1
    CUSTOM = 2
    WINDOW_MANAGEMENT = 3

class TFMenuButton(TFIconButton):
    """
    A button that displays a configurable menu when clicked.

    Provides a hierarchical menu system with sections for window control,
    custom actions, and window management.

    Args:
        parent (QWidget): Parent widget.
        position (Tuple[int, int], optional): Button position (x, y).

    Example:
        >>> menu_btn = TFMenuButton(parent=window, position=(355, 5))
        >>> menu_btn.add_action(
        ...     text="Custom Action",
        ...     callback=lambda: print("Custom action"),
        ...     section=MenuSection.CUSTOM
        ... )

    Attributes:
        actions (Dict[MenuSection, List[QAction]]): Actions organized by menu section.
    """
    def __init__(self, parent, position: Tuple[int, int] = None, skip_default: bool = False):
        super().__init__(
            parent=parent,
            icon_path="resources/images/icons/settings.png",
            position=position,
            on_click=self.on_click
        )
        self.parent = parent
        self.skip_default = skip_default
        self.setObjectName("menu_button")
        self.menu = QMenu(self.parent)

        self.actions: Dict[MenuSection, List[QAction]] = {
            section: [] for section in MenuSection
        }
        
        self.rebuild_menu()

    def on_click(self):
        if hasattr(self.parent, 'parent') and hasattr(self.parent.parent(), 'set_focused_window'):
            self.parent.parent().set_focused_window(self.parent)
        elif hasattr(self.parent, 'set_focused'):
            self.parent.set_focused(True)

        self.rebuild_menu()
        self.menu.exec(self.mapToGlobal(self.rect().bottomLeft()))

    def add_action(self, text: str, callback: Callable, section: MenuSection = MenuSection.CUSTOM, 
                index: int = -1, checkable: bool = False, checked: bool = False,
                icon_path: str = None) -> QAction:
        """
        Add a new action to the menu.

        Args:
            text (str): Action text label.
            callback (Callable): Function to call when action triggered.
            section (MenuSection, optional): Menu section. Defaults to CUSTOM.
            index (int, optional): Position in section. Defaults to -1 (append).
            checkable (bool, optional): Whether the action can be toggled. Defaults to False.
            checked (bool, optional): Initial checked state if checkable. Defaults to False.
            icon_path (str, optional): Path to the icon image. Defaults to None.
        """
        action = QAction(text, self.parent)
        action.triggered.connect(callback)
        
        if checkable:
            action.setCheckable(True)
            action.setChecked(checked)
        
        if icon_path:
            action.setIcon(QIcon(icon_path))
        
        if index == -1 or index >= len(self.actions[section]):
            self.actions[section].append(action)
        else:
            self.actions[section].insert(index, action)
            
        self.rebuild_menu()
        return action

    def remove_action(self, text: str, section: Optional[MenuSection] = None):
        """
        Remove an action from the menu.

        Args:
            text (str): Text of action to remove.
            section (Optional[MenuSection], optional): Section to search in. 
                If None, searches all sections.
        """
        sections = [section] if section else list(MenuSection)
        
        for sect in sections:
            for action in self.actions[sect]:
                if action.text() == text:
                    self.actions[sect].remove(action)
                    self.rebuild_menu()
                    return
                
    def clear_section(self, section: MenuSection):
        """
        Remove all actions from a specific section.

        Args:
            section (MenuSection): Section to clear.
        """
        self.actions[section].clear()
        self.rebuild_menu()

    def move_action(self, text: str, new_section: MenuSection, new_index: int = -1):
        """
        Move an action to a different section.

        Args:
            text (str): Text of action to move.
            new_section (MenuSection): Destination section.
            new_index (int, optional): Position in new section. Defaults to -1 (append).
        """
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
        """
        Rebuild the menu structure with current actions.
        
        Clears and reconstructs menu with actions in proper sections,
        separated by dividers where appropriate.
        """
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
