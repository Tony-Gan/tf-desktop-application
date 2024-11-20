import json
from typing import Tuple, Dict, Optional, List

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QDialog, QFrame, QGridLayout, QButtonGroup, QRadioButton, \
    QGroupBox, QLabel, QComboBox, QLineEdit

from implements.coc_tools.coc_data.data_type import Skill, WeaponType, CombatSkill
from utils.validator.tf_validation_rules import TFValidationRule
from utils.helper import resource_path
from ui.components.tf_computing_dialog import TFComputingDialog
from ui.components.tf_separator import TFSeparator
from ui.components.tf_base_button import TFBaseButton


class RuleSettingsDialog(TFComputingDialog):
    def __init__(self, parent=None, **kwargs):
        self.current_settings = kwargs.get('current_settings', {})
        super().__init__("Rule Settings", parent)
        self.setup_validation_rules()
        self.setup_content()

    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.mode_combo = self.create_option_entry(
            "Generation Mode:",
            options=["Points", "Destiny"],
            current_value="Destiny" if self.current_settings.get('generation_mode') == "destiny" else "Points",
            label_size=200,
            value_size=100
        )
        self.mode_combo.value_changed.connect(self._on_mode_changed)
        layout.addWidget(self.mode_combo)

        self.points_dice_container = QWidget()
        points_dice_layout = QVBoxLayout(self.points_dice_container)
        points_dice_layout.setContentsMargins(0, 0, 0, 0)
        points_dice_layout.setSpacing(8)
        layout.addWidget(self.points_dice_container)

        self.points_entry = self.create_value_entry(
            "Available Points:",
            number_only=True,
            label_size=200,
            value_size=50
        )
        points_dice_layout.addWidget(self.points_entry)
        self.points_entry.set_value(str(self.current_settings.get('points_available', 480)))

        self.upper_limit_entry = self.create_value_entry(
            "Stat Upper Limit:",
            number_only=True,
            label_size=200,
            value_size=50
        )
        points_dice_layout.addWidget(self.upper_limit_entry)
        self.upper_limit_entry.set_value(str(self.current_settings.get('stat_upper_limit', 80)))

        self.lower_limit_entry = self.create_value_entry(
            "Stat Lower Limit:",
            number_only=True,
            label_size=200,
            value_size=50
        )
        points_dice_layout.addWidget(self.lower_limit_entry)
        self.lower_limit_entry.set_value(str(self.current_settings.get('stat_lower_limit', 20)))

        self.custom_luck_checkbox = self.create_check_with_label(
            "Custom Luck Value",
            checked=self.current_settings.get('allow_custom_luck', False)
        )
        points_dice_layout.addWidget(self.custom_luck_checkbox)

        self.dice_entry = self.create_value_entry(
            "Number of Dice:",
            number_only=True,
            label_size=200,
            value_size=50
        )
        points_dice_layout.addWidget(self.dice_entry)
        self.dice_entry.set_value(str(self.current_settings.get('dice_count', 3)))

        layout.addWidget(TFSeparator.horizontal())
        self.occupation_limit_entry = self.create_value_entry(
            "Occupation Skill Limit:",
            number_only=True,
            label_size=200,
            value_size=50
        )
        self.occupation_limit_entry.set_value(
            str(self.current_settings.get('occupation_skill_limit', 90))
        )
        layout.addWidget(self.occupation_limit_entry)

        self.interest_limit_entry = self.create_value_entry(
            "Interest Skill Limit:",
            number_only=True,
            label_size=200,
            value_size=50
        )
        self.interest_limit_entry.set_value(
            str(self.current_settings.get('interest_skill_limit', 60))
        )
        layout.addWidget(self.interest_limit_entry)

        self.mixed_points_checkbox = self.create_check_with_label(
            "Allow mixing occupation and interest points",
            checked=self.current_settings.get('allow_mixed_points', True)
        )
        layout.addWidget(self.mixed_points_checkbox)

        exchange_layout = QHBoxLayout()
        exchange_layout.setContentsMargins(0, 0, 0, 0)

        self.stat_exchange_checkbox = self.create_check_with_label(
            "Allow stat exchange",
            checked=self.current_settings.get('allow_stat_exchange', False)
        )
        self.stat_exchange_checkbox.value_changed.connect(self._on_exchange_changed)
        exchange_layout.addWidget(self.stat_exchange_checkbox)

        exchange_widget = QWidget()
        exchange_widget.setFixedHeight(24)
        exchange_widget_layout = QHBoxLayout(exchange_widget)
        exchange_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.exchange_times_entry = self.create_value_entry(
            "Exchange Times:",
            number_only=True,
            label_size=120,
            value_size=30
        )
        self.exchange_times_entry.set_value(
            str(self.current_settings.get('stat_exchange_times', 0))
        )
        self.exchange_times_entry.setVisible(
            self.current_settings.get('allow_stat_exchange', False)
        )
        exchange_widget_layout.addWidget(self.exchange_times_entry)

        exchange_layout.addWidget(exchange_widget)
        exchange_layout.addStretch()

        layout.addLayout(exchange_layout)

        self._on_mode_changed(self.mode_combo.get_value())
        self.set_dialog_size(400, 380)

    def setup_validation_rules(self):
        self.validator.add_rules({
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
                max_val=1000,
                error_messages={
                    'min': 'Points must be at least 1',
                    'max': 'Points cannot exceed 1000'
                }
            ),
            'dice_count': TFValidationRule(
                type_=int,
                required=False,
                min_val=1,
                max_val=8,
                error_messages={
                    'min': 'Must roll at least 1 die',
                    'max': 'Cannot roll more than 8 dice'
                }
            ),
            'stat_upper_limit': TFValidationRule(
                type_=int,
                required=False,
                min_val=1,
                max_val=100,
                error_messages={
                    'min': 'Upper limit must be at least 1',
                    'max': 'Upper limit cannot exceed 100'
                }
            ),
            'stat_lower_limit': TFValidationRule(
                type_=int,
                required=False,
                min_val=1,
                max_val=100,
                error_messages={
                    'min': 'Lower limit must be at least 1',
                    'max': 'Lower limit cannot exceed 100'
                }
            ),
            'allow_custom_luck': TFValidationRule(
                type_=bool,
                required=False
            ),
            'occupation_skill_limit': TFValidationRule(
                type_=int,
                required=True,
                min_val=1,
                max_val=100,
                error_messages={
                    'required': 'Occupation skill limit is required',
                    'min': 'Limit must be at least 1',
                    'max': 'Limit cannot exceed 100'
                }
            ),
            'interest_skill_limit': TFValidationRule(
                type_=int,
                required=True,
                min_val=1,
                max_val=100,
                error_messages={
                    'required': 'Interest skill limit is required',
                    'min': 'Limit must be at least 1',
                    'max': 'Limit cannot exceed 100'
                }
            )
        })

        self.validator.add_custom_validator(
            'stat_limits',
            lambda lower, upper: (
                int(lower) <= int(upper),
                "Lower limit cannot be greater than upper limit"
            )
        )

        self.validator.add_custom_validator(
            'skill_limits',
            lambda interest, occupation: (
                int(interest) <= int(occupation),
                "Interest skill limit cannot exceed occupation skill limit"
            )
        )

        self.validator.add_rules({
            'stat_exchange_times': TFValidationRule(
                type_=int,
                required=False,
                min_val=0,
                max_val=5,
                error_messages={
                    'min': 'Exchange times cannot be negative',
                    'max': 'Exchange times cannot exceed 5'
                }
            )
        })

    def get_field_values(self):
        mode = self.mode_combo.get_value().lower()
        values = {
            'generation_mode': mode,
            'occupation_skill_limit': self.occupation_limit_entry.get_value(),
            'interest_skill_limit': self.interest_limit_entry.get_value(),
            'allow_mixed_points': self.mixed_points_checkbox.get_value(),
            'allow_stat_exchange': self.stat_exchange_checkbox.get_value(),
            'stat_exchange_times': self.exchange_times_entry.get_value() if self.stat_exchange_checkbox.get_value() else "0"
        }

        if mode == 'points':
            values.update({
                'points_available': self.points_entry.get_value(),
                'stat_upper_limit': self.upper_limit_entry.get_value(),
                'stat_lower_limit': self.lower_limit_entry.get_value(),
                'allow_custom_luck': self.custom_luck_checkbox.get_value()
            })
        else:
            values['dice_count'] = self.dice_entry.get_value()
            values['allow_custom_luck'] = False

        return values

    def process_validated_data(self, data):
        if data['generation_mode'] == 'points':
            if not self.validator.validate_field('stat_limits', (data['stat_lower_limit'], data['stat_upper_limit']))[
                0]:
                raise ValueError("Lower limit cannot be greater than upper limit")

        if not \
        self.validator.validate_field('skill_limits', (data['interest_skill_limit'], data['occupation_skill_limit']))[
            0]:
            raise ValueError("Interest skill limit cannot exceed occupation skill limit")

        for key in ['points_available', 'dice_count', 'stat_upper_limit',
                    'stat_lower_limit', 'occupation_skill_limit',
                    'interest_skill_limit', 'stat_exchange_times']:
            if key in data and data[key]:
                data[key] = int(data[key])

        return data

    def _on_mode_changed(self, mode: str):
        points_widgets = [
            self.points_entry,
            self.upper_limit_entry,
            self.lower_limit_entry,
            self.custom_luck_checkbox
        ]
        dice_widgets = [self.dice_entry]

        if mode == "Points":
            for widget in points_widgets:
                widget.setVisible(True)
            for widget in dice_widgets:
                widget.setVisible(False)
                widget.set_value(str(self.current_settings.get('dice_count', 3)))
            self.points_entry.set_value(str(self.current_settings.get('points_available', 480)))
            self.upper_limit_entry.set_value(str(self.current_settings.get('stat_upper_limit', 80)))
            self.lower_limit_entry.set_value(str(self.current_settings.get('stat_lower_limit', 20)))
            self.custom_luck_checkbox.set_value(self.current_settings.get('allow_custom_luck', False))
        else:
            for widget in points_widgets:
                widget.setVisible(False)
                if isinstance(widget, type(self.points_entry)):
                    widget.set_value('0')
            for widget in dice_widgets:
                widget.setVisible(True)
                self.dice_entry.set_value(str(self.current_settings.get('dice_count', 3)))

        self.exchange_times_entry.setVisible(self.stat_exchange_checkbox.get_value())
        if not self.stat_exchange_checkbox.get_value():
            self.exchange_times_entry.set_value('0')

    def _on_exchange_changed(self, state):
        is_checked = bool(state)
        self.exchange_times_entry.setVisible(is_checked)
        if not is_checked:
            self.exchange_times_entry.set_value("0")


class StatExchangeDialog(TFComputingDialog):
    def __init__(self, parent, remaining_times: int, current_stats: dict):
        self.remaining_times = remaining_times
        self.current_stats = current_stats
        self.stat_checkboxes = {}
        super().__init__("Exchange Stats", parent)
        self.setup_content()

    @classmethod
    def get_input(cls, parent=None, **kwargs) -> Tuple[bool, Tuple[str, str]]:
        dialog = cls(parent, kwargs.get('remaining_times'), kwargs.get('current_stats'))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return True, dialog.get_result()
        return False, None

    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)

        times_label = self.create_label(
            f"Remaining exchange times: {self.remaining_times}",
            bold=True
        )
        layout.addWidget(times_label)

        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU']
        for stat in stats:
            checkbox = self.create_check_with_label(
                f"{stat}: {self.current_stats[stat]}"
            )
            self.stat_checkboxes[stat] = checkbox
            layout.addWidget(checkbox)

    def get_field_values(self) -> dict:
        selected = []
        for stat, checkbox in self.stat_checkboxes.items():
            if checkbox.get_value():
                selected.append(stat)
        return {'selected': selected}

    def process_validated_data(self, data: dict) -> Tuple[str, str]:
        selected = data['selected']
        if len(selected) != 2:
            raise ValueError("Please select exactly two stats to exchange")
        return tuple(selected)


class AgeReductionDialog(TFComputingDialog):
    def __init__(self, parent, total_reduction: int, current_stats: dict):
        self.total_reduction = total_reduction
        self.current_stats = current_stats
        self.stat_entries = {}
        self.remaining_label = None

        button_config = [
            {"text": "OK", "callback": self._on_ok_clicked}
        ]
        super().__init__(f"Reduce Stats by {total_reduction} Points", parent, button_config=button_config)
        self._setup_validation_rules()
        self.setup_content()

    def _setup_validation_rules(self):
        rules = {}
        for stat in self.current_stats.keys():
            rules[f'reduction_{stat}'] = TFValidationRule(
                type_=int,
                required=True,
                min_val=0,
                max_val=self.total_reduction,
                error_messages={
                    'required': f'{stat} reduction is required',
                    'min': f'{stat} reduction cannot be negative',
                    'max': f'{stat} reduction cannot exceed {self.total_reduction}'
                }
            )
        rules['total_reduction'] = TFValidationRule(custom='total_reduction')
        rules['final_values'] = TFValidationRule(custom='final_values')

        self.validator.add_rules(rules)

        self.validator.add_custom_validator(
            'total_reduction',
            lambda values: (
                sum(values) == self.total_reduction,
                f"Total reduction must equal exactly {self.total_reduction}"
            )
        )

        self.validator.add_custom_validator(
            'final_values',
            lambda value: (
                self.current_stats[value[0]] - value[1] >= 1,
                f"Final {stat} value cannot be less than 1"
            )
        )

    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setContentsMargins(10, 10, 10, 10)

        instruction = self.create_label(
            f"Due to age, you must reduce your stats by {self.total_reduction} points total.",
            bold=True
        )
        layout.addWidget(instruction)

        self.remaining_label = self.create_label(
            f"Remaining points to allocate: {self.total_reduction}",
            bold=True
        )
        layout.addWidget(self.remaining_label)

        for stat in self.current_stats.keys():
            entry = self.create_value_entry(
                f"{stat} (Current: {self.current_stats[stat]}):",
                number_only=True,
                label_size=200,
                value_size=50
            )
            entry.set_value("0")
            entry.value_field.textChanged.connect(self._on_value_changed)
            self.stat_entries[stat] = entry
            layout.addWidget(entry)

        layout.addStretch()

        self.set_dialog_size(400, 250)

    def _on_value_changed(self):
        total = sum(int(entry.get_value() or 0) for entry in self.stat_entries.values())
        remaining = self.total_reduction - total
        self.remaining_label.setText(f"Remaining points to allocate: {remaining}")

    def get_field_values(self) -> dict:
        basic_values = {
            f'reduction_{stat}': entry.get_value() or "0"
            for stat, entry in self.stat_entries.items()
        }

        reductions = [int(basic_values[f'reduction_{stat}']) for stat in self.current_stats.keys()]
        basic_values['reductions_list'] = reductions

        basic_values['final_values_list'] = [
            (stat, int(basic_values[f'reduction_{stat}']))
            for stat in self.current_stats.keys()
        ]

        return basic_values

    def process_validated_data(self, data: dict) -> dict:
        reductions = [int(data[f'reduction_{stat}']) for stat in self.current_stats.keys()]
        if not self.validator.validate_field('total_reduction', reductions)[0]:
            raise ValueError(f"Total reduction must equal exactly {self.total_reduction}")

        result = {}
        for stat in self.current_stats.keys():
            reduction = int(data[f'reduction_{stat}'])
            if not self.validator.validate_field('final_values', (stat, reduction))[0]:
                raise ValueError(f"Final {stat} value cannot be less than 1")
            result[stat] = reduction

        return result

    @classmethod
    def get_input(cls, parent, total_reduction: int, current_stats: dict) -> tuple[bool, dict]:
        dialog = cls(parent, total_reduction, current_stats)
        confirmed = dialog.exec()
        return confirmed == 1, dialog.get_result() if confirmed == 1 else None


class CharacterDescriptionDialog(TFComputingDialog):
    def __init__(self, parent, stats: Dict[str, int]):
        self.stats = stats
        button_config = [{"text": "OK", "role": "accept"}]
        super().__init__("Character Description", parent, button_config=button_config)
        self.setup_content()

    def setup_validation_rules(self):
        pass

    def get_field_values(self):
        return {}

    def process_validated_data(self, data):
        return None

    def _get_str_description(self, value: int) -> str:
        if value <= 15:
            return "Struggles with even basic physical tasks"
        elif value <= 40:
            return "Notably weak, has difficulty with manual labor"
        elif value <= 60:
            return "Possesses average human strength"
        elif value <= 80:
            return "Remarkably strong, could be a successful athlete"
        else:
            return "Exceptionally powerful, rivals professional strongmen"

    def _get_con_description(self, value: int) -> str:
        if value <= 20:
            return "Chronically ill, requires frequent medical attention"
        elif value <= 40:
            return "Often sick, has a weak constitution"
        elif value <= 60:
            return "Generally healthy with normal resilience"
        elif value <= 80:
            return "Robust health, rarely gets sick"
        else:
            return "Iron constitution, seems immune to illness"

    def _get_siz_description(self, value: int) -> str:
        if value <= 20:
            return "Child-sized, very small and thin"
        elif value <= 40:
            return "Small and slight of build"
        elif value <= 60:
            return "Average height and build"
        elif value <= 80:
            return "Notably tall or broad"
        elif value <= 100:
            return "Exceptionally large, stands out in any crowd"
        else:
            return "Giant-like proportions, possibly record-breaking"

    def _get_dex_description(self, value: int) -> str:
        if value <= 20:
            return "Severely uncoordinated, struggles with basic motor tasks"
        elif value <= 40:
            return "Clumsy and awkward in movement"
        elif value <= 60:
            return "Average coordination and reflexes"
        elif value <= 80:
            return "Graceful and agile, excellent physical coordination"
        else:
            return "Exceptional agility, could be a professional acrobat"

    def _get_app_description(self, value: int) -> str:
        if value <= 20:
            return "Appearance causes discomfort in others"
        elif value <= 40:
            return "Plain, tends to blend into the background"
        elif value <= 60:
            return "Average appearance, neither striking nor forgettable"
        elif value <= 80:
            return "Attractive, draws positive attention"
        else:
            return "Stunning beauty, could be a professional model"

    def _get_int_description(self, value: int) -> str:
        if value <= 20:
            return "Severe cognitive limitations"
        elif value <= 40:
            return "Below average mental capacity"
        elif value <= 60:
            return "Average intelligence, capable of normal reasoning"
        elif value <= 80:
            return "Sharp mind, quick to understand complex concepts"
        else:
            return "Genius-level intellect"

    def _get_pow_description(self, value: int) -> str:
        if value <= 20:
            return "Weak-willed, easily manipulated"
        elif value <= 40:
            return "Lacks mental fortitude"
        elif value <= 60:
            return "Normal willpower and determination"
        elif value <= 80:
            return "Strong-willed, difficult to influence"
        elif value <= 100:
            return "Exceptional mental fortitude, almost unshakeable"
        else:
            return "Superhuman willpower, possibly psychically sensitive"

    def _get_edu_description(self, value: int) -> str:
        if value <= 20:
            return "Minimal formal education"
        elif value <= 40:
            return "Basic education, equivalent to elementary school"
        elif value <= 60:
            return "High school level education"
        elif value <= 80:
            return "University graduate, well-educated"
        else:
            return "Scholarly excellence, extensive knowledge in many fields"

    def _get_luck_description(self, value: int) -> str:
        if value <= 20:
            return "Seems to attract misfortune"
        elif value <= 40:
            return "Often experiences bad luck"
        elif value <= 60:
            return "Average fortune in life"
        elif value <= 80:
            return "Notably lucky, things tend to work out well"
        else:
            return "Incredibly fortunate, seems blessed by fate"

    def setup_content(self):
        scroll_area, container, layout = self.create_scroll_area()

        descriptions = {
            'STR': ('Strength', self._get_str_description(self.stats['strength'])),
            'CON': ('Constitution', self._get_con_description(self.stats['constitution'])),
            'SIZ': ('Size', self._get_siz_description(self.stats['size'])),
            'DEX': ('Dexterity', self._get_dex_description(self.stats['dexterity'])),
            'APP': ('Appearance', self._get_app_description(self.stats['appearance'])),
            'INT': ('Intelligence', self._get_int_description(self.stats['intelligence'])),
            'POW': ('Power', self._get_pow_description(self.stats['power'])),
            'EDU': ('Education', self._get_edu_description(self.stats['education'])),
            'LUK': ('Luck', self._get_luck_description(self.stats['luck']))
        }

        frame = QFrame()
        grid_layout = QGridLayout(frame)
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(15, 15, 15, 15)

        for idx, (stat, (full_name, desc)) in enumerate(descriptions.items()):
            stat_frame = QFrame()
            stat_layout = QVBoxLayout(stat_frame)

            header_label = self.create_label(
                f"{stat} ({full_name}): {self.stats[full_name.lower()]}",
                bold=True
            )
            header_label.setStyleSheet("color: #2c3e50;")

            desc_label = self.create_label(desc)
            desc_label.setWordWrap(True)

            stat_layout.addWidget(header_label)
            stat_layout.addWidget(desc_label)

            row = idx // 2
            col = idx % 2
            grid_layout.addWidget(stat_frame, row, col)

        layout.addWidget(frame)

        main_layout = QVBoxLayout(self.content_frame)
        main_layout.addWidget(scroll_area)

        self.set_dialog_size(800, 600)


class OccupationListDialog(TFComputingDialog):
    
    def __init__(self, parent=None):
        button_config = [
            {"text": "OK", "callback": self._on_ok_clicked}
        ]
        super().__init__("Occupation List", parent, button_config=button_config)
        self._load_occupations()
        self.filtered_occupations = self.occupations
        self.setup_content()
        
    def _load_occupations(self):
        with open(resource_path('implements/coc_tools/coc_data/occupations.json'), 'r') as f:
            self.occupations = json.load(f)
            
        self.categories = set()
        for occupation in self.occupations:
            for category in occupation['category']:
                self.categories.add(category)
        self.categories = sorted(list(self.categories))
        
    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        
        filter_layout = QHBoxLayout()
        
        self.category_combo = QComboBox()
        self.category_combo.setFont(self.create_font())
        self.category_combo.addItem("All Categories")
        self.category_combo.addItems(self.categories)
        self.category_combo.currentTextChanged.connect(self._on_category_filter)
        filter_layout.addWidget(self.create_label("Category:", bold=True))
        filter_layout.addWidget(self.category_combo)
        
        filter_layout.addSpacing(20)
        
        self.name_input = QLineEdit()
        self.name_input.setFont(self.create_font())
        self.name_input.setPlaceholderText("Enter name to filter...")
        filter_layout.addWidget(self.create_label("Name:", bold=True))
        filter_layout.addWidget(self.name_input)
        
        self.apply_name_btn = TFBaseButton(
            "Apply",
            width=80,
            enabled=True,
            on_clicked=self._on_name_filter
        )
        filter_layout.addWidget(self.apply_name_btn)
        
        layout.addLayout(filter_layout)
        
        scroll_area, _, self.container_layout = self.create_scroll_area()
        layout.addWidget(scroll_area)
        
        self._update_occupation_display()
        self.set_dialog_size(1280, 800)
        
    def _create_occupation_frame(self, occupation: Dict) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame_layout = QVBoxLayout(frame)
        
        name_label = self.create_label(occupation['name'], bold=True)
        frame_layout.addWidget(name_label)
        
        skills = occupation['occupation_skills'].split(',')
        processed_skills = [
            skill.replace(':', ' - ')
                .replace('_', ' ')
                .strip()
                .title() 
            for skill in skills
        ]
        skills_str = ', '.join(processed_skills)
        
        details = [
            f"Skill Points: {occupation['skill_points_formula']}",
            f"Skills: {skills_str}",
            f"Categories: {', '.join(occupation['category'])}",
            f"Credit Rating: {occupation['credit_rating']}"
        ]
        
        for detail in details:
            label = self.create_label(detail)
            frame_layout.addWidget(label)
            
        return frame
        
    def _update_occupation_display(self):
        while self.container_layout.count():
            widget = self.container_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
                
        for occupation in self.filtered_occupations:
            frame = self._create_occupation_frame(occupation)
            self.container_layout.addWidget(frame)
            
        self.container_layout.addStretch()
        
    def _on_category_filter(self, category: str):
        self.name_input.clear()
        
        if category == "All Categories":
            self.filtered_occupations = self.occupations
        else:
            self.filtered_occupations = [
                occ for occ in self.occupations
                if category in occ['category']
            ]
            
        self._update_occupation_display()
        
    def _on_name_filter(self):
        self.category_combo.setCurrentText("All Categories")
        
        search_text = self.name_input.text().lower()
        if not search_text:
            self.filtered_occupations = self.occupations
        else:
            self.filtered_occupations = [
                occ for occ in self.occupations
                if search_text in occ['name'].lower()
            ]
            
        self._update_occupation_display()
        
    def setup_validation_rules(self):
        pass
        
    def get_field_values(self):
        return {}
        
    def process_validated_data(self, data):
        pass


class BaseSkillSelectDialog(TFComputingDialog):
    def __init__(self, title: str, parent_ui: 'Phase2UI'):
        button_config = [
            {"text": "OK", "callback": self._on_ok_clicked},
            {"text": "Cancel", "callback": self.reject, "role": "reject"}
        ]
        super().__init__(title, parent_ui, button_config=button_config)
        self.parent_ui = parent_ui
        self.selected_skill = None
        self.radio_buttons = {}
        self.setup_content()
        self.setup_validation_rules()

    def setup_validation_rules(self):
        self.validator.add_rule('skill_selected', TFValidationRule(custom='skill_selected'))
        self.validator.add_custom_validator(
            'skill_selected',
            lambda value: (value is not None, "Please select a skill.")
        )
        self.validator.add_rule('skill_not_occupied', TFValidationRule(custom='skill_not_occupied'))

        def validate_skill_occupation(value):
            if not value:
                return True, ""
            existing_skill = next(
                (s for s in self.parent_ui.skills
                 if s.name == value.name and s.super_name == value.super_name),
                None
            )
            return (
            not existing_skill or not existing_skill.is_occupation, "This skill is already an occupation skill.")

        self.validator.add_custom_validator('skill_not_occupied', validate_skill_occupation)

    def get_field_values(self):
        return {'skill_selected': self.selected_skill, 'skill_not_occupied': self.selected_skill}

    def process_validated_data(self, data):
        return self.selected_skill

    def get_result(self) -> Optional[Skill]:
        return self.selected_skill

    def _on_radio_button_clicked(self, skill: Skill):
        self.selected_skill = skill

    def _on_ok_clicked(self):
        success, result = self.compute_result()
        if success:
            self._result = result
            self.accept()
        else:
            self.parent_ui.main_window.app.show_warning("Select Failure", result)


class InterpersonalSkillDialog(BaseSkillSelectDialog):
    def __init__(self, parent_ui: 'Phase2UI'):
        super().__init__("Select Interpersonal Skill", parent_ui)

    def setup_content(self):
        layout = QGridLayout(self.content_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        button_group = QButtonGroup(self)
        row = col = 0

        interpersonal_skills = [skill for skill in self.parent_ui.skills
                                if skill.name in ["charm", "fast_talk", "intimidate", "persuade"]]

        for skill in sorted(interpersonal_skills, key=lambda x: x.name):
            radio = QRadioButton(skill.display_name)
            radio.setFont(self.create_font())
            radio.clicked.connect(lambda checked, s=skill: self._on_radio_button_clicked(s))

            self.radio_buttons[skill.name] = radio
            button_group.addButton(radio)
            layout.addWidget(radio, row, col)

            col += 1
            if col == 4:
                col = 0
                row += 1


class SpecificSkillDialog(BaseSkillSelectDialog):
    def __init__(self, skill_type: str, parent_ui: 'Phase2UI'):
        self.skill_type = skill_type
        super().__init__(f"Select {skill_type.title()} Skill", parent_ui)

    def setup_content(self):
        layout = QGridLayout(self.content_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        button_group = QButtonGroup(self)
        row = col = 0

        type_skills = sorted(
            [skill for skill in self.parent_ui.skills
             if skill.super_name == self.skill_type.lower()],
            key=lambda x: x.name
        )

        for skill in type_skills:
            radio = QRadioButton(skill.display_name)
            radio.setFont(self.create_font())
            radio.clicked.connect(lambda checked, s=skill: self._on_radio_button_clicked(s))

            self.radio_buttons[skill.name] = radio
            button_group.addButton(radio)
            layout.addWidget(radio, row, col)

            col += 1
            if col == 4:
                col = 0
                row += 1


class AnySkillDialog(BaseSkillSelectDialog):
    def __init__(self, parent_ui: 'Phase2UI'):
        super().__init__("Select Any Skill", parent_ui)

    def setup_content(self):
        scroll_area, container, main_layout = self.create_scroll_area()
        button_group = QButtonGroup(self)

        independent_frame = QGroupBox("Independent Skills")
        independent_layout = QGridLayout(independent_frame)
        row = col = 0

        independent_skills = sorted(
            [skill for skill in self.parent_ui.skills if not skill.super_name],
            key=lambda x: x.name
        )

        for skill in independent_skills:
            radio = QRadioButton(skill.display_name)
            radio.setFont(self.create_font())
            radio.clicked.connect(lambda checked, s=skill: self._on_radio_button_clicked(s))

            self.radio_buttons[skill.name] = radio
            button_group.addButton(radio)
            independent_layout.addWidget(radio, row, col)

            col += 1
            if col == 4:
                col = 0
                row += 1

        main_layout.addWidget(independent_frame)

        parent_types = set(
            skill.super_name for skill in self.parent_ui.skills
            if skill.super_name is not None
        )

        for parent_type in sorted(parent_types):
            group = QGroupBox(parent_type.title())
            group_layout = QGridLayout(group)
            row = col = 0

            child_skills = sorted(
                [skill for skill in self.parent_ui.skills
                 if skill.super_name == parent_type],
                key=lambda x: x.name
            )

            for skill in child_skills:
                radio = QRadioButton(skill.display_name)
                radio.setFont(self.create_font())
                radio.clicked.connect(lambda checked, s=skill: self._on_radio_button_clicked(s))

                self.radio_buttons[skill.name] = radio
                button_group.addButton(radio)
                group_layout.addWidget(radio, row, col)

                col += 1
                if col == 4:
                    col = 0
                    row += 1

            main_layout.addWidget(group)

        self.content_frame.setLayout(QVBoxLayout())
        self.content_frame.layout().addWidget(scroll_area)
        self.set_dialog_size(840, 800)


class MultiOptionSkillDialog(BaseSkillSelectDialog):
    def __init__(self, skills: str, parent_ui: 'Phase2UI'):
        self.skill_options = skills.split(' / ')
        super().__init__("Select One Skill", parent_ui)

    def setup_content(self):
        layout = QGridLayout(self.content_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        button_group = QButtonGroup(self)
        row = col = 0

        for skill_option in self.skill_options:
            skill_name = skill_option.strip().lower().replace(' ', '_')

            if ':any' in skill_name:
                skill_type = skill_name.split(':')[0]
                type_skills = [s for s in self.parent_ui.skills if s.super_name == skill_type]

                for skill in sorted(type_skills, key=lambda x: x.name):
                    radio = QRadioButton(skill.display_name)
                    radio.setFont(self.create_font())
                    radio.clicked.connect(lambda checked, s=skill: self._on_radio_button_clicked(s))

                    self.radio_buttons[skill.name] = radio
                    button_group.addButton(radio)
                    layout.addWidget(radio, row, col)

                    col += 1
                    if col == 4:
                        col = 0
                        row += 1
            else:
                skill = next(
                    (s for s in self.parent_ui.skills
                     if s.name == skill_name or
                     (s.super_name and f"{s.super_name}:{s.name}" == skill_name)),
                    None
                )
                if skill:
                    radio = QRadioButton(skill.display_name)
                    radio.setFont(self.create_font())
                    radio.clicked.connect(lambda checked, s=skill: self._on_radio_button_clicked(s))

                    self.radio_buttons[skill.name] = radio
                    button_group.addButton(radio)
                    layout.addWidget(radio, row, col)

                    col += 1
                    if col == 4:
                        col = 0
                        row += 1


class NewSkillDialog(TFComputingDialog):
    def __init__(self, parent_ui: 'Phase2UI'):
        button_config = [
            {"text": "OK", "callback": self._on_ok_clicked}
        ]
        super().__init__("Add New Skill", parent_ui, button_config=button_config)
        self.parent_ui = parent_ui
        self.all_grouped_skills = set(s.super_name for s in parent_ui.skills if s.super_name)
        self.setup_validation_rules()
        self.setup_content()

    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        options = ["None"]
        for skill in sorted(self.all_grouped_skills):
            display_name = skill.replace('_', ' ').title()
            options.append(display_name)

        self.parent_combo = self.create_option_entry(
            "Skill Category:",
            options=options,
            current_value="None",
            label_size=120,
            value_size=150,
        )
        layout.addWidget(self.parent_combo)

        self.name_entry = self.create_value_entry(
            label_text="Skill Name:",
            label_size=120,
            value_size=150
        )
        self.name_entry.value_field.setValidator(
            QRegularExpressionValidator(QRegularExpression("[a-zA-Z ]+"))
        )
        layout.addWidget(self.name_entry)

        self.value_entry = self.create_value_entry(
            label_text="Base Value:",
            label_size=120,
            value_size=150,
            number_only=True,
            allow_decimal=False
        )
        self.value_entry.set_value("0")
        layout.addWidget(self.value_entry)

        layout.addStretch()
        self.set_dialog_size(350, 250)

    def setup_validation_rules(self):
        self.validator.add_rules({
            'skill_name': TFValidationRule(
                type_=str,
                required=True,
                pattern=r'^[a-zA-Z ]+$',
                error_messages={
                    'required': 'Please enter a skill name',
                    'pattern': 'Skill name can only contain letters and spaces'
                }
            ),
            'base_value': TFValidationRule(
                type_=int,
                required=True,
                min_val=0,
                max_val=99,
                error_messages={
                    'min': 'Base value cannot be negative',
                    'max': 'Base value cannot exceed 99'
                }
            ),
            'skill_category': TFValidationRule(
                type_=str,
                required=True,
                error_messages={
                    'required': 'Please select a skill category'
                }
            )
        })

    def get_field_values(self):
        return {
            'skill_name': self.name_entry.get_value().strip(),
            'base_value': self.value_entry.get_value().strip(),
            'skill_category': self.parent_combo.get_value()
        }

    def process_validated_data(self, data):
        category = data['skill_category'].lower().replace(' ', '_')
        skill_name = data['skill_name'].lower().replace(" ", "_")
        base_value = int(data['base_value'])

        if category == "none":
            super_name = None
        else:
            super_name = category

        existing_skill = next(
            (s for s in self.parent_ui.skills
             if s.name == skill_name and s.super_name == super_name),
            None
        )

        if existing_skill:
            parent_name = "Base Skills" if super_name is None else super_name.replace('_', ' ').title()
            raise ValueError(f"A skill with name '{skill_name}' already exists under {parent_name}. "
                             "Please use a different name or remove the existing skill first.")

        if super_name:
            final_name = f"{super_name}:{skill_name}"
        else:
            final_name = skill_name

        return final_name, base_value

    @classmethod
    def get_input(cls, parent) -> tuple[bool, tuple[str, int]]:
        dialog = cls(parent)
        confirmed = dialog.exec()
        return confirmed == 1, dialog.get_result() if confirmed == 1 else (None, None)

    def get_result(self) -> tuple[str, int]:
        return self._result if hasattr(self, '_result') else (None, None)


class DeleteItemDialog(TFComputingDialog):
    def __init__(self, parent=None, items=None):
        button_config = [
            {"text": "OK", "callback": self._on_ok_clicked}
        ]
        self.items = items or []
        self.checkboxes = {}
        super().__init__("Delete Items", parent, button_config)
        self.setup_content()

    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        scroll_area, container, container_layout = self.create_scroll_area()

        for widget, _, _ in self.items:
            if isinstance(widget, QLabel):
                text = widget.text()
                checkbox = self.create_check_with_label(text)
                self.checkboxes[text] = checkbox
                container_layout.addWidget(checkbox)

        container_layout.addStretch()
        layout.addWidget(scroll_area)

        self.set_dialog_size(300, 400)

    def setup_validation_rules(self):
        pass

    def get_field_values(self):
        return {"selected_items": [text for text, checkbox in self.checkboxes.items()
                                   if checkbox.get_value()]}

    def process_validated_data(self, data):
        return data["selected_items"]


class CombatSkillListDialog(TFComputingDialog):
    def __init__(self, parent, combat_skills: List[CombatSkill]):
        self.combat_skills = combat_skills
        button_config = [{"text": "OK", "role": "accept"}]
        super().__init__("Combat Skills List", parent, button_config=button_config)
        self.setup_content()

    def setup_validation_rules(self):
        pass

    def get_field_values(self):
        return {}

    def process_validated_data(self, data):
        return None

    def setup_content(self):
        scroll_area, container, layout = self.create_scroll_area()

        sorted_skills = sorted(self.combat_skills, key=lambda x: x.name)

        for skill in sorted_skills:
            skill_frame = QFrame()
            skill_frame.setObjectName("skill_frame")
            skill_layout = QVBoxLayout(skill_frame)
            skill_layout.setSpacing(5)
            skill_layout.setContentsMargins(10, 10, 10, 10)

            header_text = f"{skill.name} ({skill.damage})"
            header_label = self.create_label(header_text, bold=True)
            skill_layout.addWidget(header_label)

            for tech_name, tech_description in skill.techniques.items():
                tech_frame = QFrame()
                tech_layout = QVBoxLayout(tech_frame)
                tech_layout.setSpacing(2)
                tech_layout.setContentsMargins(5, 5, 5, 5)

                tech_name_label = self.create_label(tech_name, bold=True)
                tech_layout.addWidget(tech_name_label)

                tech_desc_label = self.create_label(tech_description)
                tech_desc_label.setWordWrap(True)
                tech_layout.addWidget(tech_desc_label)

                skill_layout.addWidget(tech_frame)

            layout.addWidget(skill_frame)

            if skill != sorted_skills[-1]:
                separator = TFSeparator.horizontal()
                separator.setContentsMargins(0, 5, 0, 5)
                layout.addWidget(separator)

        main_layout = QVBoxLayout(self.content_frame)
        main_layout.addWidget(scroll_area)

        self.set_dialog_size(500, 600)


class WeaponTypeListDialog(TFComputingDialog):
    def __init__(self, parent, weapon_types: List[WeaponType]):
        self.weapon_types = weapon_types
        button_config = [{"text": "OK", "role": "accept"}]
        super().__init__("Weapons List", parent, button_config=button_config)
        self.setup_content()

    def setup_validation_rules(self):
        pass

    def get_field_values(self):
        return {}

    def process_validated_data(self, data):
        return None

    def setup_content(self):
        scroll_area, container, layout = self.create_scroll_area()

        categories = {}
        for weapon in self.weapon_types:
            if weapon.category.value not in categories:
                categories[weapon.category.value] = []
            categories[weapon.category.value].append(weapon)

        sorted_categories = sorted(categories.keys())

        for category in sorted_categories:
            category_label = self.create_label(category, bold=True)
            layout.addWidget(category_label)

            category_frame = QFrame()
            category_frame.setObjectName("category_frame")
            category_layout = QVBoxLayout(category_frame)
            category_layout.setSpacing(10)
            category_layout.setContentsMargins(10, 10, 10, 10)

            sorted_weapons = sorted(categories[category], key=lambda x: x.name)
            for weapon in sorted_weapons:
                weapon_frame = QFrame()
                weapon_frame.setObjectName("weapon_frame")
                weapon_layout = QVBoxLayout(weapon_frame)
                weapon_layout.setSpacing(5)
                weapon_layout.setContentsMargins(10, 10, 10, 10)

                name_label = self.create_label(weapon.name, bold=True)
                weapon_layout.addWidget(name_label)

                stats_layout = QGridLayout()
                stats_layout.setSpacing(5)

                stats = [
                    ("Skill", weapon.skill.standard_text),
                    ("Damage", weapon.damage.standard_text),
                    ("Range", weapon.range.standard_text),
                    ("Penetration", weapon.penetration.value),
                    ("Rate of Fire", weapon.rate_of_fire),
                ]

                if weapon.ammo:
                    stats.append(("Ammo", weapon.ammo))
                if weapon.malfunction:
                    stats.append(("Malfunction", weapon.malfunction))

                for i, (stat_name, stat_value) in enumerate(stats):
                    row = i // 2
                    col = i % 2 * 2

                    name_label = self.create_label(f"{stat_name}:", bold=True)
                    value_label = self.create_label(str(stat_value))

                    stats_layout.addWidget(name_label, row, col)
                    stats_layout.addWidget(value_label, row, col + 1)

                weapon_layout.addLayout(stats_layout)
                category_layout.addWidget(weapon_frame)

            layout.addWidget(category_frame)

            if category != sorted_categories[-1]:
                separator = TFSeparator.horizontal()
                separator.setContentsMargins(0, 5, 0, 5)
                layout.addWidget(separator)

        main_layout = QVBoxLayout(self.content_frame)
        main_layout.addWidget(scroll_area)

        self.set_dialog_size(600, 800)


class CommonListDialog(TFComputingDialog):
    def __init__(self, title: str, items: List[str], parent=None):
        button_config = [
            {"text": "OK", "role": "accept"}
        ]
        self.items = items
        super().__init__(title, parent, button_config)
        self.setup_content()
        self.adjust_size()
        
    def setup_content(self):
        scroll_area, _, layout = self.create_scroll_area()
        
        max_width = 0
        total_height = 0
        
        for i, text in enumerate(self.items, 1):
            label = self.create_label(f"{i}. {text}")
            layout.addWidget(label)
            width = label.sizeHint().width()
            height = label.sizeHint().height()
            max_width = max(max_width, width)
            total_height += height + layout.spacing()
            
        layout.addStretch()
        self.content_frame.setLayout(QVBoxLayout())
        self.content_frame.layout().addWidget(scroll_area)
        
        self._content_width = max_width
        self._content_height = total_height

    def adjust_size(self):
        scroll_bar_width = 20
        padding = 40
        button_height = 40
        
        ideal_width = self._content_width + scroll_bar_width + padding
        ideal_height = min(self._content_height + button_height + padding, 600)
        
        screen = self.screen()
        screen_geometry = screen.geometry()
        
        max_width = int(screen_geometry.width() * 0.8)
        max_height = int(screen_geometry.height() * 0.8)
        
        final_width = min(ideal_width, max_width)
        final_height = min(ideal_height, max_height)
        
        self.resize(final_width, final_height)

    def setup_validation_rules(self):
        pass

    def get_field_values(self):
        return {}

    def process_validated_data(self, data):
        return None


class TextDisplayDialog(TFComputingDialog):
    def __init__(self, title: str, content: dict, parent=None):
        button_config = [
            {"text": "OK", "role": "accept"}
        ]
        self.content = content
        super().__init__(title, parent, button_config)

        self.setup_content()
        self.resize(600, 400)
        
    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setSpacing(10)
        
        if 'title' in self.content:
            title_label = self.create_label(self.content['title'], bold=True)
            title_label.setStyleSheet("font-size: 14px;")
            layout.addWidget(title_label)
            
        if 'paragraphs' in self.content:
            for text in self.content['paragraphs']:
                para_label = self.create_label(text)
                para_label.setWordWrap(True)
                layout.addWidget(para_label)
            
        if 'bullet_points' in self.content:
            for text in self.content['bullet_points']:
                bullet_label = self.create_label(f"• {text}")
                bullet_label.setWordWrap(True)
                layout.addWidget(bullet_label)
            
        if 'sections' in self.content:
            for section in self.content['sections']:
                subtitle_label = self.create_label(section['subtitle'], bold=True)
                subtitle_label.setStyleSheet("font-size: 12px; padding-top: 10px;")
                layout.addWidget(subtitle_label)
                
                content_label = self.create_label(section['content'])
                content_label.setWordWrap(True)
                layout.addWidget(content_label)

        layout.addStretch()

    def setup_validation_rules(self):
        pass

    def get_field_values(self):
        return {}

    def process_validated_data(self, data):
        return None
