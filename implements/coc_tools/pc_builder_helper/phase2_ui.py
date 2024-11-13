from dataclasses import dataclass
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QGroupBox

from implements.coc_tools.pc_builder_helper.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_helper.phase_ui import BasePhaseUI
from implements.coc_tools.pc_builder_helper.constants import DEFAULT_SKILLS, PARENT_SKILL_DEFAULTS
from ui.components.tf_base_button import TFPreviousButton, TFBaseButton
from ui.components.tf_value_entry import TFValueEntry
from utils.validator.tf_validator import TFValidator


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

        upper_layout.addWidget(self._create_points_group(), 2)
        upper_layout.addWidget(self._create_info_group(), 8)

        content_layout.addWidget(upper_frame, 2)
        content_layout.addWidget(self._create_skills_group(), 8)

        self.content_area.setLayout(content_layout)

    def _create_points_group(self):
        group = QGroupBox("Available Points")
        points_layout = QVBoxLayout(group)
        points_layout.setContentsMargins(10, 10, 10, 10)
        points_layout.setSpacing(10)

        personal_info = self.main_window.pc_data.get('personal_info', {})

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

        points_layout.addStretch()
        points_layout.addWidget(self.occupation_points_entry)
        points_layout.addWidget(self.interest_points_entry)
        points_layout.addStretch()

        return group

    def _create_info_group(self):
        personal_info = self.main_window.pc_data.get('personal_info', {})

        group = QGroupBox(personal_info.get('occupation', ''))
        info_layout = QHBoxLayout(group)
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(10)

        return group

    def _create_skills_group(self):
        frame = QFrame()
        frame.setObjectName("section_frame")
        skills_layout = QGridLayout(frame)
        skills_layout.setContentsMargins(10, 10, 10, 10)
        skills_layout.setSpacing(10)

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
        self.main_window.current_phase = PCBuilderPhase.PHASE1
        self.main_window.load_phase_ui()

    def _on_next_clicked(self):
        print("[Phase2UI] _on_next_clicked called.")

    def _reset_content(self):
        print("[Phase2UI] _reset_content called.")
