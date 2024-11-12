from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QComboBox, QWidget

from utils.validator.tf_validation_rules import TFValidationRule
from ui.components.tf_computing_dialog import TFComputingDialog
from ui.components.tf_separator import TFSeparator

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
