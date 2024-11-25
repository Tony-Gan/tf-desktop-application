from PyQt6.QtWidgets import QGridLayout

from implements.components.base_phase import BasePhase
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_frame import TFBaseFrame
from ui.components.tf_font import Merriweather


class Phase0(BasePhase):

    def _setup_content(self) -> None:
        super()._setup_content()

        self.contents_frame.main_layout.setContentsMargins(10, 10, 10, 10)
        self.contents_frame.main_layout.setSpacing(40)

        self.special_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="Generate Token", 
            height=35,
            width=150,
            on_clicked=self._on_special_button_clicked
        )
        self.buttons_frame.add_custom_button(self.special_button)

        """
        TOKEN:
            - Digit 1-2: PO - Points, DE - Destiny
            - Digit 3-9 in PO
                - Total Points - /5 then HEX
                - Upper - HEX
                - Lower - HEX
                - Custom LUK - E:true, L:false
            - Digit 3-9 in DE
                - Dice - NUMBER + "DCE"
                - Switch - G:true, M:false
                - Switch Count - NUMBER + "SC"
            - Digit 10-11 - occupation upper in HEX
            - Digit 12-13 - interest upper in HEX
            - Digit 14 - allow mix: Y:true, X:false
            - Digit 15 - allow mythos: J:true, K:false
            - Digit 16 - allow custom weapon: I:true, U:false
            - Digit 17 - completed mode: A:true, C:false
            - Digit 18 - instruction mode: R:true, T:false
            
            Fence encrytion - 1 time.
        """

        self.points_entry = PointsEntry(self)
        self.destiny_entry = DestinyEntry(self)
        self.general_entry = GeneralEntry(self)
        self.base_entry = BaseEntry(self)

        self.contents_frame.add_child("base_entry", self.base_entry)
        self.contents_frame.add_child("points_entry", self.points_entry)
        self.contents_frame.add_child("destiny_entry", self.destiny_entry)
        self.contents_frame.add_child("general_entry", self.general_entry)
        self.contents_frame.main_layout.addStretch()

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

    def _on_special_button_clicked(self):
        print(123)


class BaseEntry(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setSpacing(20)

        self.mode_entry = self.create_option_entry(
            name="mode",
            label_text="Mode:",
            label_font=Merriweather,
            options=["Points", "Destiny"],
            current_value="None",
            label_size=100,
            value_size=80,
            height=24
        )
        self.mode_entry.value_changed.connect(self._handle_mode_change)

        self.token_entry = self.create_value_entry(
            name="token",
            label_text="Token:",
            label_font=Merriweather,
            label_size=100,
            value_size=300,
            height=24,
            show_tooltip=True,
            tooltip_text="Token provided by your Keeper, use the token and all settings will be done automatically."
        )

        self._handle_mode_change("None")

        self.main_layout.addWidget(self.mode_entry)
        self.main_layout.addWidget(self.token_entry)

    def _handle_mode_change(self, mode: str) -> None:
        self.parent.points_entry.setEnabled(False)
        self.parent.destiny_entry.setEnabled(False)
        self.parent.general_entry.setEnabled(False)

        if mode == "Points":
            self.parent.points_entry.setEnabled(True)
            self.parent.general_entry.setEnabled(True)
        elif mode == "Destiny":
            self.parent.destiny_entry.setEnabled(True)
            self.parent.general_entry.setEnabled(True)


class PointsEntry(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QGridLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setSpacing(20)

        self.points_available_entry = self.create_value_entry(
            name="points_available",
            label_text="Points Available:",
            label_size=135,
            label_font=Merriweather,
            value_size=45,
            value_text=480,
            number_only=True,
            allow_decimal=False,
            height=24
        )

        self.stats_upper_limit_entry = self.create_value_entry(
            name="states_upper_limit",
            label_text="Stats Upper Limit:",
            label_size=135,
            label_font=Merriweather,
            value_size=30,
            value_text=80,
            height=24
        )

        self.stats_lower_limit_entry = self.create_value_entry(
            name="states_lower_limit",
            label_text="Stats Lower Limit:",
            label_size=135,
            label_font=Merriweather,
            value_size=30,
            value_text=30,
            height=24
        )

        self.allow_custom_luck_entry = self.create_check_with_label(
            name="allow_custom_luck",
            label_text="Allow Cusom Luck",
            label_font=Merriweather,
            checked=False,
            height=24,
            show_tooltip=True,
            tooltip_text="Checking this option requires the allocation of points to Luck (LUK). If not checked, Luck is determined by rolling the dice."
        )

        self.main_layout.addWidget(self.points_available_entry, 0, 0)
        self.main_layout.addWidget(self.stats_upper_limit_entry, 0, 1)
        self.main_layout.addWidget(self.stats_lower_limit_entry, 0, 2)
        self.main_layout.addWidget(self.allow_custom_luck_entry, 1, 0)


class DestinyEntry(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QGridLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setSpacing(20)

        self.dice_count_entry = self.create_value_entry(
            name="dice_count",
            label_text="Dice Count:",
            label_size=135,
            label_font=Merriweather,
            value_size=30,
            value_text="3",
            number_only=True,
            allow_decimal=False,
            height=24
        )

        self.allow_stats_exchange_entry = self.create_check_with_label(
            name="stats_exchange",
            label_text="Allow Stats Exchange",
            label_font=Merriweather,
            checked=False,
            height=24,
            show_tooltip=True,
            tooltip_text="Checking this option allows the exchange of two attributes after selection."
        )
        self.allow_stats_exchange_entry.value_changed.connect(self._handle_exchange_change)

        self.exchange_count_entry = self.create_value_entry(
            name="exchange_count",
            label_text="Exchange Count:",
            value_text="1",
            label_size=135,
            value_size=30,
            label_font=Merriweather,
            number_only=True,
            allow_decimal=False,
            height=24
        )

        self.main_layout.addWidget(self.dice_count_entry, 0, 0)
        self.main_layout.addWidget(self.allow_stats_exchange_entry, 1, 0)
        self.main_layout.addWidget(self.exchange_count_entry, 1, 1)

        self.exchange_count_entry.set_enable(False)

    def _handle_exchange_change(self, state: bool):
        self.exchange_count_entry.set_enable(state)


class GeneralEntry(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QGridLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setSpacing(20)

        self.occupation_skill_limit_entry = self.create_value_entry(
            name="occupation_skill_limit",
            label_text="Occupation Skill Limit:",
            label_size=150,
            value_size=30,
            value_text=80,
            label_font=Merriweather,
            height=24,
            show_tooltip=True,
            tooltip_text="The maximum points limit for each occupation skill."
        )

        self.interest_skill_limit_entry = self.create_value_entry(
            name="interest_skill_limit",
            label_text="Interest Skill Limit:",
            label_size=150,
            value_size=30,
            value_text=60,
            label_font=Merriweather,
            height=24,
            show_tooltip=True,
            tooltip_text="The maximum points limit for each interest skill."
        )

        self.allow_mix_points_entry = self.create_check_with_label(
            name="allow_mix_points",
            label_text="Allow Mix Points",
            label_font=Merriweather,
            checked=True,
            height=24,
            show_tooltip=True,
            tooltip_text="Checking this option allows the allocation of both occupation points and interest points to the same skill simultaneously."
        )

        tooltip = """
        Checking this option enables settings related to the Cthulhu Mythos. Specifically, Cthulhu Mythos will appear during skill allocation, \n
        and new options related to the Cthulhu background will be added during background setting.
        """
        self.allow_mythos_entry = self.create_check_with_label(
            name="allow_mythos",
            label_text="Allow Mythos",
            label_font=Merriweather,
            checked=False,
            height=24,
            show_tooltip=True,
            tooltip_text=tooltip
        )

        self.custom_weapon_type_entry = self.create_check_with_label(
            name="custom_weapon_type",
            label_text="Custom Weapon Type",
            label_font=Merriweather,
            height=24,
            show_tooltip=True,
            tooltip_text="Checking this option allows full customization of weapon attributes."
        )

        self.completed_mode_entry = self.create_check_with_label(
            name="completed_mode",
            label_text="Completed Mode",
            label_font=Merriweather,
            height=24,
            show_tooltip=True,
            tooltip_text="Checking this option will display uncommon settings for new cards, such as spells."
        )

        self.instruction_mode_entry = self.create_check_with_label(
            name="instruction_mode",
            label_text="Instruction Mode",
            label_font=Merriweather,
            checked=False,
            height=24,
            show_tooltip=True,
            tooltip_text="Checking this option activates guide mode, suitable for newcomers."
        )

        self.main_layout.addWidget(self.occupation_skill_limit_entry, 0, 0)
        self.main_layout.addWidget(self.interest_skill_limit_entry, 0, 1)
        self.main_layout.addWidget(self.allow_mix_points_entry, 0, 2)
        self.main_layout.addWidget(self.allow_mythos_entry, 1, 0)
        self.main_layout.addWidget(self.custom_weapon_type_entry, 1, 1)
        self.main_layout.addWidget(self.completed_mode_entry, 1, 2)
        self.main_layout.addWidget(self.instruction_mode_entry, 2, 0)
