from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

from implements.components.base_phase import BasePhase
from implements.components.data_reader import load_combat_skills_from_json, load_spells_from_json
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_frame import TFBaseFrame


class Phase4(BasePhase):
    def _setup_content(self) -> None:
        super()._setup_content()

        self.buttons_frame.next_button.hide()
        self.buttons_frame.complete_button.show()

        self.show_experience_packages_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="可用经历包", 
            height=35,
            width=120, 
            on_clicked=self._on_show_experience_packages_clicked
        )

        self.show_combat_skills_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="战技列表", 
            height=35,
            width=120, 
            on_clicked=self._on_show_combat_skills_clicked
        )

        self.show_spells_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="魔法列表", 
            height=35,
            width=120, 
            on_clicked=self._on_show_spells_clicked
        )

        self.buttons_frame.add_custom_button(self.show_experience_packages_button)
        self.buttons_frame.add_custom_button(self.show_combat_skills_button)
        self.buttons_frame.add_custom_button(self.show_spells_button)

        self.upper_frame = UpperFrame(self)
        self.lower_frame = LowerFrame(self)

        self.contents_frame.add_child('upper_frame', self.upper_frame)
        self.contents_frame.add_child('lower_frame', self.lower_frame)

    def reset_contents(self):
        pass

    def save_state(self):
        pass

    def check_dependencies(self):
        self.spells = load_spells_from_json()
        self.combat_skills = load_combat_skills_from_json()

    def on_complete(self):
        pass

    def _on_show_experience_packages_clicked(self):
        pass

    def _on_show_combat_skills_clicked(self):
        pass

    def _on_show_spells_clicked(self):
        pass


class UpperFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.spells_frame = SpellsFrame(self)
        self.upper_right_frame = UpperRightFrame(self)

        self.add_child('spells_frame', self.spells_frame)
        self.add_child('upper_right_frame', self.upper_right_frame)


class SpellsFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass


class UpperRightFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.combat_skills_frame = CombatSkillsFrame(self)
        self.experience_package_frame = ExperiencePackageFrame(self)

        self.add_child('combat_skills_frame', self.combat_skills_frame)
        self.add_child('experience_package_frame', self.experience_package_frame)


class CombatSkillsFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass


class ExperiencePackageFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass



class LowerFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.deposit_frame = DepositFrame(self)
        self.inner_connection_frame = InnerConnectionFrame(self)
        self.outer_connection_frame = OuterConnectionFrame(self)
        self.talents_frame = TalentsAndAbilitiesFrame(self)
        self.aspiration_frame = AspirationsAndDrives(self)
        self.notes_frame = NotesFrame(self)

        self.add_child('deposit_frame', self.deposit_frame)
        self.add_child('inner_connection_frame', self.inner_connection_frame)
        self.add_child('outer_connection_frame', self.outer_connection_frame)
        self.add_child('talents_frame', self.talents_frame)
        self.add_child('aspiration_frame', self.aspiration_frame)
        self.add_child('notes_frame', self.notes_frame)


class DepositFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.edit = self.create_text_edit(
            name="deposit",
            placeholder_text="请输入你的资产，通过逗号隔开",
            width=180,
            height=110
        )


class InnerConnectionFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.edit = self.create_text_edit(
            name="inner_connection",
            placeholder_text="请输入局内关系，通过逗号隔开",
            width=180,
            height=110
        )


class OuterConnectionFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.edit = self.create_text_edit(
            name="outer_connection",
            placeholder_text="请输入局外关系，通过逗号隔开",
            width=180,
            height=110
        )


class TalentsAndAbilitiesFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.edit = self.create_text_edit(
            name="talents",
            placeholder_text="请输入你的天赋与能力，通过逗号隔开",
            width=180,
            height=110
        )


class AspirationsAndDrives(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.edit = self.create_text_edit(
            name="aspiration",
            placeholder_text="请输入你的理想与追求，通过逗号隔开",
            width=180,
            height=110
        )


class NotesFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.edit = self.create_text_edit(
            name="notes",
            placeholder_text="请输入其他任何笔记，通过逗号隔开",
            width=180,
            height=110
        )