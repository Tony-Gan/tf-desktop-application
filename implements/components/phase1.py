from typing import Any, List, Optional, Tuple

from PyQt6.QtWidgets import QGridLayout, QHBoxLayout

from implements.components.base_phase import BasePhase
from ui.components.tf_base_dialog import TFBaseDialog
from ui.components.tf_base_frame import TFBaseFrame


class Phase1(BasePhase):

    def _setup_content(self) -> None:
        super()._setup_content()

        self.upper_frame = UpperFrame(self)
        self.lower_frame = LowerFrame(self)

        self.contents_frame.main_layout.addWidget(self.upper_frame)
        self.contents_frame.main_layout.addWidget(self.lower_frame)

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


class UpperFrame(TFBaseFrame):

    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.avatar_frame = AvatarFrame(self)
        self.player_info_group = PlayerInfoGroup(self)
        self.character_info_group = CharacterInfoGroup(self)

        self.main_layout.addWidget(self.avatar_frame)
        self.main_layout.addWidget(self.player_info_group)
        self.main_layout.addWidget(self.character_info_group)


class LowerFrame(TFBaseFrame):

    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.basic_states_group = BasicStatsGroup(self)
        self.derived_states_group = DerivedStatesGroup(self)

        self.main_layout.addWidget(self.basic_states_group)
        self.main_layout.addWidget(self.derived_states_group)


class AvatarFrame(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        pass


class PlayerInfoGroup(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        self.player_name_entry = self.create_value_entry(
            name="player_name",
            label_text="Player Name:",
            label_size=100,
            value_size=80,
            height=24
        )

        self.campaign_date_entry = self.create_date_entry(
            name="compaign_date",
            label_text="Compaign Date:",
            label_size=100,
            value_size=80,
            height=24
        )

        self.era_entry = self.create_option_entry(
            name="era",
            label_text="Era:",
            options=["None", "1920s", "Modern"],
            current_value="None",
            label_size=100,
            value_size=80,
            height=24
        )

        self.main_layout.addWidget(self.player_name_entry)
        self.main_layout.addWidget(self.era_entry)
        self.main_layout.addWidget(self.campaign_date_entry)


class CharacterInfoGroup(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(layout_type=QGridLayout, radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        self.char_name_entry = self.create_value_entry(
            name="char_name",
            label_text="Character Name:",
            label_size=100,
            value_size=80,
            height=24
        )

        self.age_entry = self.create_value_entry(
            name="age",
            label_text="Age:",
            label_size=100,
            value_size=80,
            height=24,
            number_only=True,
            allow_decimal=False,
            max_digits=2
        )

        self.gender_entry = self.create_option_entry(
            name="gender",
            label_text="Gender:",
            options=["None", "Male", "Female", "Other"],
            current_value="None",
            label_size=100,
            value_size=80,
            height=24
        )

        self.natinality_entry = self.create_value_entry(
            name="nationality",
            label_text="Nationality:",
            label_size=100,
            value_size=80,
            height=24
        )

        self.residence_entry = self.create_value_entry(
            name="residence",
            label_text="Residence:",
            label_size=100,
            value_size=80,
            height=24
        )

        self.birthpalce_entry = self.create_value_entry(
            name="birthpalce",
            label_text="Birthplace:",
            label_size=100,
            value_size=80,
            height=24
        )

        self.language_own_entry = self.create_button_entry(
            name="language_own",
            button_text="Set Language",
            button_callback=self._on_language_select,
            reverse=True,
            border_radius=5
        )
        self.language_own_entry.set_entry_enabled(False)

        self.main_layout.addWidget(self.char_name_entry)
        self.main_layout.addWidget(self.age_entry)
        self.main_layout.addWidget(self.gender_entry)
        self.main_layout.addWidget(self.natinality_entry)
        self.main_layout.addWidget(self.residence_entry)
        self.main_layout.addWidget(self.birthpalce_entry)
        self.main_layout.addWidget(self.language_own_entry)

    def _on_language_select(self):
        success, selected_language = LanguageSelectionDialog.get_input(self)
        if success and selected_language:
            self.language_own_entry.set_text(selected_language)


class BasicStatsGroup(TFBaseFrame):
    
    def __init__(self, parent=None):
        self.stats_entries = {}
        super().__init__(layout_type=QGridLayout, radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK']
        for i, stat in enumerate(stats):
            row = i // 3
            col = i % 3
            entry = self.create_value_entry(
                name=stat.lower(),
                label_text=f"{stat}:",
                value_text="0",
                value_size=40,
                label_size=40,
                number_only=True,
                allow_decimal=False,
            )
            self.stats_entries[stat] = entry
            self.main_layout.addWidget(entry, row, col)


class DerivedStatesGroup(TFBaseFrame):
    
    def __init__(self, parent=None):
        self.derived_entries = {}
        super().__init__(radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        derived_stats = [
            ('HP', 'HP'),
            ('MP', 'MP'),
            ('SAN', 'San'),
            ('MOV', 'Move'),
            ('DB', 'DB'),
            ('Build', 'Build')
        ]

        for stat_key, label_text in derived_stats:
            entry = self.create_value_entry(
                name=label_text.lower(),
                label_text=label_text + ":",
                value_text="",
                value_size=40,
                label_size=40,
                number_only=True,
            )
            self.derived_entries[stat_key] = entry
            self.main_layout.addWidget(entry)


class LanguageSelectionDialog(TFBaseDialog):
    def __init__(self, parent=None):
        super().__init__(
            title="Select Language",
            layout_type=QGridLayout,
            parent=parent
        )

    def _setup_content(self) -> None:
        languages = [
            "English", "Spanish", "French", "German", "Italian",
            "Chinese", "Japanese", "Korean", "Russian", "Arabic",
            "Portuguese", "Dutch", "Swedish", "Greek", "Turkish",
            "Hindi", "Thai", "Vietnamese", "Polish", "Hebrew",
            "Bengali", "Persian", "Ukrainian", "Urdu", "Romanian",
            "Malay", "Hungarian", "Czech", "Danish", "Finnish"
        ]

        self.language_group = self.create_radio_group(
            name="language_selection",
            options=languages[:30],
            height=24,
            spacing=10
        )

        for i, radio in enumerate(self.language_group.radio_buttons):
            row = i // 5
            if row >= 2:
                row += 1
            col = i % 5
            self.main_layout.addWidget(radio, row, col)

    def validate(self) -> List[Tuple[Any, str]]:
        if not self.language_group.get_value():
            return [(self.language_group, "Please select a language")]
        return []

    def get_validated_data(self) -> Optional[str]:
        return self.language_group.get_value()
