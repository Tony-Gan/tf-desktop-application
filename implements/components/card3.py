import json
from PyQt6.QtWidgets import QHBoxLayout, QScrollArea, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, QSize

from implements.components.base_card import BaseCard
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_frame import TFBaseFrame
from ui.components.tf_flow_layout import TFFlowLayout
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
        self.weapons_frame.show_armors_button.show()

        items = p_data.get('loadout', {}).get('items', {})
        self.items_frame.carried_item_frame.load_items(items.get('carried', []))
        self.items_frame.backpack_item_frame.load_items(items.get('backpack', []))

    def enable_edit(self):
        self.weapons_frame.add_button.show()
        self.weapons_frame.delete_button.show()
        self.weapons_frame.add_button.setEnabled(True)  
        self.weapons_frame.delete_button.setEnabled(True)
        
        for i in range(self.weapons_frame.content_widget.main_layout.count()):
            weapon_entry = self.weapons_frame.content_widget.main_layout.itemAt(i).widget()
            weapon_entry.name_entry.set_enable(True)
            weapon_entry.skill_entry.set_enable(True)
            weapon_entry.damage_entry.set_enable(True)

        for item_button in self.items_frame.carried_item_frame.content_widget.findChildren(ItemButton):
            item_button.setEnabled(True)
        
        for item_button in self.items_frame.backpack_item_frame.content_widget.findChildren(ItemButton):
            item_button.setEnabled(True)

    def save_data(self, p_data):
        weapons = []
        for i in range(self.weapons_frame.content_widget.main_layout.count()):
            weapon_entry = self.weapons_frame.content_widget.main_layout.itemAt(i).widget()
            name = weapon_entry.name_entry.get_value()
            skill = weapon_entry.skill_entry.get_value().split('(')[0]
            damage = weapon_entry.damage_entry.get_value()
            
            weapon = {
                'name': name,
                'type': 'N/A',
                'category': 'N/A',
                'skill': skill,
                'damage': damage,
                'range': 'N/A',
                'penetration': 'N/A', 
                'rof': 'N/A',
                'ammo': 'N/A',
                'malfunction': 'N/A',
                'notes': 'N/A'
            }
            weapons.append(weapon)
        
        p_data['loadout']['weapons'] = weapons

        carried_items = []
        for item_button in self.items_frame.carried_item_frame.content_widget.findChildren(ItemButton):
            carried_items.append({
                'name': item_button.text(),
                'notes': 'N/A'
            })
        
        backpack_items = []
        for item_button in self.items_frame.backpack_item_frame.content_widget.findChildren(ItemButton):
            backpack_items.append({
                'name': item_button.text(),
                'notes': 'N/A'
            })

        if 'items' not in p_data['loadout']:
            p_data['loadout']['items'] = {}
        p_data['loadout']['items']['carried'] = carried_items
        p_data['loadout']['items']['backpack'] = backpack_items

        self.weapons_frame.add_button.hide()
        self.weapons_frame.delete_button.hide()
        
        for i in range(self.weapons_frame.content_widget.main_layout.count()):
            weapon_entry = self.weapons_frame.content_widget.main_layout.itemAt(i).widget()
            weapon_entry.name_entry.set_enable(False)
            weapon_entry.skill_entry.set_enable(False)
            weapon_entry.damage_entry.set_enable(False)

        for item_button in self.items_frame.carried_item_frame.content_widget.findChildren(ItemButton):
            item_button.setEnabled(False)
        
        for item_button in self.items_frame.backpack_item_frame.content_widget.findChildren(ItemButton):
            item_button.setEnabled(False)


class WeaponsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        self.setFixedHeight(200)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.content_widget = TFBaseFrame(level=1, parent=scroll)
        self.content_widget.main_layout.setSpacing(10)
        self.content_widget.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_widget.main_layout.setContentsMargins(10, 10, 10, 10)
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

        self.show_armors_button.hide()
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
        super().__init__(layout_type=QHBoxLayout, level=1, radius=5, parent=parent)

    def _setup_content(self):
        self.carried_item_frame = CarriedItemFrame(self)
        self.backpack_item_frame = BackpackItemFrame(self)

        self.add_child('carried_item_frame', self.carried_item_frame)
        self.add_child('backpack_item_frame', self.backpack_item_frame)


class ItemButton(TFBaseButton):
    def __init__(self, text: str, parent=None):
        super().__init__(
            text=text,
            parent=parent,
            border_radius=10,
            font_size=10,
            height=24,
            enabled=False
        )
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(10)

    def sizeHint(self):
        metrics = self.fontMetrics()
        width = metrics.horizontalAdvance(self.text()) + 10
        return QSize(width, 24)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # TODO: 处理点击事件
            print("Yo!")
        super().mousePressEvent(event)


class ItemContainer(TFBaseFrame):
    def __init__(self, title: str, parent=None):
        self.title = title
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        self.title_label = self.create_label(
            text=self.title,
            height=24,
            fixed_width=None,
            serif=True
        )
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.content_widget = TFBaseFrame(level=1, layout_type=TFFlowLayout, parent=scroll)
        scroll.setWidget(self.content_widget)

        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(scroll)

    def load_items(self, items):
        flow_layout = self.content_widget.layout()
        flow_layout.clear()
        
        for item in items:
            name = item.get('name', '')
            if name:
                btn = ItemButton(name)
                flow_layout.addWidget(btn)


class CarriedItemFrame(ItemContainer):
    def __init__(self, parent=None):
        super().__init__(title="随身物品", parent=parent)


class BackpackItemFrame(ItemContainer):
    def __init__(self, parent=None):
        super().__init__(title="背包物品", parent=parent)
