import os
import shutil
import random
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Tuple

from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGroupBox, QButtonGroup,
                           QLabel, QRadioButton, QGridLayout, QWidget, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from ui.components.tf_base_button import TFBaseButton, TFConfirmButton
from ui.components.tf_computing_dialog import TFComputingDialog
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_option_entry import TFOptionEntry
from implements.coc_tools.pc_builder_helper.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_helper.phase_ui import BasePhaseUI
from utils.validator.tf_validation_rules import TFValidationRule
from utils.validator.tf_validator import TFValidator
from utils.helper import resource_path


@dataclass
class Occupation:
    name: str
    skill_points_formula: str

    def __str__(self):
        return self.name

    def format_formula_for_display(self) -> str:
        return self.skill_points_formula.replace('*', '×').replace('MAX', 'max')

    def _calculate_max_stats(self, stats_str: str, stats: Dict[str, int]) -> int:
        stats_list = [s.strip() for s in stats_str.split(',')]
        return max(stats[stat] for stat in stats_list)

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
                total += stats[stat] * multiplier

        return total


OCCUPATIONS = [
    Occupation("Private Detective", "EDU*2 + MAX(DEX, STR)*2"),
    Occupation("Professor", "EDU*4"),
    Occupation("Police Officer", "EDU*2 + MAX(STR, DEX, POW)*2"),
    Occupation("Doctor", "EDU*4"),
    Occupation("Journalist", "EDU*2 + MAX(APP, DEX, POW)*2")
]


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
        self.occupation_formula_label = None
        self.skill_points_label = None
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
            height=30,
            on_clicked=self._on_calculate
        )
        self.exchange_button = TFBaseButton(
            "Stat Exchange",
            self,
            height=30,
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

        self.char_name = TFValueEntry("Character Name:", value_size=150)
        self.age = TFValueEntry("Age:", value_size=150, number_only=True)

        occupation_options = [str(occ) for occ in OCCUPATIONS]
        self.occupation = TFOptionEntry("Occupation:", occupation_options, value_size=150)

        # Create formula label
        self.occupation_formula_label = QLabel("")
        self.occupation.value_field.currentTextChanged.connect(self._update_occupation_formula)

        self.residence = TFValueEntry("Residence:", value_size=150)
        self.birthplace = TFValueEntry("Birthplace:", value_size=150)

        layout.addWidget(self.char_name)
        layout.addWidget(self.age)
        layout.addWidget(self.occupation)
        layout.addWidget(self.occupation_formula_label)
        layout.addWidget(self.residence)
        layout.addWidget(self.birthplace)
        layout.addStretch()

        self._update_occupation_formula()
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

    def _update_occupation_formula(self):
        current_text = self.occupation.get_value()
        selected_occupation = next((occ for occ in OCCUPATIONS if str(occ) == current_text), None)
        if selected_occupation:
            formatted_formula = selected_occupation.format_formula_for_display()
            self.occupation_formula_label.setText(f"Skill Points: {formatted_formula}")

    def _setup_points_mode(self):
        left_layout = QVBoxLayout(self.stats_left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        left_layout.addStretch()

        self.remaining_points = self.config.points_available
        self.points_label = QLabel(f"Remaining Points: {self.remaining_points}")
        left_layout.addWidget(self.points_label)

        left_layout.addWidget(QLabel(f"Max Stat: {self.config.stat_upper_limit}"))
        left_layout.addWidget(QLabel(f"Min Stat: {self.config.stat_lower_limit}"))

        self.custom_luck_label = QLabel(
            "Luck Value: Custom" if self.config.allow_custom_luck else "Luck Value: Based on Roll"
        )
        left_layout.addWidget(self.custom_luck_label)

        self.skill_points_label = QLabel()
        left_layout.addWidget(self.skill_points_label)

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
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Avatar Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if not file_path:
            return

        try:
            avatar_dir = Path(resource_path("resources/coc/pcs/avatars"))
            avatar_dir.mkdir(parents=True, exist_ok=True)

            avatar_filename = os.path.basename(file_path)
            avatar_path = avatar_dir / avatar_filename

            if avatar_path.exists():
                response = self.main_window.app.show_question(
                    "File Exists",
                    f"File {avatar_filename} already exists. Do you want to overwrite it?",
                    buttons=["Yes", "No"]
                )
                if response == "No":
                    base, ext = os.path.splitext(avatar_filename)
                    counter = 1
                    while avatar_path.exists():
                        avatar_filename = f"{base}_{counter}{ext}"
                        avatar_path = avatar_dir / avatar_filename
                        counter += 1

            shutil.copy2(file_path, avatar_path)

            pixmap = QPixmap(str(avatar_path))
            scaled_pixmap = pixmap.scaled(
                self.avatar_label.size(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation
            )
            self.avatar_label.setPixmap(scaled_pixmap)

            relative_path = str(avatar_path.relative_to(Path.cwd()))
            if 'metadata' not in self.main_window.pc_data:
                self.main_window.pc_data['metadata'] = {}
            self.main_window.pc_data['metadata']['avatar'] = relative_path

        except Exception as e:
            self.main_window.app.show_warning(
                "Avatar Upload Error",
                f"Failed to upload avatar: {str(e)}",
                buttons=["OK"]
            )

    def _calculate_skill_points(self) -> Tuple[int, int]:
        stats = {
            'STR': int(self.stat_entries['STR'].get_value()),
            'DEX': int(self.stat_entries['DEX'].get_value()),
            'POW': int(self.stat_entries['POW'].get_value()),
            'CON': int(self.stat_entries['CON'].get_value()),
            'APP': int(self.stat_entries['APP'].get_value()),
            'EDU': int(self.stat_entries['EDU'].get_value()),
            'SIZ': int(self.stat_entries['SIZ'].get_value()),
            'INT': int(self.stat_entries['INT'].get_value())
        }

        current_occupation = next(
            (occ for occ in OCCUPATIONS if str(occ) == self.occupation.get_value()),
            None
        )

        if not current_occupation:
            return 0, 0

        occupation_points = current_occupation.calculate_skill_points(stats)
        interest_points = stats['INT'] * 2

        return occupation_points, interest_points

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
            if stat == 'LUCK' and not self.config.allow_mixed_points:
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

        occupation_points, interest_points = self._calculate_skill_points()
        self.skill_points_label.setText(
            f"Occupation Skill Points: {occupation_points}\n"
            f"Interest Skill Points: {interest_points}"
        )

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
        total_improvement, improvement_details = self._perform_edu_improvements(edu_improvement_count, current_edu)

        if total_improvement > 0:
            new_edu = min(99, current_edu + total_improvement)
            modifications.append(f"EDU increased from {current_edu} to {new_edu}")
            modifications.extend(improvement_details)
            self.stat_entries['EDU'].set_value(str(new_edu))

        if age >= 40:
            base_reduction = 5 * ((min(age, 70) - 40) // 10)
            if base_reduction > 0:
                self._handle_physical_reduction(base_reduction, modifications)

            if age >= 70:
                current_app = int(self.stat_entries['APP'].get_value())
                new_app = max(1, current_app - 10)
                if new_app != current_app:
                    modifications.append(f"APP reduced from {current_app} to {new_app}")
                    self.stat_entries['APP'].set_value(str(new_app))

                self._handle_physical_reduction(15, modifications)

        if not self.config.allow_mixed_points:
            pow_val = int(self.stat_entries['POW'].get_value())
            self.stat_entries['LUCK'].set_value(str(pow_val * 5))
            
        if modifications:
            self.main_window.app.show_warning(
                "Age-based Modifications",
                "The following modifications were applied:\n" + "\n".join(modifications),
                buttons=["OK"]
            )

    def _perform_edu_improvements(self, improvement_count: int, current_edu: int) -> tuple[int, list[str]]:
        total_improvement = 0
        improvement_details = []

        for i in range(improvement_count):
            check_roll = random.randint(1, 100)
            if check_roll > current_edu:
                improvement = random.randint(1, 10)
                total_improvement += improvement
                improvement_details.append(
                    f"Check {i + 1}: Roll {check_roll} > EDU {current_edu}, gained {improvement} points")
            else:
                improvement_details.append(f"Check {i + 1}: Roll {check_roll} ≤ EDU {current_edu}, no improvement")

        return total_improvement, improvement_details

    def _handle_physical_reduction(self, total_reduction: int, modifications: list) -> None:
        physical_stats = ['STR', 'CON', 'DEX']
        current_stats = {
            stat: int(self.stat_entries[stat].get_value())
            for stat in physical_stats
        }

        dialog = AgeReductionDialog(self, total_reduction, current_stats)
        success, reductions = dialog.get_input()

        if success:
            for stat, reduction in reductions.items():
                old_val = current_stats[stat]
                new_val = old_val - reduction
                if new_val != old_val:
                    modifications.append(f"{stat} reduced from {old_val} to {new_val}")
                    self.stat_entries[stat].set_value(str(new_val))

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

        if self.config.allow_mixed_points:
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
        for entry in self.stat_entries.values():
            entry.value_field.setEnabled(False)

        self.age.value_field.setEnabled(False)
        self.occupation.value_field.setEnabled(False)

        if self.config.is_points_mode():
            self.custom_luck_label.setEnabled(False)
        else:
            self.roll_button.setEnabled(False)

        self.calculate_button.setEnabled(False)

    def _reset_content(self):
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

        if self.skill_points_label:
            self.skill_points_label.setText("")

        self.calculate_button.setEnabled(True)
        self.exchange_button.setEnabled(False)
        self.next_button.setEnabled(False)

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
        self._setup_validation_rules()
        super().__init__(f"Reduce Stats by {total_reduction} Points", parent)
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

        self.validator.add_rules(rules)

        self.validator.add_custom_validator(
            'total_reduction',
            lambda values: (
                sum(int(v) for v in values) == self.total_reduction,
                f"Total reduction must equal exactly {self.total_reduction}"
            )
        )

        self.validator.add_custom_validator(
            'final_values',
            lambda stat, reduction: (
                int(self.current_stats[stat]) - int(reduction) >= 1,
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
        try:
            total = sum(int(entry.get_value() or 0) for entry in self.stat_entries.values())
            remaining = self.total_reduction - total
            self.remaining_label.setText(f"Remaining points to allocate: {remaining}")
        except ValueError:
            pass

    def get_field_values(self) -> dict:
        return {
            f'reduction_{stat}': entry.get_value() or "0"
            for stat, entry in self.stat_entries.items()
        }

    def process_validated_data(self, data: dict) -> dict:
        reductions = [int(val) for val in data.values()]
        if not self.validator.validate_field('total_reduction', reductions)[0]:
            raise ValueError(f"Total reduction must equal exactly {self.total_reduction}")

        result = {}
        for stat in ['STR', 'CON', 'DEX']:
            reduction = int(data[f'reduction_{stat}'])
            if not self.validator.validate_field('final_values', (stat, reduction))[0]:
                raise ValueError(f"Final {stat} value cannot be less than 1")
            result[stat] = reduction

        return result
