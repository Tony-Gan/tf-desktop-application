import os
import shutil
import random
from datetime import datetime
from pathlib import Path
from typing import Tuple

from PyQt6 import sip
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGroupBox, QButtonGroup,
                             QDialog, QScrollArea, QLabel, QRadioButton, QGridLayout,
                             QWidget, QFileDialog, QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont

from ui.components.tf_base_button import TFBaseButton, TFConfirmButton
from ui.components.tf_computing_dialog import TFComputingDialog
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_option_entry import TFOptionEntry
from implements.coc_tools.pc_builder_helper.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_helper.phase_ui import BasePhaseUI
from implements.coc_tools.pc_builder_helper.phase_status import PhaseStatus
from implements.coc_tools.pc_builder_helper.occupation import OCCUPATIONS
from utils.validator.tf_validation_rules import TFValidationRule
from utils.validator.tf_validator import TFValidator
from utils.helper import resource_path


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
        
        self.gender = None
        self.occupation = None
        self.nationality = None
        self.residence = None
        self.birthplace = None
        self.skill_points = None
        
        self.stats_left_panel = None
        self.stats_right_panel = None
        self.stat_entries = {}
        self.points_label = None
        self.occupation_points_entry = None
        self.interest_points_entry = None
        self.custom_luck_entry = None
        self.remaining_points_entry = None
        self.max_stat_entry = None
        self.min_stat_entry = None
        self.derived_entries = {}
        
        self.roll_button = None
        self.roll_results_frame = None
        self.roll_checkboxes = []
        self.confirm_roll_button = None
        self.remaining_exchange_times = self.config.stat_exchange_times

        super().__init__(PCBuilderPhase.PHASE1, main_window, parent)

        self.validator = TFValidator()
        self._setup_validation_rules()
        self.main_window.config_updated.connect(self._on_config_updated)

    def _setup_ui(self):
        content_layout = QVBoxLayout()
        content_layout.setParent(self.main_window)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        
        upper_frame = QFrame()
        upper_layout = QHBoxLayout(upper_frame)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(10)

        upper_layout.addWidget(self._create_avatar_group())
        
        mid_panel = QFrame()
        mid_layout = QVBoxLayout(mid_panel)
        mid_layout.setContentsMargins(0, 0, 0, 0)
        mid_layout.setSpacing(10)
        
        mid_layout.addWidget(self._create_metadata_group())
        mid_layout.addWidget(self._create_left_personal_info_group())
        
        upper_layout.addWidget(mid_panel)
        
        upper_layout.addWidget(self._create_personal_info_group())
        
        content_layout.addWidget(upper_frame)
        
        content_layout.addWidget(self._create_derived_stats_group())
        
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        
        self.stats_left_panel = QFrame()
        self.stats_right_panel = QFrame()
        
        stats_layout.addWidget(self.stats_left_panel, 1)
        stats_layout.addWidget(self.stats_right_panel, 2)
        
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
        self.validator.add_custom_validator(
            'check_occupation',
            lambda x: (x != "None", "Please select an occupation")
        )
        self.validator.add_custom_validator(
            'check_gender',
            lambda x: (x != "None", "Please select a gender")
        )
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
            'personal_info.gender': TFValidationRule(
                type_=str,
                required=True,
                custom='check_gender'
            ),
            'personal_info.occupation': TFValidationRule(
                type_=str,
                required=True,
                custom='check_occupation'
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

        if self.config.is_points_mode():
            for stat in ['strength', 'constitution', 'size', 'dexterity',
                         'appearance', 'intelligence', 'power', 'education']:
                rules[f'basic_stats.{stat}'] = TFValidationRule(
                    type_=int,
                    required=True,
                    min_val=self.config.stat_lower_limit,
                    max_val=self.config.stat_upper_limit
                )

            if self.config.allow_custom_luck:
                rules['basic_stats.luck'] = TFValidationRule(
                    type_=int,
                    required=True,
                    min_val=self.config.stat_lower_limit,
                    max_val=self.config.stat_upper_limit
                )

        self.validator.add_rules(rules)

    def _on_config_updated(self):
        self.remaining_exchange_times = self.config.stat_exchange_times
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
        
        layout.addStretch()
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
            label_size=135,
            value_size=140,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.campaign_date = TFValueEntry(
            "Campaign Date:",
            label_size=135,
            value_size=140,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        
        era_options = ["Medieval", "1890s", "1920s", "Modern", "Near Future", "Future"]
        self.era = TFOptionEntry(
            "Era:",
            era_options,
            current_value="Modern",
            label_size=135,
            value_size=140,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        
        layout.addWidget(self.player_name)
        layout.addWidget(self.campaign_date)
        layout.addWidget(self.era)
        layout.addStretch()
        return group

    def _create_left_personal_info_group(self):
        group = QGroupBox("Personal Information")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.char_name = TFValueEntry(
            "Character Name:", 
            value_size=140, 
            label_size=135,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.age = TFValueEntry(
            "Age:", 
            value_size=140, 
            label_size=135, 
            number_only=True,
            alignment=Qt.AlignmentFlag.AlignLeft,
            allow_decimal=False
        )
        
        layout.addWidget(self.char_name)
        layout.addWidget(self.age)
        layout.addStretch()
        return group

    def _create_personal_info_group(self):
        group = QGroupBox("Personal Information")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)

        self.gender = TFOptionEntry(
            "Gender:", 
            ["None", "Male", "Female", "Other"],
            label_size=130,
            value_size=140,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        
        occupation_options = ["None"] + sorted([str(occ) for occ in OCCUPATIONS])
        self.occupation = TFOptionEntry(
            "Occupation:", 
            occupation_options, 
            label_size=130, 
            value_size=140,
            alignment=Qt.AlignmentFlag.AlignLeft,
            extra_value_width=40
        )
        
        self.skill_points_formula = TFValueEntry(
            "Skill Points:",
            label_size=130,
            value_size=140,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.skill_points_formula.value_field.setEnabled(False)
        self.occupation.value_field.currentTextChanged.connect(self._update_occupation_formula)
        
        self.nationality = TFValueEntry(
            "Nationality:", 
            label_size=130, 
            value_size=140,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        
        self.residence = TFValueEntry(
            "Residence:", 
            label_size=130, 
            value_size=140,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        
        self.birthplace = TFValueEntry(
            "Birthplace:", 
            label_size=130, 
            value_size=140,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        
        layout.addWidget(self.gender)
        layout.addWidget(self.occupation)
        layout.addWidget(self.skill_points_formula)
        layout.addWidget(self.nationality)
        layout.addWidget(self.residence)
        layout.addWidget(self.birthplace)
        layout.addStretch()
        
        return group

    def _create_derived_stats_group(self) -> QFrame:
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        derived_stats = [
            ('HP', 'HP'),
            ('MP', 'MP'),
            ('SAN', 'San'),
            ('MOV', 'Move'),
            ('DB', 'DB'),
            ('Build', 'Build')
        ]

        for stat_key, label_text in derived_stats:
            entry = TFValueEntry(
                label_text + ":",
                value_size=40,
                label_size=40,
                number_only=True,
                alignment=Qt.AlignmentFlag.AlignLeft
            )
            entry.value_field.setEnabled(False)
            entry.set_value("")
            self.derived_entries[stat_key] = entry
            layout.addWidget(entry)

        return frame

    def _update_stats_display(self):
        if self.stats_left_panel.layout():
            while self.stats_left_panel.layout().count():
                item = self.stats_left_panel.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            sip.delete(self.stats_left_panel.layout())

        if self.stats_right_panel.layout():
            while self.stats_right_panel.layout().count():
                item = self.stats_right_panel.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            sip.delete(self.stats_right_panel.layout())

        self.stat_entries.clear()
        self.points_label = None
        self.skill_points_label = None

        if self.config.is_points_mode():
            self._setup_points_mode()
        else:
            self._setup_destiny_mode()

    def _update_occupation_formula(self):
        current_text = self.occupation.get_value()
        selected_occupation = next((occ for occ in OCCUPATIONS if str(occ) == current_text), None)
        if selected_occupation:
            formula = selected_occupation.skill_points_formula
            if 'MAX' in formula:
                base_part = formula.split('+')[0].strip()
                max_part = formula.split('+')[1].strip()
                
                stats = max_part[max_part.find('(')+1:max_part.find(')')].replace(',', '|').replace(' ', '')
                multiplier = max_part[max_part.find('*')+1:]
                
                formatted_formula = f"{base_part}+{stats}*{multiplier}"
            else:
                formatted_formula = formula
            
            self.skill_points_formula.set_value(formatted_formula)

    def _setup_points_mode(self):
        left_layout = QVBoxLayout(self.stats_left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        left_layout.addStretch()

        self.remaining_points = self.config.points_available
        self.remaining_points_entry = TFValueEntry(
            "Remaining Points:",
            str(self.remaining_points),
            label_size=135,
            value_size=60,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        left_layout.addWidget(self.remaining_points_entry)

        self.max_stat_entry = TFValueEntry(
            "Max Stat:",
            str(self.config.stat_upper_limit),
            label_size=135,
            value_size=60,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        left_layout.addWidget(self.max_stat_entry)

        self.min_stat_entry = TFValueEntry(
            "Min Stat:",
            str(self.config.stat_lower_limit),
            label_size=135,
            value_size=60,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        left_layout.addWidget(self.min_stat_entry)

        self.custom_luck_entry = TFValueEntry(
            "Luck Value:",
            "Custom" if self.config.allow_custom_luck else "Based on Roll",
            label_size=135,
            value_size=100,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        left_layout.addWidget(self.custom_luck_entry)

        self.occupation_points_entry = TFValueEntry(
            "Occupation Points:",
            "",
            label_size=135,
            value_size=60,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        left_layout.addWidget(self.occupation_points_entry)

        self.interest_points_entry = TFValueEntry(
            "Interest Points:",
            "",
            label_size=135,
            value_size=60,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        left_layout.addWidget(self.interest_points_entry)

        left_layout.addStretch()

        right_layout = QGridLayout(self.stats_right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)

        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK']
        for i, stat in enumerate(stats):
            row = i // 3
            col = i % 3
            
            entry = TFValueEntry(
                f"{stat}:",
                value_size=40,
                label_size=40,
                number_only=True,
                allow_decimal=False,
                alignment=Qt.AlignmentFlag.AlignLeft
            )
            if stat == 'LUK':
                if self.config.allow_custom_luck:
                    entry.value_field.setEnabled(True)
                    entry.value_field.textChanged.connect(self._on_stat_value_changed)
                else:
                    entry.value_field.setEnabled(False)
                    entry.set_value(0)
            else:
                entry.value_field.setEnabled(True)
                entry.value_field.textChanged.connect(self._on_stat_value_changed)

            self.stat_entries[stat] = entry
            right_layout.addWidget(entry, row, col)
            
            if col == 2:
                right_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum), row, 3)

    def _setup_destiny_mode(self):
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        self.dice_count_entry = TFValueEntry(
            "Dice Count:",
            str(self.config.dice_count),
            label_size=135,
            value_size=60,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        left_layout.addWidget(self.dice_count_entry)
        
        self.roll_button = TFBaseButton(
            "Roll for Stats",
            self,
            on_clicked=self._on_roll_stats
        )
        left_layout.addWidget(self.roll_button)
        
        self.occupation_points_entry = TFValueEntry(
            "Occupation Points:",
            "",
            label_size=135,
            value_size=60,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        left_layout.addWidget(self.occupation_points_entry)

        self.interest_points_entry = TFValueEntry(
            "Interest Points:",
            "",
            label_size=135,
            value_size=60,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        left_layout.addWidget(self.interest_points_entry)
        
        left_layout.addStretch()
        
        self.stats_left_panel.setLayout(left_layout)
        
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        self.roll_results_frame = QFrame()
        self.roll_results_frame.setMinimumHeight(200)
        self.roll_results_frame.setLayout(QVBoxLayout())
        self.roll_results_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        right_layout.addWidget(self.roll_results_frame)
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
            avatar_dir = Path(resource_path("resources/data/coc/pcs/avatars"))
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
            self.main_window.pc_data['metadata']['avatar_file'] = relative_path

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

    def _calculate_derived_stats(self) -> dict:
        try:
            con = int(self.stat_entries['CON'].get_value())
            siz = int(self.stat_entries['SIZ'].get_value())
            pow_stat = int(self.stat_entries['POW'].get_value())
            str_stat = int(self.stat_entries['STR'].get_value())
            dex = int(self.stat_entries['DEX'].get_value())

            hp = (con + siz) // 10
            self.derived_entries['HP'].set_value(str(hp))

            mp = pow_stat // 5
            self.derived_entries['MP'].set_value(str(mp))

            san = pow_stat
            self.derived_entries['SAN'].set_value(str(san))

            if dex < siz and str_stat < siz:
                mov = 7
            elif dex > siz and str_stat > siz:
                mov = 9
            else:
                mov = 8
            self.derived_entries['MOV'].set_value(str(mov))

            str_siz = str_stat + siz

            if 2 <= str_siz <= 64:
                build = -2
                db = "-2"
            elif 65 <= str_siz <= 84:
                build = -1
                db = "-1"
            elif 85 <= str_siz <= 124:
                build = 0
                db = "0"
            elif 125 <= str_siz <= 164:
                build = 1
                db = "+1d4"
            elif 165 <= str_siz <= 204:
                build = 2
                db = "+1d6"
            else:
                build = 3
                db = "+2d6"

            self.derived_entries['DB'].set_value(db)
            self.derived_entries['Build'].set_value(str(build))

            return {
                "hp_max": hp,
                "hp_current": hp,
                "mp_max": mp,
                "mp_current": mp,
                "san_max": san,
                "san_current": san,
                "movement_rate": mov,
                "damage_bonus": db,
                "build": build
            }

        except (ValueError, KeyError) as e:
            return

    def _on_roll_stats(self):
        if self.roll_results_frame is not None:
            layout = self.roll_results_frame.layout()
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
            else:
                self.roll_results_frame.setLayout(QVBoxLayout())
        else:
            self.roll_results_frame = QFrame()
            self.roll_results_frame.setLayout(QVBoxLayout())
            if self.stats_right_panel.layout():
                self.stats_right_panel.layout().addWidget(self.roll_results_frame)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(2)
        content_layout.setContentsMargins(5, 5, 5, 5)

        self.roll_checkboxes.clear()
        button_group = QButtonGroup(self)

        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK']

        for _ in range(self.config.dice_count):
            group_frame = QFrame()
            group_layout = QVBoxLayout(group_frame)
            group_layout.setSpacing(2)
            group_layout.setContentsMargins(2, 2, 2, 2)

            stat_values = {stat: self._roll_stat(stat) for stat in stats}
            stats_text = ", ".join(
                f"{stat}: {value}" if stat != "INT" else f"\n{stat}: {value}"
                for stat, value in stat_values.items()
            )
            
            radio = QRadioButton(stats_text)
            radio.setFont(QFont("Inconsolata", 10))
            button_group.addButton(radio)

            self.roll_checkboxes.append((radio, stat_values))
            group_layout.addWidget(radio)
            content_layout.addWidget(group_frame)

        self.confirm_roll_button = TFConfirmButton(
            self,
            enabled=True,
            on_clicked=self._on_confirm_roll
        )
        content_layout.addWidget(self.confirm_roll_button)
        scroll_area.setWidget(scroll_content)

        self.roll_results_frame.layout().addWidget(scroll_area)

        self.roll_results_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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
            self.stat_entries.clear()
            QWidget().setLayout(self.roll_results_frame.layout())
            
        layout = QGridLayout()
        
        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK']
        for i, stat in enumerate(stats):
            row = i // 3
            col = i % 3

            entry = TFValueEntry(
                f"{stat}:",
                value_size=40,
                label_size=40,
                number_only=True,
                allow_decimal=False
            )
            entry.value_field.setEnabled(False)
            entry.set_value(selected_group[stat])
            
            self.stat_entries[stat] = entry
            layout.addWidget(entry, row, col)

            if col == 2:
                layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum), row, 3)
        
        self.roll_results_frame.setLayout(layout)

        occupation_points, interest_points = self._calculate_skill_points()
        if self.occupation_points_entry and self.interest_points_entry:
            self.occupation_points_entry.set_value(str(occupation_points))
            self.interest_points_entry.set_value(str(interest_points))

    def _on_custom_luck_changed(self, state):
        luck_entry = self.stat_entries.get('LUK')
        if luck_entry:
            luck_entry.value_field.setEnabled(state == Qt.CheckState.Checked.value)
            if not state:
                luck_entry.set_value(0)

    def _on_stat_value_changed(self):
        total_points = 0
        for stat, entry in self.stat_entries.items():
            if stat == 'LUK' and not self.config.allow_custom_luck:
                continue
            try:
                value = int(entry.get_value() or 0)
                total_points += value
            except ValueError:
                pass

        self.remaining_points = self.config.points_available - total_points
        self.remaining_points_entry.set_value(str(self.remaining_points))

    def _on_calculate(self):
        if not self._validate_all_fields():
            return

        try:
            if not self.config.allow_custom_luck:
                luck_value = (sum(random.randint(1, 6) for _ in range(2)) + 6) * 5
                if 'LUK' in self.stat_entries and not sip.isdeleted(self.stat_entries['LUK']):
                    self.stat_entries['LUK'].set_value(str(luck_value))
        except (RuntimeError, KeyError):
            pass

        self._perform_age_calculation()
        derived_stats = self._calculate_derived_stats()
        if derived_stats is None:
            return

        occupation_points, interest_points = self._calculate_skill_points()
        if self.occupation_points_entry and self.interest_points_entry:
            self.occupation_points_entry.set_value(str(occupation_points))
            self.interest_points_entry.set_value(str(interest_points))

        self._save_data_to_pc_data()
        self._lock_fields()

        self.next_button.setEnabled(True)
        self.calculate_button.setEnabled(False)

        if self.config.allow_stat_exchange:
            self.exchange_button.setEnabled(True)

        self.main_window.set_phase_status(self.phase, PhaseStatus.COMPLETED)

    def _on_exchange(self):
        current_stats = {
            stat: int(entry.get_value())
            for stat, entry in self.stat_entries.items()
            if stat != 'LUK'
        }
        
        success, result = StatExchangeDialog.get_input(
            self, 
            remaining_times=self.remaining_exchange_times,
            current_stats=current_stats
        )
        
        if success and result:
            stat1, stat2 = result
            val1 = self.stat_entries[stat1].get_value()
            val2 = self.stat_entries[stat2].get_value()
            self.stat_entries[stat1].set_value(val2)
            self.stat_entries[stat2].set_value(val1)
            
            self.remaining_exchange_times -= 1
            if self.remaining_exchange_times == 0:
                self.exchange_button.setEnabled(False)

            self._calculate_derived_stats()

    def _on_next_clicked(self):
        if not self._validate_all_fields():
            return
        
        if not self.main_window.can_proceed_to_next_phase():
            return

        derived_stats = self._calculate_derived_stats()
        if derived_stats is None:
            return

        current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        if 'metadata' not in self.main_window.pc_data:
            self.main_window.pc_data['metadata'] = {}

        metadata = self.main_window.pc_data['metadata']
        metadata.update({
            'player_name': self.player_name.get_value(),
            'campaign_date': self.campaign_date.get_value(),
            'era': self.era.get_value(),
            'updated_at': current_time
        })

        if 'created_at' not in metadata:
            metadata['created_at'] = current_time

        if 'avatar_file' not in metadata:
            metadata['avatar_file'] = ""

        occupation_points, interest_points = self._calculate_skill_points()

        self.main_window.pc_data['personal_info'] = {
            'name': self.char_name.get_value(),
            'age': int(self.age.get_value()),
            'occupation': self.occupation.get_value(),
            'residence': self.residence.get_value(),
            'birthplace': self.birthplace.get_value(),
            'nationality': "",
            'occupation_skill_points': occupation_points,
            'interest_skill_points': interest_points
        }

        self.main_window.pc_data['basic_stats'] = {
            'strength': int(self.stat_entries['STR'].get_value()),
            'constitution': int(self.stat_entries['CON'].get_value()),
            'size': int(self.stat_entries['SIZ'].get_value()),
            'dexterity': int(self.stat_entries['DEX'].get_value()),
            'appearance': int(self.stat_entries['APP'].get_value()),
            'intelligence': int(self.stat_entries['INT'].get_value()),
            'power': int(self.stat_entries['POW'].get_value()),
            'education': int(self.stat_entries['EDU'].get_value()),
            'luck': int(self.stat_entries['LUK'].get_value())
        }

        self.main_window.pc_data['status'] = derived_stats

        super()._on_next_clicked()
    
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
            self.stat_entries['LUK'].set_value(str(pow_val * 5))
            
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
                'gender': self.gender.get_value(),
                'occupation': self.occupation.get_value(),
                'nationality': self.nationality.get_value(),
                'residence': self.residence.get_value(),
                'birthplace': self.birthplace.get_value()
            }
        }

        if self.config.is_points_mode():
            data['basic_stats'] = {
                'strength': self.stat_entries['STR'].get_value(),
                'constitution': self.stat_entries['CON'].get_value(),
                'size': self.stat_entries['SIZ'].get_value(),
                'dexterity': self.stat_entries['DEX'].get_value(),
                'appearance': self.stat_entries['APP'].get_value(),
                'intelligence': self.stat_entries['INT'].get_value(),
                'power': self.stat_entries['POW'].get_value(),
                'education': self.stat_entries['EDU'].get_value()
            }

            if self.config.allow_custom_luck:
                data['basic_stats']['luck'] = self.stat_entries['LUK'].get_value()

            if not self.next_button.isEnabled() and self.remaining_points != 0:
                self._show_validation_error(
                    f"Points allocation must be exact. "
                    f"Currently {abs(self.remaining_points)} points "
                    f"{'over' if self.remaining_points < 0 else 'remaining'}"
                )
                return False

        errors = self.validator.validate_dict(data, is_new=True)
        if errors:
            self._show_validation_error("\n".join(errors))
            return False
            
        return True

    def _save_data_to_pc_data(self):
        metadata = {
            'player_name': self.player_name.get_value(),
            'campaign_date': self.campaign_date.get_value(),
            'era': self.era.get_value()
        }

        occupation_points, interest_points = self._calculate_skill_points()
        
        personal_info = {
            'name': self.char_name.get_value(),
            'age': int(self.age.get_value()),
            'gender': self.gender.get_value(),
            'occupation': self.occupation.get_value(),
            'nationality': self.nationality.get_value(),
            'residence': self.residence.get_value(),
            'birthplace': self.birthplace.get_value(),
            'occupation_skill_points': occupation_points,
            'interest_skill_points': interest_points
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
            'luck': int(self.stat_entries['LUK'].get_value())
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
            self.custom_luck_entry.setEnabled(False)
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
        self.gender.set_value("None")
        self.occupation.set_value("None")
        self.nationality.set_value("")
        self.residence.set_value("")
        self.birthplace.set_value("")
        self.skill_points_formula.set_value("")

        self.age.value_field.setEnabled(True)
        self.occupation.value_field.setEnabled(True)

        for entry in self.derived_entries.values():
            entry.set_value("")

        if self.config.is_points_mode():
            self.remaining_points = self.config.points_available
            if self.remaining_points_entry:
                self.remaining_points_entry.set_value(str(self.remaining_points))
            if self.occupation_points_entry:
                self.occupation_points_entry.set_value("")
            if self.interest_points_entry:
                self.interest_points_entry.set_value("")
            for stat in ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK']:
                if stat in self.stat_entries:
                    self.stat_entries[stat].set_value("")
                    if stat != 'LUK':
                        self.stat_entries[stat].value_field.setEnabled(True)
        else:
            self.roll_button.setEnabled(True)
            if self.roll_results_frame.layout():
                while self.roll_results_frame.layout().count():
                    item = self.roll_results_frame.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            for stat in self.stat_entries.values():
                stat.value_field.setEnabled(False)

        if self.occupation_points_entry:
            self.occupation_points_entry.set_value("")

        if self.interest_points_entry:
            self.interest_points_entry.set_value("")

        if self.roll_results_frame is not None:
            if self.roll_results_frame.layout():
                while self.roll_results_frame.layout().count():
                    item = self.roll_results_frame.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            else:
                self.roll_results_frame.setLayout(QVBoxLayout())
        else:
            self.roll_results_frame = QFrame()
            self.roll_results_frame.setLayout(QVBoxLayout())
            self.roll_results_frame.setMinimumHeight(200)
            self.roll_results_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if self.stats_right_panel.layout():
                self.stats_right_panel.layout().addWidget(self.roll_results_frame)

        self.calculate_button.setEnabled(True)
        self.exchange_button.setEnabled(False)
        self.next_button.setEnabled(False)

        super()._reset_content()

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
        super().__init__(f"Reduce Stats by {total_reduction} Points", parent)
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
