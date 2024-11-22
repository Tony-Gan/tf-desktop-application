import os
import math
import shutil
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from PyQt6 import sip
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGroupBox, QButtonGroup,QScrollArea,
                             QLabel, QRadioButton, QGridLayout, QWidget, QFileDialog, QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QPainter, QPen, QColor

from ui.components.tf_base_button import TFBaseButton, TFConfirmButton
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_option_entry import TFOptionEntry
from ui.components.tf_date_entry import TFDateEntry
from implements.coc_tools.coc_data.dialogs import StatExchangeDialog, AgeReductionDialog, CharacterDescriptionDialog, OccupationListDialog
from implements.coc_tools.pc_builder_elements.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.legacy.phase_ui import BasePhaseUI
from implements.coc_tools.pc_builder_elements.phase_status import PhaseStatus
from utils.validator.tf_validation_rules import TFValidationRule
from utils.validator.tf_validator import TFValidator
from utils.helper import resource_path


class Phase1UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        self.config = main_window.config
        self.main_window = main_window
        
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
        self.stats_mid_panel = None
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
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        
        upper_frame = QFrame()
        upper_layout = QHBoxLayout(upper_frame)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(10)

        upper_layout.addWidget(self._create_avatar_group(), 1)
        
        mid_panel = QFrame()
        mid_layout = QVBoxLayout(mid_panel)
        mid_layout.setContentsMargins(0, 0, 0, 0)
        mid_layout.setSpacing(10)
        
        mid_layout.addWidget(self._create_metadata_group())
        mid_layout.addWidget(self._create_left_personal_info_group())
        
        upper_layout.addWidget(mid_panel, 2)
        
        upper_layout.addWidget(self._create_personal_info_group(), 2)
        
        content_layout.addWidget(upper_frame, 4)
        
        content_layout.addWidget(self._create_derived_stats_group(), 1)
        
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        
        self.stats_left_panel = QFrame()
        self.stats_mid_panel = QFrame()
        self.stats_right_panel = QFrame()
        
        stats_layout.addWidget(self.stats_left_panel, 4)
        stats_layout.addWidget(self.stats_mid_panel, 7)
        stats_layout.addWidget(self.stats_right_panel, 6)
        
        content_layout.addWidget(stats_frame, 11)
        
        self.content_area.setLayout(content_layout)
        self._update_stats_display()

    def _setup_phase_buttons(self, button_layout: QHBoxLayout):
        self.occupation_list_button = TFBaseButton(
            "Occupation List",
            self,
            height=30,
            on_clicked=self._on_occupation_list_clicked
        )
        self.occupation_list_button.setObjectName("occupation_list_button")
        self.calculate_button = TFBaseButton(
            "Check",
            self,
            height=30,
            on_clicked=self._on_calculate
        )
        self.calculate_button.setObjectName("calculate_button")
        self.exchange_button = TFBaseButton(
            "Stat Exchange",
            self,
            height=30,
            enabled=False,
            on_clicked=self._on_exchange
        )
        self.exchange_button.setObjectName("exchange_button")
        self.age_modification_button = TFBaseButton(
            "Age Modify",
            self,
            height=30,
            enabled=False,
            on_clicked=self._on_age_modification
        )
        self.age_modification_button.setObjectName("age_modification_button")
        self.description_button = TFBaseButton(
            "Char. Info",
            self,
            height=30,
            enabled=False,
            on_clicked=self._on_description_clicked
        )
        self.description_button.setObjectName("description_button")

        button_layout.addWidget(self.occupation_list_button)
        button_layout.addWidget(self.calculate_button)
        button_layout.addWidget(self.exchange_button)
        button_layout.addWidget(self.age_modification_button)
        button_layout.addWidget(self.description_button)

    def _setup_validation_rules(self):
        self.validator.add_custom_validator(
            'check_occupation',
            lambda x: (x is not None and x != "None", "Please select an occupation")
        )
        
        self.validator.add_custom_validator(
            'check_gender',
            lambda x: (x is not None and x != "None", "Please select a gender")
        )
        
        self.validator.add_custom_validator(
            'check_stats_total',
            lambda stats: (
                sum(int(v) for v in stats.values()) == self.config.points_available,
                f"Total stats points must equal exactly {self.config.points_available}"
            )
        )
        
        self.validator.add_custom_validator(
            'check_roll_complete',
            lambda x: (
                (not self.roll_button.isEnabled() and
                len(self.stat_entries) == 9 and
                all(stat in self.stat_entries for stat in ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK'])),
                "Please complete rolling and selecting stats before calculating"
            )
        )

        base_rules = {
            'player_name': TFValidationRule(
                type_=str,
                required=True,
                error_messages={'required': 'Player name is required'}
            ),
            'campaign_date': TFValidationRule(
                type_=str,
                required=True,
                error_messages={'required': 'Campaign date is required'}
            ),
            'era': TFValidationRule(
                type_=str,
                required=True,
                choices=['Medieval', '1890s', '1920s', 'Modern', 'Near Future', 'Future'],
                error_messages={'choices': 'Invalid era selection'}
            ),
            'char_name': TFValidationRule(
                type_=str,
                required=True,
                error_messages={'required': 'Character name is required'}
            ),
            'age': TFValidationRule(
                type_=int,
                required=True,
                min_val=15,
                max_val=90,
                error_messages={
                    'required': 'Age is required',
                    'min': 'Age must be at least 15',
                    'max': 'Age cannot exceed 90'
                }
            ),
            'gender': TFValidationRule(
                type_=str,
                required=True,
                custom='check_gender'
            ),
            'occupation': TFValidationRule(
                type_=str,
                required=True,
                custom='check_occupation'
            ),
            'check_roll_complete': TFValidationRule(
                custom='check_roll_complete'
            ),
            'nationality': TFValidationRule(
                type_=str,
                required=True,
                error_messages={'required': 'Nationality is required'}
            ),
            'residence': TFValidationRule(
                type_=str,
                required=True,
                error_messages={'required': 'Residence is required'}
            ),
            'birthplace': TFValidationRule(
                type_=str,
                required=True,
                error_messages={'required': 'Birthplace is required'}
            )
        }

        if self.config.is_points_mode():
            stats_rules = {
                stat: TFValidationRule(
                    type_=int,
                    required=True,
                    min_val=self.config.stat_lower_limit,
                    max_val=self.config.stat_upper_limit,
                    error_messages={
                        'required': f'{stat} value is required',
                        'min': f'{stat} cannot be lower than {self.config.stat_lower_limit}',
                        'max': f'{stat} cannot exceed {self.config.stat_upper_limit}'
                    }
                )
                for stat in ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU']
            }
            
            if self.config.allow_custom_luck:
                stats_rules['LUK'] = TFValidationRule(
                    type_=int,
                    required=True,
                    min_val=self.config.stat_lower_limit,
                    max_val=self.config.stat_upper_limit,
                    error_messages={
                        'required': 'Luck value is required',
                        'min': f'Luck cannot be lower than {self.config.stat_lower_limit}',
                        'max': f'Luck cannot exceed {self.config.stat_upper_limit}'
                    }
                )
            
            base_rules.update(stats_rules)

        self.validator.add_rules(base_rules)

    def _on_config_updated(self):
        self.config = self.main_window.config
        self.remaining_exchange_times = self.config.stat_exchange_times
        self._update_stats_display()

    def _create_avatar_group(self):
        group = QGroupBox("Avatar")
        layout = QVBoxLayout(group)
        layout.setObjectName("avatar_group_layout")
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setStyleSheet("border: 1px solid gray")
        
        self.avatar_button = TFBaseButton(
            "Upload Avatar",
            self,
            on_clicked=self._on_avatar_upload,
            width=100
        )
        
        layout.addStretch()
        layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(self.avatar_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        return group

    def _create_metadata_group(self):
        group = QGroupBox("Metadata")
        layout = QVBoxLayout(group)
        layout.setObjectName("metadata_group_layout")
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.player_name = TFValueEntry(
            "Player Name:",
            label_size=135,
            value_size=150,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.campaign_date = TFDateEntry(
            "Campaign Date:",
            label_size=135,
            value_size=150,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        
        era_options = ["Medieval", "1890s", "1920s", "Modern", "Near Future", "Future"]
        self.era = TFOptionEntry(
            "Era:",
            era_options,
            current_value="Modern",
            label_size=135,
            value_size=150,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.era.value_field.setEditable(False)
        self.era.set_value("Modern")
        
        layout.addWidget(self.player_name)
        layout.addWidget(self.campaign_date)
        layout.addWidget(self.era)
        layout.addStretch()
        return group

    def _create_left_personal_info_group(self):
        group = QGroupBox("Personal Information")
        layout = QVBoxLayout(group)
        layout.setObjectName("left_personal_info_group_layout")
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.char_name = TFValueEntry(
            "Character Name:", 
            value_size=150, 
            label_size=135,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.age = TFValueEntry(
            "Age:", 
            value_size=150, 
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
        layout.setObjectName("personal_info_group_layout")
        layout.setContentsMargins(5, 5, 5, 5)

        self.gender = TFOptionEntry(
            "Gender:", 
            ["None", "Male", "Female", "Other"],
            label_size=130,
            value_size=170,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.gender.value_field.setEditable(False)
        
        occupation_options = ["None"] + sorted([occ.name for occ in self.occupation_list])
        self.occupation = TFOptionEntry(
            "Occupation:", 
            occupation_options, 
            label_size=130, 
            value_size=170,
            alignment=Qt.AlignmentFlag.AlignLeft,
            extra_value_width=60
        )
        self.occupation.value_field.setEditable(False)
        
        self.skill_points_formula = TFValueEntry(
            "Skill Points:",
            label_size=130,
            value_size=170,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.skill_points_formula.value_field.setEnabled(False)
        self.occupation.value_field.currentTextChanged.connect(self._update_occupation_formula)
        
        self.nationality = TFValueEntry(
            "Nationality:", 
            label_size=130, 
            value_size=170,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        
        self.residence = TFValueEntry(
            "Residence:", 
            label_size=130, 
            value_size=170,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        
        self.birthplace = TFValueEntry(
            "Birthplace:", 
            label_size=130, 
            value_size=170,
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
        layout.setObjectName("derived_stats_group_layout")
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

        if self.stats_mid_panel.layout():
            while self.stats_mid_panel.layout().count():
                item = self.stats_mid_panel.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            sip.delete(self.stats_mid_panel.layout())

        self.stat_entries.clear()
        self.points_label = None
        self.skill_points_label = None

        if self.config.is_points_mode():
            self._setup_points_mode()
        else:
            self._setup_destiny_mode()

    def _update_right_panel_chart(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        radar_chart = StatRadarChart()
        stats = {
            stat: int(entry.get_value())
            for stat, entry in self.stat_entries.items()
        }
        radar_chart.set_stats(stats)
        
        layout.addWidget(radar_chart)
        self.stats_right_panel.setLayout(layout)

    def _update_occupation_formula(self):
        current_text = self.occupation.get_value()
        selected_occupation = next((occ for occ in self.occupation_list if occ.name == current_text), None)
        
        if not selected_occupation:
            return
            
        formula = selected_occupation.skill_points_formula
        
        if 'MAX' in formula:
            parts = formula.split('+')
            formatted_parts = []
            
            for part in parts:
                part = part.strip()
                if 'MAX' in part:
                    max_content = part[part.find('(')+1:part.find(')')].strip()
                    stat_parts = max_content.split(',')
                    processed_stats = []
                    
                    for stat_part in stat_parts:
                        stat_part = stat_part.strip()
                        if '*' in stat_part:
                            stat, multiplier = stat_part.split('*')
                            processed_stats.append(f"{stat.strip()}×{multiplier.strip()}")
                        else:
                            processed_stats.append(stat_part)
                    
                    formatted_parts.append('MAX(' + '|'.join(processed_stats) + ')')
                else:
                    if '*' in part:
                        stat, multiplier = part.split('*')
                        formatted_parts.append(f"{stat.strip()}×{multiplier.strip()}")
                    else:
                        formatted_parts.append(part)
            
            formatted_formula = '+'.join(formatted_parts)
        else:
            formatted_formula = formula.replace('*', '×')
        
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

        right_layout = QGridLayout(self.stats_mid_panel)
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
            entry.set_value("0")

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
        left_layout.setSpacing(15)

        left_layout.addStretch()

        self.dice_count_entry = TFValueEntry(
            "Dice Count:",
            str(self.config.dice_count),
            label_size=135,
            value_size=60,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        left_layout.addWidget(self.dice_count_entry)

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

        self.roll_button = TFBaseButton(
            "Roll for Stats",
            self,
            on_clicked=self._on_roll_stats,
            height=45,
            width=150
        )
        left_layout.addWidget(self.roll_button)

        left_layout.addStretch()

        self.stats_left_panel.setLayout(left_layout)

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(5, 5, 5, 5)

        self.roll_results_frame = QFrame(self.stats_mid_panel)
        self.roll_results_frame.setMinimumHeight(200)
        self.roll_results_frame.setLayout(QVBoxLayout())
        self.roll_results_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        right_layout.addWidget(self.roll_results_frame)
        self.stats_mid_panel.setLayout(right_layout)
    
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
            'STR': int(self.stat_entries['STR'].get_value() or '0'),
            'DEX': int(self.stat_entries['DEX'].get_value() or '0'),
            'POW': int(self.stat_entries['POW'].get_value() or '0'),
            'CON': int(self.stat_entries['CON'].get_value() or '0'),
            'APP': int(self.stat_entries['APP'].get_value() or '0'),
            'EDU': int(self.stat_entries['EDU'].get_value() or '0'),
            'SIZ': int(self.stat_entries['SIZ'].get_value() or '0'),
            'INT': int(self.stat_entries['INT'].get_value() or '0')
        }

        current_occupation = next(
            (occ for occ in self.occupation_list if occ.name == self.occupation.get_value()),
            None
        )

        if not current_occupation:
            return 0, 0

        occupation_points = current_occupation.calculate_skill_points(stats)
        interest_points = stats['INT'] * 2

        return occupation_points, interest_points

    def _calculate_derived_stats(self) -> dict:
        con = int(self.stat_entries['CON'].get_value() or '0')
        siz = int(self.stat_entries['SIZ'].get_value() or '0')
        pow_stat = int(self.stat_entries['POW'].get_value() or '0')
        str_stat = int(self.stat_entries['STR'].get_value() or '0')
        dex = int(self.stat_entries['DEX'].get_value() or '0')

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
            if self.stats_mid_panel.layout():
                self.stats_mid_panel.layout().addWidget(self.roll_results_frame)
        
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
            total_without_luck = sum(value for stat, value in stat_values.items() if stat != 'LUK')
            total_with_luck = sum(stat_values.values())
            base_stats_text = "|".join(
                f"{stat}:{value}" if stat not in ["INT"] else f"\n{stat}:{value}"
                for stat, value in stat_values.items()
            )
            stats_text = f"{base_stats_text}\nTotals(base/with luck): {total_without_luck}/{total_with_luck}"
            
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
        if stat_type in ['SIZ', 'INT', 'EDU']:
            result = (sum(random.randint(1, 6) for _ in range(2)) + 6) * 5
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
                value = int(entry.get_value() or '0')
                total_points += value
            except ValueError:
                pass

        self.remaining_points = self.config.points_available - total_points
        self.remaining_points_entry.set_value(str(self.remaining_points))

    def _on_calculate(self):
        if not self._validate_all_fields():
            return

        if not self.config.allow_custom_luck:
            luck_value = (sum(random.randint(1, 6) for _ in range(2)) + 6) * 5

            age = int(self.age.get_value())
            if age < 20:
                extra_luck_value = (sum(random.randint(1, 6) for _ in range(2)) + 6) * 5
                if extra_luck_value > luck_value:
                    luck_value = extra_luck_value

            if 'LUK' in self.stat_entries and not sip.isdeleted(self.stat_entries['LUK']):
                self.stat_entries['LUK'].set_value(str(luck_value))

        derived_stats = self._calculate_derived_stats()
        if derived_stats is None:
            return

        occupation_points, interest_points = self._calculate_skill_points()
        if self.occupation_points_entry and self.interest_points_entry:
            self.occupation_points_entry.set_value(str(occupation_points))
            self.interest_points_entry.set_value(str(interest_points))

        self._lock_fields()

        self.age_modification_button.setEnabled(True)
        self.calculate_button.setEnabled(False)

        if self.config.allow_stat_exchange:
            self.exchange_button.setEnabled(True)

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

    def _on_occupation_list_clicked(self):
        dialog = OccupationListDialog(self)
        dialog.exec()
    
    def _on_description_clicked(self):
        stats = {
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
        
        dialog = CharacterDescriptionDialog(self, stats)
        dialog.exec()

    def _on_age_modification(self):
        success = self._perform_age_calculation()
        if success:
            self.description_button.setEnabled(True)
            self.age_modification_button.setEnabled(False)
            self.next_button.setEnabled(True)

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

        if age < 20:
            base_reduction = 5
            app_reduction = 0
            edu_reduction = 5
        elif age < 40:
            base_reduction = 0
            app_reduction = 0
            edu_reduction = 0
        elif age < 50:
            base_reduction = 5
            app_reduction = 5
            edu_reduction = 0
        elif age < 60:
            base_reduction = 10
            app_reduction = 10
            edu_reduction = 0
        elif age < 70:
            base_reduction = 20
            app_reduction = 15
            edu_reduction = 0
        elif age < 80:
            base_reduction = 40
            app_reduction = 20
            edu_reduction = 0
        else:
            base_reduction = 80
            app_reduction = 25
            edu_reduction = 0

        if base_reduction > 0:
            if age < 20:
                confirmed, result = self._handle_physical_reduction(base_reduction, modifications, 2)
                if not confirmed:
                    return False
            elif age < 40:
                self._handle_physical_reduction(base_reduction, modifications, 3)
            else:
                confirmed, result = self._handle_physical_reduction(base_reduction, modifications, 1)
                if not confirmed:
                    return False

        current_edu = int(self.stat_entries['EDU'].get_value())
        total_improvement, improvement_details = self._perform_edu_improvements(edu_improvement_count, current_edu)

        if total_improvement > 0:
            new_edu = min(99, current_edu + total_improvement)
            modifications.append(f"EDU increased from {current_edu} to {new_edu}")
            modifications.extend(improvement_details)
            self.stat_entries['EDU'].set_value(str(new_edu))

        current_app = int(self.stat_entries['APP'].get_value())
        new_app = max(1, current_app - app_reduction)
        if new_app != current_app:
            modifications.append(f"APP reduced from {current_app} to {new_app}")
            self.stat_entries['APP'].set_value(str(new_app))

        current_edu = int(self.stat_entries['EDU'].get_value())
        new_edu = max(1, current_edu - edu_reduction)
        if new_edu != current_edu:
            modifications.append(f"EDU reduced from {current_edu} to {new_edu}")
            self.stat_entries['EDU'].set_value(str(new_edu))

        self._update_right_panel_chart()
        self.main_window.set_phase_status(self.phase, PhaseStatus.COMPLETED)

        if modifications:
            self.main_window.app.show_warning(
                "Age-based Modifications",
                "The following modifications were applied:\n" + "\n".join(modifications),
                buttons=["OK"]
            )

        return True

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

    def _handle_physical_reduction(self, total_reduction: int, modifications: list, mode: int = 1) -> tuple[bool, dict]:
        current_stats = None
        if mode == 1:
            physical_stats = ['STR', 'CON', 'DEX']
            current_stats = {
                stat: int(self.stat_entries[stat].get_value())
                for stat in physical_stats
            }
        elif mode == 2:
            physical_stats = ['STR', 'SIZ']
            current_stats = {
                stat: int(self.stat_entries[stat].get_value())
                for stat in physical_stats
            }

        if mode != 3:
            confirmed, result = AgeReductionDialog.get_input(
                self,
                total_reduction=total_reduction,
                current_stats=current_stats
            )

            if not confirmed:
                return False, None

            if mode == 1:
                str_deduction = result.get('STR', 0)
                con_deduction = result.get('CON', 0)
                dex_deduction = result.get('DEX', 0)

                self.stat_entries['STR'].set_value(str(current_stats['STR'] - str_deduction))
                self.stat_entries['CON'].set_value(str(current_stats['CON'] - con_deduction))
                self.stat_entries['DEX'].set_value(str(current_stats['DEX'] - dex_deduction))

                if str_deduction != 0:
                    modifications.append(f"STR reduced {str_deduction} points.")
                if con_deduction != 0:
                    modifications.append(f"CON reduced {con_deduction} points.")
                if dex_deduction != 0:
                    modifications.append(f"DEX reduced {dex_deduction} points.")

                return True, result
            else:
                str_deduction = result.get('STR', 0)
                siz_deduction = result.get('SIZ', 0)

                self.stat_entries['STR'].set_value(str(current_stats['STR'] - str_deduction))
                self.stat_entries['SIZ'].set_value(str(current_stats['SIZ'] - siz_deduction))

                if str_deduction != 0:
                    modifications.append(f"STR reduced {str_deduction} points.")
                if siz_deduction != 0:
                    modifications.append(f"SIZ reduced {siz_deduction} points.")

                return True, result

        return True, {}

    def _validate_all_fields(self) -> bool:
        error_messages = []
        
        field_mappings = {
            'player_name': self.player_name.get_value(),
            'campaign_date': self.campaign_date.get_value(),
            'era': self.era.get_value(),
            'char_name': self.char_name.get_value(),
            'age': self.age.get_value(),
            'gender': self.gender.get_value(),
            'occupation': self.occupation.get_value(),
            'nationality': self.nationality.get_value(),
            'residence': self.residence.get_value(),
            'birthplace': self.birthplace.get_value()
        }

        for field_name, value in field_mappings.items():
            is_valid, message = self.validator.validate_field(field_name, value)
            if not is_valid:
                error_messages.append(f"{message}")

        if self.config.is_points_mode():
            stats_values = {}
            for stat in ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU']:
                value = self.stat_entries[stat].get_value() or '0'
                is_valid, message = self.validator.validate_field(stat, value)
                if not is_valid:
                    error_messages.append(message)
                else:
                    stats_values[stat] = int(value)
            
            if self.config.allow_custom_luck:
                luck_value = self.stat_entries['LUK'].get_value() or '0'
                is_valid, message = self.validator.validate_field('LUK', luck_value)
                if not is_valid:
                    error_messages.append(message)
            
            if not error_messages and stats_values:
                is_valid, message = self.validator.validate_field('check_stats_total', stats_values)
                if not is_valid:
                    error_messages.append(message)
        else:
            is_valid, message = self.validator.validate_field('check_roll_complete', None)
            if not is_valid:
                error_messages.append(message)

        if error_messages:
            self._show_validation_error('\n'.join(error_messages))
            return False
        
        return True

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
        super()._reset_content()
        
        self.remaining_exchange_times = self.config.stat_exchange_times

        for entry in self.stat_entries.values():
            if not sip.isdeleted(entry):
                try:
                    if hasattr(entry.value_field, 'textChanged'):
                        entry.value_field.textChanged.disconnect()
                except TypeError:
                    pass
                entry.value_field.setEnabled(False)

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
        self.occupation.value_field.setCurrentText("None")
        self.nationality.set_value("")
        self.residence.set_value("")
        self.birthplace.set_value("")
        self.skill_points_formula.set_value("")

        self.player_name.value_field.setEnabled(True)
        self.campaign_date.date_field.setEnabled(True)
        self.era.value_field.setEnabled(True)
        self.char_name.value_field.setEnabled(True)
        self.age.value_field.setEnabled(True)
        self.gender.value_field.setEnabled(True)
        self.occupation.value_field.setEnabled(True)
        self.nationality.value_field.setEnabled(True)
        self.residence.value_field.setEnabled(True)
        self.birthplace.value_field.setEnabled(True)

        for entry in self.derived_entries.values():
            if not sip.isdeleted(entry):
                entry.set_value("")

        self._update_stats_display()

        if self.config.is_points_mode():
            self.remaining_points = self.config.points_available
            if self.remaining_points_entry and not sip.isdeleted(self.remaining_points_entry):
                self.remaining_points_entry.set_value(str(self.remaining_points))
            if self.occupation_points_entry and not sip.isdeleted(self.occupation_points_entry):
                self.occupation_points_entry.set_value("")
            if self.interest_points_entry and not sip.isdeleted(self.interest_points_entry):
                self.interest_points_entry.set_value("")

            for stat in ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK']:
                if stat in self.stat_entries and not sip.isdeleted(self.stat_entries[stat]):
                    self.stat_entries[stat].set_value("")
                    if stat != 'LUK' or (stat == 'LUK' and self.config.allow_custom_luck):
                        self.stat_entries[stat].value_field.setEnabled(True)
                        self.stat_entries[stat].value_field.textChanged.connect(self._on_stat_value_changed)

        else:
            if not sip.isdeleted(self.roll_button):
                self.roll_button.setEnabled(True)

            if self.roll_results_frame and self.roll_results_frame.layout():
                QWidget().setLayout(self.roll_results_frame.layout())
                self.roll_results_frame.setLayout(QVBoxLayout())

            for stat, entry in list(self.stat_entries.items()):
                if not sip.isdeleted(entry):
                    entry.value_field.setEnabled(False)
                    entry.set_value("")

        if self.occupation_points_entry and not sip.isdeleted(self.occupation_points_entry):
            self.occupation_points_entry.set_value("")

        if self.interest_points_entry and not sip.isdeleted(self.interest_points_entry):
            self.interest_points_entry.set_value("")

        if self.stats_right_panel.layout():
            while self.stats_right_panel.layout().count():
                item = self.stats_right_panel.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            sip.delete(self.stats_right_panel.layout())

        self.calculate_button.setEnabled(True)
        self.exchange_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.description_button.setEnabled(False)
        self.age_modification_button.setEnabled(False)

        self.main_window.set_phase_status(self.phase, PhaseStatus.NOT_START)

    def _show_validation_error(self, message: str):
        self.main_window.app.show_warning(
            "Validation Error",
            message,
            buttons=["OK"]
        )

    def on_exit(self):
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

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
            'nationality': self.nationality.get_value(),
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

        derived_stats = self._calculate_derived_stats()
        if derived_stats:
            self.main_window.pc_data['status'] = derived_stats

    def on_enter(self):
        super().on_enter()

class StatRadarChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats = {}
        self.stats_order = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK']
        
    def set_stats(self, stats: dict):
        self.stats = stats
        self.update()
        
    def paintEvent(self, event):
        if not self.stats:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 40 
        
        grid_pen = QPen(QColor(180, 180, 180)) 
        grid_pen.setWidth(1)
        
        for i in range(5):
            current_radius = radius * (i + 1) / 5
            points = []
            for j in range(9):
                angle = j * 2 * math.pi / 9 - math.pi / 2
                x = center_x + current_radius * math.cos(angle)
                y = center_y + current_radius * math.sin(angle)
                points.append((x, y))
            
            painter.setPen(grid_pen)
            for j in range(9):
                painter.drawLine(
                    int(points[j][0]), 
                    int(points[j][1]), 
                    int(points[(j + 1) % 9][0]), 
                    int(points[(j + 1) % 9][1])
                )
            
            if i < 4:
                value = (i + 1) * 20
                painter.drawText(
                    int(center_x - 10), 
                    int(center_y - current_radius - 5),
                    str(value)
                )
        
        for i in range(9):
            angle = i * 2 * math.pi / 9 - math.pi / 2
            end_x = center_x + radius * math.cos(angle)
            end_y = center_y + radius * math.sin(angle)
            painter.drawLine(
                int(center_x),
                int(center_y),
                int(end_x),
                int(end_y)
            )
            
        stat_pen = QPen(QColor(0, 139, 139))
        stat_pen.setWidth(2)
        painter.setPen(stat_pen)
        
        points = []
        for i, stat in enumerate(self.stats_order):
            value = min(self.stats[stat], 100)
            current_radius = radius * value / 100
            angle = i * 2 * math.pi / 9 - math.pi / 2
            x = center_x + current_radius * math.cos(angle)
            y = center_y + current_radius * math.sin(angle)
            points.append((x, y))
        
        for i in range(len(points)):
            painter.drawLine(
                int(points[i][0]),
                int(points[i][1]),
                int(points[(i + 1) % 9][0]),
                int(points[(i + 1) % 9][1])
            )

        text_pen = QPen(QColor(100, 100, 100))
        painter.setPen(text_pen)
        
        font = QFont()
        font.setPointSize(9)
        painter.setFont(font)
        
        for i, stat in enumerate(self.stats_order):
            value = min(self.stats[stat], 100)
            angle = i * 2 * math.pi / 9 - math.pi / 2
            label_radius = radius + 20
            label_x = center_x + label_radius * math.cos(angle)
            label_y = center_y + label_radius * math.sin(angle)
            
            text = f"{stat}:{value}"
            painter.drawText(
                int(label_x - 20), 
                int(label_y + 5), 
                text
            )
