import re
import random
from enum import Enum
from typing import Tuple, List


class CheckResult(Enum):
    CRITICAL_FAILURE = -2
    FAILURE = -1
    SUCCESS = 0
    HARD_SUCCESS = 1
    EXTREME_SUCCESS = 2
    CRITICAL_SUCCESS = 3


class TFDice:
    VALID_FACES = {2, 3, 4, 6, 8, 10, 12, 20, 100}

    @staticmethod
    def roll(dice_str: str) -> Tuple[bool, str, List[int], int]:
        default_res = (False, dice_str, [], 0)

        if not dice_str or not dice_str.strip():
            return default_res
        
        try:
            pattern = r'([+-]?\s*\d*d\d+|[+-]?\s*\d+)'
            parts = re.findall(pattern, dice_str)

            if not parts:
                return default_res
            
            formatted_parts = []
            results = []
            total = 0

            for part in parts:
                part = part.strip()

                if part.lstrip('+-').isdigit():
                    number = int(part)
                    total += number
                    formatted_parts.append(part)
                    continue

                match = re.match(r'([+-]?\s*)?(\d*)[dD](\d+)', part)
                if not match:
                    return default_res
                
                sign = match.group(1) or ''
                count = match.group(2)
                faces = int(match.group(3))

                if faces not in TFDice.VALID_FACES:
                    return default_res
                
                count = int(count) if count else 1

                rolls = [random.randint(1, faces) for _ in range(count)]
                results.extend(rolls)
                roll_sum = sum(rolls)

                if sign == '-':
                    total -= roll_sum
                else:
                    total += roll_sum

                formatted_part = f"{sign}{count}d{faces}" if sign else f"{count}d{faces}"
                formatted_parts.append(formatted_part)

            formatted_str = formatted_parts[0]
            for part in formatted_parts[1:]:
                if part.startswith('+') or part.startswith('-'):
                    formatted_str += f"{part}"
                else:
                    formatted_str += f"+{part}"

            return True, formatted_str, results, total
        
        except Exception:
            return default_res
        
    @staticmethod
    def skill_check(skill_level: int, rule_type: int = 1) -> Tuple[bool, int, CheckResult]:
        roll_success, _, _, dice_result = TFDice.roll("d100")
        
        if not roll_success:
            return False, 0, CheckResult.FAILURE
        
        check_level = TFDice._check_result(skill_level, dice_result, rule_type)
        
        return True, dice_result, check_level
    
    @staticmethod
    def versus_check(skill1: int, skill2: int, higher_level_required: bool = False, rule_type: int = 1) -> Tuple[bool, Tuple[int, int], Tuple[CheckResult, CheckResult], bool]:
        roll1_success, dice1, level1 = TFDice.skill_check(skill1, rule_type)
        roll2_success, dice2, level2 = TFDice.skill_check(skill2, rule_type)
        
        if not roll1_success or not roll2_success:
            return False, (0, 0), (CheckResult.FAILURE, CheckResult.FAILURE), False
            
        if higher_level_required:
            skill1_wins = level1.value > level2.value
        else:
            if level1.value != level2.value:
                skill1_wins = level1.value > level2.value
            else:
                if skill1 != skill2:
                    skill1_wins = skill1 > skill2
                else:
                    if dice1 != dice2:
                        skill1_wins = dice1 < dice2
                    else:
                        skill1_wins = False
        
        return True, (dice1, dice2), (level1, level2), skill1_wins
        
    @staticmethod
    def _check_result(skill_level: int, dice_result: int, rule_type: int = 1) -> CheckResult:
        if rule_type not in [1, 2, 3, 4]:
            rule_type = 1
            
        if rule_type == 1:
            if (skill_level < 50 and dice_result >= 96) or dice_result == 100:
                return CheckResult.CRITICAL_FAILURE
            if dice_result == 1:
                return CheckResult.CRITICAL_SUCCESS
        elif rule_type == 2:
            if dice_result >= 98:
                return CheckResult.CRITICAL_FAILURE
            if dice_result <= 3:
                return CheckResult.CRITICAL_SUCCESS
        elif rule_type == 3:
            if dice_result >= 96:
                return CheckResult.CRITICAL_FAILURE
            if dice_result <= 5:
                return CheckResult.CRITICAL_SUCCESS
        elif rule_type == 4:
            if dice_result == 100:
                return CheckResult.CRITICAL_FAILURE
            if dice_result == 1:
                return CheckResult.CRITICAL_SUCCESS
                
        if dice_result <= skill_level:
            if dice_result <= skill_level // 5:
                return CheckResult.EXTREME_SUCCESS
            elif dice_result <= skill_level // 2:
                return CheckResult.HARD_SUCCESS
            return CheckResult.SUCCESS
            
        return CheckResult.FAILURE
