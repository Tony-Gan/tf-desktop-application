from dataclasses import dataclass
from typing import List, Optional
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QFont, QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QGroupBox, QLabel, QRadioButton, QButtonGroup, QPushButton, QLineEdit

from implements.coc_tools.pc_builder_helper.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_helper.phase_ui import BasePhaseUI
from implements.coc_tools.pc_builder_helper.constants import DEFAULT_SKILLS, PARENT_SKILL_DEFAULTS, INTERPERSONAL_SKILLS
from implements.coc_tools.pc_builder_helper.phase_status import PhaseStatus
from implements.coc_tools.pc_builder_helper.occupation_list_dialog import OccupationListDialog
from ui.components.tf_base_button import TFPreviousButton, TFBaseButton
from ui.components.tf_number_receiver import TFNumberReceiver
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_computing_dialog import TFComputingDialog
from utils.validator.tf_validator import TFValidator
from utils.validator.tf_validation_rules import TFValidationRule
from utils.helper import resource_path

TEXT_FONT = QFont("Inconsolata")
TEXT_FONT.setPointSize(10)

LABEL_FONT = QFont("Inconsolata SemiCondensed")
LABEL_FONT.setPointSize(10)

@dataclass
class Skill:
    name: str
    super_name: str
    default_point: int
    is_occupation: bool = False
    occupation_point: int = 0
    interest_point: int = 0

    @property
    def total_point(self) -> int:
        return self.default_point + self.occupation_point + self.interest_point

    @property
    def display_name(self) -> str:
        formatted_name = self.name.replace("_", " ").title()
        if self.super_name:
            formatted_super_name = self.super_name.replace("_", " ").title()
            return f"{formatted_super_name} - {formatted_name}"
        return formatted_name


class SkillEntry(QFrame):

    def __init__(self, skill: Skill, occupation_points=None, interest_points=None, parent=None):
        super().__init__(parent)

        self.skill = skill
        self.setObjectName(f"skill_entry_{skill.super_name}_{skill.name}" if skill.super_name else f"skill_entry_{skill.name}")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(2)

        self.name_label = QLabel(skill.display_name)
        self.name_label.setFont(LABEL_FONT)
        self.name_label.setFixedWidth(115) 

        if skill.is_occupation:
            self.name_label.setStyleSheet("color: #3498DB;")
        elif self.skill.interest_point > 0:
            self.name_label.setStyleSheet("color: #2ECC71;")
        else:
            self.name_label.setStyleSheet("")

        occupation_int = occupation_points or 0
        self.occupation_points = TFNumberReceiver(
            text=str(occupation_int),
            width=20,
            font=TEXT_FONT,
            alignment=Qt.AlignmentFlag.AlignCenter,
            allow_decimal=False,
            allow_negative=False
        )
        self.occupation_points.setStyleSheet("padding: 0;")
        self.occupation_points.setMaxLength(2)
        self.occupation_points.setEnabled(skill.is_occupation)

        interest_int = interest_points or 0
        self.interest_points = TFNumberReceiver(
            text=str(interest_int),
            width=20,
            font=TEXT_FONT,
            alignment=Qt.AlignmentFlag.AlignCenter,
            allow_decimal=False,
            allow_negative=False
        )
        self.interest_points.setStyleSheet("padding: 0;")
        self.occupation_points.setMaxLength(2)
        self.interest_points.textChanged.connect(self._update_label_color)

        self.default_value = TFNumberReceiver(
            text=str(skill.default_point),
            width=20,
            font=TEXT_FONT,
            alignment=Qt.AlignmentFlag.AlignCenter,
            allow_decimal=False,
            allow_negative=False
        )
        self.default_value.setEnabled(False)
        self.default_value.setStyleSheet("padding: 0;")

        self.total = TFNumberReceiver(
            text=str(skill.default_point),
            width=25,
            font=TEXT_FONT,
            alignment=Qt.AlignmentFlag.AlignCenter,
            allow_decimal=False,
            allow_negative=False
        )
        self.total.setEnabled(False)
        self.total.setStyleSheet("padding: 0;")

        self.occupation_points.textChanged.connect(self._update_total)
        self.interest_points.textChanged.connect(self._update_total)

        layout.addWidget(self.name_label)
        layout.addWidget(self.occupation_points)
        layout.addWidget(self.interest_points)
        layout.addWidget(self.default_value)
        layout.addWidget(self.total)
        layout.addStretch()

    def _update_total(self):
        self.skill.occupation_point = int(self.occupation_points.text() or 0)
        self.skill.interest_point = int(self.interest_points.text() or 0)
        self.total.setText(str(self.skill.total_point))

        parent = self.parent()
        while parent and not isinstance(parent, Phase2UI):
            if hasattr(parent, 'parent_ui'):
                parent = parent.parent_ui
            elif hasattr(parent, 'parent'):
                if callable(parent.parent):
                    parent = parent.parent()
                else:
                    parent = parent.parent
            else:
                break
        
        if parent and isinstance(parent, Phase2UI):
            parent.update_points_display()
            parent.reset_completion_status()

    def get_values(self) -> dict:
        return {
            'occupation_points': int(self.occupation_points.text() or 0),
            'interest_points': int(self.interest_points.text() or 0),
            'total': int(self.total.text())
        }
    
    def _update_label_color(self):
        if self.skill.is_occupation:
            self.name_label.setStyleSheet("color: #3498DB;")
        elif int(self.interest_points.text() or 0) > 0:
            self.name_label.setStyleSheet("color: #2ECC71;")
        else:
            self.name_label.setStyleSheet("")

    def reset(self):
        self.occupation_points.setText("0")
        self.interest_points.setText("0")
        self._update_total()
        if self.skill.is_occupation:
            self.name_label.setStyleSheet("color: #3498DB;")
        else:
            self.name_label.setStyleSheet("")
        self._update_total()


class PointsGroup(QGroupBox):
    def __init__(self, pc_data, parent:'Phase2UI'):
        super().__init__("Available Points", parent)
        self.parent = parent
        self.setObjectName("points_group")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.pc_data = pc_data
        self._setup_content()

    def _setup_content(self):
        personal_info = self.pc_data.get('personal_info', {})

        self.occupation_points_entry = TFValueEntry(
            label_text="Occupation Points:",
            value_text=str(personal_info.get('occupation_skill_points', 0)),
            label_size=180,
            value_size=50,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.interest_points_entry = TFValueEntry(
            label_text="Interest Points:",
            value_text=str(personal_info.get('interest_skill_points', 0)),
            label_size=180,
            value_size=50,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        self._update_points_color(self.occupation_points_entry)
        self._update_points_color(self.interest_points_entry)

        self.occupation_point_limit_entry = TFValueEntry(
            label_text="Occupation Points Limit:",
            value_text=str(self.parent.config.occupation_skill_limit),
            label_size=180,
            value_size=50,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.interest_point_limit_entry = TFValueEntry(
            label_text="Interest Points Limit:",
            value_text=str(self.parent.config.interest_skill_limit),
            label_size=180,
            value_size=50,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.mix_points_entry = TFValueEntry(
            label_text="Mixed Points:",
            value_text="True" if self.parent.config.allow_mixed_points else "False",
            label_size=180,
            value_size=50,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        self.layout.addWidget(self.occupation_points_entry)
        self.layout.addWidget(self.interest_points_entry)
        self.layout.addWidget(self.occupation_point_limit_entry)
        self.layout.addWidget(self.interest_point_limit_entry)
        self.layout.addWidget(self.mix_points_entry)

    def _update_points_color(self, entry: TFValueEntry):
        try:
            value = int(entry.get_value())
            if value > 0:
                entry.value_field.setStyleSheet("color: #3498DB;")
            elif value < 0:
                entry.value_field.setStyleSheet("color: #FF6B6B;")
            else:
                entry.value_field.setStyleSheet("color: #2ECC71;")
        except (ValueError, TypeError):
            entry.value_field.setStyleSheet("")


class InfoCell(QHBoxLayout):

    def __init__(self, text: str, on_button_clicked=None):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(5)

        self.initial_text = text 

        self.label = QLabel(text)
        self.label.setFont(LABEL_FONT)
        self.addWidget(self.label)

        self.button = None
        if on_button_clicked is not None:
            self.button = TFBaseButton("Select", None, height=24, width=50)
            self.button.clicked.connect(lambda: on_button_clicked(self))
            self.addWidget(self.button)

        self.addStretch()

    def update_display(self, text: str, button_text: str = None):
        self.label.setText(text)
        if self.button and button_text:
            self.button.setText(button_text)

    @staticmethod
    def format_skill_name(skill: str) -> str:
        if '|' in skill:
            skills = [s.replace('_', ' ').title() for s in skill.split('|')]
            return ' / '.join(skills)
        elif ':' in skill:
            parent, child = skill.split(':')
            parent = parent.replace('_', ' ').title()
            if 'any' in child.lower():
                return parent
            child = child.replace('_', ' ').title()
            return f"{parent} - {child}"
        elif skill.lower() == 'any':
            return "Any Skill"
        else:
            return skill.replace('_', ' ').title()


class InfoGroup(QGroupBox):

    def __init__(self, pc_data, parent:'Phase2UI'):
        personal_info = pc_data.get('personal_info', {})
        occupation_name = personal_info.get('occupation', '')
        super().__init__(occupation_name, parent)
        self.parent = parent

        self.setObjectName("info_group")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self._pc_data = pc_data
        self._occupation_name = occupation_name
        self.info_cells = []
        
        self._setup_content()
        self._setup_legend()

    def _setup_content(self):
        content_frame = QFrame()
        grid_layout = QGridLayout(content_frame)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(5)

        occupation = next((occ for occ in self.parent.occupation_list if occ.name == self._occupation_name), None)
        if not occupation:
            return

        occ_skills = occupation.get_skills().split(',')
        row, col = 0, 0

        for skill in occ_skills:
            skill_text = InfoCell.format_skill_name(skill)

            if 'any' in skill.lower() or '|' in skill:
                cell = InfoCell(
                    text=skill_text,
                    on_button_clicked=self._on_skill_select
                )
            else:
                cell = InfoCell(text=skill_text)
                if ':' in skill:
                    super_name, skill_name = skill.split(':')
                else:
                    skill_name = skill
                    super_name = None

                target_skill = next(
                    (s for s in self.parent.skills
                     if s.name == skill_name and s.super_name == super_name),
                    None
                )
                if target_skill:
                    target_skill.is_occupation = True

            grid_layout.addLayout(cell, row, col)
            self.info_cells.append(cell)

            col += 1
            if col == 3:
                col = 0
                row += 1

        credit_min = occupation.get_credit_rating_min()
        credit_max = occupation.get_credit_rating_max()
        credit_cell = InfoCell(f"Credit Rating ({credit_min} - {credit_max})")
        grid_layout.addLayout(credit_cell, row, col)
        self.info_cells.append(credit_cell)

        col += 1
        while col < 3:
            empty_cell = InfoCell("")
            grid_layout.addLayout(empty_cell, row, col)
            self.info_cells.append(empty_cell)
            col += 1
            if col == 3 and row < 2:
                col = 0
                row += 1

        self.layout.addWidget(content_frame, 3)

    def _setup_legend(self):
        legend_frame = QFrame()
        legend_layout = QVBoxLayout(legend_frame)
        legend_layout.setContentsMargins(5, 5, 5, 5)
        legend_layout.setSpacing(5)
        
        descriptions = [
            "Each skill row consists of four input boxes from left to right:",
            "• Occ (Occupation Points): Can only be allocated to occupation skills (shown in blue)",
            "• Int (Interest Points): Can be allocated to any skills to improve them",
            "• Base (Base Value): The initial value of the skill (cannot be modified)",
            "• Total: The sum of Base + Occupation + Interest points (automatically calculated)",
        ]
        
        for text in descriptions:
            label = QLabel(text)
            label.setFont(TEXT_FONT)
            legend_layout.addWidget(label)

        self.layout.addWidget(legend_frame, 1)

    def _on_skill_select(self, target_cell: InfoCell):
        dialog = None

        if target_cell.button and target_cell.button.text() == "Switch":
            current_skill = next(
                (s for s in self.parent.skills if s.display_name == target_cell.label.text()),
                None
            )

        skill = target_cell.initial_text

        if '/' in skill:
            dialog = MultiOptionSkillDialog(skill, parent_ui=self.parent)
        elif "interpersonal skill" == skill.lower():
            dialog = InterpersonalSkillDialog(parent_ui=self.parent)
        elif skill.lower() in ["language", "fighting", "firearm", "science", "art", "pilot", "survival"]:
            skill_type = skill.split(":")[0]
            dialog = SpecificSkillDialog(skill_type=skill_type, parent_ui=self.parent)
        elif skill.lower() == "any skill":
            dialog = AnySkillDialog(parent_ui=self.parent)

        if dialog and dialog.exec():
            selected_skill = dialog.get_result()
            if selected_skill:
                if target_cell.button.text() == "Switch":
                    current_skill = next(
                        (s for s in self.parent.skills if s.display_name == target_cell.label.text()),
                        None
                    )
                    if current_skill:
                        current_skill.is_occupation = False
                        
                selected_skill.is_occupation = True
                target_cell.update_display(selected_skill.display_name, "Switch")
                self.parent.refresh_skill_display()
                self.parent.reset_completion_status()


class SkillGroup(QFrame):
    def __init__(self, pc_data, parent:'Phase2UI'):
        super().__init__(parent)
        self.setObjectName("section_frame")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(5)

        self.parent = parent
        self.skills = self.parent.skills
        self._pc_data = pc_data
        self._setup_content()

    def _setup_content(self):
        skills_frame = QFrame()
        skills_layout = QGridLayout(skills_frame)
        skills_layout.setContentsMargins(0, 0, 0, 0)
        skills_layout.setSpacing(5)

        basic_skills = [skill for skill in self.skills if not skill.super_name]
        basic_skills.sort(key=lambda x: x.name)

        for i, skill in enumerate(basic_skills):
            row = i // 4
            col = i % 4
            entry = SkillEntry(skill)
            skills_layout.addWidget(entry, row, col)

        self.main_layout.addWidget(skills_frame, 9)

        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        for skill in PARENT_SKILL_DEFAULTS:
            button = TFBaseButton(
                f"Expand {skill.title()}",
                self,
                height=30,
                on_clicked=lambda _, s=skill: self._on_expand_skill(s)
            )
            buttons_layout.addWidget(button)

        add_skill_button = TFBaseButton(
            "Add New Skill",
            self,
            height=30,
            on_clicked=self._on_add_new_skill
        )
        buttons_layout.addWidget(add_skill_button)

        self.main_layout.addWidget(buttons_frame, 1)

    def _on_expand_skill(self, skill: str):
        dialog = SkillExpandDialog(skill.lower(), self)
        dialog.exec()

    def _on_add_new_skill(self):
        confirmed, result = NewSkillDialog.get_input(self)
        if not confirmed:
            return

        skill_key, default_value = result

        if ':' in skill_key:
            super_name, name = skill_key.split(':')
        else:
            super_name, name = None, skill_key

        new_skill = Skill(
            name=name,
            super_name=super_name,
            default_point=default_value
        )

        self.skills.append(new_skill)

        if not super_name:
            skills_frame = None
            for i in range(self.layout().count()):
                widget = self.layout().itemAt(i).widget()
                if isinstance(widget, QFrame) and widget.layout() and isinstance(widget.layout(), QGridLayout):
                    skills_frame = widget
                    break

            if skills_frame:
                grid_layout = skills_frame.layout()
                total_items = grid_layout.count()
                row = total_items // 4
                col = total_items % 4
                entry = SkillEntry(new_skill)
                grid_layout.addWidget(entry, row, col)

        self.parent.refresh_skill_display()


class Phase2UI(BasePhaseUI):

    def __init__(self, main_window, parent=None):
        self.config = main_window.config
        self.main_window = main_window

        self.max_occupation_points = self.main_window.pc_data.get('personal_info', {}).get('occupation_skill_points', 0)
        self.max_interest_points = self.main_window.pc_data.get('personal_info', {}).get('interest_skill_points', 0)

        self.check_button = None
        self.previous_button = None

        basic_stats = self.main_window.pc_data.get('basic_stats', {})
        dexterity = basic_stats.get('dexterity', 0)
        education = basic_stats.get('education', 0)
        self.skills = []
        for skill_key, default_point in DEFAULT_SKILLS.items():
            name = skill_key.split(":")[1] if ":" in skill_key else skill_key
            super_name = skill_key.split(":")[0] if ":" in skill_key else None
            
            if name == 'dodge':
                default_point = dexterity // 2
            
            elif name == 'language_own':
                default_point = education
                
            skill = Skill(
                name=name,
                super_name=super_name,
                default_point=default_point
            )
            self.skills.append(skill)

        super().__init__(PCBuilderPhase.PHASE2, main_window, parent)

        self.validator = TFValidator()
        self._setup_validation_rules()

    def _setup_ui(self):
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        upper_frame = QFrame()
        upper_layout = QHBoxLayout(upper_frame)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(10)

        self.points_group = PointsGroup(self.main_window.pc_data, self)
        self.info_group = InfoGroup(self.main_window.pc_data, self)
        upper_layout.addWidget(self.points_group, 3)
        upper_layout.addWidget(self.info_group, 7)

        self.skill_group = SkillGroup(self.main_window.pc_data, self)
        content_layout.addWidget(upper_frame, 2)
        content_layout.addWidget(self.skill_group, 8)

        self.content_area.setLayout(content_layout)

    def _setup_phase_buttons(self, button_layout):
        self.occupation_list_button = TFBaseButton(
            "Occupation List",
            self,
            height=30,
            on_clicked=self._on_occupation_list_clicked
        )
        self.occupation_list_button.setObjectName("occupation_list_button")
        self.check_button = TFBaseButton(
            "Check",
            self,
            height=30,
            on_clicked=self._on_check_clicked
        )
        self.check_button.setObjectName("check_button")
        self.previous_button = TFPreviousButton(
            self,
            height=30,
            on_clicked=self._on_previous_clicked
        )

        button_layout.addWidget(self.occupation_list_button)
        button_layout.addWidget(self.check_button)
        button_layout.addWidget(self.previous_button)

    def _setup_validation_rules(self):
        def validate_occupation_skill(skill):
            if skill.name == 'language_own' and skill.occupation_point == 0 and skill.interest_point == 0:
                return True, ""
            if not skill.is_occupation:
                return True, ""
            if skill.total_point > self.config.occupation_skill_limit:
                return False, f"'{skill.display_name}' exceeds occupation skill limit of {self.config.occupation_skill_limit}"
            return True, ""
        
        def validate_interest_skill(skill):
            if skill.name == 'language_own' and skill.occupation_point == 0 and skill.interest_point == 0:
                return True, ""
            if skill.is_occupation:
                return True, ""
            if skill.total_point > self.config.interest_skill_limit:
                return False, f"'{skill.display_name}' exceeds interest skill limit of {self.config.interest_skill_limit}"
            return True, ""
        
        def validate_mixed_points(skill):
            if skill.name == 'language_own' and skill.occupation_point == 0 and skill.interest_point == 0:
                return True, ""
            if not self.config.allow_mixed_points:
                if skill.occupation_point > 0 and skill.interest_point > 0:
                    return False, f"'{skill.display_name}' cannot have both occupation and interest points when mixed points are disabled"
            return True, ""
        
        def validate_remaining_points(points):
            if points < 0:
                return False, "Remaining points cannot be negative"
            return True, ""
        
        def validate_credit_rating(skill):
            if skill.name != 'credit_rating':
                return True, ""
            occupation = next(
                (occ for occ in self.occupation_list if occ.name == self.main_window.pc_data['personal_info']['occupation']),
                None
            )
            min_rating = occupation.get_credit_rating_min()
            max_rating = occupation.get_credit_rating_max()
            
            if not (min_rating <= skill.total_point <= max_rating):
                return False, f"Credit Rating must be between {min_rating} and {max_rating} for {occupation.name}"
                
            return True, ""
        
        self.validator.add_custom_validator('occupation_skill_limit', validate_occupation_skill)
        self.validator.add_custom_validator('interest_skill_limit', validate_interest_skill)
        self.validator.add_custom_validator('mixed_points', validate_mixed_points)
        self.validator.add_custom_validator('remaining_points', validate_remaining_points)
        self.validator.add_custom_validator('credit_rating_range', validate_credit_rating)

    def _on_occupation_list_clicked(self):
        dialog = OccupationListDialog(self, self.occupation_list)
        dialog.exec()

    def _on_check_clicked(self):
        remaining_occ = int(self.points_group.occupation_points_entry.get_value())
        remaining_int = int(self.points_group.interest_points_entry.get_value())

        is_valid, message = self.validator._custom_validators['remaining_points'](remaining_occ)
        if not is_valid:
            self._show_validation_error("Occupation " + message)
            return False
            
        is_valid, message = self.validator._custom_validators['remaining_points'](remaining_int)
        if not is_valid:
            self._show_validation_error("Interest " + message)
            return False
        
        if remaining_occ > 0 or remaining_int > 0:
            message = "You still have "
            if remaining_occ > 0:
                message += f"{remaining_occ} occupation points"
                if remaining_int > 0:
                    message += " and "
            if remaining_int > 0:
                message += f"{remaining_int} interest points"
            message += " remaining. Do you want to continue?"
            
            response = self.main_window.app.show_warning(
                "Points Remaining",
                message,
                buttons=["Yes", "No"]
            )
            if response != "Yes":
                return False

        error_messages = []
        
        for skill in self.skills:
            is_valid, message = self.validator._custom_validators['occupation_skill_limit'](skill)
            if not is_valid:
                error_messages.append(message)
                
            is_valid, message = self.validator._custom_validators['interest_skill_limit'](skill)
            if not is_valid:
                error_messages.append(message)
                
            is_valid, message = self.validator._custom_validators['mixed_points'](skill)
            if not is_valid:
                error_messages.append(message)

            is_valid, message = self.validator._custom_validators['credit_rating_range'](skill)
            if not is_valid:
                error_messages.append(message)

        if error_messages:
            error_message = "\n".join(error_messages)
            self._show_validation_error(error_message)
            return False
        
        self.check_button.setEnabled(False)
        self.enable_next_button(True)

        self.main_window.set_phase_status(self.phase, PhaseStatus.COMPLETED)
        return True
    
    def _show_validation_error(self, message: str):
        self.main_window.app.show_warning(
            "Validation Error",
            message,
            buttons=["OK"]
        )

    def _on_previous_clicked(self):
        self.main_window._on_phase_selected(PCBuilderPhase.PHASE1)

    def _reset_content(self):
        super()._reset_content()

        if 'skills' in self.main_window.pc_data:
            del self.main_window.pc_data['skills']

        for skill in self.skills:
            skill.occupation_point = 0
            skill.interest_point = 0
            skill.is_occupation = False

        if self.skill_group:
            for skill_entry in self.skill_group.findChildren(SkillEntry):
                skill_entry.reset()

        if self.info_group:
            for cell in self.info_group.info_cells:
                if cell.button and cell.button.text() == "Switch":
                    cell.update_display(cell.initial_text, "Select")

        self.update_points_display()
        
        self.check_button.setEnabled(True)
        self.enable_next_button(False)

        self.refresh_skill_display()

        self.main_window.set_phase_status(self.phase, PhaseStatus.NOT_START)

    def on_enter(self):
        super().on_enter()

    def on_exit(self):
        if 'skills' not in self.main_window.pc_data:
            self.main_window.pc_data['skills'] = {}

        skills_data = {}
        
        special_skills = {'language_own', 'dodge', 'credit_rating'}
        
        for skill in self.skills:
            if skill.super_name:
                skill_key = f"{skill.super_name}:{skill.name}"
            else:
                skill_key = skill.name
                
            if skill.name in special_skills or skill.total_point > skill.default_point:
                skills_data[skill_key] = skill.total_point

        self.main_window.pc_data['skills'] = skills_data

    def refresh_skill_display(self):
        for skill_entry in self.skill_group.findChildren(SkillEntry):
            skill_entry.occupation_points.setEnabled(skill_entry.skill.is_occupation)
            if skill_entry.skill.is_occupation:
                skill_entry.name_label.setStyleSheet("color: #3498DB;")
            elif skill_entry.skill.interest_point > 0:
                skill_entry.name_label.setStyleSheet("color: #2ECC71;")
            else:
                skill_entry.name_label.setStyleSheet("")

    def calculate_remaining_points(self):
        occupation_used = sum(skill.occupation_point for skill in self.skills)
        interest_used = sum(skill.interest_point for skill in self.skills)
        
        return {
            'occupation': self.max_occupation_points - occupation_used,
            'interest': self.max_interest_points - interest_used
        }

    def update_points_display(self):
        remaining = self.calculate_remaining_points()
        self.points_group.occupation_points_entry.set_value(str(remaining['occupation']))
        self.points_group.interest_points_entry.set_value(str(remaining['interest']))

        self.points_group._update_points_color(self.points_group.occupation_points_entry)
        self.points_group._update_points_color(self.points_group.interest_points_entry)

    def reset_completion_status(self):
        if self.main_window.get_phase_status(self.phase) == PhaseStatus.NOT_START:
            self.main_window.set_phase_status(self.phase, PhaseStatus.COMPLETING)
        if self.main_window.get_phase_status(self.phase) == PhaseStatus.COMPLETED:
            self.main_window.set_phase_status(self.phase, PhaseStatus.COMPLETING)
            self.check_button.setEnabled(True)
            self.enable_next_button(False)


class SkillExpandDialog(TFComputingDialog):
    def __init__(self, skill_type: str, parent_ui: 'Phase2UI'):
        super().__init__(f"Expand {skill_type.title()}", parent_ui)
        self.skill_type = skill_type
        self.parent_ui = parent_ui
        self.skill_entries = {}
        self.setup_content()

    def setup_content(self):
        scroll_area, _, layout = self.create_scroll_area()

        for skill in sorted([s for s in self.parent_ui.skills if s.super_name == self.skill_type], 
                        key=lambda x: x.name):
            entry = SkillEntry(
                skill, 
                occupation_points=skill.occupation_point, 
                interest_points=skill.interest_point, 
                parent=self
            )
            self.skill_entries[skill.name] = entry
            layout.addWidget(entry)

        self.buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(self.buttons_frame)
        buttons_layout.setContentsMargins(1, 1, 1, 1)
        buttons_layout.setSpacing(10)
        
        plus_icon = QIcon(resource_path("resources/images/icons/plus.png"))
        self.plus_button = QPushButton()
        self.plus_button.setIcon(plus_icon)
        self.plus_button.setFixedSize(24, 24)
        self.plus_button.clicked.connect(self._on_add_clicked)
        
        minus_icon = QIcon(resource_path("resources/images/icons/minus.png"))
        self.minus_button = QPushButton()
        self.minus_button.setIcon(minus_icon)
        self.minus_button.setFixedSize(24, 24)
        self.minus_button.clicked.connect(self._on_remove_clicked)
        
        buttons_layout.addWidget(self.plus_button)
        buttons_layout.addWidget(self.minus_button)
        buttons_layout.addStretch()
        
        layout.addWidget(self.buttons_frame)
        layout.addStretch()

        self.content_frame.setLayout(QVBoxLayout())
        self.content_frame.layout().addWidget(scroll_area)

    def _on_add_clicked(self):
        input_field = QLineEdit()
        input_field.setFixedHeight(30)
        input_field.setFont(TEXT_FONT)
        
        parent_layout = self.buttons_frame.parentWidget().layout()
        index = parent_layout.indexOf(self.buttons_frame)
        parent_layout.insertWidget(index, input_field)
        input_field.setFocus()
        
        input_field.focusOutEvent = lambda e: self._on_input_focus_lost(e, input_field)

    def _on_input_focus_lost(self, event, input_field: QLineEdit):
        skill_name = input_field.text().strip()
        if skill_name:
            if any(s.name == skill_name.lower() and s.super_name == self.skill_type 
                  for s in self.parent_ui.skills):
                self.parent_ui.main_window.app.show_warning(
                    "Duplicate Skill",
                    "This skill already exists.",
                    buttons=["OK"]
                )
                input_field.deleteLater()
                return
            
            new_skill = Skill(
                name=skill_name.lower(),
                super_name=self.skill_type,
                default_point=PARENT_SKILL_DEFAULTS.get(self.skill_type, 1)
            )
            
            self.parent_ui.skills.append(new_skill)

            entry = SkillEntry(new_skill, self)
            self.skill_entries[new_skill.name] = entry
            
            parent_layout = self.buttons_frame.parentWidget().layout()
            index = parent_layout.indexOf(self.buttons_frame)
            parent_layout.insertWidget(index, entry)

        input_field.deleteLater()

    def _on_remove_clicked(self):
        parent_layout = self.buttons_frame.parentWidget().layout()
        index = parent_layout.indexOf(self.buttons_frame) - 1
        if index >= 0:
            item = parent_layout.itemAt(index)
            if item and item.widget():
                entry = item.widget()
                if isinstance(entry, SkillEntry):
                    self.parent_ui.skills.remove(entry.skill)
                    entry.deleteLater()
                    if entry.skill.name in self.skill_entries:
                        del self.skill_entries[entry.skill.name]

    def get_result(self) -> List[Skill]:
        return [entry.skill for entry in self.skill_entries.values()]
    
    def get_field_values(self) -> dict:
        skill_data = {}
        for name, entry in self.skill_entries.items():
            skill_data[name] = entry.get_values()
        return skill_data
    
    def process_validated_data(self, data: dict) -> any:
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
            return (not existing_skill or not existing_skill.is_occupation, "This skill is already an occupation skill.")
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
                                    if skill.name in INTERPERSONAL_SKILLS]

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
    