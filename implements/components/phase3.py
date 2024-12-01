from PyQt6.QtWidgets import QFrame, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt

from implements.components.base_phase import BasePhase
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_frame import TFBaseFrame


class Phase3(BasePhase):
    def _setup_content(self) -> None:
        self.allow_mythos = None
        self.allow_custom_weapon_type = None
        self.complete_mode = None
        super()._setup_content()

        self.show_weapon_type_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="武器类型列表", 
            height=35,
            width=120, 
            on_clicked=self._on_show_weapon_type_clicked
        )

        self.custom_weapon_type_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="自定义武器", 
            height=35,
            width=120, 
            on_clicked=self._on_custom_weapon_type_clicked
        )

        self.buttons_frame.add_custom_button(self.show_weapon_type_button)
        self.buttons_frame.add_custom_button(self.custom_weapon_type_button)

        self.custom_weapon_type_button.hide()

        self.left_frame = LeftFrame(self)
        self.potraits_frame = PortraitsFrame(self)

        self.contents_frame.add_child('left_frame', self.left_frame)
        self.contents_frame.add_child('potraits_frame', self.potraits_frame)

    def reset_contents(self):
        pass

    def initialize(self):
        self.check_dependencies()

    def save_state(self):
        pass

    def check_dependencies(self):
        self.allow_mythos = self.config['general']['allow_mythos']
        self.allow_custom_weapon_type = self.config['general']['custom_weapon_type']
        self.complete_mode = self.config['general']['completed_mode']

        if self.allow_custom_weapon_type:
            self.custom_weapon_type_button.show()

        self.potraits_frame.update_contents()

    def validate(self):
        pass

    def _on_show_weapon_type_clicked(self):
        pass

    def _on_custom_weapon_type_clicked(self):
        pass


class LeftFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.background_frame = BackgroundFrame(self)
        self.weapons_frame = WeaponsFrame(self)
        self.left_lower_frame = LeftLowerFrame(self)

        self.add_child('background_frame', self.background_frame)
        self.add_child('weapons_frame', self.weapons_frame)
        self.add_child('left_lower_frame', self.left_lower_frame)


class PortraitsFrame(TFBaseFrame):
    PORTRAIT_CONFIGS = [
        ("角色外貌", "描述你的角色的外貌特征，包括身高、体型、发型、穿着等。"),
        ("思想与信念", "描述你的角色的核心价值观、信仰和人生态度。"),
        ("重要之人", "描述对你的角色有重要影响的人物，可以是亲人、朋友或导师。"),
        ("意义非凡之地", "描述对你的角色具有特殊意义的地点，可以是出生地、工作场所或其他重要场所。"),
        ("宝贵之物", "描述你的角色视为珍贵的物品，可以是家传之物、工具或具有纪念意义的物品。"),
        ("特质", "描述你的角色的独特性格特征或习惯。"),
        ("伤口和疤痕", "描述你的角色身上的伤痕，可以是物理上的或心理上的。"),
        ("恐惧和狂躁", "描述你的角色的恐惧症和躁动症状。")
    ]

    MYTHOS_CONFIGS = [
        ("禁忌接触", "描述你的角色接触到的克苏鲁神话相关的事物或经历。"),
        ("禁忌书籍", "描述你的角色接触到的克苏鲁神话相关的典籍或文献。")
    ]

    def __init__(self, parent=None):
        self.entries = []
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedWidth(360)
        self.main_layout.setContentsMargins(0, 15, 0, 15)
        self.main_layout.setSpacing(0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = TFBaseFrame(QVBoxLayout, level=1, radius=10, parent=scroll)
        content_widget.main_layout.setContentsMargins(10, 10, 10, 10)
        content_widget.main_layout.setSpacing(10)
        
        scroll.setWidget(content_widget)
        self.main_layout.addWidget(scroll)
        
        self.content_widget = content_widget

    def update_contents(self):
        configs = self.PORTRAIT_CONFIGS.copy()
        if self.parent.allow_mythos:
            configs.extend(self.MYTHOS_CONFIGS)

        for title, tooltip in configs:
            entry = PortraintsEntry(title, tooltip, self)
            self.content_widget.main_layout.addWidget(entry)
            self.entries.append(entry)

        self.content_widget.main_layout.addStretch()

    def get_values(self) -> dict:
        values = {}
        for entry in self.entries:
            title = entry.title
            content = entry.content_edit.toPlainText()
            values[title] = content
        return values

    def set_values(self, values: dict) -> None:
        for entry in self.entries:
            if entry.title in values:
                entry.content_edit.setPlainText(values[entry.title])


class PortraintsEntry(TFBaseFrame):
    def __init__(self, title: str, tooltip: str, parent=None):
        self.title = title
        self.tooltip = tooltip
        super().__init__(QVBoxLayout, level=2, radius=5, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

        self.title_label = self.create_label_with_tip(
            name=f"{self.title}_label",
            text=self.title,
            tooltip_text=self.tooltip,
            height=24
        )

        self.content_edit = self.create_text_edit(
            name=f"{self.title}_content",
            height=100,
            width=320,
            placeholder_text=f"请输入{self.title}相关的描述..."
        )

        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.content_edit)


class BackgroundFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(5)

        self.title_label = self.create_label_with_tip(
            name="background_label",
            text="背景故事",
            tooltip_text="描述你的调查员的成长经历、生活状态、重要事件等。",
            height=24
        )

        self.content_edit = self.create_text_edit(
            name="background_content",
            width=400,
            height=200,
            placeholder_text="请输入角色的背景故事..."
        )

        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.content_edit)


class WeaponsFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass


class LeftLowerFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass