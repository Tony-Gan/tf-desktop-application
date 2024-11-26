import os
from pathlib import Path
import random
import shutil
from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QFileDialog, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from implements.components.base_phase import BasePhase
from ui.components.tf_base_dialog import TFBaseDialog
from ui.components.tf_base_frame import TFBaseFrame
from ui.components.tf_font import Merriweather
from ui.tf_application import TFApplication


class Phase1(BasePhase):

    def _setup_content(self) -> None:
        super()._setup_content()

        self.upper_frame = UpperFrame(self)
        self.lower_frame = LowerFrame(self)

        self.contents_frame.main_layout.addWidget(self.upper_frame)
        self.contents_frame.main_layout.addWidget(self.lower_frame)

    def reset_contents(self):
        self.upper_frame.avatar_frame.avatar_label.clear()
        if hasattr(self.upper_frame.avatar_frame, '_current_avatar_path'):
            delattr(self.upper_frame.avatar_frame, '_current_avatar_path')
            
        player_info = self.upper_frame.player_info_group
        player_info.player_name_entry.set_value("")
        player_info.era_entry.set_value("None")
        
        char_info = self.upper_frame.character_info_group
        char_info.char_name_entry.set_value("")
        char_info.age_entry.set_value("")
        char_info.gender_entry.set_value("None")
        char_info.natinality_entry.set_value("")
        char_info.residence_entry.set_value("")
        char_info.birthpalce_entry.set_value("")
        char_info.language_own_entry.set_text("")

        mode = self.config.get("mode")
        if mode == "Destiny":
            if self.lower_frame.basic_stats_group:
                self.lower_frame.basic_stats_group.hide()
            if self.lower_frame.dice_result_frame:
                self.lower_frame.dice_result_frame.show()
        elif mode == "Points":
            if self.lower_frame.dice_result_frame:
                self.lower_frame.dice_result_frame.hide()
            if self.lower_frame.basic_stats_group:
                self.lower_frame.basic_stats_group.show()
                stats = self.lower_frame.basic_stats_group.stats_entries
                for entry in stats.values():
                    entry.set_value("0")
                self.lower_frame.basic_stats_group._update_derived_stats()

    def initialize(self):
        self.check_dependencies()

    def save_state(self):
        values = self.contents_frame.get_values()
        
        player_info = values.get('player_info_entry', {})
        if player_info:
            self.p_data['player_info'] = player_info
            
        character_info = values.get('character_info_entry', {})
        avatar_info = values.get('avatar_entry', {})
        if avatar_info.get('avatar_path'):
            character_info['avatar_path'] = avatar_info['avatar_path']
        if character_info:
            self.p_data['character_info'] = character_info
            
        basic_stats = values.get('basic_stats_entry', {})
        if basic_stats:
            self.p_data['basic_stats'] = basic_stats

    def restore_state(self):
        pass

    def check_dependencies(self):
        mode = self.config.get("mode", "Destiny")
        self.lower_frame.stats_info_group.update_from_config(self.config)
        self.lower_frame.handle_mode_change(mode, self.config)


class UpperFrame(TFBaseFrame):

    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedHeight(200)

        self.avatar_frame = AvatarFrame(self)
        self.player_info_group = PlayerInfoGroup(self)
        self.character_info_group = CharacterInfoGroup(self)

        self.add_child("avatar_entry", self.avatar_frame)
        self.add_child("player_info_entry", self.player_info_group)
        self.add_child("character_info_entry", self.character_info_group)


class LowerFrame(TFBaseFrame):

    def __init__(self,  parent=None):
        self.dice_result_frame = None
        self.selected_stats_index = -1
        super().__init__(QHBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.stats_info_group = StatsInformationGroup(self)
        self.basic_stats_group = BasicStatsGroup(self)

        self.basic_stats_group.hide()

        self.add_child("stats_info_entry", self.stats_info_group)
        self.add_child("basic_stats_entry", self.basic_stats_group)

    def handle_mode_change(self, mode: str, config: dict) -> None:
        if mode == "Points":
            if self.dice_result_frame:
                self.dice_result_frame.hide()
            self.basic_stats_group.show()
            for entry in self.basic_stats_group.stats_entries.values():
                entry.set_enable(True)
                entry.set_value("0")

        elif mode == "Destiny":
            self.basic_stats_group.hide()
            if self.dice_result_frame:
                self.dice_result_frame.show()
            else:
                dice_count = int(config.get("destiny", {}).get("dice_count", 3))
                self.dice_result_frame = DiceResultFrame(dice_count, self)
                self.dice_result_frame.values_changed.connect(self._handle_dice_result_confirmed)
                self.layout().addWidget(self.dice_result_frame)

    def _handle_dice_result_confirmed(self, values: dict) -> None:
        selected_stats = values.get("selected_stats", {})
        if selected_stats:
            self.selected_stats_index = next(
                (i for i, stats in enumerate(self.dice_result_frame.rolls_data)
                 if stats == selected_stats),
                -1
            )
            
            self.dice_result_frame.hide()
            self.basic_stats_group.show()
            
            for stat, value in selected_stats.items():
                entry = self.basic_stats_group.stats_entries.get(stat)
                if entry:
                    entry.set_value(str(value))
                    entry.set_enable(False)
                    
            self.basic_stats_group._update_derived_stats()


class AvatarFrame(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(layout_type=QVBoxLayout, radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedWidth(160)

        self.avatar_label = self.create_label(
            text="",
            alignment=Qt.AlignmentFlag.AlignCenter,
            height=100
        )
        self.avatar_label.setFixedWidth(100)
        self.avatar_label.setObjectName("avatar_label")
        self.avatar_label.setStyleSheet("""
            QLabel#avatar_label {
                border: 1px solid #666666;
                background-color: #242831;
                border-radius: 5px;
            }
        """)

        self.upload_button = self.create_button(
            name="avatar_upload",
            text="Update Avatar",
            width=120,
            height=24,
            font_size=10,
            enabled=True,
            tooltip="Click to upload a new avatar image",
            border_radius=5,
            on_clicked=self._on_avatar_upload
        )

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.upload_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addStretch()

    def _on_avatar_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Avatar Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if not file_path:
            return

        try:
            avatar_dir = Path("resources/data/coc/pcs/avatars")
            avatar_dir.mkdir(parents=True, exist_ok=True)

            avatar_filename = os.path.basename(file_path)
            avatar_path = avatar_dir / avatar_filename

            if avatar_path.exists():
                base, ext = os.path.splitext(avatar_filename)
                counter = 1
                while avatar_path.exists():
                    avatar_filename = f"{base}_{counter}{ext}"
                    avatar_path = avatar_dir / avatar_filename
                    counter += 1

            shutil.copy2(file_path, avatar_path)

            self._update_avatar_display(str(avatar_path))
            
            self._current_avatar_path = str(avatar_path.relative_to(Path.cwd()))
            self._emit_values_changed()
            
        except Exception as e:
            TFApplication.instance().show_message(str(e), 5000, "yellow")

    def _update_avatar_display(self, image_path: str):
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(
            self.avatar_label.size(),
            aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
            transformMode=Qt.TransformationMode.SmoothTransformation
        )
        self.avatar_label.setPixmap(scaled_pixmap)

    def get_values(self) -> dict:
        values = super().get_values()
        if hasattr(self, '_current_avatar_path'):
            values['avatar_path'] = self._current_avatar_path
        return values

    def update_component_value(self, name: str, value: str) -> None:
        super().update_component_value(name, value)
        if name == 'avatar_path' and value:
            self._current_avatar_path = value
            self._update_avatar_display(value)


class PlayerInfoGroup(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedWidth(180)

        self.player_name_entry = self.create_value_entry(
            name="player_name",
            label_text="Player Name:",
            label_size=90,
            value_size=70,
            height=24
        )

        self.era_entry = self.create_option_entry(
            name="era",
            label_text="Era:",
            options=["None", "1920s", "Modern"],
            current_value="None",
            label_size=90,
            value_size=70,
            height=24
        )

        self.main_layout.addWidget(self.player_name_entry)
        self.main_layout.addWidget(self.era_entry)


class CharacterInfoGroup(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(layout_type=QGridLayout, radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        self.char_name_entry = self.create_value_entry(
            name="char_name",
            label_text="Name:",
            label_size=80,
            value_size=75,
            height=24
        )

        self.age_entry = self.create_value_entry(
            name="age",
            label_text="Age:",
            label_size=75,
            value_size=75,
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
            label_size=75,
            value_size=75,
            height=24
        )

        self.natinality_entry = self.create_value_entry(
            name="nationality",
            label_text="Nationality:",
            label_size=80,
            value_size=75,
            height=24
        )

        self.residence_entry = self.create_value_entry(
            name="residence",
            label_text="Residence:",
            label_size=75,
            value_size=75,
            height=24
        )

        self.birthpalce_entry = self.create_value_entry(
            name="birthpalce",
            label_text="Birthplace:",
            label_size=75,
            value_size=75,
            height=24
        )

        self.language_own_entry = self.create_button_entry(
            name="language_own",
            label_text="Language:",
            label_size=80,
            button_text="Select",
            button_callback=self._on_language_select,
            button_size=75,
            entry_size=75,
            border_radius=5
        )
        self.language_own_entry.set_entry_enabled(False)

        self.main_layout.addWidget(self.char_name_entry, 0, 0)
        self.main_layout.addWidget(self.age_entry, 0, 1)
        self.main_layout.addWidget(self.gender_entry, 1, 1)
        self.main_layout.addWidget(self.natinality_entry, 1, 0)
        self.main_layout.addWidget(self.residence_entry, 0, 2)
        self.main_layout.addWidget(self.birthpalce_entry, 1, 2)
        self.main_layout.addWidget(self.language_own_entry, 2, 0, 1, 2)

    def _on_language_select(self):
        success, selected_language = LanguageSelectionDialog.get_input(self)
        if success and selected_language:
            self.language_own_entry.set_text(selected_language)


class StatsInformationGroup(TFBaseFrame):

    def __init__(self, parent=None):
        self.entries = {}
        super().__init__(radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedWidth(210)
    
        self.entries['dice_mode'] = self.create_value_entry(
            name="dice_mode",
            label_text="Dice Mode:",
            label_size=120,
            value_size=70,
            height=24,
            enable=False
        )
        self.main_layout.addWidget(self.entries['dice_mode'])

    def update_from_config(self, config: dict) -> None:
        for name, entry in list(self.entries.items()):
            if name != 'dice_mode':
                try:
                    entry.blockSignals(True)
                    if name in self._components:
                        del self._components[name]
                    self.main_layout.removeWidget(entry)
                    del self.entries[name]
                    entry.deleteLater()
                except RuntimeError:
                    continue

        mode = config.get("mode", "Destiny")
        self.entries['dice_mode'].blockSignals(True)
        self.entries['dice_mode'].set_value(mode)
        self.entries['dice_mode'].blockSignals(False)

        if mode == "Points":
            points_config = config.get("points", {})
            available_points = points_config.get("available", 480)
            self.parent.basic_stats_group.total_points = available_points
            
            self.entries['points_available'] = self.create_value_entry(
                name="points_available",
                label_text="Points Available:",
                label_size=120,
                value_text=str(available_points),
                value_size=70,
                height=24,
                enable=False
            )

            stats_range = f"{points_config.get('lower_limit', 30)}-{points_config.get('upper_limit', 80)}"
            self.entries['stats_range'] = self.create_value_entry(
                name="stats_range",
                label_text="Stats Range:",
                label_size=120,
                value_size=70,
                value_text=stats_range,
                height=24,
                enable=False
            )

            custom_luck = "Yes" if points_config.get("custom_luck", False) else "No"
            self.entries['allow_custom_luck'] = self.create_value_entry(
                name="allow_custom_luck",
                label_text="Custom Luck:",
                label_size=120,
                value_size=70,
                value_text=custom_luck,
                height=24,
                enable=False
            )

            self.main_layout.addWidget(self.entries['points_available'])
            self.main_layout.addWidget(self.entries['stats_range'])
            self.main_layout.addWidget(self.entries['allow_custom_luck'])

        elif mode == "Destiny":
            destiny_config = config.get("destiny", {})
            
            self.entries['dice_count'] = self.create_value_entry(
                name="dice_count",
                label_text="Dice Count:",
                label_size=120,
                value_size=70,
                value_text=str(destiny_config.get("dice_count", "3")),
                height=24,
                enable=False
            )

            allow_exchange = destiny_config.get("allow_exchange", False)
            self.entries['allow_exchange'] = self.create_value_entry(
                name="allow_stats_exchange",
                label_text="Stats Exchange:",
                label_size=120,
                value_size=70,
                value_text="Yes" if allow_exchange else "No",
                height=24,
                enable=False
            )

            exchange_count = destiny_config.get("exchange_count", "1") if allow_exchange else "N/A"
            self.entries['exchange_count'] = self.create_value_entry(
                name="exchange_count",
                label_text="Exchange Times:",
                label_size=120,
                value_size=70,
                value_text=exchange_count,
                height=24,
                enable=False
            )

            self.main_layout.addWidget(self.entries['dice_count'])
            self.main_layout.addWidget(self.entries['allow_exchange'])
            self.main_layout.addWidget(self.entries['exchange_count'])


class BasicStatsGroup(TFBaseFrame):
    
    def __init__(self, parent=None):
        self.stats_entries = {}
        self.derived_entries = {}
        self.total_points = 0
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
            entry.value_changed.connect(self._update_derived_stats)
            entry.value_changed.connect(self._update_points_available)
            self.stats_entries[stat] = entry
            self.main_layout.addWidget(entry, row, col)


        derived_stats = [
            ('HP', 'HP'),
            ('MP', 'MP'),
            ('SAN', 'San'),
            ('MOV', 'Move'),
            ('DB', 'DB'),
            ('Build', 'Build')
        ]

        for i, (stat_key, label_text) in enumerate(derived_stats):
            row = i // 2
            col = 3 + (i % 2)
            entry = self.create_value_entry(
                name=label_text.lower(),
                label_text=label_text + ":",
                value_text="N/A",
                value_size=40,
                label_size=40,
                number_only=True,
                enable=False
            )
            self.derived_entries[stat_key] = entry
            self.main_layout.addWidget(entry, row, col)

    def _get_stat_value(self, stat: str) -> int:
        try:
            value = self.stats_entries[stat].get_value()
            return int(value) if value else 0
        except (ValueError, KeyError):
            return 0
        
    def _update_derived_stats(self) -> None:
        str_val = self._get_stat_value('STR')
        con_val = self._get_stat_value('CON')
        siz_val = self._get_stat_value('SIZ')
        dex_val = self._get_stat_value('DEX')
        pow_val = self._get_stat_value('POW')

        if self.stats_entries['CON'].get_value() and self.stats_entries['SIZ'].get_value():
            hp = (con_val + siz_val) // 10
            self.derived_entries['HP'].set_value(str(hp))
        else:
            self.derived_entries['HP'].set_value("N/A")

        if self.stats_entries['POW'].get_value():
            mp = pow_val // 5
            self.derived_entries['MP'].set_value(str(mp))
        else:
            self.derived_entries['MP'].set_value("N/A")

        if self.stats_entries['POW'].get_value():
            self.derived_entries['SAN'].set_value(str(pow_val))
        else:
            self.derived_entries['SAN'].set_value("N/A")

        if (self.stats_entries['STR'].get_value() and 
            self.stats_entries['DEX'].get_value() and 
            self.stats_entries['SIZ'].get_value()):
            mov = self._calculate_mov(str_val, dex_val, siz_val)
            self.derived_entries['MOV'].set_value(mov)
        else:
            self.derived_entries['MOV'].set_value("N/A")

        if self.stats_entries['STR'].get_value() and self.stats_entries['SIZ'].get_value():
            db, build = self._calculate_db_and_build(str_val, siz_val)
            self.derived_entries['DB'].set_value(db)
            self.derived_entries['Build'].set_value(build)
        else:
            self.derived_entries['DB'].set_value("N/A")
            self.derived_entries['Build'].set_value("N/A")

    def _calculate_mov(self, str_val: int, dex_val: int, siz_val: int) -> str:
        if not all([str_val, dex_val, siz_val]):
            return "N/A"
            
        if str_val >= siz_val and dex_val >= siz_val:
            return "9"
        elif str_val <= siz_val and dex_val <= siz_val:
            return "7"
        else:
            return "8"
        
    def _calculate_db_and_build(self, str_val: int, siz_val: int) -> tuple[str, str]:
        if not all([str_val, siz_val]):
            return "N/A", "N/A"
            
        total = str_val + siz_val
        
        if total < 65:
            return "-2", "-2"
        elif total < 85:
            return "-1", "-1"
        elif total < 125:
            return "0", "0"
        elif total < 165:
            return "+1d4", "+1"
        elif total < 205:
            return "+1d6", "+2"
        elif total < 285:
            return "+2d6", "+3"
        elif total < 365:
            return "+3d6", "+4"
        elif total < 445:
            return "+4d6", "+5"
        else:
            return "+5d6", "+6"
        
    def _update_points_available(self) -> None:
        if self.parent.stats_info_group.entries['dice_mode'].get_value() != "Points":
            return
            
        total_used = sum(self._get_stat_value(stat) for stat in self.stats_entries)
        
        points_remaining = self.total_points - total_used
        points_entry = self.parent.stats_info_group.entries.get('points_available')
        points_entry.set_value(str(points_remaining))


class DiceResultFrame(TFBaseFrame):
    
    def __init__(self, dice_count: int, parent=None):
        self.dice_count = dice_count
        self.rolls_data: List[Dict[str, int]] = []
        super().__init__(QVBoxLayout, radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        self.rolls_data = self._generate_rolls()
        
        options = []
        for _, roll in enumerate(self.rolls_data, 1):
            base_stats = []
            total_without_luck = 0
            for stat, value in roll.items():
                if stat != 'LUK':
                    base_stats.append(f"{stat}:{value}")
                    total_without_luck += value
            total_with_luck = total_without_luck + roll['LUK']
            
            base_stats_text = " ".join(base_stats)
            stats_text = f"{base_stats_text}\nTotals(base/with luck): {total_without_luck}/{total_with_luck}"
            options.append(stats_text)

        self.radio_group = self.create_radio_group(
            name="dice_results",
            options=options,
            label_font=Merriweather,
            spacing=5
        )
        
        for btn in self.radio_group.radio_buttons:
            btn.value_changed.connect(self._on_selection_changed)
        
        self.main_layout.addWidget(self.radio_group)

    def _on_selection_changed(self, checked: bool) -> None:
        if checked:
            selected_index = self.radio_group.radio_buttons.index(
                self.sender()
            )
            selected_stats = self.rolls_data[selected_index]
            self.values_changed.emit({"selected_stats": selected_stats})

    def _generate_rolls(self) -> List[Dict[str, int]]:
        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK']
        rolls = []
        
        for _ in range(self.dice_count):
            roll = {}
            for stat in stats:
                roll[stat] = self._roll_stat(stat)
            rolls.append(roll)
            
        return rolls

    def _roll_stat(self, stat_type: str) -> int:
        if stat_type in ['SIZ', 'INT', 'EDU']:
            result = (sum(random.randint(1, 6) for _ in range(2)) + 6) * 5
        else:
            result = sum(random.randint(1, 6) for _ in range(3)) * 5
        return result
        
    def _on_confirm_clicked(self) -> None:
        selected_index = self.radio_group.radio_buttons.index(
            next(btn for btn in self.radio_group.radio_buttons if btn.is_checked())
        )
        if selected_index >= 0:
            selected_stats = self.rolls_data[selected_index]
            self.values_changed.emit({"selected_stats": selected_stats})

    def get_values(self) -> dict:
        values = super().get_values()
        if hasattr(self, 'radio_group'):
            selected_index = next(
                (i for i, btn in enumerate(self.radio_group.radio_buttons) if btn.is_checked()),
                -1
            )
            if selected_index >= 0:
                values["selected_stats"] = self.rolls_data[selected_index]
        return values


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