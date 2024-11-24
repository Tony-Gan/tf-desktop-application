from PyQt6.QtWidgets import QGridLayout, QHBoxLayout
from implements.components.base_phase import BasePhase
from ui.components.tf_base_frame import TFBaseFrame


class Phase0(BasePhase):

    def _setup_content(self) -> None:
        super()._setup_content()

        self.mode_entry = self.create_option_entry(
            name="mode",
            label_text="Mode:",
            options=["Destiny", "Points"],
            current_value="None",
            label_size=100,
            value_size=80,
            height=24
        )

        self.points_entry = PointsEntry(self)
        self.destiny_entry = DestinyEntry(self)
        self.general_entry = GeneralEntry(self)

        self.contents_frame.main_layout.addWidget(self.mode_entry)

        self.contents_frame.add_child("points_entry", self.points_entry)
        self.contents_frame.add_child("destiny_entry", self.destiny_entry)
        self.contents_frame.add_child("general_entry", self.general_entry)

    def reset_contents(self):
        pass

    def initialize(self):
        pass

    def save_state(self):
        pass

    def restore_state(self):
        pass

    def check_dependencies(self):
        pass


class PointsEntry(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.points_available_entry = self.create_value_entry(
            name="points_available",
            label_text="Points Available:",
            label_size=135,
            value_size=80,
            height=24
        )

        self.stats_upper_limit_entry = self.create_value_entry(
            name="states_upper_limit",
            label_text="Stats Upper Limit:",
            label_size=135,
            value_size=80,
            height=24
        )

        self.stats_lower_limit_entry = self.create_value_entry(
            name="states_lower_limit",
            label_text="Stats Lower Limit:",
            label_size=135,
            value_size=80,
            height=24
        )

        self.allow_custom_luck_entry = self.create_check_with_label(
            name="allow_custom_luck",
            label_text="Allow Cusom Luck",
            height=24
        )

        self.main_layout.addWidget(self.points_available_entry)
        self.main_layout.addWidget(self.stats_upper_limit_entry)
        self.main_layout.addWidget(self.stats_lower_limit_entry)
        self.main_layout.addWidget(self.allow_custom_luck_entry)


class DestinyEntry(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.dice_count_entry = self.create_value_entry(
            name="dice_count",
            label_text="Dice Count:",
            label_size=135,
            value_size=80,
            height=24
        )

        self.allow_stats_exchange_entry = self.create_check_with_label(
            name="stats_exchange",
            label_text="Allow Stats Exchange",
            height=24
        )

        self.exchange_count_entry = self.create_value_entry(
            name="exchange_count",
            label_text="Exchange Count:",
            label_size=135,
            value_size=80,
            height=24
        )

        self.main_layout.addWidget(self.dice_count_entry)
        self.main_layout.addWidget(self.allow_stats_exchange_entry)
        self.main_layout.addWidget(self.exchange_count_entry)


class GeneralEntry(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.occupation_skill_limit_entry = self.create_value_entry(
            name="occupation_skill_limit",
            label_text="Occupation Skill Limit:",
            label_size=135,
            value_size=80,
            height=24
        )

        self.interest_skill_limit_entry = self.create_value_entry(
            name="interest_skill_limit",
            label_text="Interest Skill Limit:",
            label_size=135,
            value_size=80,
            height=24
        )

        self.allow_mix_points_entry = self.create_check_with_label(
            name="allow_mix_points",
            label_text="Allow Mix Points",
            height=24
        )

        self.main_layout.addWidget(self.occupation_skill_limit_entry)
        self.main_layout.addWidget(self.interest_skill_limit_entry)
        self.main_layout.addWidget(self.allow_mix_points_entry)
