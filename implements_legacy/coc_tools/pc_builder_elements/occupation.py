from dataclasses import dataclass
from typing import Dict, List

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
        return self.skill_points_formula.replace('*', '×').replace('MAX', 'max')
    
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

    def _calculate_max_stats(self, stats_str: str, stats: Dict[str, int]) -> int:
        stats_list = [s.strip() for s in stats_str.split(',')]
        return max(stats.get(stat, 0) for stat in stats_list)

    def calculate_skill_points(self, stats: Dict[str, int]) -> int:
        formula = self.skill_points_formula
        parts = [p.strip() for p in formula.split('+')]
        total = 0

        for part in parts:
            if 'MAX(' in part:
                max_content = part[part.find('(') + 1:part.find(')')].strip()
                total += self._calculate_max_stats(max_content, stats)
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
        
        for skill in skills:
            skill = skill.strip()
            
            if '|' in skill:
                sub_skills = [self._format_single_skill(s.strip()) for s in skill.split('|')]
                formatted = ' / '.join(sub_skills)
            else:
                formatted = self._format_single_skill(skill)
                
            formatted_skills.append(formatted)
        
        return ', '.join(formatted_skills)

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
            category=data["category"] if isinstance(data["category"], list) else [data["category"]],  # 处理新旧两种格式
            credit_rating=data["credit_rating"]
        )
