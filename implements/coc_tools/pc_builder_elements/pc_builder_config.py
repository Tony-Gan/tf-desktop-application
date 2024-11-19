from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum

from utils.validator.tf_validation_rules import TFValidationRule
from utils.validator.tf_validator import TFValidator


class GenerationMode(Enum):
    POINTS = "points"
    DESTINY = "destiny"


@dataclass
class PCBuilderConfig:
    generation_mode: str = GenerationMode.DESTINY.value
    points_available: int = 480
    dice_count: int = 3
    stat_upper_limit: int = 80
    stat_lower_limit: int = 20
    allow_custom_luck: bool = False
    occupation_skill_limit: int = 90
    interest_skill_limit: int = 60
    allow_mixed_points: bool = True
    allow_stat_exchange: bool = False
    stat_exchange_times: int = 0

    def update_from_dict(self, settings_dict: Dict[str, Any]) -> None:
        for key, value in settings_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'generation_mode': self.generation_mode,
            'points_available': self.points_available,
            'dice_count': self.dice_count,
            'stat_upper_limit': self.stat_upper_limit,
            'stat_lower_limit': self.stat_lower_limit,
            'allow_custom_luck': self.allow_custom_luck,
            'occupation_skill_limit': self.occupation_skill_limit,
            'interest_skill_limit': self.interest_skill_limit,
            'allow_mixed_points': self.allow_mixed_points,
            'allow_stat_exchange': self.allow_stat_exchange,
            'stat_exchange_times': self.stat_exchange_times
        }

    def get_mode_specific_settings(self) -> Dict[str, Any]:
        if self.is_points_mode():
            return {
                'points_available': self.points_available,
                'stat_upper_limit': self.stat_upper_limit,
                'stat_lower_limit': self.stat_lower_limit,
                'allow_custom_luck': self.allow_custom_luck
            }
        else:
            return {
                'dice_count': self.dice_count
            }

    def is_points_mode(self) -> bool:
        return self.generation_mode == GenerationMode.POINTS.value

    def is_destiny_mode(self) -> bool:
        return self.generation_mode == GenerationMode.DESTINY.value

    @staticmethod
    def setup_validator(validator: 'TFValidator') -> None:
        validator.add_rules({
            'generation_mode': TFValidationRule(
                type_=str,
                required=True,
                choices=['points', 'destiny'],
                error_messages={'choices': 'Invalid generation mode'}
            ),
            'points_available': TFValidationRule(
                type_=int,
                required=False,
                min_val=1,
                max_val=1000
            ),
            'dice_count': TFValidationRule(
                type_=int,
                required=False,
                min_val=1,
                max_val=10
            ),
            'stat_upper_limit': TFValidationRule(
                type_=int,
                required=False,
                min_val=1,
                max_val=100
            ),
            'stat_lower_limit': TFValidationRule(
                type_=int,
                required=False,
                min_val=1,
                max_val=100
            ),
            'allow_custom_luck': TFValidationRule(
                type_=bool,
                required=False
            ),
            'occupation_skill_limit': TFValidationRule(
                type_=int,
                required=True,
                min_val=1,
                max_val=100
            ),
            'interest_skill_limit': TFValidationRule(
                type_=int,
                required=True,
                min_val=1,
                max_val=100
            ),
            'stat_exchange_times': TFValidationRule(
                type_=int,
                required=False,
                min_val=0,
                max_val=5
            )
        })

        validator.add_custom_validator(
            'stat_limits',
            lambda lower, upper: (
                int(lower) <= int(upper),
                "Lower limit cannot be greater than upper limit"
            )
        )

        validator.add_custom_validator(
            'skill_limits',
            lambda interest, occupation: (
                int(interest) <= int(occupation),
                "Interest skill limit cannot exceed occupation skill limit"
            )
        )