from PyQt6.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout
from implements.components.base_phase import BasePhase
from ui.components.tf_base_frame import TFBaseFrame


class Phase1(BasePhase):

    def _setup_content(self) -> None:
        super()._setup_content()

        self.upper_frame = UpperFrame(self)
        self.lower_frame = LowerFrame(self)

        self.contents_frame.main_layout.addWidget(self.upper_frame)
        self.contents_frame.main_layout.addWidget(self.lower_frame)


class UpperFrame(TFBaseFrame):

    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.avatar_frame = AvatarFrame(self)
        self.player_info_group = PlayerInfoGroup(self)
        self.character_info_group = CharacterInfoGroup(self)

        self.main_layout.addWidget(self.avatar_frame)
        self.main_layout.addWidget(self.player_info_group)
        self.main_layout.addWidget(self.character_info_group)


class LowerFrame(TFBaseFrame):

    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.basic_states_group = BasicStatsGroup(self)
        self.derived_states_group = DerivedStatesGroup(self)
        self.points_info_group = PointsInfoGroup(self)

        self.main_layout.addWidget(self.basic_states_group)
        self.main_layout.addWidget(self.derived_states_group)
        self.main_layout.addWidget(self.points_info_group)


class AvatarFrame(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(level=1, radius=15, parent=parent)

    def _setup_content(self) -> None:
        pass


class PlayerInfoGroup(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(level=1, radius=15, parent=parent)

    def _setup_content(self) -> None:
        pass


class CharacterInfoGroup(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(layout_type=QGridLayout, level=1, radius=15, parent=parent)

    def _setup_content(self) -> None:
        pass


class BasicStatsGroup(TFBaseFrame):
    
    def __init__(self, parent=None):
        super().__init__(layout_type=QGridLayout, level=1, radius=15, parent=parent)

    def _setup_content(self) -> None:
        pass


class DerivedStatesGroup(TFBaseFrame):
    
    def __init__(self, parent=None):
        super().__init__(level=1, radius=15, parent=parent)

    def _setup_content(self) -> None:
        pass


class PointsInfoGroup(TFBaseFrame):
    
    def __init__(self, parent=None):
        super().__init__(level=1, radius=15, parent=parent)

    def _setup_content(self) -> None:
        pass
