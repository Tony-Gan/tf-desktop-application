import json
from PyQt6.QtWidgets import QHBoxLayout, QScrollArea, QFrame
from PyQt6.QtCore import Qt

from implements.components.base_card import BaseCard
from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication
from utils.helper import resource_path


class Card3(BaseCard):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def _setup_content(self):
        self.weapons_frame = WeaponsFrame(self)
        self.items_frame = ItemsFrame(self)

        self.add_child('weapons_frame', self.weapons_frame)
        self.add_child('items_frame', self.items_frame)

    def load_data(self, p_data):
        weapons = p_data.get('loadout', {}).get('weapons', [])
        skills = p_data.get('skills', {})
        
        self.weapons_frame.load_weapons(weapons, skills)

    def save_data(self, p_data):
        pass

    def enable_edit(self):
        pass


class WeaponsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.content_widget = TFBaseFrame(level=1, parent=scroll)
        self.content_widget.main_layout.setSpacing(10)
        self.content_widget.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.content_widget)

        self.button_frame = TFBaseFrame(level=1, layout_type=QHBoxLayout, parent=self)
        self.button_frame.setFixedHeight(30)
        self.button_frame.main_layout.setContentsMargins(30, 0, 30, 0)
        self.button_frame.main_layout.setSpacing(15)
        
        self.show_armors_button = self.button_frame.create_button(
            name="show_armour",
            text="显示护甲",
            height=24,
            width=90,
            on_clicked=self._on_show_armours_clicked
        )
        
        self.add_button = self.button_frame.create_button(
            name="add_weapon",
            text="添加武器",
            height=24,
            width=90,
            enabled=False,
            on_clicked=self._on_add_clicked
        )
        
        self.delete_button = self.button_frame.create_button(
            name="delete_weapon",
            text="删除武器",
            height=24,
            width=90,
            enabled=False,
            on_clicked=self._on_delete_clicked
        )

        self.button_frame.main_layout.addWidget(self.show_armors_button)
        self.button_frame.main_layout.addWidget(self.add_button)
        self.button_frame.main_layout.addWidget(self.delete_button)
        self.button_frame.main_layout.addStretch()

        self.add_button.hide()
        self.delete_button.hide()

        self.main_layout.addWidget(scroll)
        self.main_layout.addWidget(self.button_frame)

    def _on_show_armours_clicked(self):
        print("Yo!")

    def _on_add_clicked(self):
        print("Yo!")

    def _on_delete_clicked(self):
        print("Yo!")

    def load_weapons(self, weapons, skills):
        for i in reversed(range(self.content_widget.main_layout.count())):
            item = self.content_widget.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for weapon in weapons:
            entry = WeaponEntry(self)
            entry.load_data(weapon, skills)
            self.content_widget.main_layout.addWidget(entry)


class WeaponEntry(TFBaseFrame):
    # TODO: 点击后显示Notes
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, layout_type=QHBoxLayout, parent=parent)

    def _setup_content(self):
        self.name_entry = self.create_value_entry(
            name="name",
            label_text="名称:",
            value_text="N/A",
            label_size=35,
            value_size=60,
            enable=False
        )

        self.skill_entry = self.create_value_entry(
            name="skill",
            label_text="技能:",
            value_text="N/A",
            label_size=35,
            value_size=60,
            enable=False
        )

        self.damage_entry = self.create_value_entry(
            name="damage",
            label_text="伤害:",
            value_text="N/A",
            label_size=35,
            value_size=60,
            enable=False
        )

        self.main_layout.addWidget(self.name_entry)
        self.main_layout.addWidget(self.skill_entry)
        self.main_layout.addWidget(self.damage_entry)

    def load_data(self, weapon, skills):
        default_skills = {}
        try:
            with open(resource_path('implements/data/default_skills.json'), 'r', encoding='utf-8') as f:
                default_skills = json.load(f)
        except Exception as e:
            TFApplication.instance().show_message(str(e), 5000, 'yellow')

        self.name_entry.set_value(weapon.get('name', '未命名'))
        
        skill_name = weapon.get('skill', '')
        skill_value = 0
        default_value = 0

        for k, v in default_skills.items():
            if skill_name in k:
                default_value = v

        if skill_name:
            if skill_name in skills:
                skill_value = skills[skill_name].get('total_point', default_value)
            else:
                skill_value = default_value
        
        self.skill_entry.set_value(f"{skill_name}({skill_value})")
        self.damage_entry.set_value(weapon.get('damage', 'N/A'))


class ItemsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        pass
