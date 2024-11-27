from typing import Dict
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QStackedWidget

from implements.components.base_phase import BasePhase
from implements.components.data_reader import load_skills_from_json, load_occupations_from_json
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_frame import TFBaseFrame


class Phase2(BasePhase):

    def __init__(self, p_data: Dict, config: Dict, parent: QStackedWidget):
        super().__init__(p_data, config, parent)
        curr_dex = int(p_data["basic_stats"]["dex"])
        curr_edu = int(p_data["basic_stats"]["edu"])
        language_own = p_data["character_info"]["language_own"].lower()
        self.skills = load_skills_from_json(curr_dex, curr_edu, language_own)
        self.occupations = load_occupations_from_json()

    def _setup_content(self) -> None:
        super()._setup_content()

        self.show_occupation_list_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="Occ. List", 
            height=35,
            width=120,
            on_clicked=self._on_occupation_list_clicked
        )

        self.buttons_frame.add_custom_button(self.show_occupation_list_button)

        self.upper_frame = UpperFrame(self)
        self.skills_frame = SkillsFrame(self)

        self.add_child("upper_frame", self.upper_frame)
        self.add_child("skill_frame", self.skill_frame)

    def _on_occupation_list_clicked(self):
        pass


class UpperFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.basic_info_frame = BasicInformationFrame(self)
        self.occupation_skills_frame = OccupationSkillsFrame(self)

        self.add_child("basic_info", self.basic_info_frame)
        self.add_child("occupation_skills", self.occupation_skills_frame)


class BasicInformationFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass


class OccupationSkillsFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QGridLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass


class UpperFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass


class SkillsFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QGridLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass
