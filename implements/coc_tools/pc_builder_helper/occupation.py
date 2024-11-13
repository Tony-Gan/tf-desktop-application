from dataclasses import dataclass
from typing import Dict, List

INTERPERSONAL_SKILLS: List[str] = ["charm", "fast_talk", "intimidate", "persuade"]

@dataclass
class Occupation:
    name: str
    skill_points_formula: str
    occupation_skills: str
    category: str
    credit_rating: str

    def __str__(self):
        return f"{self.name} ({self.category})"

    def format_formula_for_display(self) -> str:
        return self.skill_points_formula.replace('*', '×').replace('MAX', 'max')

    def _calculate_max_stats(self, stats_str: str, stats: Dict[str, int]) -> int:
        stats_list = [s.strip() for s in stats_str.split(',')]
        return max(stats.get(stat, 0) for stat in stats_list)

    def calculate_skill_points(self, stats: Dict[str, int]) -> int:
        parts = self.skill_points_formula.split('+')
        total = 0

        for part in parts:
            part = part.strip()
            if 'MAX(' in part:
                stat_str = part[part.find('(') + 1:part.find(')')]
                max_value = self._calculate_max_stats(stat_str, stats)
                multiplier = int(part[part.find('*') + 1:])
                total += max_value * multiplier
            else:
                stat = part[:part.find('*')]
                multiplier = int(part[part.find('*') + 1:])
                total += stats.get(stat, 0) * multiplier

        return total

    def get_skills(self) -> str:
        return self.occupation_skills
    
    def get_credit_rating_min(self) -> int:
        return int(self.credit_rating.split('-')[0])

    def get_credit_rating_max(self) -> int:
        return int(self.credit_rating.split('-')[1])

    @classmethod
    def from_json(cls, data: Dict) -> 'Occupation':
        return cls(
            name=data["name"],
            skill_points_formula=data["skill_points_formula"],
            occupation_skills=data["occupation_skills"],
            category=data["category"],
            credit_rating=data["credit_rating"]
        )
