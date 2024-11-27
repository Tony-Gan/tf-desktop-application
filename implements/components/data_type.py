import re
from dataclasses import dataclass
from typing import List, Optional, Dict

from implements.components.data_enum import Penetration, Category

@dataclass
class Skill:
    name: str
    super_name: str
    default_point: int
    is_occupation: bool = False
    occupation_point: int = 0
    interest_point: int = 0

    @property
    def total_point(self) -> int:
        return self.default_point + self.occupation_point + self.interest_point

    @property
    def display_name(self) -> str:
        formatted_name = self.name.replace("_", " ").title()
        if self.super_name:
            formatted_super_name = self.super_name.replace("_", " ").title()
            return f"{formatted_super_name} - {formatted_name}"
        return formatted_name


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


@dataclass
class CombatSkill:
    name: str
    damage: str
    techniques: Dict[str, str]


@dataclass
class Spell:
    name: str
    pow_cost: str
    mag_cost: str
    san_cost: str
    casting_time: str
    description: str

@dataclass
class Occupation:
    name: str
    skill_points_formula: str
    occupation_skills: str
    category: List[str]
    credit_rating: str

    def __str__(self):
        return f"{self.name} ({self.category[0]})" 

    def format_formula_for_display(self) -> str:
        return self.skill_points_formula.replace('*', ' × ').replace('+', ' + ').replace(',', ', ')
    
    def _calculate_max_stats(self, formula_part: str, stats: Dict[str, int]) -> int:
        parts = [part.strip() for part in formula_part.split(',')]
        results = []
        
        for part in parts:
            if '*' in part:
                stat, multiplier = part.split('*')
                stat_value = stats.get(stat.strip(), 0)
                results.append(stat_value * int(multiplier))
            else:
                results.append(stats.get(part.strip(), 0))
                
        return max(results)

    def calculate_skill_points(self, stats: Dict[str, int]) -> int:
        formula = self.skill_points_formula
        parts = [p.strip() for p in formula.split('+')]
        total = 0

        for part in parts:
            if 'MAX(' in part:
                max_content = part[part.find('(') + 1:part.find(')')].strip()
                max_value = self._calculate_max_stats(max_content, stats)
                if '*' in part:
                    multiplier = int(part.split('*')[-1])
                    max_value *= multiplier
                total += max_value
            else:
                if '*' in part:
                    stat, multiplier = part.split('*')
                    stat_value = stats.get(stat.strip(), 0)
                    total += stat_value * int(multiplier)
                else:
                    total += stats.get(part.strip(), 0)

        return total

    def get_skills(self) -> str:
        return self.occupation_skills
    
    def get_credit_rating_min(self) -> int:
        return int(self.credit_rating.split('-')[0])

    def get_credit_rating_max(self) -> int:
        return int(self.credit_rating.split('-')[1])
    
    def format_skills(self) -> str:
        skills = self.occupation_skills.split(',')
        formatted_skills = []
        
        for i, skill in enumerate(skills):
            skill = skill.strip()
            
            if '|' in skill:
                sub_skills = [self._format_single_skill(s.strip()) for s in skill.split('|')]
                formatted = ' / '.join(sub_skills)
            else:
                formatted = self._format_single_skill(skill)
            
            formatted_skills.append(formatted)
            if i == 3:
                formatted_skills.append('\n')
        
        result = ''
        for i, skill in enumerate(formatted_skills):
            if skill == '\n':
                result += skill
            elif result.endswith('\n'):
                result += skill
            else:
                result += (', ' if i > 0 else '') + skill
        
        return result

    def _format_single_skill(self, skill: str) -> str:
        if ':' in skill:
            category, subtype = skill.split(':')
            if subtype == 'any':
                return f"{category.replace('_', ' ').title()} - Any Skill"
            return f"{category.replace('_', ' ').title()} - {subtype.replace('_', ' ').title()}"
        if skill == 'any':
            return "Any Skill"
        return skill.replace('_', ' ').title()

    @classmethod
    def from_json(cls, data: Dict) -> 'Occupation':
        return cls(
            name=data["name"],
            skill_points_formula=data["skill_points_formula"], 
            occupation_skills=data["occupation_skills"],
            category=data["category"] if isinstance(data["category"], list) else [data["category"]],
            credit_rating=data["credit_rating"]
        )

