import json
from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QScrollArea, QHBoxLayout, QDialog, QFileDialog, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from implements.components.base_phase import BasePhase
from implements.components.data_enum import Category
from implements.components.data_reader import load_weapon_types_from_json, load_skills_from_json
from implements.components.data_type import WeaponType
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_dialog import TFBaseDialog
from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication


label_font = QFont("Noto Serif SC")
label_font.setPointSize(12)


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
        if hasattr(self.potraits_frame, 'entries'):
            for entry in self.potraits_frame.entries:
                entry.content_edit.clear()

        self.left_frame.background_frame.content_edit.clear()

        self.left_frame.carried_items_frame.edit.clear()
        self.left_frame.backpack_items_frame.edit.clear()

        weapons_frame = self.left_frame.weapons_frame
        if hasattr(weapons_frame, 'weapon_entries'):
            while weapons_frame.weapon_entries:
                weapons_frame._on_delete_weapon()
            weapons_frame.selected_weapons.clear()
            weapons_frame.delete_button.setEnabled(False)

    def initialize(self):
        self.check_dependencies()

    def save_state(self):
        background = {
            'background': self.left_frame.background_frame.content_edit.toPlainText().strip() or "N/A",
            'portraits': {entry.title: entry.content_edit.toPlainText().strip() or "N/A" 
                            for entry in self.potraits_frame.entries}
        }

        loadout = {
            'weapons': [],
            'items': {'carried': [], 'backpack': []}
        }

        for weapon in self.left_frame.weapons_frame.selected_weapons:
            weapon_type = weapon['weapon_type']
            weapon_data = {
                'name': weapon['name'] or "N/A",
                'type': weapon_type.name,
                'category': weapon_type.category.value,
                'skill': weapon_type.skill.standard_text,
                'damage': weapon_type.damage.standard_text,
                'range': weapon_type.range.standard_text,
                'penetration': weapon_type.penetration.value,
                'rof': weapon_type.rate_of_fire,
                'ammo': weapon_type.ammo if weapon_type.ammo and weapon_type.ammo != 'N/A' else "N/A",
                'malfunction': weapon_type.malfunction if weapon_type.malfunction and weapon_type.malfunction != 'N/A' else "N/A",
                'notes': "N/A"
            }
            loadout['weapons'].append(weapon_data)

        for section, frame in [
            ('carried', self.left_frame.left_lower_frame.carried_items_frame),
            ('backpack', self.left_frame.left_lower_frame.backpack_items_frame)
        ]:
            items = [item.strip() for item in frame.edit.toPlainText().replace('，', ',').split(',') if item.strip()]
            loadout['items'][section] = [{'name': item or "N/A", 'notes': "N/A"} for item in items]

        self.p_data.update({'background': background, 'loadout': loadout})

    def check_dependencies(self):
        self.allow_mythos = self.config['general']['allow_mythos']
        self.allow_custom_weapon_type = self.config['general']['custom_weapon_type']
        self.complete_mode = self.config['general']['completed_mode']

        if self.complete_mode:
            self.buttons_frame.next_button.show()
            self.buttons_frame.complete_button.hide()
        else:
            self.buttons_frame.next_button.hide()
            self.buttons_frame.complete_button.show()

        nine_stats = ['str', 'con', 'siz', 'dex', 'app', 'int', 'pow', 'edu', 'luk']
        self.basic_stats = {k.upper(): int(self.p_data["basic_stats"][k]) for k in nine_stats}
        self.skills = load_skills_from_json(self.basic_stats["DEX"], self.basic_stats["EDU"])

        self.weapon_types = load_weapon_types_from_json()

        if self.allow_custom_weapon_type:
            self.custom_weapon_type_button.show()

        self.potraits_frame.update_contents()

    def validate(self):
        invalid_items = []
        background_text = self.left_frame.background_frame.content_edit.toPlainText().strip()
        if not background_text:
            invalid_items.append((self.left_frame.background_frame, "背景故事不能为空"))
        return invalid_items

    def on_complete(self):
        self.save_state()
        print(self.p_data)
        dialog = CharacterPreviewDialog(self.p_data, self)
        dialog.exec()

    def _on_show_weapon_type_clicked(self):
        success, selected_type = WeaponTypeListDialog.get_input(self, weapon_types=self.weapon_types)
        if success and selected_type:
            dialog = WeaponAddDialog(self.weapon_types, self)
            dialog.category_entry.set_value(selected_type.category.value)
            dialog.type_entry.combo_box.setEnabled(True)
            filtered_types = ["选择武器"] + [
                wt.name for wt in self.weapon_types
                if wt.category.value == selected_type.category.value
            ]
            dialog.type_entry.update_options(filtered_types)
            dialog.type_entry.set_value(selected_type.name)
            dialog._on_type_changed(selected_type.name)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                result = dialog.get_validated_data()
                self.left_frame.weapons_frame.selected_weapons.append(result)
                
                entry = WeaponEntry(result, self.left_frame.weapons_frame)
                self.left_frame.weapons_frame.weapon_entries.append(entry)
                self.left_frame.weapons_frame.content_widget.main_layout.addWidget(entry)
                
                self.left_frame.weapons_frame.delete_button.setEnabled(True)

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
            width=560,
            height=135,
            placeholder_text="请输入角色的背景故事..."
        )

        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.content_edit)
        self.main_layout.addStretch()


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
        level = -1
        for k, v in self.parent.parent.parent.p_data.get("skills", {}).items():
            if skill_name in k:
                level = v['total_point']
                break
        skill_value = default_value if level == -1 else level
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
    def __init__(self, parent=None):
        super().__init__(level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setContentsMargins(5, 2, 0, 2)
        self.main_layout.setSpacing(5)

        self.label = self.create_label_with_tip(
            name="carried_items_label",
            text="随身物品",
            tooltip_text="角色随身携带的物品清单。",
            height=24
        )

        self.edit = self.create_text_edit(
            name="carried_items",
            placeholder_text="请输入随身物品，通过逗号隔开",
            width=270,
            height=110
        )
        
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.edit)


class BackpackItemsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setContentsMargins(0, 2, 5, 2)
        self.main_layout.setSpacing(5)

        self.label = self.create_label_with_tip(
            name="backpack_items_label",
            text="背包物品",
            tooltip_text="角色在背包中存放的物品清单。",
            height=24
        )

        self.edit = self.create_text_edit(
            name="backpack_items",
            placeholder_text="请输入背包物品，通过逗号隔开",
            width=278,
            height=110
        )
        
        self.main_layout.addWidget(self.label)
        self.main_layout.addStretch()
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


class WeaponTypeListDialog(TFBaseDialog):
    def __init__(self, parent=None, weapon_types: List[WeaponType] = None):
        self.weapon_types = weapon_types
        self._selected_type = None
        self._entry_widgets = []
        super().__init__(title="武器类型列表", layout_type=QVBoxLayout, parent=parent, button_config=[])

    def _setup_content(self) -> None:
        self.resize(1000, 780)
        self.main_layout.setSpacing(15)

        search_frame = TFBaseFrame(QHBoxLayout, parent=self)
        search_frame.main_layout.setSpacing(30)
        
        self.name_filter = self.create_line_edit(
            name="name_filter",
            text="",
            width=100,
            height=24
        )
        self.name_filter.setPlaceholderText("根据名称筛选... (未实现)")
        
        search_frame.main_layout.addWidget(self.name_filter)
        search_frame.main_layout.addStretch()
        
        self.main_layout.addWidget(search_frame)
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.scroll_content = TFBaseFrame(QVBoxLayout, parent=scroll)
        scroll.setWidget(self.scroll_content)
        
        for weapon_type in self.weapon_types:
            entry = WeaponTypeEntry(weapon_type, parent=self.scroll_content)
            self.scroll_content.main_layout.addWidget(entry)
            self._entry_widgets.append(entry)
        
        self.main_layout.addWidget(scroll)

    def accept_type(self, weapon_type: WeaponType):
        response = TFApplication.instance().show_question(
            "添加武器",
            f"是否要添加一个{weapon_type.name}?",
            ["确定", "取消"]
        )
        if response == "确定":
            self._selected_type = weapon_type
            self.accept()
        
    def get_result(self) -> Optional[WeaponType]:
        return self._selected_type
    

class WeaponTypeEntry(TFBaseFrame):
    def __init__(self, weapon_type: WeaponType, parent=None):
        self.weapon_type = weapon_type
        super().__init__(QHBoxLayout, level=1, radius=10, parent=parent)
        self.setMouseTracking(True)

    def _setup_content(self) -> None:
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(5)

        details = [
            ("名称", self.weapon_type.name),
            ("类型", self.weapon_type.category.value),
            ("技能", self.weapon_type.skill.standard_text),
            ("伤害", self.weapon_type.damage.standard_text),
            ("射程", self.weapon_type.range.standard_text),
            ("穿透", self.weapon_type.penetration.value),
            ("射速", self.weapon_type.rate_of_fire),
            ("弹药", self.weapon_type.ammo if self.weapon_type.ammo else "N/A"),
            ("故障值", self.weapon_type.malfunction if self.weapon_type.malfunction else "N/A")
        ]

        for label, value in details:
            entry = self.create_value_entry(
                name=label.lower(),
                label_text=f"{label}:",
                value_text=str(value),
                label_size=60,
                value_size=100,
                height=24,
                enable=False
            )
            self.main_layout.addWidget(entry)

        self.setObjectName("weaponTypeEntry")
        self.setStyleSheet("""
            #weaponTypeEntry {
                background-color: transparent;
            }
            #weaponTypeEntry:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dialog = self.window()
            if isinstance(dialog, WeaponTypeListDialog):
                dialog.accept_type(self.weapon_type)


class CharacterPreviewDialog(TFBaseDialog):
    LABEL_MAP = {
        "player_name": "玩家姓名",
        "era": "时代",
        "char_name": "调查员姓名", 
        "age": "年龄",
        "gender": "性别",
        "nationality": "国籍",
        "residence": "居住地",
        "birthplace": "出生地",
        "language_own": "母语",
        "occupation": "职业"
    }

    def __init__(self, p_data: dict, parent=None):
        self.p_data = p_data
        super().__init__(title="角色预览", parent=parent)
    
    def _add_section_header(self, parent: TFBaseFrame, title: str) -> None:
        header_frame = TFBaseFrame(QVBoxLayout, parent=parent)
        header_frame.main_layout.setSpacing(5)
        label = header_frame.create_label(title, height=30)
        label.setFont(label_font)
        header_frame.main_layout.addWidget(label)
        parent.main_layout.addWidget(header_frame)
        
    def _setup_content(self) -> None:
        self.setFixedWidth(800)
        self.resize(800, 600)
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = TFBaseFrame(QVBoxLayout, parent=scroll)
        content_widget.main_layout.setSpacing(20)
        scroll.setWidget(content_widget)

        if self.p_data.get('metadata') or self.p_data.get('player_info'):
            self._add_section_header(content_widget, "基础信息")
            info_frame = TFBaseFrame(QGridLayout, parent=content_widget)
            
            row = 0
            meta_data = [
                ("玩家姓名", self.p_data['player_info'].get('player_name', '')),
                ("令牌", self.p_data['metadata'].get('token', '')),
                ("时代", self.p_data['player_info'].get('era', ''))
            ]
            
            for label, value in meta_data:
                if value:
                    entry = info_frame.create_value_entry(
                        name=f"meta_{label}",
                        label_text=label,
                        value_text=str(value),
                        enable=False,
                        label_size=100,
                        value_size=200
                    )
                    info_frame.main_layout.addWidget(entry, row, 0)
                    row += 1
            content_widget.main_layout.addWidget(info_frame)

        if self.p_data.get('character_info'):
            self._add_section_header(content_widget, "角色信息")
            char_frame = TFBaseFrame(QGridLayout, parent=content_widget)
            
            char_info = self.p_data['character_info']
            non_empty_fields = [(k, v) for k, v in char_info.items() if v]
            
            for i, (key, value) in enumerate(non_empty_fields):
                entry = char_frame.create_value_entry(
                    name=f"char_{key}",
                    label_text=self.LABEL_MAP.get(key, key),
                    value_text=str(value),
                    enable=False,
                    label_size=90,
                    value_size=100
                )
                char_frame.main_layout.addWidget(entry, i // 2, i % 2)
            content_widget.main_layout.addWidget(char_frame)

        if self.p_data.get('basic_stats'):
            self._add_section_header(content_widget, "属性值")
            stats_frame = TFBaseFrame(QGridLayout, parent=content_widget)
            
            stats = self.p_data['basic_stats']
            non_empty_stats = [(k, v) for k, v in stats.items() if v and k.lower()[:4] != 'curr']
            
            for i, (key, value) in enumerate(non_empty_stats):
                entry = stats_frame.create_value_entry(
                    name=f"stat_{key}",
                    label_text=key.upper(),
                    value_text=str(value),
                    enable=False,
                    label_size=50,
                    value_size=40
                )
                stats_frame.main_layout.addWidget(entry, i // 3, i % 3)
            content_widget.main_layout.addWidget(stats_frame)

        if self.p_data.get('skills'):
            self._add_section_header(content_widget, "技能")
            skills_frame = TFBaseFrame(QGridLayout, parent=content_widget)
            
            row = 0
            col = 0
            for skill_name, skill_data in self.p_data['skills'].items():
                if skill_data.get('total_point'):
                    entry = skills_frame.create_value_entry(
                        name=f"skill_{skill_name}",
                        label_text=skill_name,
                        value_text=str(skill_data['total_point']),
                        enable=False,
                        label_size=80,
                        value_size=40
                    )
                    skills_frame.main_layout.addWidget(entry, row, col)
                    
                    col += 1
                    if col >= 3:
                        col = 0
                        row += 1
            content_widget.main_layout.addWidget(skills_frame)

        if self.p_data.get('background', {}).get('background') or self.p_data.get('background', {}).get('portraits'):
            self._add_section_header(content_widget, "背景描述")
            background_frame = self._create_background_section()
            content_widget.main_layout.addWidget(background_frame)

        if self.p_data.get('loadout'):
            self._add_section_header(content_widget, "装备")
            loadout_frame = self._create_loadout_section()
            content_widget.main_layout.addWidget(loadout_frame)
        
        self.main_layout.addWidget(scroll)

    def _create_background_section(self) -> TFBaseFrame:
        frame = TFBaseFrame(QVBoxLayout, parent=None)
        
        background = self.p_data['background'].get('background')
        if background:
            background_text = frame.create_text_edit(
                name="background_text",
                text=background,
                width=505,
                height=100,
                read_only=True
            )
            frame.main_layout.addWidget(background_text)
        
        portraits = self.p_data['background'].get('portraits', {})
        if portraits:
            portraits_grid = TFBaseFrame(QGridLayout, parent=frame)
            non_empty_portraits = [(k, v) for k, v in portraits.items() if v]
            
            for i, (key, value) in enumerate(non_empty_portraits):
                entry = portraits_grid.create_value_entry(
                    name=f"portrait_{key}",
                    label_text=key,
                    value_text=str(value),
                    enable=False,
                    label_size=100,
                    value_size=400
                )
                portraits_grid.main_layout.addWidget(entry, i, 0)
            frame.main_layout.addWidget(portraits_grid)
        
        return frame

    def _create_loadout_section(self) -> TFBaseFrame:
        WEAPON_LABELS = {
            'type': '类型',
            'category': '分类',
            'skill': '技能',
            'damage': '伤害'
        }

        frame = TFBaseFrame(QVBoxLayout, parent=None)
        
        weapons = self.p_data['loadout'].get('weapons', [])
        if weapons:
            weapons_grid = TFBaseFrame(QGridLayout, parent=frame)
            for i, weapon in enumerate(weapons):
                weapon_frame = TFBaseFrame(QHBoxLayout, parent=weapons_grid)
                label = weapon_frame.create_label(weapon['name'], height=24)
                label.setFont(label_font)
                weapon_frame.main_layout.addWidget(label)
                
                for key in ['type', 'category', 'skill', 'damage']:
                    if weapon.get(key):
                        entry = weapon_frame.create_value_entry(
                            name=f"weapon_{i}_{key}",
                            label_text=WEAPON_LABELS[key],
                            value_text=str(weapon[key]),
                            enable=False,
                            label_size=40,
                            value_size=80
                        )
                        weapon_frame.main_layout.addWidget(entry)
                
                weapons_grid.main_layout.addWidget(weapon_frame, i, 0)
            frame.main_layout.addWidget(weapons_grid)

        items = self.p_data['loadout'].get('items', {})
        if items:
            items_frame = TFBaseFrame(QVBoxLayout, parent=frame)
            
            carried_items = items.get('carried', [])
            if carried_items:
                label = items_frame.create_label("随身物品", height=24)
                label.setFont(label_font)
                items_frame.main_layout.addWidget(label)
                
                items_text = "、".join(item['name'] for item in carried_items if item.get('name'))
                if items_text:
                    text_display = items_frame.create_text_edit(
                        name="carried_items_text",
                        text=items_text,
                        width=500,
                        height=60,
                        read_only=True,
                        word_wrap=True
                    )
                    items_frame.main_layout.addWidget(text_display)
            
            backpack_items = items.get('backpack', [])
            if backpack_items:
                label = items_frame.create_label("背包物品", height=24)
                label.setFont(label_font)
                items_frame.main_layout.addWidget(label)
                
                items_text = "、".join(item['name'] for item in backpack_items if item.get('name'))
                if items_text:
                    text_display = items_frame.create_text_edit(
                        name="backpack_items_text",
                        text=items_text,
                        width=500,
                        height=60,
                        read_only=True,
                        word_wrap=True
                    )
                    items_frame.main_layout.addWidget(text_display)
            
            frame.main_layout.addWidget(items_frame)
        
        return frame

    def _on_ok_clicked(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存角色数据",
            "",
            "JSON文件 (*.json)"
        )
        
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.p_data, f, ensure_ascii=False, indent=4)
            
            self.accept()
