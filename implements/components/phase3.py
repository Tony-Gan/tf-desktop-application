from typing import Any, Dict, List, Tuple
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QScrollArea, QHBoxLayout, QDialog
from PyQt6.QtCore import Qt

from implements.components.base_phase import BasePhase
from implements.components.data_enum import Category
from implements.components.data_reader import load_weapon_types_from_json, load_skills_from_json
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_dialog import TFBaseDialog
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

        nine_stats = ['str', 'con', 'siz', 'dex', 'app', 'int', 'pow', 'edu', 'luk']
        self.basic_stats = {k.upper(): int(self.p_data["basic_stats"][k]) for k in nine_stats}
        self.skills = load_skills_from_json(self.basic_stats["DEX"], self.basic_stats["EDU"])

        self.weapon_types = load_weapon_types_from_json()

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
        self.add_child('left_lower_frame', self.left_lower_frame)
        self.add_child('weapons_frame', self.weapons_frame)


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
        self.setFixedWidth(320)
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
            width=280,
            placeholder_text=f"请输入{self.title}相关的描述..."
        )

        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.content_edit)


class BackgroundFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedHeight(200)
        self.main_layout.setContentsMargins(10, 0, 10, 0)
        self.main_layout.setSpacing(5)

        self.title_label = self.create_label_with_tip(
            name="background_label",
            text="背景故事",
            tooltip_text="描述你的调查员的成长经历、生活状态、重要事件等。",
            height=24
        )

        self.content_edit = self.create_text_edit(
            name="background_content",
            width=515,
            height=170,
            placeholder_text="请输入角色的背景故事..."
        )

        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.content_edit)


class WeaponsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        self.weapon_entries = []
        self.selected_weapons = []
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedHeight(260)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        button_container = TFBaseFrame(QHBoxLayout, level=1, parent=self)
        button_container.main_layout.setContentsMargins(0, 0, 0, 0)
        button_container.main_layout.setSpacing(5)

        self.add_button = self.create_button(
            name="add_weapon",
            text="添加武器",
            width=100,
            height=24,
            on_clicked=self._on_add_weapon
        )

        self.delete_button = self.create_button(
            name="delete_weapon",
            text="删除武器",
            width=100,
            height=24,
            on_clicked=self._on_delete_weapon,
            enabled=False
        )

        button_container.main_layout.addWidget(self.add_button)
        button_container.main_layout.addWidget(self.delete_button)
        button_container.main_layout.addStretch()

        self.main_layout.addWidget(button_container)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.content_widget = TFBaseFrame(QVBoxLayout, level=1, radius=10, parent=scroll)
        self.content_widget.main_layout.setContentsMargins(5, 5, 5, 5)
        self.content_widget.main_layout.setSpacing(5)
        self.content_widget.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.content_widget)
        self.main_layout.addWidget(scroll)
        self.main_layout.addStretch()

    def _on_add_weapon(self) -> None:
        success, result = WeaponAddDialog.get_input(self, weapon_types=self.parent.parent.weapon_types)
        if success and result:
            self.selected_weapons.append(result)
            
            entry = WeaponEntry(result, self)
            self.weapon_entries.append(entry)
            self.content_widget.main_layout.addWidget(entry)
            
            self.delete_button.setEnabled(True)

    def _on_delete_weapon(self) -> None:
        if not self.weapon_entries:
            return

        entry = self.weapon_entries.pop()
        self.selected_weapons.pop()
        self.content_widget.main_layout.removeWidget(entry)
        entry.deleteLater()

        self.delete_button.setEnabled(bool(self.weapon_entries))


class WeaponEntry(TFBaseFrame):
    def __init__(self, weapon_data: Dict, parent=None):
        self.weapon_data = weapon_data
        super().__init__(QHBoxLayout, level=1, radius=5, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(10)

        name_type = f"{self.weapon_data['name']} ({self.weapon_data['weapon_type'].name})"
        self.name_label = self.create_label(
            text=name_type,
            fixed_width=160,
            height=24,
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            serif=True
        )

        skill_name = self.weapon_data["weapon_type"].skill.standard_text
        default_value = 0
        for s in self.parent.parent.parent.skills:
            if s.name == skill_name:
                default_value = s.default_point
                break
        skill_value = self.parent.parent.parent.p_data.get("skills", {}).get(skill_name, default_value)
        display_skill_name = skill_name
        
        self.skill_entry = self.create_value_entry(
            name="skill",
            label_text="技能:",
            value_text=f"{display_skill_name}（{skill_value}）",
            label_size=35,
            value_size=80,
            height=24,
            enable=False
        )

        self.damage_entry = self.create_value_entry(
            name="damage",
            label_text="伤害:",
            value_text=self.weapon_data["weapon_type"].damage.standard_text,
            label_size=35,
            value_size=70,
            height=24,
            enable=False
        )

        self.detail_button = self.create_button(
            name="detail",
            text="详情",
            width=40,
            height=24,
            on_clicked=self._show_details
        )

        self.main_layout.addWidget(self.name_label)
        self.main_layout.addWidget(self.skill_entry)
        self.main_layout.addWidget(self.damage_entry)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.detail_button)

    def _show_details(self) -> None:
        detail_dialog = WeaponDetailDialog(self.weapon_data, self)
        if detail_dialog.exec() == QDialog.DialogCode.Accepted:
            name_type = f"{self.weapon_data['name']} ({self.weapon_data['weapon_type'].name})"
            self.name_label.setText(name_type)


class LeftLowerFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.carried_items_frame = CarriedItemsFrame(self)
        self.backpack_items_frame = BackpackItemsFrame(self)

        self.add_child('carried_items_frame', self.carried_items_frame)
        self.add_child('backpack_items_frame', self.backpack_items_frame)


class CarriedItemsFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setContentsMargins(5, 2, 0, 2)
        self.main_layout.setSpacing(5)

        self.edit = self.create_text_edit(
            name="carried_items",
            placeholder_text="请输入随身物品，通过逗号隔开",
            width=252,
            height=110
        )
        
        self.main_layout.addWidget(self.edit)


class BackpackItemsFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setContentsMargins(0, 2, 5, 2)
        self.main_layout.setSpacing(5)

        self.edit = self.create_text_edit(
            name="backpack_items",
            placeholder_text="请输入背包物品，通过逗号隔开",
            width=250,
            height=110
        )
        
        self.main_layout.addWidget(self.edit)


class WeaponAddDialog(TFBaseDialog):
    def __init__(self, weapon_types, parent=None):
        self.weapon_types = weapon_types
        super().__init__(
            title="新武器",
            parent=parent,
            button_config=[{"text": "确定", "callback": self._on_ok_clicked}]
        )

    def _setup_content(self) -> None:
        categories = ["选择类型"] + [cat.value for cat in Category]
        self.category_entry = self.create_option_entry(
            name="weapon_category",
            label_text="武器类型:",
            options=categories,
            label_size=80,
            value_size=180,
            height=24
        )

        self.type_entry = self.create_option_entry(
            name="weapon_type",
            label_text="具体武器:",
            options=["选择武器"],
            label_size=80,
            value_size=180,
            height=24,
            enable=False
        )

        self.name_entry = self.create_value_entry(
            name="weapon_name",
            label_text="武器名称:",
            label_size=80,
            value_size=180,
            height=24
        )

        self.skill_entry = self.create_value_entry(
            name="weapon_skill",
            label_text="技能:",
            label_size=80,
            value_size=180,
            height=24,
            enable=False
        )

        self.damage_entry = self.create_value_entry(
            name="weapon_damage",
            label_text="伤害:",
            label_size=80,
            value_size=180,
            height=24,
            enable=False
        )

        self.range_entry = self.create_value_entry(
            name="weapon_range",
            label_text="射程:",
            label_size=80,
            value_size=180,
            height=24,
            enable=False
        )

        self.penetration_entry = self.create_value_entry(
            name="weapon_penetration",
            label_text="穿透:",
            label_size=80,
            value_size=180,
            height=24,
            enable=False
        )

        self.rof_entry = self.create_value_entry(
            name="weapon_rof",
            label_text="射速:",
            label_size=80,
            value_size=180,
            height=24,
            enable=False
        )

        self.ammo_entry = self.create_value_entry(
            name="weapon_ammo",
            label_text="弹药:",
            label_size=80,
            value_size=180,
            height=24,
            enable=False
        )

        self.malfunction_entry = self.create_value_entry(
            name="weapon_malfunction",
            label_text="故障值:",
            label_size=80,
            value_size=180,
            height=24,
            enable=False
        )

        for entry in [
            self.category_entry, self.type_entry, self.name_entry,
            self.skill_entry, self.damage_entry, self.range_entry,
            self.penetration_entry, self.rof_entry, self.ammo_entry,
            self.malfunction_entry
        ]:
            self.main_layout.addWidget(entry)

        self.category_entry.value_changed.connect(self._on_category_changed)
        self.type_entry.value_changed.connect(self._on_type_changed)

    def _on_category_changed(self, category: str) -> None:
        if category == "选择类型":
            self.type_entry.combo_box.setEnabled(False)
            self.type_entry.set_options(["选择武器"])
            return

        self.type_entry.combo_box.setEnabled(True)
        filtered_types = ["选择武器"] + [
            wt.name for wt in self.weapon_types
            if wt.category.value == category
        ]
        self.type_entry.update_options(filtered_types)

    def _on_type_changed(self, weapon_type: str) -> None:
        if weapon_type == "选择武器":
            return

        selected_type = next(
            (wt for wt in self.weapon_types if wt.name == weapon_type),
            None
        )
        if selected_type:
            self.skill_entry.set_value(selected_type.skill.standard_text)
            self.damage_entry.set_value(selected_type.damage.standard_text)
            self.range_entry.set_value(selected_type.range.standard_text)
            self.penetration_entry.set_value(selected_type.penetration.value)
            self.rof_entry.set_value(selected_type.rate_of_fire)
            self.ammo_entry.set_value(selected_type.ammo if selected_type.ammo else "N/A")
            self.malfunction_entry.set_value(selected_type.malfunction if selected_type.malfunction else "N/A")

    def validate(self) -> List[Tuple[Any, str]]:
        invalid_items = []
        if self.category_entry.get_value() == "选择类型":
            invalid_items.append((self.category_entry, "请选择武器类型"))
        if self.type_entry.get_value() == "选择武器":
            invalid_items.append((self.type_entry, "请选择具体武器"))
        return invalid_items

    def get_validated_data(self) -> Dict:
        name = self.name_entry.get_value()
        if not name:
            name = "未命名"
            
        weapon_type = next(
            (wt for wt in self.weapon_types 
             if wt.name == self.type_entry.get_value()),
            None
        )
        
        return {
            "name": name,
            "weapon_type": weapon_type
        }


class WeaponDetailDialog(TFBaseDialog):
    def __init__(self, weapon_data: Dict, parent=None):
        self.weapon_data = weapon_data
        super().__init__(
            title="武器详情",
            parent=parent,
            button_config=[{"text": "确定", "callback": self._on_ok_clicked}]
        )

    def _setup_content(self) -> None:
        self.name_entry = self.create_value_entry(
            name="weapon_name",
            label_text="武器名称:",
            value_text=self.weapon_data["name"],
            label_size=80,
            value_size=180,
            height=24
        )
        self.main_layout.addWidget(self.name_entry)

        details = [
            ("武器类型", self.weapon_data["weapon_type"].category.value),
            ("具体武器", self.weapon_data["weapon_type"].name),
            ("技能", self.weapon_data["weapon_type"].skill.standard_text),
            ("伤害", self.weapon_data["weapon_type"].damage.standard_text),
            ("射程", self.weapon_data["weapon_type"].range.standard_text),
            ("穿透", self.weapon_data["weapon_type"].penetration.value),
            ("射速", self.weapon_data["weapon_type"].rate_of_fire),
            ("弹药", self.weapon_data["weapon_type"].ammo if self.weapon_data["weapon_type"].ammo else "N/A"),
            ("故障值", self.weapon_data["weapon_type"].malfunction if self.weapon_data["weapon_type"].malfunction else "N/A")
        ]

        for label, value in details:
            entry = self.create_value_entry(
                name=label.lower(),
                label_text=label + ":",
                value_text=str(value),
                label_size=80,
                value_size=180,
                height=24,
                enable=False
            )
            self.main_layout.addWidget(entry)

    def _on_ok_clicked(self) -> None:
        self.weapon_data["name"] = self.name_entry.get_value()
        super()._on_ok_clicked()