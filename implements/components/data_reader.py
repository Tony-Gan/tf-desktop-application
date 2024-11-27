import json
from typing import List

from implements.components.data_enum import Category, Penetration
from implements.components.data_type import CombatSkill, WeaponType, Range, Damage, WeaponSkill, Skill, Occupation
from utils.helper import resource_path


def load_occupations_from_json() -> List[Occupation]:
    with open(resource_path("implements/data/occupations.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    occupations = [Occupation.from_json(entry) for entry in data]
    return occupations

def load_skills_from_json( dex: int, edu: int, language_own: str) -> List[Skill]:
    skills = []

    with open(resource_path("implements/data/default_skills.json"), 'r', encoding='utf-8') as file:
        data = json.load(file)

        for skill_key, default_point in data.items():
            name = skill_key.split(":")[1] if ":" in skill_key else skill_key
            super_name = skill_key.split(":")[0] if ":" in skill_key else None

            if name == 'dodge':
                default_point = dex // 2
            elif name == 'language_own':
                name = language_own
                default_point = edu

            skill = Skill(
                name=name,
                super_name=super_name,
                default_point=default_point
            )
            skills.append(skill)

    return skills


def load_weapon_types_from_json() -> List[WeaponType]:
    weapon_types = []
    with open(resource_path("implements/data/weapon_types.json"), 'r', encoding='utf-8') as file:
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


def load_combat_skills_from_json() -> List[CombatSkill]:
    combat_skills = []

    with open(resource_path("implements/data/combat_skills.json"), 'r', encoding='utf-8') as file:
        data = json.load(file)

        for name, details in data.items():
            damage = details.get("damage", "1D3 + DB")
            techniques = details.get("techniques", {})

            combat_skill = CombatSkill(
                name=name,
                damage=damage,
                techniques=techniques
            )

            combat_skills.append(combat_skill)

    return combat_skills
