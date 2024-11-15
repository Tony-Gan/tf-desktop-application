from dataclasses import dataclass
from typing import List, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QGroupBox, QLabel, QRadioButton, QButtonGroup, QPushButton, QLineEdit

from implements.coc_tools.pc_builder_helper.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_helper.phase_ui import BasePhaseUI
from implements.coc_tools.pc_builder_helper.constants import DEFAULT_SKILLS, PARENT_SKILL_DEFAULTS, INTERPERSONAL_SKILLS
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
    def __init__(self, skill: Skill, parent=None):
        super().__init__(parent)

        self.skill = skill
        self.setObjectName(f"skill_entry_{skill.super_name}_{skill.name}" if skill.super_name else f"skill_entry_{skill.name}")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(2)

        self.name_label = QLabel(skill.display_name)
        self.name_label.setFont(LABEL_FONT)
        self.name_label.setFixedWidth(100) 

        if skill.is_occupation:
            self.name_label.setStyleSheet("color: blue;")

        self.occupation_points = TFNumberReceiver(
            text="0",
            width=20,
            font=TEXT_FONT,
            alignment=Qt.AlignmentFlag.AlignCenter,
            allow_decimal=False,
            allow_negative=False
        )
        self.occupation_points.setStyleSheet("padding: 0;")

        self.interest_points = TFNumberReceiver(
            text="0",
            width=20,
            font=TEXT_FONT,
            alignment=Qt.AlignmentFlag.AlignCenter,
            allow_decimal=False,
            allow_negative=False
        )
        self.interest_points.setStyleSheet("padding: 0;")

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
            width=20,
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
        try:
            self.skill.occupation_point = int(self.occupation_points.text() or 0)
            self.skill.interest_points = int(self.interest_points.text() or 0)
            self.total.setText(str(self.skill.total_point))
        except ValueError:
            pass

    def get_values(self) -> dict:
        return {
            'occupation_points': int(self.occupation_points.text() or 0),
            'interest_points': int(self.interest_points.text() or 0),
            'total': int(self.total.text())
        }

    def reset(self):
        self.occupation_points.setText("0")
        self.interest_points.setText("0")
        self._update_total()


class PointsGroup(QGroupBox):
    def __init__(self, pc_data, parent:'Phase2UI'):
        super().__init__("Available Points", parent)
        self.setObjectName("points_group")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self.pc_data = pc_data
        self._setup_content()

    def _setup_content(self):
        personal_info = self.pc_data.get('personal_info', {})

        self.occupation_points_entry = TFValueEntry(
            label_text="Occupation Points:",
            value_text=str(personal_info.get('occupation_skill_points', 0)),
            label_size=135,
            value_size=40,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.interest_points_entry = TFValueEntry(
            label_text="Interest Points:",
            value_text=str(personal_info.get('interest_skill_points', 0)),
            label_size=135,
            value_size=40,
            enabled=False,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        self.layout.addStretch()
        self.layout.addWidget(self.occupation_points_entry)
        self.layout.addWidget(self.interest_points_entry)
        self.layout.addStretch()


class InfoGroup(QGroupBox):
    def __init__(self, pc_data, parent:'Phase2UI'):
        personal_info = pc_data.get('personal_info', {})
        occupation_name = personal_info.get('occupation', '')
        super().__init__(occupation_name, parent)
        self.parent = parent

        self.setObjectName("info_group")
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self._pc_data = pc_data
        self._occupation_name = occupation_name
        self._setup_content()

    def _setup_content(self):
        occupation = next((occ for occ in self.parent.occupation_list if occ.name == self._occupation_name), None)
        if not occupation:
            return QGroupBox(self._occupation_name)

        occ_skills = occupation.get_skills().split(',')
        row, col = 0, 0

        for skill in occ_skills:
            skill_text = InfoCell.format_skill_name(skill)

            if 'any' in skill.lower():
                cell = InfoCell(
                    text=skill_text,
                    on_button_clicked=lambda checked, s=skill: self._on_skill_select(s)
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

            self.layout.addLayout(cell, row, col)

            col += 1
            if col == 3:
                col = 0
                row += 1

        credit_min = occupation.get_credit_rating_min()
        credit_max = occupation.get_credit_rating_max()
        credit_cell = InfoCell(f"Credit Rating ({credit_min} - {credit_max})")
        self.layout.addLayout(credit_cell, row, col)

        col += 1
        while col < 3:
            empty_cell = InfoCell("")
            self.layout.addLayout(empty_cell, row, col)
            col += 1
            if col == 3 and row < 2:
                col = 0
                row += 1

    def _on_skill_select(self, skill: str):
        dialog = None
        target_cell = None

        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            if isinstance(item, InfoCell) and item.label.text() == InfoCell.format_skill_name(skill):
                target_cell = item
                break

        if target_cell and target_cell.button:
            if target_cell.button.text() == "Switch":
                current_skill = next(
                    (s for s in self.parent.skills if s.display_name == target_cell.label.text()),
                    None
                )
                if current_skill:
                    current_skill.is_occupation = False
                    self.parent.refresh_skill_display()

            if "interpersonal_skill:any" in skill.lower():
                dialog = InterpersonalSkillDialog(parent_ui=self.parent)
            elif ":any" in skill.lower():
                skill_type = skill.split(":")[0]
                dialog = SpecificSkillDialog(skill_type=skill_type, parent_ui=self.parent)
            elif skill.lower() == "any":
                dialog = AnySkillDialog(parent_ui=self.parent)

            if dialog and dialog.exec():
                selected_skill = dialog.get_result()
                if selected_skill:
                    selected_skill.is_occupation = True
                    target_cell.update_display(selected_skill.display_name, "Switch")
                    self.parent.refresh_skill_display()


class InfoCell(QHBoxLayout):

    def __init__(self, text: str, on_button_clicked=None):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(5)

        self.label = QLabel(text)
        self.label.setFont(LABEL_FONT)
        self.addWidget(self.label)

        self.button = None
        if on_button_clicked is not None:
            self.button = TFBaseButton("Select", None, height=24, width=50)
            self.button.clicked.connect(on_button_clicked)
            self.addWidget(self.button)

        self.addStretch()

    def update_display(self, text: str, button_text: str = None):
        self.label.setText(text)
        if self.button and button_text:
            self.button.setText(button_text)

    @staticmethod
    def format_skill_name(skill: str) -> str:
        if ':' in skill:
            parent, child = skill.split(':')
            parent = parent.replace('_', ' ').title()
            if 'any' in child.lower():
                return parent
            child = child.replace('_', ' ').title()
            return f"{parent} - {child}"
        elif skill == 'any':
            return "Any Skill"
        else:
            return skill.replace('_', ' ').title()


class Phase2UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        self.config = main_window.config
        self.main_window = main_window

        self.check_button = None
        self.previous_button = None
        self.skills = [
            Skill(
                name=skill_key.split(":")[1] if ":" in skill_key else skill_key,
                super_name=skill_key.split(":")[0] if ":" in skill_key else None,
                default_point=default_point
            )
            for skill_key, default_point in DEFAULT_SKILLS.items()
        ]

        super().__init__(PCBuilderPhase.PHASE2, main_window, parent)

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

        self.points_group = PointsGroup(self.main_window.pc_data,self)
        self.info_group = InfoGroup(self.main_window.pc_data, self)
        upper_layout.addWidget(self.points_group, 2)
        upper_layout.addWidget(self.info_group, 8)

        self.skill_group = self._create_skills_group()
        content_layout.addWidget(upper_frame, 2)
        content_layout.addWidget(self.skill_group, 8)

        self.content_area.setLayout(content_layout)

    def _create_skills_group(self):
        frame = QFrame()
        frame.setObjectName("section_frame")
        main_layout = QVBoxLayout(frame)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

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

        main_layout.addWidget(skills_frame, 9)

        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        for skill in PARENT_SKILL_DEFAULTS:
            button = TFBaseButton(
                f"Expand {skill.title()}",
                self,
                height=30,
                on_clicked=lambda checked, s=skill: self._on_expand_skill(s)
            )
            buttons_layout.addWidget(button)

        add_skill_button = TFBaseButton(
            "Add New Skill",
            self,
            height=30,
            on_clicked=self._on_add_new_skill
        )
        buttons_layout.addWidget(add_skill_button)

        main_layout.addWidget(buttons_frame, 1)

        return frame

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
        pass

    def _on_occupation_list_clicked(self):
        print("[Phase2UI] on_occupation_list_clicked called.")

    def _on_config_updated(self):
        print("[Phase2UI] _on_config_updated called.")

    def _on_check_clicked(self):
        print("[Phase2UI] _on_check_clicked called.")

    def _on_previous_clicked(self):
        self.main_window._on_phase_selected(PCBuilderPhase.PHASE1)

    def _reset_content(self):
        print("[Phase2UI] _reset_content called.")

    def on_enter(self):
        """Called when the phase becomes active"""
        super().on_enter()

    def on_exit(self):
        """Called when the phase becomes inactive"""
        pass

    def _on_expand_skill(self, skill: str):
        print(skill)

    def _on_add_new_skill(self):
        print("Adding new skill")

    def refresh_skill_display(self):
        for skill_entry in self.skill_group.findChildren(SkillEntry):
            if skill_entry.skill.is_occupation:
                skill_entry.name_label.setStyleSheet("color: blue;")
            else:
                skill_entry.name_label.setStyleSheet("")


class SkillExpandDialog(TFComputingDialog):
    def __init__(self, skill_type: str, parent_ui: 'Phase2UI', existing_skills: List[Skill] = None):
        super().__init__(f"Expand {skill_type.title()}", parent_ui)
        self.skill_type = skill_type
        self.parent_ui = parent_ui
        self.existing_skills = existing_skills or []
        self.skill_entries = {}
        self.setup_content()

    def setup_content(self):
        scroll_area, container, layout = self.create_scroll_area()

        for skill in sorted([s for s in self.parent_ui.skills if s.super_name == self.skill_type], 
                        key=lambda x: x.name):
            entry = SkillEntry(skill, self)
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
            self.parent_ui.main_window.app.show_warning("Select Failure", "This skill is already an occupation skill.")


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
             if skill.super_name == self.skill_type],
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
