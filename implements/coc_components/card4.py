from implements.coc_components.base_card import BaseCard
from ui.components.tf_base_frame import TFBaseFrame


class Card4(BaseCard):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def _setup_content(self):
        self.spells_frame = SpellsFrame(self)
        self.combat_skills_frame = CombatSkillsFrame(self)

        self.add_child('spells_frame', self.spells_frame)
        self.add_child('combat_skills_frame', self.combat_skills_frame)

    def load_data(self, p_data):
        pass

    def save_data(self, p_data):
        pass

    def enable_edit(self):
        pass


class SpellsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        pass


class CombatSkillsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        pass
    