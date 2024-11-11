from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGroupBox, QButtonGroup,
                           QLabel, QRadioButton, QCheckBox, QGridLayout, QWidget)
from PyQt6.QtCore import Qt
from ui.components.tf_base_button import TFBaseButton, TFConfirmButton
from ui.components.tf_computing_dialog import TFComputingDialog
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_option_entry import TFOptionEntry
from implements.coc_tools.pc_builder_helper.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_helper.phase_ui import BasePhaseUI
from utils.validator.tf_validation_rules import TFValidationRule
from utils.validator.tf_validator import TFValidator

class Phase1UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        self.config = main_window.config
        
        self.avatar_label = None
        self.avatar_button = None
        
        self.player_name = None
        self.campaign_date = None
        self.era = None
        
        self.char_name = None
        self.age = None
        self.occupation = None
        self.residence = None
        self.birthplace = None
        
        self.stats_left_panel = None
        self.stats_right_panel = None
        self.stat_entries = {}
        self.points_label = None
        self.custom_luck_checkbox = None
        self.remaining_points = 0
        
        self.roll_button = None
        self.roll_results_frame = None
        self.roll_checkboxes = []
        self.confirm_roll_button = None
        self.remaining_exchange_times = self.config.stat_exchange_times

        self._setup_validation_rules()
        
        super().__init__(PCBuilderPhase.PHASE1, main_window, parent)
        self.main_window.config_updated.connect(self._on_config_updated)

    def _setup_ui(self):
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        
        upper_frame = QFrame()
        upper_layout = QHBoxLayout()
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(10)
        
        upper_layout.addWidget(self._create_avatar_group())
        upper_layout.addWidget(self._create_metadata_group())
        upper_layout.addWidget(self._create_personal_info_group())
        
        upper_frame.setLayout(upper_layout)
        content_layout.addWidget(upper_frame)
        
        stats_frame = QFrame()
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        
        self.stats_left_panel = QFrame()
        self.stats_right_panel = QFrame()
        
        stats_layout.addWidget(self.stats_left_panel)
        stats_layout.addWidget(self.stats_right_panel)
        
        stats_frame.setLayout(stats_layout)
        content_layout.addWidget(stats_frame)
        
        self.content_area.setLayout(content_layout)
        
        self._update_stats_display()

    def _setup_phase_buttons(self, button_layout: QHBoxLayout):
        self.calculate_button = TFBaseButton(
            "Calculate",
            self,
            on_clicked=self._on_calculate
        )
        self.exchange_button = TFBaseButton(
            "Stat Exchange",
            self,
            enabled=False,
            on_clicked=self._on_exchange
        )
        
        button_layout.addWidget(self.calculate_button)
        button_layout.addWidget(self.exchange_button)

    def _setup_validation_rules(self):
        rules = {
            'metadata.player_name': TFValidationRule(
                type_=str,
                required=True
            ),
            'metadata.campaign_date': TFValidationRule(
                type_=str,
                required=True
            ),
            'metadata.era': TFValidationRule(
                type_=str,
                required=True,
                choices=['Medieval', '1890s', '1920s', 'Modern', 'Near Future', 'Future']
            ),
            'personal_info.name': TFValidationRule(
                type_=str,
                required=True
            ),
            'personal_info.age': TFValidationRule(
                type_=int,
                required=True,
                min_val=12,
                max_val=80
            ),
            'personal_info.occupation': TFValidationRule(
                type_=str,
                required=True
            ),
            'personal_info.residence': TFValidationRule(
                type_=str,
                required=True
            ),
            'personal_info.birthplace': TFValidationRule(
                type_=str,
                required=True
            )
        }
        
        for stat in ['strength', 'constitution', 'size', 'dexterity', 
                    'appearance', 'intelligence', 'power', 'education']:
            rules[f'basic_stats.{stat}'] = TFValidationRule(
                type_=int,
                required=True,
                min_val=self.config.stat_lower_limit,
                max_val=self.config.stat_upper_limit
            )
        
        rules['basic_stats.luck'] = TFValidationRule(
            type_=int,
            required=False,
            min_val=self.config.stat_lower_limit,
            max_val=self.config.stat_upper_limit
        )
        
        self.validator = TFValidator()
        self.validator.add_rules(rules)

    def _on_config_updated(self):
        self._update_stats_display()

    def _create_avatar_group(self):
        group = QGroupBox("Avatar")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setStyleSheet("border: 1px solid gray")
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.avatar_button = TFBaseButton(
            "Upload Avatar",
            self,
            on_clicked=self._on_avatar_upload
        )
        
        layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.avatar_button)
        layout.addStretch()
        return group

    def _create_metadata_group(self):
        group = QGroupBox("Metadata")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.player_name = TFValueEntry(
            "Player Name:",
            value_size=150
        )
        self.campaign_date = TFValueEntry(
            "Campaign Date:",
            value_size=150
        )
        
        era_options = ["Medieval", "1890s", "1920s", "Modern", "Near Future", "Future"]
        self.era = TFOptionEntry(
            "Era:",
            era_options,
            current_value="Modern",
            value_size=150
        )
        
        layout.addWidget(self.player_name)
        layout.addWidget(self.campaign_date)
        layout.addWidget(self.era)
        layout.addStretch()
        return group
        
    def _create_personal_info_group(self):
        group = QGroupBox("Personal Information")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.char_name = TFValueEntry(
            "Character Name:",
            value_size=150
        )
        self.age = TFValueEntry(
            "Age:",
            value_size=150,
            number_only=True
        )
        
        occupation_options = ["Private Detective", "Professor"]
        self.occupation = TFOptionEntry(
            "Occupation:",
            occupation_options,
            value_size=150
        )
        
        self.residence = TFValueEntry(
            "Residence:",
            value_size=150
        )
        self.birthplace = TFValueEntry(
            "Birthplace:",
            value_size=150
        )
        
        layout.addWidget(self.char_name)
        layout.addWidget(self.age)
        layout.addWidget(self.occupation)
        layout.addWidget(self.residence)
        layout.addWidget(self.birthplace)
        layout.addStretch()
        return group
    
    def _update_stats_display(self):
        if self.stats_left_panel.layout():
            QWidget().setLayout(self.stats_left_panel.layout())
        if self.stats_right_panel.layout():
            QWidget().setLayout(self.stats_right_panel.layout())
            
        if self.config.is_points_mode():
            self._setup_points_mode()
        else:
            self._setup_destiny_mode()

    def _setup_points_mode(self):
        left_layout = QVBoxLayout(self.stats_left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        self.remaining_points = self.config.points_available
        self.points_label = QLabel(f"Remaining Points: {self.remaining_points}")
        left_layout.addWidget(self.points_label)
        
        left_layout.addWidget(QLabel(f"Max Stat: {self.config.stat_upper_limit}"))
        left_layout.addWidget(QLabel(f"Min Stat: {self.config.stat_lower_limit}"))
        
        self.custom_luck_checkbox = QCheckBox("Custom Luck Value")
        self.custom_luck_checkbox.stateChanged.connect(self._on_custom_luck_changed)
        left_layout.addWidget(self.custom_luck_checkbox)
        
        left_layout.addStretch()
        
        right_layout = QGridLayout(self.stats_right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)
        
        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUCK']
        for i, stat in enumerate(stats):
            entry = TFValueEntry(
                f"{stat}:",
                value_size=60,
                number_only=True
            )
            if stat == 'LUCK':
                entry.value_field.setEnabled(False)
                entry.set_value(0)
            else:
                entry.value_field.setEnabled(True)
                entry.value_field.textChanged.connect(self._on_stat_value_changed)
                
            self.stat_entries[stat] = entry
            right_layout.addWidget(entry, i // 3, i % 3)

    def _setup_destiny_mode(self):
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        left_layout.addWidget(QLabel(f"Dice Count: {self.config.dice_count}"))
        self.roll_button = TFBaseButton(
            "Roll for Stats",
            self,
            on_clicked=self._on_roll_stats
        )
        left_layout.addWidget(self.roll_button)
        left_layout.addStretch()
        
        self.stats_left_panel.setLayout(left_layout)
        
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        self.roll_results_frame = QFrame()
        right_layout.addWidget(self.roll_results_frame)
        right_layout.addStretch()
        
        self.stats_right_panel.setLayout(right_layout)
    
    def _on_avatar_upload(self):
        # TODO: Implement avatar upload
        pass

    def _on_roll_stats(self):
        if self.roll_results_frame.layout():
            QWidget().setLayout(self.roll_results_frame.layout())
            
        layout = QVBoxLayout()
        
        self.roll_checkboxes.clear()
        
        button_group = QButtonGroup(self)
        
        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUCK']
        
        for i in range(self.config.dice_count):
            group_frame = QFrame()
            group_layout = QVBoxLayout()
            
            stat_values = {stat: self._roll_stat(stat) for stat in stats}
            
            radio = QRadioButton(f"Result Set {i + 1}")
            button_group.addButton(radio)
            self.roll_checkboxes.append((radio, stat_values))
            group_layout.addWidget(radio)
            
            stats_text = ", ".join(f"{stat}: {value}" for stat, value in stat_values.items())
            group_layout.addWidget(QLabel(stats_text))
            
            group_frame.setLayout(group_layout)
            layout.addWidget(group_frame)
        
        self.confirm_roll_button = TFConfirmButton(
            self,
            enabled=True,
            on_clicked=self._on_confirm_roll
        )
        layout.addWidget(self.confirm_roll_button)
        
        self.roll_results_frame.setLayout(layout)
        
        self.roll_button.setEnabled(False)

    def _roll_stat(self, stat_type: str) -> int:
        import random
        
        if stat_type in ['SIZ', 'INT']:
            result = (sum(random.randint(1, 6) for _ in range(2)) + 6) * 5
        elif stat_type == 'EDU':
            result = (sum(random.randint(1, 6) for _ in range(3)) + 3) * 5
        else:
            result = sum(random.randint(1, 6) for _ in range(3)) * 5
            
        return result

    def _on_confirm_roll(self):
        selected_group = None
        for radio, stat_values in self.roll_checkboxes:
            if radio.isChecked():
                selected_group = stat_values
                break
        
        if selected_group is None:
            self.main_window.app.show_warning(
                "Selection Required",
                "Please select one set of results.",
                buttons=["OK"]
            )
            return
        
        if self.roll_results_frame.layout():
            QWidget().setLayout(self.roll_results_frame.layout())
            
        layout = QGridLayout()
        
        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUCK']
        for i, stat in enumerate(stats):
            entry = TFValueEntry(
                f"{stat}:",
                value_size=60,
                number_only=True
            )
            entry.value_field.setEnabled(False)
            entry.set_value(selected_group[stat])
            
            self.stat_entries[stat] = entry
            layout.addWidget(entry, i // 3, i % 3)
        
        self.roll_results_frame.setLayout(layout)

    def _on_custom_luck_changed(self, state):
        luck_entry = self.stat_entries.get('LUCK')
        if luck_entry:
            luck_entry.value_field.setEnabled(state == Qt.CheckState.Checked.value)
            if not state:
                luck_entry.set_value(0)

    def _on_stat_value_changed(self):
        total_points = 0
        for stat, entry in self.stat_entries.items():
            if stat == 'LUCK' and not self.custom_luck_checkbox.isChecked():
                continue
            try:
                value = int(entry.get_value() or 0)
                total_points += value
            except ValueError:
                pass
        
        self.remaining_points = self.config.points_available - total_points
        self.points_label.setText(f"Remaining Points: {self.remaining_points}")
        
    def _on_calculate(self):
        if not self._validate_all_fields():
            return
            
        self._perform_age_calculation()
        
        self._save_data_to_pc_data()
        
        self._lock_fields()
        self.next_button.setEnabled(True)
        if self.config.allow_stat_exchange:
            self.exchange_button.setEnabled(True)
        
    def _on_exchange(self):
        current_stats = {
            stat: int(entry.get_value())
            for stat, entry in self.stat_entries.items()
            if stat != 'LUCK'
        }
        
        dialog = StatExchangeDialog(self, self.remaining_exchange_times, current_stats)
        success, result = dialog.get_input()
        
        if success and result:
            stat1, stat2 = result
            val1 = self.stat_entries[stat1].get_value()
            val2 = self.stat_entries[stat2].get_value()
            self.stat_entries[stat1].set_value(val2)
            self.stat_entries[stat2].set_value(val1)
            
            self.remaining_exchange_times -= 1
            if self.remaining_exchange_times == 0:
                self.exchange_button.setEnabled(False)
            
            self._save_data_to_pc_data()
    
    def _perform_age_calculation(self):
        age = int(self.age.get_value())
        modifications = []
        
        edu_improvement_count = 0
        if age < 20:
            edu_improvement_count = 0
        elif age < 40:
            edu_improvement_count = 1
        elif age < 50:
            edu_improvement_count = 2
        elif age < 60:
            edu_improvement_count = 3
        elif age < 70:
            edu_improvement_count = 4
        else:
            edu_improvement_count = 4
            
        current_edu = int(self.stat_entries['EDU'].get_value())
        # TODO: 实际的EDU提升逻辑需要掷骰，这里暂时简化处理
        new_edu = min(99, current_edu + edu_improvement_count * 5)
        if new_edu != current_edu:
            modifications.append(f"EDU increased from {current_edu} to {new_edu}")
            self.stat_entries['EDU'].set_value(str(new_edu))
        
        if age >= 40:
            physical_stats = ['STR', 'CON', 'DEX']
            reduction = 5 * ((age - 40) // 10)
            for stat in physical_stats:
                current_val = int(self.stat_entries[stat].get_value())
                new_val = max(1, current_val - reduction)
                if new_val != current_val:
                    modifications.append(f"{stat} reduced from {current_val} to {new_val}")
                    self.stat_entries[stat].set_value(str(new_val))
        
        if age >= 70:
            current_app = int(self.stat_entries['APP'].get_value())
            new_app = max(1, current_app - 10)
            if new_app != current_app:
                modifications.append(f"APP reduced from {current_app} to {new_app}")
                self.stat_entries['APP'].set_value(str(new_app))
        
        if not self.custom_luck_checkbox.isChecked():
            pow_val = int(self.stat_entries['POW'].get_value())
            self.stat_entries['LUCK'].set_value(str(pow_val * 5))
            
        if modifications:
            self.main_window.app.show_warning(
                "Age-based Modifications",
                "The following modifications were applied:\n" + "\n".join(modifications),
                buttons=["OK"]
            )

    def _validate_all_fields(self) -> bool:
        data = {
            'metadata': {
                'player_name': self.player_name.get_value(),
                'campaign_date': self.campaign_date.get_value(),
                'era': self.era.get_value()
            },
            'personal_info': {
                'name': self.char_name.get_value(),
                'age': self.age.get_value(),
                'occupation': self.occupation.get_value(),
                'residence': self.residence.get_value(),
                'birthplace': self.birthplace.get_value()
            },
            'basic_stats': {
                'strength': self.stat_entries['STR'].get_value(),
                'constitution': self.stat_entries['CON'].get_value(),
                'size': self.stat_entries['SIZ'].get_value(),
                'dexterity': self.stat_entries['DEX'].get_value(),
                'appearance': self.stat_entries['APP'].get_value(),
                'intelligence': self.stat_entries['INT'].get_value(),
                'power': self.stat_entries['POW'].get_value(),
                'education': self.stat_entries['EDU'].get_value()
            }
        }
        
        if self.custom_luck_checkbox.isChecked():
            data['basic_stats']['luck'] = self.stat_entries['LUCK'].get_value()
        
        errors = self.validator.validate_dict(data, is_new=True)
        if errors:
            self._show_validation_error("\n".join(errors))
            return False
            
        if self.config.is_points_mode() and self.remaining_points != 0:
            self._show_validation_error(
                f"Points allocation must be exact. "
                f"Currently {abs(self.remaining_points)} points "
                f"{'over' if self.remaining_points < 0 else 'remaining'}"
            )
            return False
            
        return True

    def _save_data_to_pc_data(self):
        metadata = {
            'player_name': self.player_name.get_value(),
            'campaign_date': self.campaign_date.get_value(),
            'era': self.era.get_value()
        }
        
        personal_info = {
            'name': self.char_name.get_value(),
            'age': int(self.age.get_value()),
            'occupation': self.occupation.get_value(),
            'residence': self.residence.get_value(),
            'birthplace': self.birthplace.get_value()
        }
        
        basic_stats = {
            'strength': int(self.stat_entries['STR'].get_value()),
            'constitution': int(self.stat_entries['CON'].get_value()),
            'size': int(self.stat_entries['SIZ'].get_value()),
            'dexterity': int(self.stat_entries['DEX'].get_value()),
            'appearance': int(self.stat_entries['APP'].get_value()),
            'intelligence': int(self.stat_entries['INT'].get_value()),
            'power': int(self.stat_entries['POW'].get_value()),
            'education': int(self.stat_entries['EDU'].get_value()),
            'luck': int(self.stat_entries['LUCK'].get_value())
        }
        
        self.main_window.pc_data.update({
            'metadata': metadata,
            'personal_info': personal_info,
            'basic_stats': basic_stats
        })

    def _lock_fields(self):
        self.char_name.value_field.setEnabled(False)
        self.age.value_field.setEnabled(False)
        self.occupation.value_field.setEnabled(False)
        self.residence.value_field.setEnabled(False)
        self.birthplace.value_field.setEnabled(False)
        
        for entry in self.stat_entries.values():
            entry.value_field.setEnabled(False)
        
        if self.config.is_points_mode():
            self.custom_luck_checkbox.setEnabled(False)
        else:
            self.roll_button.setEnabled(False)
        
        self.calculate_button.setEnabled(False)

    def _perform_reset(self):
        self.remaining_exchange_times = self.config.stat_exchange_times
        
        if 'metadata' in self.main_window.pc_data:
            del self.main_window.pc_data['metadata']
        if 'personal_info' in self.main_window.pc_data:
            del self.main_window.pc_data['personal_info']
        if 'basic_stats' in self.main_window.pc_data:
            del self.main_window.pc_data['basic_stats']
        
        self.player_name.set_value("")
        self.campaign_date.set_value("")
        self.era.set_value("Modern")
        
        self.char_name.set_value("")
        self.age.set_value("")
        self.occupation.set_value(self.occupation.value_field.itemText(0))
        self.residence.set_value("")
        self.birthplace.set_value("")
        
        self._update_stats_display()
        
        self.calculate_button.setEnabled(True)
        self.exchange_button.setEnabled(False)
        self.next_button.setEnabled(False)
        
        self.char_name.value_field.setEnabled(True)
        self.age.value_field.setEnabled(True)
        self.occupation.value_field.setEnabled(True)
        self.residence.value_field.setEnabled(True)
        self.birthplace.value_field.setEnabled(True)

    def _show_validation_error(self, message: str):
        self.main_window.app.show_warning(
            "Validation Error",
            message,
            buttons=["OK"]
        )

class StatExchangeDialog(TFComputingDialog):
    def __init__(self, parent, remaining_times: int, current_stats: dict):
        self.remaining_times = remaining_times
        self.current_stats = current_stats
        self.stat_checkboxes = {}
        super().__init__("Exchange Stats", parent)
        
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
            if checkbox.isChecked():
                selected.append(stat)
        return {'selected': selected}
        
    def process_validated_data(self, data: dict) -> tuple[str, str]:
        selected = data['selected']
        if len(selected) != 2:
            raise ValueError("Please select exactly two stats to exchange")
        return tuple(selected)
