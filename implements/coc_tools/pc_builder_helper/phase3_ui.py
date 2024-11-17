import re
import json
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from PyQt6.QtWidgets import QVBoxLayout

from implements.coc_tools.pc_builder_helper.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_helper.phase_ui import BasePhaseUI
from ui.components.tf_base_button import TFPreviousButton, TFBaseButton
from utils.validator.tf_validator import TFValidator
from utils.helper import resource_path

"""
设计笔记：
1. 用户可以从已有的type中选择模板，先选择类型，然后选择具体，选择模板后将自动填充每个Field，但也可以单独修改
2. 单独修改需要手动填写武器的每个属性，点击某些属性，例如range之类的，会弹出新对话框进行设计
核心体验是用户可以根据某个模板快速自定义自己想要的武器效果
"""


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
    # TODO: 计算有很大问题，需要GPT-o1
    dmg_text: str

    @property
    def damage_type(self) -> str:
        if "/" in self.dmg_text and re.match(r"\d+D\d+/\d+D\d+/\d+D\d+", self.dmg_text):
            return "attenuation"
        elif "/" in self.dmg_text and re.search(r"\d+\s?(yards?|feet?|meters?)", self.dmg_text, re.IGNORECASE):
            return "ranged"
        else:
            return "normal"

    @property
    def damage_range(self) -> str:
        if self.damage_type == "ranged":
            match = re.search(r"(\d+)\s?(yards?|feet?|meters?)", self.dmg_text, re.IGNORECASE)
            if match:
                distance = int(match.group(1))
                unit = match.group(2).lower()
                if "yards" in unit:
                    return f"{self._convert_yards_to_meters(distance)} meters"
                elif "feet" in unit:
                    return f"{self._convert_feet_to_meters(distance)} meters"
                elif "meters" in unit:
                    return f"{distance} meters"
        elif self.damage_type == "attenuation":
            return self.dmg_text
        return None

    @property
    def dice_part(self) -> str | None:
        if self.damage_type == "attenuation":
            return self.dmg_text
        match = re.findall(r"\d+D\d+", self.dmg_text)
        return "+".join(match) if match else None

    @property
    def static_part(self) -> int:
        if self.damage_type == "attenuation":
            return 0
        match = re.findall(r"[\+\-]?\d+", self.dmg_text)
        return sum(int(m) for m in match) if match else 0

    @property
    def db_modifier(self) -> float:
        if self.damage_type == "attenuation":
            return 0
        if "halfDB" in self.dmg_text:
            return 0.5
        elif re.search(r"\bDB\b", self.dmg_text):
            return 1.0
        db_matches = re.findall(r"(\d+)DB", self.dmg_text)
        return float(db_matches[0]) if db_matches else 0

    @property
    def special_effect(self) -> str | None:
        if self.damage_type == "attenuation":
            return None
        match = re.search(r"(burn|stun|fire|shock)", self.dmg_text, re.IGNORECASE)
        return match.group(0).capitalize() if match else None

    @property
    def standard_text(self) -> str | None:
        if self.damage_type == "attenuation":
            return self.dmg_text
        parts = []
        if self.dice_part:
            parts.append(self.dice_part)
        if self.db_modifier == 0.5:
            parts.append("1/2DB")
        elif self.db_modifier > 0:
            parts.append(f"{int(self.db_modifier)}DB")
        if self.static_part != 0:
            parts.append(f"{self.static_part:+}")
        if self.special_effect:
            parts.append(self.special_effect)
        if self.damage_type == "ranged" and self.damage_range:
            parts.append(f"{self.damage_range}")
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
class WeaponType:
    name: str
    skill: str
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
    


class Phase3UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        self.config = main_window.config
        self.main_window = main_window

        self.check_button = None
        self.previous_button = None

        super().__init__(PCBuilderPhase.PHASE3, main_window, parent)

        self.validator = TFValidator()
        self._setup_validation_rules()

    def _setup_ui(self):
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        self.content_area.setLayout(content_layout)

        self.weapon_types = self._load_weapon_types_from_json(resource_path("implements/coc_tools/pc_builder_helper/weapon_types.json"))

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
                penetration = Penetration.YES if item["penetration"].lower() == "yes" else Penetration.NO
                damage = Damage(item["damage"])
                range = Range(item["range"])
                category = Category(item["category"])
                weapon_type = WeaponType(
                    name=item["name"],
                    skill=item["skill"],
                    damage=damage,
                    range=range,
                    penetration=penetration,
                    rate_of_fire=item["rate_of_fire"],
                    ammo=item.get("ammo"),
                    malfunction=item.get("malfunction"),
                    category=category
                )
                weapon_types.append(weapon_type)
                print(weapon_type)
        return weapon_types
