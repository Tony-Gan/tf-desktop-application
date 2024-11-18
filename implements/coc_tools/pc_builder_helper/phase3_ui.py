import re
import json
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QWidget, QGridLayout, QGroupBox, QScrollArea

from implements.coc_tools.pc_builder_helper.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_helper.phase_ui import BasePhaseUI
from ui.components.tf_base_button import TFPreviousButton, TFBaseButton
from ui.components.tf_option_entry import TFOptionEntry
from ui.components.tf_value_entry import TFValueEntry
from utils.validator.tf_validator import TFValidator
from utils.helper import resource_path

"""
armour部分替换为战技。首先是选择一个基本Move，默认为徒手攻击，没什么特别的战技。徒手攻击可以换成别的，就会有额外战技
显示对应的伤害，战技全都为文本显示，要看具体的需要按下方按钮。
"""

LABEL_FONT = QFont("Inconsolata SemiCondensed")
LABEL_FONT.setPointSize(10)

class Penetration(Enum):
    YES = "Yes"
    NO = "No"


class Category(Enum):
    COLD_WEAPON = "Cold Weapon"
    THROWN_WEAPO = "Thrown Weapon"
    HANDGUN = "Handgun"
    RIFLE = "Rifle"
    SHOTGUN = "Shotgun"
    SMG = "SMG"
    EXPLOSIVE = "Explosive"
    HEAVY_WEAPON = "Heavy Weapon"
    ARTILLERY = "Artillery"


@dataclass
class Damage:
    dmg_text: str

    @property
    def damage_type(self) -> str:
        slash_count = self.dmg_text.count('/')
        if slash_count == 1:
            return "ranged"
        elif slash_count > 1:
            return "attenuated"
        return "normal"

    @property
    def range_modifier(self) -> str:
        if self.damage_type == "normal":
            return "N/A"

        # For ranged damage
        if self.damage_type == "ranged":
            parts = self.dmg_text.split('/')
            if len(parts) == 2:
                match = re.search(r'(\d+)\s*(?:yards?|feet)', parts[1])
                if match:
                    number = float(match.group(1))
                    if 'yard' in parts[1]:
                        return f"x{self._convert_yards_to_meters(number)}"
                    else:
                        return f"x{self._convert_feet_to_meters(number)}"

        elif self.damage_type == "attenuated":
            return "9, 18, 45"

        return "N/A"

    @property
    def dice_part(self) -> str:
        if self.dmg_text.lower() == "stun":
            return "N/A"

        if self.damage_type == "attenuated":
            return self.dmg_text

        dice_pattern = re.findall(r'\d+D\d+', self.dmg_text)
        if not dice_pattern:
            return "N/A"
        return "+".join(dice_pattern)

    @property
    def static_part(self) -> int:
        if self.damage_type == "attenuated":
            return 0

        match = re.search(r'(?<!\d)\+\s*(\d+)(?!\s*D)', self.dmg_text)
        if match:
            return int(match.group(1))
        return 0

    @property
    def db_modifier(self) -> float:
        if self.damage_type == "attenuated":
            return 0

        if "halfDB" in self.dmg_text.replace(" ", "").lower():
            return 0.5
        elif "+DB" in self.dmg_text.replace(" ", "").upper():
            return 1.0
        return 0

    @property
    def special_effect(self) -> str | None:
        special_effects = ["burn", "stun"]
        for effect in special_effects:
            if effect in self.dmg_text.lower():
                return effect
        return "N/A"

    @property
    def standard_text(self) -> str | None:
        if self.dmg_text.lower() == "stun":
            return "Stun"

        if self.special_effect != "N/A":
            return f"{self.dice_part} {self.special_effect.capitalize()}"

        if self.damage_type == "attenuated":
            return self.dmg_text

        parts = []
        if self.dice_part != "N/A":
            parts.append(self.dice_part)

        if self.db_modifier == 1:
            parts.append("DB")
        elif self.db_modifier == 0.5:
            parts.append("1/2DB")

        if self.static_part > 0:
            parts.append(str(self.static_part))

        if self.damage_type == "ranged":
            return f"{'+'.join(parts)}, {self.range_modifier}"

        return "+".join(parts)

    def _convert_yards_to_meters(self, yards: float) -> int:
        meters = yards * 0.9144
        return round(meters)

    def _convert_feet_to_meters(self, feet: float) -> int:
        meters = feet * 0.3048
        return round(meters)


@dataclass
class Range:
    range_text: str

    @property
    def standard_text(self) -> str:
        if self.range_text.lower() == "melee":
            return "0"

        if "STR" in self.range_text:
            return self._convert_str_range(self.range_text)

        if "/" in self.range_text:
            return self._convert_multiple_ranges(self.range_text)

        return self._convert_single_range(self.range_text)
    
    def _convert_yards_to_meters(self, yards: float) -> int:
        meters = yards * 0.9144
        return round(meters)

    def _convert_feet_to_meters(self, feet: float) -> int:
        meters = feet * 0.3048
        return round(meters)
    
    def _convert_str_range(self, text: str) -> str:
        if "feet" in text.lower():
            conversion_factor = round(0.3048, 2)
            return f"STR*{conversion_factor}"
        elif "yards" in text.lower():
            conversion_factor = round(0.9144, 2)
            return f"STR*{conversion_factor}"
        return text

    def _convert_multiple_ranges(self, text: str) -> str:
        ranges = text.split("/")
        converted_ranges = []
        for r in ranges:
            match = re.search(r"(\d+)\s?(yards?|feet?)", r, re.IGNORECASE)
            if match:
                distance = int(match.group(1))
                unit = match.group(2).lower()
                if "yards" in unit:
                    converted_ranges.append(str(self._convert_yards_to_meters(distance)))
                elif "feet" in unit:
                    converted_ranges.append(str(self._convert_feet_to_meters(distance)))
        return "/".join(converted_ranges)

    def _convert_single_range(self, text: str) -> str:
        match = re.search(r"(\d+)\s?(yards?|feet?)", text, re.IGNORECASE)
        if match:
            distance = int(match.group(1))
            unit = match.group(2).lower()
            if "yards" in unit:
                return str(self._convert_yards_to_meters(distance))
            elif "feet" in unit:
                return str(self._convert_feet_to_meters(distance))
        return text


@dataclass
class WeaponSkill:
    skill_text: str

    @property
    def standard_text(self):
        return self.skill_text.split(":")[-1].strip().title()


@dataclass
class WeaponType:
    name: str
    skill: WeaponSkill
    damage: Damage
    range: Range
    penetration: Penetration
    rate_of_fire: str
    ammo: Optional[str]
    malfunction: Optional[str]
    category: Category

    def __str__(self) -> str:
        damage_text = self.damage.standard_text if self.damage else "N/A"
        range_text = self.range.standard_text if self.range else "N/A"
        return (f"Weapon: {self.name}\n"
                f"Skill: {self.skill}\n"
                f"Damage: {damage_text}\n"
                f"Range: {range_text}\n"
                f"Penetration: {self.penetration.value}\n"
                f"Rate of Fire: {self.rate_of_fire}\n"
                f"Ammo: {self.ammo if self.ammo else 'N/A'}\n"
                f"Malfunction: {self.malfunction if self.malfunction else 'N/A'}\n"
                f"Category: {self.category.value}\n")


class WeaponGroup(QGroupBox):
    MAX_WEAPONS = 3

    def __init__(self, parent:'Phase3UI'):
        super().__init__("Weapons", parent)
        self.parent = parent
        self.setObjectName("section_frame")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.weapon_entries = []

        self._setup_content()

    def _setup_content(self):
        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(5)

        self.add_button = TFBaseButton(
            "Add Weapon",
            width=100,
            height=30,
            enabled=True,
            object_name="add_weapon_button",
            tooltip="Add a new weapon entry",
            on_clicked=self._add_weapon
        )

        self.delete_button = TFBaseButton(
            "Delete Weapon",
            width=100,
            height=30,
            enabled=False,
            object_name="delete_weapon_button",
            tooltip="Delete the last weapon entry",
            on_clicked=self._delete_weapon
        )

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addStretch()

        self.layout.addStretch()
        self.layout.addWidget(self.button_container)

    def _add_weapon(self):
        if len(self.weapon_entries) >= self.MAX_WEAPONS:
            return

        entry = WeaponEntry(self)
        self.layout.insertWidget(len(self.weapon_entries), entry)
        self.weapon_entries.append(entry)

        self._update_button_states()

    def _delete_weapon(self):
        if self.weapon_entries:
            entry = self.weapon_entries.pop()
            self.layout.removeWidget(entry)
            entry.deleteLater()

            self._update_button_states()

    def _update_button_states(self):
        current_count = len(self.weapon_entries)
        self.add_button.setEnabled(current_count < self.MAX_WEAPONS)
        self.delete_button.setEnabled(current_count > 0)

    def clear_all_weapons(self):
        while self.weapon_entries:
            self._delete_weapon()


class WeaponEntry(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.categories = ["None"] + [category.value for category in Category]
        if isinstance(self.parent, WeaponGroup):
            self.weapon_types = self.parent.parent.weapon_types

        self._setup_content()

    def _setup_content(self):
        self.name_entry = TFValueEntry(
            label_text="Name",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=40,
            value_size=80,
            height=30,
            object_name="name"
        )

        self.category_selector = TFOptionEntry(
            label_text="Cate.",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            options=self.categories,
            current_value="None",
            label_size=35,
            value_size=100,
            height=30,
            object_name="weapon_category",
            extra_value_width=60
        )
        self.category_selector.value_field.setEditable(True)
        self.category_selector.value_field.setPlaceholderText("None")

        self.type_selector = TFOptionEntry(
            label_text="Type",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            options=["None"],
            label_size=35,
            value_size=120,
            height=30,
            object_name="weapon_type",
            extra_value_width=80
        )
        self.type_selector.value_field.setEnabled(False)
        self.type_selector.value_field.setEditable(True)
        self.type_selector.value_field.setPlaceholderText("None")

        self.skill_entry = TFValueEntry(
            label_text="Skill",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=35,
            value_size=80,
            height=30,
            object_name="weapon_skill"
        )

        self.damage_entry = TFValueEntry(
            label_text="Damage",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=40,
            value_size=80,
            height=30,
            object_name="weapon_damage"
        )

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_layout.setSpacing(0)

        self.expand_button = TFBaseButton(
            text="Expand",
            width=80,
            height=24,
            object_name="expand_button",
            on_clicked=self._toggle_expand
        )

        button_layout.addWidget(self.expand_button)

        self.range_entry = TFValueEntry(
            label_text="Range",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=40,
            value_size=30,
            height=30,
            object_name="weapon_range"
        )

        self.penetration_entry = TFValueEntry(
            label_text="Pen.",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=35,
            value_size=30,
            height=30,
            object_name="weapon_penetration"
        )

        self.rof_entry = TFValueEntry(
            label_text="RoF",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=35,
            value_size=30,
            height=30,
            object_name="weapon_rof"
        )

        self.ammo_entry = TFValueEntry(
            label_text="Ammo",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=35,
            value_size=30,
            height=30,
            object_name="weapon_ammo"
        )

        self.malfunction_entry = TFValueEntry(
            label_text="Malf",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=40,
            value_size=30,
            height=30,
            object_name="weapon_malfunction"
        )

        self.layout.addWidget(self.name_entry, 0, 0)
        self.layout.addWidget(self.category_selector, 0, 1)
        self.layout.addWidget(self.type_selector, 0, 2)
        self.layout.addWidget(self.skill_entry, 0, 3)
        self.layout.addWidget(self.damage_entry, 0, 4)
        self.layout.addWidget(button_container, 0, 5)
        self.layout.addWidget(self.range_entry, 1, 0)
        self.layout.addWidget(self.penetration_entry, 1, 1)
        self.layout.addWidget(self.rof_entry, 1, 2)
        self.layout.addWidget(self.ammo_entry, 1, 3)
        self.layout.addWidget(self.malfunction_entry, 1, 4)

        self._hide_second_row()

        self.category_selector.value_field.currentTextChanged.connect(self._on_category_changed)
        self.type_selector.value_field.currentTextChanged.connect(self._on_type_changed)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)
        self.layout.setColumnStretch(4, 1)

    def _on_category_changed(self, category: str):
        if category == "None":
            self.type_selector.setEnabled(False)
            self.type_selector.set_options(["None"])
            self.type_selector.set_value("None")
            return

        self.type_selector.value_field.setEnabled(True)

        filtered_types = ["None"] + [wt.name for wt in self.weapon_types
                                     if wt.category.value == category]

        current_text = self.type_selector.get_value()
        self.type_selector.set_options(filtered_types)

        if current_text in filtered_types:
            self.type_selector.set_value(current_text)
        else:
            self.type_selector.set_value("None")

    def _on_type_changed(self, weapon_type: str):
        if weapon_type == "None":
            return

        selected_type = next((wt for wt in self.weapon_types
                              if wt.name == weapon_type), None)
        if selected_type:
            self.skill_entry.set_value(selected_type.skill.standard_text) or "N/A"
            self.damage_entry.set_value(selected_type.damage.standard_text) or "N/A"
            self.range_entry.set_value(selected_type.range.standard_text) or "N/A"
            self.penetration_entry.set_value(selected_type.penetration.value) or "N/A"
            self.rof_entry.set_value(selected_type.rate_of_fire) or "N/A"
            self.ammo_entry.set_value(selected_type.ammo if selected_type.ammo else "N/A")
            self.malfunction_entry.set_value(selected_type.malfunction if selected_type.malfunction else "N/A")

    def _hide_second_row(self):
        self.range_entry.hide()
        self.penetration_entry.hide()
        self.rof_entry.hide()
        self.ammo_entry.hide()
        self.malfunction_entry.hide()

    def _show_second_row(self):
        self.range_entry.show()
        self.penetration_entry.show()
        self.rof_entry.show()
        self.ammo_entry.show()
        self.malfunction_entry.show()

    def _toggle_expand(self):
        if self.range_entry.isVisible():
            self._hide_second_row()
            self.expand_button.setText("Expand")
        else:
            self._show_second_row()
            self.expand_button.setText("Collapse")


class ArmourGroup(QGroupBox):
    def __init__(self, parent:'Phase3UI'):
        super().__init__("Armour", parent)
        self.parent = parent
        self.setObjectName("section_frame")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self._setup_content()

    def _setup_content(self):
        self.name_entry = TFValueEntry(
            label_text="Name",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=40,
            value_size=80,
            height=30,
            object_name="name"
        )

        self.type_entry = TFValueEntry(
            label_text="Armour Type",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=40,
            value_size=80,
            height=30,
            object_name="armour_type"
        )

        self.points_entry = TFValueEntry(
            label_text="Points",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=40,
            value_size=80,
            height=30,
            object_name="points"
        )

        self.layout.addWidget(self.name_entry)
        self.layout.addWidget(self.type_entry)
        self.layout.addWidget(self.points_entry)


class LowerGroup(QFrame):
    def __init__(self, parent:'Phase3UI'):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("section_frame")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self._setup_content()

    def _setup_content(self):
        pass


class Phase3UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        self.config = main_window.config
        self.main_window = main_window

        self.check_button = None
        self.previous_button = None

        super().__init__(PCBuilderPhase.PHASE3, main_window, parent)

        self.weapon_types = self._load_weapon_types_from_json(resource_path("implements/coc_tools/pc_builder_helper/weapon_types.json"))
        self.weapon_scroll_area = None
        self.armour_scroll_area = None
        self.lower_scroll_area = None

        self.validator = TFValidator()
        self._setup_validation_rules()

    def _setup_ui(self):
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        self.weapon_scroll = QScrollArea()
        self.weapon_scroll.setWidgetResizable(True)
        self.weapon_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.weapon_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.weapon_scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.armour_scroll = QScrollArea()
        self.armour_scroll.setWidgetResizable(True)
        self.armour_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.armour_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.armour_scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.weapon_group = WeaponGroup(self)
        self.armour_group = ArmourGroup(self)
        self.lower_group = LowerGroup(self)

        self.weapon_scroll.setWidget(self.weapon_group)
        self.armour_scroll.setWidget(self.armour_group)

        content_layout.addWidget(self.weapon_scroll, 4)
        content_layout.addWidget(self.armour_scroll, 1)
        content_layout.addWidget(self.lower_group, 5)

        self.content_area.setLayout(content_layout)

    def _setup_phase_buttons(self, button_layout):
        self.check_button = TFBaseButton(
            "Check",
            self,
            height=30,
            on_clicked=self._on_check_clicked
        )
        self.previous_button = TFPreviousButton(
            self,
            height=30,
            on_clicked=self._on_previous_clicked
        )

        button_layout.addWidget(self.check_button)
        button_layout.addWidget(self.previous_button)

    def _setup_validation_rules(self):
        pass

    def _on_occupation_list_clicked(self):
        print("[Phase3UI] on_occupation_list_clicked called.")

    def _on_config_updated(self):
        print("[Phase3UI] _on_config_updated called.")

    def _on_check_clicked(self):
        print("[Phase3UI] _on_check_clicked called.")

    def _on_previous_clicked(self):
        self.main_window._on_phase_selected(PCBuilderPhase.PHASE2)

    def _on_next_clicked(self):
        print("[Phase3UI] _on_next_clicked called.")

    def _reset_content(self):
        print("[Phase3UI] _reset_content called.")

    def on_enter(self):
        super().on_enter()

    def on_exit(self):
        super().on_exit()

    def _load_weapon_types_from_json(self, file_path: str) -> List[WeaponType]:
        weapon_types = []
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                weapon_skill = WeaponSkill(item["skill"])
                penetration = Penetration.YES if item["penetration"].lower() == "yes" else Penetration.NO
                damage = Damage(item["damage"])
                weapon_range = Range(item["range"])
                category = Category(item["category"])
                weapon_type = WeaponType(
                    name=item["name"],
                    skill=weapon_skill,
                    damage=damage,
                    range=weapon_range,
                    penetration=penetration,
                    rate_of_fire=item["rate_of_fire"],
                    ammo=item.get("ammo"),
                    malfunction=item.get("malfunction"),
                    category=category
                )
                weapon_types.append(weapon_type)
        return weapon_types
