import json

from PyQt6.QtWidgets import QVBoxLayout, QFileDialog
from PyQt6.QtCore import Qt, QStandardPaths
from PyQt6.QtGui import QKeySequence, QShortcut

from core.windows.tf_draggable_window import TFDraggableWindow
from ui.components.tf_animated_button import TFAnimatedButton
from ui.components.tf_tab_widget import TFTabWidget
from ui.tf_application import TFApplication
from utils.registry.tf_tool_matadata import TFToolMetadata
from implements.components.card1 import Card1
from implements.components.card2 import Card2
from implements.components.card3 import Card3
from implements.components.card4 import Card4
from implements.components.card5 import Card5


class TFPcCardV2(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="调查员角色卡v2",
        window_title="调查员角色卡v2",
        window_size=(400, 500),
        description="PC card",
        max_instances=6
    )

    def __init__(self, parent=None):
        self.edit_mode = False
        self.p_data = {}
        self._current_file_path = None
        super().__init__(parent)
        
        self.open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        self.open_shortcut.activated.connect(self._open_shortcut_handler)
        self.open_shortcut.setEnabled(False)

        self.edit_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.edit_shortcut.activated.connect(self._edit_shortcut_handler)
        self.edit_shortcut.setEnabled(False)

        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self._save_shortcut_handler)
        self.save_shortcut.setEnabled(False)
        
        self.parent().set_focused_window(self)

    def _open_shortcut_handler(self):
        if self.focused or len(self.parent().windows) == 1:
            self._load_character()

    def _edit_shortcut_handler(self):
        if self.focused or len(self.parent().windows) == 1:
            self._enable_edit()

    def _save_shortcut_handler(self):
        if self.focused or len(self.parent().windows) == 1 and self.edit_mode:
            self._enable_edit()
    
    @property
    def focused(self) -> bool:
        focused = super().focused
        self.open_shortcut.setEnabled(focused or len(self.parent().windows) == 1)
        self.edit_shortcut.setEnabled(focused or len(self.parent().windows) == 1)
        self.save_shortcut.setEnabled(focused or len(self.parent().windows) == 1)
        return focused

    @focused.setter
    def focused(self, value: bool):
        super(TFPcCardV2, self.__class__).focused.fset(self, value)
        self.open_shortcut.setEnabled(value or len(self.parent().windows) == 1)
        self.edit_shortcut.setEnabled(value or len(self.parent().windows) == 1)
        self.save_shortcut.setEnabled(value or len(self.parent().windows) == 1)

    def initialize_window(self):
        main_layout = QVBoxLayout(self.content_container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        navigation_bar = TFTabWidget(self)
        self.cards = []
        card1 = Card1(self)
        card2 = Card2(self)
        card3 = Card3(self)
        # card4 = Card4(self)
        # card5 = Card5(self)
        navigation_bar.addTab(card1, '基础属性')
        navigation_bar.addTab(card2, '技能列表')
        navigation_bar.addTab(card3, '物品列表')
        # navigation_bar.addTab(card4, '魔法/战技')
        # navigation_bar.addTab(card5, '其他')
        self.cards.append(card1)
        self.cards.append(card2)
        self.cards.append(card3)
        # self.cards.append(card4)
        # self.cards.append(card5)

        main_layout.addWidget(navigation_bar)

    def init_custom_menu_items(self, layout):
        self._load_character_button = TFAnimatedButton(
            icon_name="load",
            tooltip="加载角色(Ctrl+O)",
            size=20 ,
            parent=self
        )
        self._load_character_button.clicked_signal.connect(self._load_character)

        self._enable_edit_button = TFAnimatedButton(
            icon_name="edit",
            tooltip="编辑角色(Ctrl+F)",
            size=20 ,
            parent=self
        )
        self._enable_edit_button.clicked_signal.connect(self._enable_edit)

        layout.addWidget(self._load_character_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._enable_edit_button, alignment=Qt.AlignmentFlag.AlignVCenter)

    def _load_character(self):
        initial_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择角色卡文件",
            initial_dir,
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            required_keys = [
                "metadata",
                "player_info",
                "character_info",
                "basic_stats",
                "skills",
                "background",
                "loadout"
            ]
            
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                missing_keys_str = ", ".join(missing_keys)
                TFApplication.instance().show_message(f"无效的角色卡文件：缺少必需的键 {missing_keys_str}", 5000, 'yellow')
                return
            
            TFApplication.instance().show_message('角色卡加载成功', 5000, 'green')
            
            self.p_data = data
            self._current_file_path = file_path
            for card in self.cards:
                card.load_data(self.p_data)
                
        except json.JSONDecodeError:
            TFApplication.instance().show_message("无效的JSON文件格式", 5000, 'yellow')

    def _enable_edit(self):
        if self.p_data == {}:
            TFApplication.instance().show_message("请先加载角色卡", 5000, 'yellow')
            return
        if not self.edit_mode:
            self.edit_mode = True
            TFApplication.instance().show_message("启动编辑模式", 5000, 'green')
            for card in self.cards:
                card.enable_edit()
        else:
            self.edit_mode = False
            for card in self.cards:
                card.save_data(self.p_data)

            with open(self._current_file_path, 'w', encoding='utf-8') as file:
                json.dump(self.p_data, file, ensure_ascii=False, indent=2)
            TFApplication.instance().show_message('角色卡保存成功', 5000, 'green')
