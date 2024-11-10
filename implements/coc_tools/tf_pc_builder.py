from PyQt6.QtWidgets import QVBoxLayout, QFrame, QComboBox, QWidget, QHBoxLayout
from PyQt6.QtGui import QFont

from core.windows.tf_draggable_window import TFDraggableWindow
from utils.registry.tf_tool_matadata import TFToolMetadata
from utils.validator.tf_validator import TFValidator
from utils.validator.tf_validation_rules import TFValidationRule
from ui.components.tf_computing_dialog import TFComputingDialog
from ui.components.tf_separator import TFSeparator
from ui.components.tf_settings_widget import MenuSection

LABEL_FONT = QFont("Inconsolata SemiBold")
LABEL_FONT.setPointSize(10)

EDIT_FONT = QFont("Inconsolatav")
EDIT_FONT.setPointSize(10)

GROUPED_SKILLS = {'art', 'science', 'survival', 'pilot'}
SPECIAL_SKILLS = {'fighting', 'firearms'}

DEFAULT_SKILLS = {
    "accounting": 5,
    "anthropology": 1,
    "appraise": 5,
    "archaeology": 1,
    "art:all": 5,
    "charm": 15,
    "climb": 20,
    "credit_rating": 0,
    "cthulhu_mythos": 0,
    "disguise": 5,
    "dodge": 0,
    "drive_auto": 20,
    "electrical_repair": 10,
    "electronics": 1,
    "fast_talk": 5,
    "fighting:brawl": 25,
    "fighting:chainsaw": 10,
    "fighting:flail": 10,
    "fighting:garrote": 15,
    "fighting:sword": 20,
    "fighting:whip": 5,
    "firearms:handgun": 20,
    "firearms:heavy_weapons": 10,
    "firearms:rifle": 25,
    "firearms:shotgun": 25,
    "firearms:smg": 15,
    "first_aid": 30,
    "history": 5,
    "intimidate": 15,
    "jump": 20,
    "language": 0,
    "language:all": 1,
    "law": 5,
    "library_use": 20,
    "listen": 20,
    "locksmith": 1,
    "mechanical_repair": 10,
    "medicine": 1,
    "natural_world": 10,
    "navigate": 10,
    "occult": 5,
    "operate_heavy_machinery": 1,
    "persuade": 10,
    "pilot:all": 1,
    "psychoanalysis": 1,
    "psychology": 10,
    "ride": 5,
    "science:all": 1,
    "sleight_of_hand": 10,
    "spot_hidden": 25,
    "stealth": 20,
    "survival:all": 10,
    "swim": 20,
    "throw": 20,
    "track": 10
}

WEAPON_TYPES = {
    "Knife, Small": ("fighting:brawl", "1d4+db", 0),
    "Knife, Medium": ("fighting:brawl", "1d4+2+db", 0),
    "Knife, Large": ("fighting:brawl", "1d8+db", 0)
}

class TFPcBuilder(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="pc_builder",
        menu_path="Tools/COC",
        menu_title="Add PC Builder",
        window_title="PC Builder",
        window_size=(960, 600),
        description="PC builder",
        max_instances=1
    )

    def __init__(self, parent=None):
        self.generation_mode = "points"
        self.points_available = 480
        self.dice_count = 3
        self.stat_upper_limit = 80
        self.stat_lower_limit = 20
        self.occupation_skill_limit = 90
        self.interest_skill_limit = 60
        self.allow_mixed_points = True
        self.allow_stat_exchange = False
        self.stat_exchange_times = 0

        super().__init__(parent)
        self.pc_data = None
        self._phase = 1

        self.validator = TFValidator()
        self._setup_menu()
        self._setup_shortcut()

    def get_tooltip_hover_text(self):
        return "Unfinished"
    
    def initialize_window(self):
        main_layout = QVBoxLayout(self.content_container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.phase_container = QFrame()
        main_layout.addWidget(self.phase_container)

    def _setup_menu(self):
        self.rule_settings_action = self.menu_button.add_action(
            "Rule Settings",
            self._show_rule_settings,
            MenuSection.CUSTOM
        )

    def _setup_shortcut(self):
        pass

    def _show_rule_settings(self):
        confirmed, result = RuleSettingsDialog.get_input(
            self,
            current_settings={
                'generation_mode': self.generation_mode,
                'points_available': self.points_available,
                'dice_count': self.dice_count,
                'stat_upper_limit': self.stat_upper_limit,
                'stat_lower_limit': self.stat_lower_limit,
                'occupation_skill_limit': self.occupation_skill_limit,
                'interest_skill_limit': self.interest_skill_limit,
                'allow_mixed_points': self.allow_mixed_points,
                'allow_stat_exchange': self.allow_stat_exchange,
                'stat_exchange_times': self.stat_exchange_times
            }
        )
        
        if confirmed:
            self.generation_mode = result['generation_mode']
            self.occupation_skill_limit = result['occupation_skill_limit']
            self.interest_skill_limit = result['interest_skill_limit']
            self.allow_mixed_points = result['allow_mixed_points']
            self.allow_stat_exchange = result['allow_stat_exchange']
            self.stat_exchange_times = result['stat_exchange_times']

            if result['generation_mode'] == 'points':
                self.points_available = result['points_available']
                self.stat_upper_limit = result['stat_upper_limit']
                self.stat_lower_limit = result['stat_lower_limit']
            elif result['generation_mode'] == 'destiny':
                self.dice_count = result['dice_count']

        print("\nCurrent Settings:")
        print(f"Generation Mode: {self.generation_mode}")
        print(f"Points Available: {self.points_available}")
        print(f"Dice Count: {self.dice_count}")
        print(f"Stat Upper Limit: {self.stat_upper_limit}")
        print(f"Stat Lower Limit: {self.stat_lower_limit}")
        print(f"Occupation Skill Limit: {self.occupation_skill_limit}")
        print(f"Interest Skill Limit: {self.interest_skill_limit}")
        print(f"Allow Mixed Points: {self.allow_mixed_points}")
        print(f"Allow Stat Exchange: {self.allow_stat_exchange}")
        print(f"Stat Exchange Times: {self.stat_exchange_times}\n")

class Phase1UI(QFrame):
    pass

class Phase2UI(QFrame):
    pass

class Phase3UI(QFrame):
    pass

class Phase4UI(QFrame):
    pass

class Phase5UI(QFrame):
    pass

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

        mode_layout = QHBoxLayout()
        mode_layout.setContentsMargins(2, 0, 2, 0)
        mode_label = self.create_label("Generation Mode:", bold=True)
        mode_label.setFixedWidth(190)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Points", "Destiny"])
        self.mode_combo.setCurrentText(
            "Destiny" if self.current_settings.get('generation_mode') == "destiny" 
            else "Points"
        )
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        self.mode_combo.setFixedWidth(100)
        
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

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

        self.mixed_points_checkbox = self.create_checkbox(
            "Allow mixing occupation and interest points"
        )
        self.mixed_points_checkbox.setChecked(
            self.current_settings.get('allow_mixed_points', True)
        )
        layout.addWidget(self.mixed_points_checkbox)

        exchange_layout = QHBoxLayout()
        exchange_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stat_exchange_checkbox = self.create_checkbox(
            "Allow stat exchange"
        )
        self.stat_exchange_checkbox.setChecked(
            self.current_settings.get('allow_stat_exchange', False)
        )
        self.stat_exchange_checkbox.stateChanged.connect(self._on_exchange_changed)
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

        self._on_mode_changed(self.mode_combo.currentText())
        self.set_dialog_size(400, 360)

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
                max_val=10,
                error_messages={
                    'min': 'Must roll at least 1 die',
                    'max': 'Cannot roll more than 10 dice'
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
        mode = self.mode_combo.currentText().lower()
        values = {
            'generation_mode': mode,
            'occupation_skill_limit': self.occupation_limit_entry.get_value(),
            'interest_skill_limit': self.interest_limit_entry.get_value(),
            'allow_mixed_points': self.mixed_points_checkbox.isChecked(),
            'allow_stat_exchange': self.stat_exchange_checkbox.isChecked(),
            'stat_exchange_times': self.exchange_times_entry.get_value() if self.stat_exchange_checkbox.isChecked() else "0"
        }
        
        if mode == 'points':
            values.update({
                'points_available': self.points_entry.get_value(),
                'stat_upper_limit': self.upper_limit_entry.get_value(),
                'stat_lower_limit': self.lower_limit_entry.get_value()
            })
        else:
            values['dice_count'] = self.dice_entry.get_value()
            
        return values

    def process_validated_data(self, data):
        if data['generation_mode'] == 'points':
            if not self.validator.validate_field('stat_limits', (data['stat_lower_limit'], data['stat_upper_limit']))[0]:
                raise ValueError("Lower limit cannot be greater than upper limit")

        if not self.validator.validate_field('skill_limits', (data['interest_skill_limit'], data['occupation_skill_limit']))[0]:
            raise ValueError("Interest skill limit cannot exceed occupation skill limit")

        for key in ['points_available', 'dice_count', 'stat_upper_limit', 
                    'stat_lower_limit', 'occupation_skill_limit', 
                    'interest_skill_limit', 'stat_exchange_times']:
            if key in data and data[key]:
                data[key] = int(data[key])
        
        return data
    
    def _on_mode_changed(self, mode):
        points_widgets = [self.points_entry, self.upper_limit_entry, self.lower_limit_entry]
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
        else:
            for widget in points_widgets:
                widget.setVisible(False)
                widget.set_value('0')
            for widget in dice_widgets:
                widget.setVisible(True)
                self.dice_entry.set_value(str(self.current_settings.get('dice_count', 3)))
        
        self.exchange_times_entry.setVisible(self.stat_exchange_checkbox.isChecked())
        if not self.stat_exchange_checkbox.isChecked():
            self.exchange_times_entry.set_value('0')

    def _on_exchange_changed(self, state):
        is_checked = bool(state)
        self.exchange_times_entry.setVisible(is_checked)
        if not is_checked:
            self.exchange_times_entry.set_value("0")
