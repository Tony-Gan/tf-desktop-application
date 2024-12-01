from typing import List, Tuple
from PyQt6.QtWidgets import QGridLayout, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QFont

from implements.components.base_phase import BasePhase
from ui.components.if_state_controll import IStateController
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_frame import TFBaseFrame
from ui.components.tf_font import NotoSerifNormal
from ui.tf_application import TFApplication


class Phase0(BasePhase):

    # TODO: 新增的自定义职业没加入TOKEN

    def _setup_content(self) -> None:
        super()._setup_content()

        self.buttons_frame.prev_button.hide()

        self.contents_frame.main_layout.setContentsMargins(10, 10, 10, 10)
        self.contents_frame.main_layout.setSpacing(40)

        self.generate_token_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="生成令牌", 
            height=35,
            width=120,
            font_family=QFont("Noto Serif SC"),
            on_clicked=self._on_token_generate_clicked
        )
        self.buttons_frame.add_custom_button(self.generate_token_button)

        self.points_entry = PointsEntry(self)
        self.destiny_entry = DestinyEntry(self)
        self.general_entry = GeneralEntry(self)
        self.base_entry = BaseEntry(self)

        self.contents_frame.add_child("base_entry", self.base_entry)
        self.contents_frame.add_child("points_entry", self.points_entry)
        self.contents_frame.add_child("destiny_entry", self.destiny_entry)
        self.contents_frame.add_child("general_entry", self.general_entry)
        self.contents_frame.main_layout.addStretch()

    def reset_contents(self):
        self.reset_validation_state()
        
        self.base_entry.mode_entry.set_value("选择模式")
        self.base_entry.token_entry.set_value("")
        self.base_entry.setEnabled(True)
        self.base_entry._handle_mode_change("选择模式")
        
        points_entry = self.points_entry
        points_entry.points_available_entry.set_value("480")
        points_entry.stats_upper_limit_entry.set_value("80")
        points_entry.stats_lower_limit_entry.set_value("30")
        points_entry.allow_custom_luck_entry.set_checked(False)
        points_entry.setEnabled(False)
        
        destiny_entry = self.destiny_entry
        destiny_entry.dice_count_entry.set_value("3")
        destiny_entry.allow_stats_exchange_entry.set_checked(False)
        destiny_entry.exchange_count_entry.set_value("1")
        destiny_entry.exchange_count_entry.set_enable(False)
        destiny_entry.setEnabled(False)
        
        general_entry = self.general_entry
        general_entry.occupation_skill_limit_entry.set_value("80")
        general_entry.interest_skill_limit_entry.set_value("60")
        general_entry.allow_mix_points_entry.set_checked(True)
        general_entry.allow_mythos_entry.set_checked(False)
        general_entry.custom_weapon_type_entry.set_checked(False)
        general_entry.completed_mode_entry.set_checked(False)
        general_entry.custom_occupation_entry.set_checked(False)
        general_entry.instruction_mode_entry.set_checked(False)
        general_entry.setEnabled(False)

    def initialize(self):
        pass

    def save_state(self):
        values = self.contents_frame.get_values()
        base_values = values.get('base_entry', {})
        points_values = values.get('points_entry', {})
        destiny_values = values.get('destiny_entry', {})
        general_values = values.get('general_entry', {})

        self.config['mode'] = base_values.get('mode', 'None')
        self.config['input_token'] = base_values.get('token', '')

        if self.config['mode'] == '购点':
            self.config['points'] = {
                'available': int(points_values.get('points_available', 480)),
                'upper_limit': int(points_values.get('states_upper_limit', 80)),
                'lower_limit': int(points_values.get('states_lower_limit', 30)),
                'custom_luck': points_values.get('allow_custom_luck', False)
            }
        elif self.config['mode'] == '天命':
            self.config['destiny'] = {
                'dice_count': destiny_values.get('dice_count', '3'),
                'allow_exchange': destiny_values.get('stats_exchange', False),
                'exchange_count': destiny_values.get('exchange_count', '1')
            }

        self.config['general'] = {
            'occupation_skill_limit': int(general_values.get('occupation_skill_limit', 80)),
            'interest_skill_limit': int(general_values.get('interest_skill_limit', 60)),
            'allow_mix_points': general_values.get('allow_mix_points', True),
            'allow_mythos': general_values.get('allow_mythos', False),
            'custom_weapon_type': general_values.get('custom_weapon_type', False),
            'completed_mode': general_values.get('completed_mode', False),
            'instruction_mode': general_values.get('instruction_mode', False),
            'custom_occupation': general_values.get('custom_occupation', False),
        }

        if 'metadata' not in self.p_data:
            self.p_data['metadata'] = {}
        self.p_data['metadata']['token'] = self._generate_token(values)

    def restore_state(self):
        pass

    def check_dependencies(self):
        pass

    def validate(self) -> List[Tuple[IStateController, str]]:
        invalid_items = []
        base_values = self.contents_frame.get_values().get('base_entry', {})
        mode = base_values.get('mode', 'None')
        
        if mode == '选择模式':
            invalid_items.append((self.base_entry.mode_entry, "请选择一个模式"))
            return invalid_items
            
        if mode == '购点':
            points_values = self.contents_frame.get_values().get('points_entry', {})
            
            points = int(points_values.get('points_available', 480))
            if points < 300 or points > 680:
                invalid_items.append(
                    (self.points_entry.points_available_entry, 
                     "可分配点数必须在 300 到 680 之间")
                )
            
            upper = int(points_values.get('states_upper_limit', 80))
            lower = int(points_values.get('states_lower_limit', 30))
            if upper <= lower:
                invalid_items.append(
                    (self.points_entry.stats_upper_limit_entry,
                     "属性上限必须大于属性下限")
                )
                invalid_items.append(
                    (self.points_entry.stats_lower_limit_entry,
                     "属性下限必须小于属性上限")
                )
            if upper > 90:
                invalid_items.append(
                    self.points_entry.stats_upper_limit_entry, "属性上限不能超过 90"
                )
            if lower < 10:
                invalid_items.append(
                    self.points_entry.stats_lower_limit_entry, "属性下限不能低于 10"
                )
                
        elif mode == '天命':
            destiny_values = self.contents_frame.get_values().get('destiny_entry', {})
            
            dice_count = int(destiny_values.get('dice_count', '3'))
            if dice_count < 1 or dice_count > 7:
                invalid_items.append(
                    (self.destiny_entry.dice_count_entry,
                     "骰子数量必须在 1 到 7 之间")
                )
            
            if destiny_values.get('stats_exchange', False):
                exchange_count = int(destiny_values.get('exchange_count', '1'))
                if exchange_count < 1 or exchange_count > 3:
                    invalid_items.append(
                        (self.destiny_entry.exchange_count_entry,
                         "属性交换次数必须在 1 到 3 之间")
                    )
        
        general_values = self.contents_frame.get_values().get('general_entry', {})
        
        occupation_limit = int(general_values.get('occupation_skill_limit', 80))
        if occupation_limit < 50 or occupation_limit > 95:
            invalid_items.append(
                (self.general_entry.occupation_skill_limit_entry,
                 "职业技能上限必须在 50 到 95 之间")
            )
            
        interest_limit = int(general_values.get('interest_skill_limit', 60))
        if interest_limit < 30 or interest_limit > 90:
            invalid_items.append(
                (self.general_entry.interest_skill_limit_entry,
                 "兴趣技能上限必须在 30 到 90 之间")
            )
            
        return invalid_items

    def _on_token_generate_clicked(self):
        values = self.contents_frame.get_values()
        token = self._generate_token(values)
        if token:
            try:
                TFApplication.clipboard().setText(token)
                TFApplication.instance().show_message(f"令牌已复制到剪贴板：{token}", 5000)
            except Exception:
                TFApplication.instance().show_message(f"生成的令牌（请手动复制）：{token}", 5000)

    def _generate_token(self, values: dict) -> str:
        base_values = values.get('base_entry', {})
        points_values = values.get('points_entry', {})
        destiny_values = values.get('destiny_entry', {})
        general_values = values.get('general_entry', {})

        mode = base_values.get('mode', 'None')
        if mode == 'None':
            return ""

        token_parts = []
        mode_prefix = 'PO' if mode == '购点' else 'DE'
        token_parts.append(mode_prefix)

        if mode == 'Points':
            points = int(points_values.get('points_available', 480))
            upper = int(points_values.get('states_upper_limit', 80))
            lower = int(points_values.get('states_lower_limit', 30))
            custom_luck = 'E' if points_values.get('allow_custom_luck', False) else 'L'
            
            token_parts.append(hex(points // 5)[2:].upper().zfill(2))
            token_parts.append(hex(upper)[2:].upper())
            token_parts.append(hex(lower)[2:].upper())
            token_parts.append(custom_luck)
        else:
            dice_count = destiny_values.get('dice_count', '3')
            allow_exchange = destiny_values.get('stats_exchange', False)
            exchange_count = destiny_values.get('exchange_count', '1')
            
            token_parts.append(f"{dice_count}DCE")
            token_parts.append('G' if allow_exchange else 'M')
            token_parts.append(f"{exchange_count}SC")

        token_parts.extend([
            hex(int(general_values.get('occupation_skill_limit', 80)))[2:].upper().zfill(2),
            hex(int(general_values.get('interest_skill_limit', 60)))[2:].upper().zfill(2),
            'Y' if general_values.get('allow_mix_points', True) else 'X',
            'J' if general_values.get('allow_mythos', False) else 'K',
            'I' if general_values.get('custom_weapon_type', False) else 'U',
            'A' if general_values.get('completed_mode', False) else 'C',
            'R' if general_values.get('instruction_mode', False) else 'T'
        ])

        return ''.join(token_parts)
    
    def go_next(self):
        TFApplication.instance().show_message("所有设置已锁定", 5000, 'green')

        self.base_entry.setEnabled(False)
        self.points_entry.setEnabled(False)
        self.destiny_entry.setEnabled(False)
        self.general_entry.setEnabled(False)
        super().go_next()


class BaseEntry(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setSpacing(20)

        self.mode_entry = self.create_option_entry(
            name="mode",
            label_text="模式选择:",
            label_font=NotoSerifNormal,
            options=["选择模式", "购点", "天命"],
            current_value="选择模式",
            label_size=65,
            value_size=100,
            height=24
        )
        self.mode_entry.value_changed.connect(self._handle_mode_change)
        self.mode_entry.label.setStyleSheet("color: #FFB700;")

        self.token_entry = self.create_value_entry(
            name="token",
            label_text="令牌:",
            label_font=NotoSerifNormal,
            label_size=65,
            value_size=300,
            height=24,
            show_tooltip=True,
            tooltip_text="KP提供的令牌，使用该令牌后，所有设置将自动完成，并无法进行修改。"
        )
        self.token_entry.value_changed.connect(self._handle_token_change)

        self._handle_mode_change("选择模式")

        self.main_layout.addWidget(self.mode_entry)
        self.main_layout.addWidget(self.token_entry)

    def _handle_token_change(self, token: str) -> None:
        if len(token) < 18:
            return
            
        if self._validate_token(token):
            self._apply_token(token)
        else:
            TFApplication.show_message("无效的令牌格式", 5000, "yellow")

    def _handle_mode_change(self, mode: str) -> None:
        self.parent.points_entry.setEnabled(False)
        self.parent.destiny_entry.setEnabled(False)
        self.parent.general_entry.setEnabled(False)

        if mode == "选择模式":
            self.mode_entry.label.setStyleSheet("color: #FFB700;")
        else:
            self.mode_entry.label.setStyleSheet("")

        if mode == "购点":
            self.parent.points_entry.setEnabled(True)
            self.parent.general_entry.setEnabled(True)
        elif mode == "天命":
            self.parent.destiny_entry.setEnabled(True)
            self.parent.general_entry.setEnabled(True)

    def _apply_token(self, token: str) -> None:
        mode = "购点" if token.startswith('PO') else "天命"
        self.mode_entry.set_value(mode)
        
        if mode == "Points":
            points = int(token[2:4], 16) * 5
            upper = int(token[4:6], 16)
            lower = int(token[6:8], 16)
            custom_luck = token[8] == 'E'
            
            points_entry = self.parent.points_entry
            points_entry.points_available_entry.set_value(str(points))
            points_entry.stats_upper_limit_entry.set_value(str(upper))
            points_entry.stats_lower_limit_entry.set_value(str(lower))
            points_entry.allow_custom_luck_entry.set_checked(custom_luck)
        else:
            dice_count = token[2]
            allow_exchange = token[6] == 'G'
            exchange_count = token[7]
            
            destiny_entry = self.parent.destiny_entry
            destiny_entry.dice_count_entry.set_value(dice_count)
            destiny_entry.allow_stats_exchange_entry.set_checked(allow_exchange)
            destiny_entry.exchange_count_entry.set_value(exchange_count)

        general_entry = self.parent.general_entry
        general_entry.occupation_skill_limit_entry.set_value(str(int(token[10:12], 16)))
        general_entry.interest_skill_limit_entry.set_value(str(int(token[12:14], 16)))
        general_entry.allow_mix_points_entry.set_checked(token[14] == 'Y')
        general_entry.allow_mythos_entry.set_checked(token[15] == 'J')
        general_entry.custom_weapon_type_entry.set_checked(token[16] == 'I')
        general_entry.completed_mode_entry.set_checked(token[17] == 'A')
        general_entry.instruction_mode_entry.set_checked(token[18] == 'R')

        self.setEnabled(False)

    def _validate_token(self, token: str) -> bool:
        try:
            if not (token.startswith('PO') or token.startswith('DE')):
                return False
                
            if token.startswith('PO'):
                int(token[2:4], 16)
                int(token[4:6], 16)
                int(token[6:8], 16)
                if token[8] not in ['E', 'L']:
                    return False
            else:
                if not (token[2].isdigit() and token[3:6] == 'DCE'):
                    return False
                if token[6] not in ['G', 'M']:
                    return False
                if not (token[7].isdigit() and token[8:10] == 'SC'):
                    return False

            int(token[10:12], 16)
            int(token[12:14], 16)
            if token[14] not in ['Y', 'X']:
                return False
            if token[15] not in ['J', 'K']:
                return False
            if token[16] not in ['I', 'U']:
                return False
            if token[17] not in ['A', 'C']:
                return False
            if token[18] not in ['R', 'T']:
                return False

            return True
        except (ValueError, IndexError):
            return False


class PointsEntry(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QGridLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setSpacing(20)

        self.points_available_entry = self.create_value_entry(
            name="points_available",
            label_text="可分配点数:",
            label_size=80,
            label_font=NotoSerifNormal,
            value_size=45,
            value_text=480,
            number_only=True,
            allow_decimal=False,
            max_digits=3,
            height=24
        )

        self.stats_upper_limit_entry = self.create_value_entry(
            name="states_upper_limit",
            label_text="属性上限:",
            label_size=60,
            label_font=NotoSerifNormal,
            value_size=30,
            value_text=80,
            number_only=True,
            allow_decimal=False,
            max_digits=2,
            height=24
        )

        self.stats_lower_limit_entry = self.create_value_entry(
            name="states_lower_limit",
            label_text="属性下限:",
            label_size=60,
            label_font=NotoSerifNormal,
            value_size=30,
            value_text=30,
            number_only=True,
            allow_decimal=False,
            max_digits=2,
            height=24
        )

        self.allow_custom_luck_entry = self.create_check_with_label(
            name="allow_custom_luck",
            label_text="启用自定义幸运",
            label_font=NotoSerifNormal,
            checked=False,
            height=24,
            show_tooltip=True,
            tooltip_text="勾选此选项需要将点数分配到幸运值（LUK）。如果未勾选，幸运值将通过掷骰子决定。"
        )

        self.main_layout.addWidget(self.points_available_entry, 0, 0)
        self.main_layout.addWidget(self.stats_upper_limit_entry, 0, 1)
        self.main_layout.addWidget(self.stats_lower_limit_entry, 0, 2)
        self.main_layout.addWidget(self.allow_custom_luck_entry, 1, 0)


class DestinyEntry(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QGridLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setSpacing(20)

        self.dice_count_entry = self.create_value_entry(
            name="dice_count",
            label_text="骰子数量:",
            label_size=80,
            label_font=NotoSerifNormal,
            value_size=30,
            value_text="3",
            number_only=True,
            allow_decimal=False,
            max_digits=1,
            height=24
        )

        self.allow_stats_exchange_entry = self.create_check_with_label(
            name="stats_exchange",
            label_text="启用属性交换",
            label_font=NotoSerifNormal,
            checked=False,
            height=24,
            show_tooltip=True,
            tooltip_text="勾选此选项允许在选择后交换两个属性值。"
        )
        self.allow_stats_exchange_entry.value_changed.connect(self._handle_exchange_change)

        self.exchange_count_entry = self.create_value_entry(
            name="exchange_count",
            label_text="属性交换次数:",
            value_text="1",
            label_size=90,
            value_size=30,
            label_font=NotoSerifNormal,
            number_only=True,
            allow_decimal=False,
            max_digits=1,
            height=24
        )

        dummy_spacer = QSpacerItem(40, 24, QSizePolicy.Policy.Expanding)

        self.main_layout.addWidget(self.dice_count_entry, 0, 0)
        self.main_layout.addWidget(self.allow_stats_exchange_entry, 1, 0)
        self.main_layout.addWidget(self.exchange_count_entry, 1, 1)
        self.main_layout.addItem(dummy_spacer, 1, 2)

        self.exchange_count_entry.set_enable(False)

    def _handle_exchange_change(self, state: bool):
        self.exchange_count_entry.set_enable(state)


class GeneralEntry(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QGridLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setSpacing(20)

        self.occupation_skill_limit_entry = self.create_value_entry(
            name="occupation_skill_limit",
            label_text="职业技能上限:",
            label_size=90,
            value_size=30,
            value_text=80,
            label_font=NotoSerifNormal,
            number_only=True,
            allow_decimal=False,
            max_digits=2,
            height=24,
            show_tooltip=True,
            tooltip_text="每项职业技能的点数上限。"
        )

        self.interest_skill_limit_entry = self.create_value_entry(
            name="interest_skill_limit",
            label_text="兴趣技能上限:",
            label_size=90,
            value_size=30,
            value_text=60,
            label_font=NotoSerifNormal,
            number_only=True,
            allow_decimal=False,
            max_digits=2,
            height=24,
            show_tooltip=True,
            tooltip_text="每项兴趣技能的点数上限。"
        )

        self.allow_mix_points_entry = self.create_check_with_label(
            name="allow_mix_points",
            label_text="启用混点",
            label_font=NotoSerifNormal,
            checked=True,
            height=24,
            show_tooltip=True,
            tooltip_text="勾选此选项允许同时将职业点数和兴趣点数分配给同一技能。"
        )

        tooltip = """
        勾选这个选项后，会开启克苏鲁神话相关的设置。克苏鲁神话技能会出现在技能分配阶段，背景设置里也会增加一些和克苏鲁背景有关的选项。
        """
        self.allow_mythos_entry = self.create_check_with_label(
            name="allow_mythos",
            label_text="启用神话",
            label_font=NotoSerifNormal,
            checked=False,
            height=24,
            show_tooltip=True,
            tooltip_text=tooltip
        )

        self.custom_weapon_type_entry = self.create_check_with_label(
            name="custom_weapon_type",
            label_text="自定义武器类型",
            label_font=NotoSerifNormal,
            height=24,
            show_tooltip=True,
            tooltip_text="勾选此选项后，可以完全自定义武器属性。"
        )

        self.completed_mode_entry = self.create_check_with_label(
            name="completed_mode",
            label_text="完整模式",
            label_font=NotoSerifNormal,
            height=24,
            show_tooltip=True,
            tooltip_text="勾选此选项后，会显示新卡片的非常规设置，包括防具，格斗技，法术，局内局外关系，经历包等。"
        )

        self.custom_occupation_entry = self.create_check_with_label(
            name="custom_occupation",
            label_text="自定义职业",
            label_font=NotoSerifNormal,
            checked=False,
            height=24,
            show_tooltip=True,
            tooltip_text="勾选此选项后，可以完全自定义职业。"
        )

        self.instruction_mode_entry = self.create_check_with_label(
            name="instruction_mode",
            label_text="引导模式",
            label_font=NotoSerifNormal,
            checked=False,
            height=24,
            show_tooltip=True,
            tooltip_text="勾选此选项后，将启用引导模式，适合新手使用。"
        )

        self.main_layout.addWidget(self.occupation_skill_limit_entry, 0, 0)
        self.main_layout.addWidget(self.interest_skill_limit_entry, 0, 1)
        self.main_layout.addWidget(self.allow_mix_points_entry, 0, 2)
        self.main_layout.addWidget(self.allow_mythos_entry, 1, 0)
        self.main_layout.addWidget(self.custom_weapon_type_entry, 1, 1)
        self.main_layout.addWidget(self.completed_mode_entry, 1, 2)
        self.main_layout.addWidget(self.custom_occupation_entry, 2, 0)
        self.main_layout.addWidget(self.instruction_mode_entry, 2, 1)
