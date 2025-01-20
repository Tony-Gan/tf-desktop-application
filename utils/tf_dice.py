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
                count_str = match.group(2)
                faces = int(match.group(3))

                if faces not in TFDice.VALID_FACES:
                    return default_res

                count = int(count_str) if count_str else 1

                rolls_now = [random.randint(1, faces) for _ in range(count)]
                results.extend(rolls_now)
                roll_sum = sum(rolls_now)

                if sign.strip() == '-':
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

        except (ValueError, TypeError) as e:
            print(f"Error parsing dice string '{dice_str}': {e}")
            return default_res

    @staticmethod
    def _roll_coc_d100(advantage_dice: int = 0) -> Tuple[int, List[int]]:
        tens_count = 1 + abs(advantage_dice)
        tens_rolls = [random.randint(0, 9) for _ in range(tens_count)]
        ones_digit = random.randint(0, 9)

        possible_results = []
        for t in tens_rolls:
            if t == 0 and ones_digit == 0:
                possible_results.append(100)
            else:
                possible_results.append(t * 10 + ones_digit)

        if advantage_dice >= 0:
            final_result = min(possible_results)
        else:
            final_result = max(possible_results)

        return final_result, possible_results

    @staticmethod
    def skill_check(
        skill_level: int,
        rule_type: int = 1,
        advantage_dice: int = 0
    ) -> Tuple[bool, int, Tuple[int, ...], CheckResult]:
        if skill_level < 1:
            return False, 0, (), CheckResult.FAILURE
        
        final_result, all_results = TFDice._roll_coc_d100(advantage_dice)
        check_level = TFDice._check_result(skill_level, final_result, rule_type)

        return True, final_result, tuple(all_results), check_level

    @staticmethod
    def versus_check(
        skill1: int,
        skill2: int,
        advantage_dice1: int = 0,
        advantage_dice2: int = 0,
        higher_level_required: bool = False,
        rule_type: int = 1
    ) -> Tuple[
        bool,
        Tuple[int, int],
        Tuple[Tuple[int, ...], Tuple[int, ...]],
        Tuple[CheckResult, CheckResult],
        bool
    ]:
        if skill1 < 1 or skill2 < 1:
            return False, (0, 0), ((), ()), (CheckResult.FAILURE, CheckResult.FAILURE), False
        
        final1, all_res1 = TFDice._roll_coc_d100(advantage_dice1)
        level1 = TFDice._check_result(skill1, final1, rule_type)

        final2, all_res2 = TFDice._roll_coc_d100(advantage_dice2)
        level2 = TFDice._check_result(skill2, final2, rule_type)

        roll_success = True

        if higher_level_required:
            skill1_wins = (level1.value > level2.value)
        else:
            if level1.value != level2.value:
                skill1_wins = (level1.value > level2.value)
            else:
                if skill1 != skill2:
                    skill1_wins = (skill1 > skill2)
                else:
                    if final1 != final2:
                        skill1_wins = (final1 < final2)
                    else:
                        skill1_wins = False

        return roll_success, (final1, final2), (tuple(all_res1), tuple(all_res2)), (level1, level2), skill1_wins

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

    @staticmethod
    def command_entry(cmd: str):
        """
        根据指令字符串 cmd，分析要进行的功能，然后调用相应方法。
        指令格式:
          1) r   [dice_str]           => 普通掷骰, 例如: r 3d10+4
          2) ra  [skill] [可选: bN或pN] => 技能检定, 例如: ra 50 / ra 50 b1 / ra 30 p2
          3) rav [skill1] [可选:bN/pN] [skill2] [可选:bN/pN] [可选:s] => 对抗检定, 例如: rav 50 60 / rav 50 b1 60 p2 / rav 24 35 s
          4) rah 同 rav，只是指令不同（可以复用相同逻辑） 
          5) rh  => 暂时留空, 暗骰
        """

        cmd = cmd.strip()
        if not cmd:
            return {"success": False, "error": "Empty command."}

        # 将指令部分和参数部分分开
        parts = cmd.split(' ', 1)
        command_main = parts[0].lower()
        command_args = parts[1].strip() if len(parts) > 1 else ""

        if command_main == 'r':
            # 普通掷骰
            ok, formula, results, total = TFDice.roll(command_args)
            return {
                "success": ok,
                "type": "normal_roll",
                "formula": formula,
                "results": results,
                "total": total
            }

        elif command_main == 'ra':
            # 技能检定
            # 格式: ra skill [bN|pN]?
            # 例如: ra 50, ra 50 b1, ra 50 p3
            pattern = r'^\s*(\d+)(?:\s+(b|p)(\d+))?\s*$'
            match = re.match(pattern, command_args, re.IGNORECASE)
            if not match:
                return {"success": False, "error": "参数格式不正确，请使用: ra <技能值> [bN | pN]"}

            skill_str = match.group(1)
            adv_type = match.group(2)
            adv_count = match.group(3)

            skill_level = int(skill_str)
            advantage_dice = 0

            if adv_type and adv_count:
                if adv_type.lower() == 'b':
                    advantage_dice = int(adv_count)  # 优势
                else:
                    advantage_dice = -int(adv_count) # 劣势

            ok, final_result, all_results, check_level = TFDice.skill_check(
                skill_level, rule_type=1, advantage_dice=advantage_dice
            )
            return {
                "success": ok,
                "type": "skill_check",
                "skill": skill_level,
                "advantage_dice": advantage_dice,
                "final_result": final_result,
                "all_results": all_results,
                "check_level": check_level
            }

        elif command_main in ('rav', 'rah'):
            # 对抗检定
            # 格式: rav skill1 [bN|pN]? skill2 [bN|pN]? [s]?
            # 例如:
            #   rav 50 60
            #   rav 50 b1 60 p2
            #   rah 24 b3 35 s
            #   （最后的 s 表示严格模式，否则不是）
            pattern = r'^\s*(\d+)(?:\s+(b|p)(\d+))?\s+(\d+)(?:\s+(b|p)(\d+))?(?:\s+(s))?\s*$'
            match = re.match(pattern, command_args, re.IGNORECASE)
            if not match:
                return {"success": False, "error": "对抗掷参数格式不正确，请参考: rav <技能1> [bN|pN] <技能2> [bN|pN] [s]"}

            skill1_str = match.group(1)
            adv_type1  = match.group(2)
            adv_count1 = match.group(3)

            skill2_str = match.group(4)
            adv_type2  = match.group(5)
            adv_count2 = match.group(6)

            strict_flag = match.group(7)  # 's' 或 None

            skill1 = int(skill1_str)
            skill2 = int(skill2_str)

            advantage_dice1 = 0
            advantage_dice2 = 0

            if adv_type1 and adv_count1:
                if adv_type1.lower() == 'b':
                    advantage_dice1 = int(adv_count1)
                else:
                    advantage_dice1 = -int(adv_count1)

            if adv_type2 and adv_count2:
                if adv_type2.lower() == 'b':
                    advantage_dice2 = int(adv_count2)
                else:
                    advantage_dice2 = -int(adv_count2)

            higher_level_required = (strict_flag is not None)

            ok, finals, all_res, levels, skill1_wins = TFDice.versus_check(
                skill1, skill2,
                advantage_dice1, advantage_dice2,
                higher_level_required=higher_level_required,
                rule_type=1
            )
            return {
                "success": ok,
                "type": "versus_check",
                "skills": (skill1, skill2),
                "advantage_dice": (advantage_dice1, advantage_dice2),
                "final_results": finals,
                "all_results": all_res,
                "check_levels": levels,
                "strict_mode": higher_level_required,
                "skill1_wins": skill1_wins
            }

        elif command_main == 'rh':
            # 暗骰 - 这里先做占位，未来可以根据需求实现
            return {
                "success": True,
                "type": "hidden_roll",
                "info": "尚未实现具体暗骰逻辑"
            }

        else:
            return {"success": False, "error": f"未知指令: {command_main}"}
