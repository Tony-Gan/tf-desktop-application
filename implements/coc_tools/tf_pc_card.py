import os
import json
import copy
from typing import Dict, Tuple
from datetime import datetime, timezone

from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox,
                             QPushButton, QTextEdit, QFileDialog, QWidget, 
                             QLineEdit, QScrollArea, QGridLayout, QDialog)
from PyQt6.QtCore import Qt, QRegularExpression, QTimer
from PyQt6.QtGui import QPixmap, QFont, QKeySequence, QShortcut, QRegularExpressionValidator

from core.windows.tf_draggable_window import TFDraggableWindow
from utils.registry.tf_tool_matadata import TFToolMetadata
from ui.components.tf_settings_widget import MenuSection
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_separator import TFSeparator
from ui.components.tf_number_receiver import TFNumberReceiver
from ui.components.tf_computing_dialog import TFComputingDialog
from utils.helper import format_datetime, resource_path
from utils.validator.tf_validator import TFValidator
from utils.validator.tf_validation_rules import TFValidationRule

LABEL_FONT = QFont("Inconsolata SemiBold")
LABEL_FONT.setPointSize(10)

EDIT_FONT = QFont("Inconsolatav")
EDIT_FONT.setPointSize(10)

GROUPED_SKILLS = {'art', 'science', 'survival', 'pilot'}
SPECIAL_SKILLS = {'fighting', 'firearms'}

DEFAULT_SKILLS = {
    "accounting": 5,
    "anthropology": 1,
    "appraise": 5,
    "archaeology": 1,
    "art:all": 5,
    "charm": 15,
    "climb": 20,
    "credit_rating": 0,
    "cthulhu_mythos": 0,
    "disguise": 5,
    "dodge": 0,
    "drive_auto": 20,
    "electrical_repair": 10,
    "electronics": 1,
    "fast_talk": 5,
    "fighting:brawl": 25,
    "fighting:chainsaw": 10,
    "fighting:flail": 10,
    "fighting:garrote": 15,
    "fighting:sword": 20,
    "fighting:whip": 5,
    "firearms:handgun": 20,
    "firearms:heavy_weapons": 10,
    "firearms:rifle": 25,
    "firearms:shotgun": 25,
    "firearms:smg": 15,
    "first_aid": 30,
    "history": 5,
    "intimidate": 15,
    "jump": 20,
    "language": 0,
    "language:all": 1,
    "law": 5,
    "library_use": 20,
    "listen": 20,
    "locksmith": 1,
    "mechanical_repair": 10,
    "medicine": 1,
    "natural_world": 10,
    "navigate": 10,
    "occult": 5,
    "operate_heavy_machinery": 1,
    "persuade": 10,
    "pilot:all": 1,
    "psychoanalysis": 1,
    "psychology": 10,
    "ride": 5,
    "science:all": 1,
    "sleight_of_hand": 10,
    "spot_hidden": 25,
    "stealth": 20,
    "survival:all": 10,
    "swim": 20,
    "throw": 20,
    "track": 10
}

class TFPcCard(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="pc_card",
        menu_path="Tools/COC",
        window_title="PC Card",
        menu_title="Add PC Card",
        window_size=(600, 1080),
        description="PC information card",
        max_instances=6
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pc_data = None
        self.current_file_path = None
        self.has_unsaved_changes = False

        self.validator = TFValidator()
        self.validator.add_rules(CharacterRules.create_rules())
        self.validator.add_custom_validator('hp_san_relation', CharacterRules.validate_hp_san_relation)
        self.validator.add_custom_validator('db_build_relation', CharacterRules.validate_db_build_relation)

        self._setup_menu()
        self._setup_shortcuts()

    def initialize_window(self):
        main_layout = QVBoxLayout(self.content_container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        upper_frame = QFrame()
        upper_frame.setObjectName("upper_container")
        upper_frame.setFixedHeight(380)
        upper_frame.setFrameShape(QFrame.Shape.Box)
        main_layout.addWidget(upper_frame)

        upper_layout = QHBoxLayout(upper_frame)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(10)

        self.left_info_panel = LeftInfoPanel()
        self.left_info_panel.setObjectName("section_frame")
        self.left_info_panel.setFrameShape(QFrame.Shape.Box)
        self.left_info_panel.setFixedWidth(300)
        upper_layout.addWidget(self.left_info_panel)

        self.pc_info_panel = PCInfoPanel()
        self.pc_info_panel.setObjectName("section_frame")
        self.pc_info_panel.setFrameShape(QFrame.Shape.Box)
        upper_layout.addWidget(self.pc_info_panel)

        self.lower_panel = LowerPanel(self)
        self.lower_panel.setObjectName("section_frame")
        self.lower_panel.setFrameShape(QFrame.Shape.Box)
        main_layout.addWidget(self.lower_panel)

    def _setup_menu(self):
        self.load_action = self.menu_button.add_action(
            "Load Character", 
            self._load_character_file, 
            MenuSection.CUSTOM
        )
        self.toggle_edit_action = self.menu_button.add_action(
            "Toggle Editing",
            self._toggle_editing,
            MenuSection.CUSTOM,
            checkable=True
        )

    def _load_character_file(self):
        if self.toggle_edit_action.isChecked() and self.has_unsaved_changes:
            response = self.app.show_question(
                "Save Changes?",
                "Do you want to save the changes you made?",
                buttons=["Save", "Don't Save", "Cancel"]
            )
            if response == "Cancel":
                return
            elif response == "Save":
                try:
                    self._save_current_data()
                    if self.has_unsaved_changes:
                        return
                except Exception as e:
                    self.app.show_error("Save Error", f"Failed to save: {str(e)}")
                    return
        
        if self.toggle_edit_action.isChecked():
            self._disconnect_change_signals()
            self.toggle_edit_action.setChecked(False)
            self._update_panel_edit_state(self.left_info_panel, False)
            self._update_panel_edit_state(self.pc_info_panel, False)
            self._update_panel_edit_state(self.lower_panel, False)
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Character File",
            resource_path("resources/data/coc/pcs/"),
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            required_sections = {'metadata', 'personal_info', 'basic_stats', 'status', 'skills'}
            if not all(section in data for section in required_sections):
                missing_sections = required_sections - set(data.keys())
                self.app.show_error(
                    "Invalid File Format",
                    f"Missing sections: {', '.join(missing_sections)}"
                )
                return

            self.pc_data = data
            self.current_file_path = file_path
            self.has_unsaved_changes = False
            self.app.show_message("Character data loaded successfully", 2000, 'green')

            self.title = self.pc_data['personal_info']['name']
            
            self._update_ui()
            
        except json.JSONDecodeError:
            self.app.show_error("Invalid File", "The selected file is not a valid JSON file")
        except Exception as e:
            self.app.show_error("Load Error", f"Error loading file: {str(e)}")

    def _toggle_editing(self):
        action = self.toggle_edit_action
        is_editing = action.isChecked()
        
        if self.pc_data is None:
            action.setChecked(False)
            self.app.show_message("Please load a character file first", 2000, 'yellow')
            return

        if not is_editing and self.has_unsaved_changes:
            skills_to_remove = []
            for skill_name, value in self.pc_data['skills'].items():
                base_skill = skill_name.split(':')[0] if ':' in skill_name else skill_name
                if base_skill in GROUPED_SKILLS:
                    default_value = DEFAULT_SKILLS.get(f"{base_skill}:all", 0)
                else:
                    default_value = DEFAULT_SKILLS.get(skill_name, 0)
                    
                if value == default_value:
                    skills_to_remove.append(skill_name)

            if skills_to_remove:
                try:
                    with open(self.current_file_path, 'r+', encoding='utf-8') as file:
                        data = json.load(file)
                        for skill_name in skills_to_remove:
                            data['skills'].pop(skill_name, None)
                            self.pc_data['skills'].pop(skill_name, None)
                        
                        file.seek(0)
                        json.dump(data, file, indent=4, ensure_ascii=False)
                        file.truncate()

                    self.lower_panel.skills_grid.modified_skills = self.pc_data['skills']
                    self.lower_panel.skills_grid.update_skills(self.pc_data['skills'])
                    
                except Exception as e:
                    self.app.show_error("Save Error", f"Failed to update skills: {str(e)}")
                    return

            if not self._save_current_data():
                action.setChecked(True)
                return

        self._update_panel_edit_state(self.left_info_panel, is_editing)
        self._update_panel_edit_state(self.pc_info_panel, is_editing)
        self._update_panel_edit_state(self.lower_panel, is_editing)
        self.lower_panel.notes_panel.set_edit_enabled(is_editing)
        self.lower_panel.skills_grid.set_edit_mode(is_editing)

        if is_editing:
            self._connect_change_signals()
        else:
            self._disconnect_change_signals()
            self.has_unsaved_changes = False

        message = "Editing mode enabled" if is_editing else "Editing mode disabled"
        self.app.show_message(message, 2000, 'green')

    def _on_text_changed(self):
        self.has_unsaved_changes = True

    def _connect_change_signals(self):
        self._manage_text_changed_signals(connect=True)

    def _disconnect_change_signals(self):
        self._manage_text_changed_signals(connect=False)

    def _manage_text_changed_signals(self, connect=True):
        for panel in [self.left_info_panel, self.pc_info_panel, self.lower_panel]:
            for line_edit in panel.findChildren(QLineEdit):
                if connect:
                    line_edit.textChanged.connect(self._on_text_changed)
                else:
                    try:
                        line_edit.textChanged.disconnect()
                    except TypeError:
                        pass

        if connect:
            self.lower_panel.notes_panel.notes_edit.textChanged.connect(self._on_text_changed)
        else:
            try:
                self.lower_panel.notes_panel.notes_edit.textChanged.disconnect()
            except TypeError:
                pass

    def _update_panel_edit_state(self, panel, enabled):
        for line_edit in panel.findChildren(QLineEdit):
            line_edit.setEnabled(enabled)

    def _save_current_data(self):
        try:
            updated_data = copy.deepcopy(self.pc_data)

            metadata_fields = {
                'player_name': str,
                'era': str,
                'campaign_date': str
            }
            for field, type_conv in metadata_fields.items():
                edit = self.pc_info_panel.findChild(QLineEdit, f"edit_{field}")
                if edit and edit.text().strip():
                    updated_data['metadata'][field] = type_conv(edit.text())
            
            personal_fields = {
                'name': str,
                'age': int,
                'occupation': str,
                'residence': str,
                'birthplace': str,
                'nationality': str
            }
            for field, type_conv in personal_fields.items():
                edit = self.left_info_panel.findChild(QLineEdit, f"edit_{field}")
                if edit and edit.text().strip():
                    try:
                        updated_data['personal_info'][field] = type_conv(edit.text())
                    except ValueError as e:
                        self.app.show_error(
                            "Invalid Input",
                            f"Invalid value for {field}: {str(e)}"
                        )
                        return False
            
            basic_stats = {
                'strength': int,
                'constitution': int,
                'size': int,
                'dexterity': int,
                'appearance': int,
                'intelligence': int,
                'power': int,
                'education': int,
                'luck': int
            }
            for stat, type_conv in basic_stats.items():
                edit = self.pc_info_panel.findChild(QLineEdit, f"edit_{stat}")
                if edit and edit.text().strip():
                    try:
                        updated_data['basic_stats'][stat] = type_conv(edit.text())
                    except ValueError as e:
                        self.app.show_error(
                            "Invalid Input",
                            f"Invalid value for {stat}: {str(e)}"
                        )
                        return False
            
            status_fields = {
                'hp_current': int,
                'hp_max': int,
                'mp_current': int,
                'mp_max': int,
                'san_current': int,
                'san_max': int,
                'movement_rate': int,
                'damage_bonus': str,
                'build': int
            }
            for field, type_conv in status_fields.items():
                edit = self.lower_panel.findChild(QLineEdit, f"edit_{field}")
                if edit and edit.text().strip():
                    try:
                        updated_data['status'][field] = type_conv(edit.text())
                    except ValueError as e:
                        self.app.show_error(
                            "Invalid Input",
                            f"Invalid value for {field}: {str(e)}"
                        )
                        return False
            
            for skill_entry in self.lower_panel.skills_grid.findChildren(TFValueEntry):
                skill_name = skill_entry.label.text().lower()
                skill_name = self._convert_display_to_storage_name(skill_name)
                
                if "_-_others" in skill_name:
                    continue
                    
                value = skill_entry.get_value()
                if value and value.strip():
                    try:
                        value = int(value)
                        base_skill = skill_name.split(':')[0] if ':' in skill_name else skill_name
                        if base_skill in GROUPED_SKILLS:
                            default_value = DEFAULT_SKILLS.get(f"{base_skill}:all", 0)
                        else:
                            default_value = DEFAULT_SKILLS.get(skill_name, 0)
                        
                        if value != default_value:
                            updated_data['skills'][skill_name] = value
                        elif skill_name in updated_data['skills']:
                            del updated_data['skills'][skill_name]
                            
                    except ValueError as e:
                        self.app.show_error(
                            "Invalid Input",
                            f"Invalid value for skill {skill_name}: {str(e)}"
                        )
                        return False
                    
            for item_entry in self.lower_panel.items_panel.findChildren(TFValueEntry):
                value = item_entry.get_value()
                display_name = item_entry.label.text().lower()
                item_name = '_'.join(display_name.split())
                
                for category in ['weapons', 'armours', 'others']:
                    if category in updated_data['items']:
                        if isinstance(updated_data['items'][category], dict):
                            if item_name in updated_data['items'][category]:
                                updated_data['items'][category][item_name]['notes'] = value
                                break
                    
            notes_text = self.lower_panel.notes_panel.notes_edit.toPlainText()
            updated_data['notes'] = notes_text
                    
            errors = self.validator.validate_dict(updated_data, is_new=False)

            for stat in ['hp', 'mp', 'san']:
                current = updated_data['status'][f'{stat}_current']
                max_ = updated_data['status'][f'{stat}_max']
                is_valid, message = CharacterRules.validate_hp_san_relation(current, max_, stat.upper())
                if not is_valid:
                    errors.append(message)

            db = updated_data['status']['damage_bonus']
            build = updated_data['status']['build']
            is_valid, message = CharacterRules.validate_db_build_relation(db, build)
            if not is_valid:
                errors.append(message)

            if errors:
                error_msg = "\n".join(errors)
                self.app.show_error("Validation Error", f"Please fix the following issues:\n{error_msg}")
                return False
            
            self.pc_data = updated_data
            
            self.pc_data['metadata']['updated_at'] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            self._safe_save_to_file(self.pc_data, self.current_file_path)
            
            self.has_unsaved_changes = False
            self.app.show_message("Character data saved successfully", 2000, 'green')
            return True
            
        except IOError as e:
            self.app.show_error("Save Error", f"Failed to write file: {str(e)}")
        except Exception as e:
            self.app.show_error("Save Error", f"Unexpected error while saving: {str(e)}")

    def _safe_save_to_file(self, data, filepath):
        temp_file = filepath + '.tmp'
        backup_file = filepath + '.bak'
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            if os.path.exists(filepath):
                try:
                    os.replace(filepath, backup_file)
                except OSError:
                    os.remove(temp_file)
                    raise
            
            try:
                os.replace(temp_file, filepath)
            except OSError:
                if os.path.exists(backup_file):
                    os.replace(backup_file, filepath)
                raise
            
            if os.path.exists(backup_file):
                os.remove(backup_file)
                
        except Exception as e:
            for f in [temp_file, backup_file]:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except OSError:
                        pass
            raise e

    def _convert_display_to_storage_name(self, display_name):
        original_name = self.lower_panel.skills_grid.original_skill_names.get(display_name.lower())
        if original_name:
            return original_name
        
        for storage_name, abbr in SkillsGrid.SKILL_ABBREVIATIONS.items():
            if abbr.lower() == display_name.lower():
                return storage_name
        
        return display_name.lower().replace(' ', '_')

    def _update_ui(self):
        self._setup_avator()
        self.pc_info_panel.update_data(self.pc_data)
        self.left_info_panel.update_data(self.pc_data)
        self.lower_panel.update_data(self.pc_data)

    def _setup_avator(self):
        avatar_path = resource_path(self.pc_data.get('metadata', {}).get('avatar_file'))
        if not avatar_path:
            self.app.show_message("No avatar path found in character data", 2000, 'yellow')
            return
            
        image_container = self.findChild(QLabel, "image_container")
        image_label = image_container.findChild(QLabel, "pc_image")
            
        try:
            image_container = self.findChild(QLabel, "image_container")
            image_label = image_container.findChild(QLabel, "pc_image")
            
            pixmap = QPixmap(avatar_path)
            if pixmap.isNull():
                self.app.show_message("Avatar image cannot be loaded", 2000, 'yellow')
                return
                
            image_label.setPixmap(pixmap)
            
        except FileNotFoundError:
            self.app.show_message("Avatar file not found in specified path", 2000, 'red')

        except Exception as e:
            self.app.logger.error(f"Unexpected error while loading avatar: {str(e)}")
            self.app.show_message("Unexpected error occurred while loading avatar", 2000, 'red')

    def _setup_shortcuts(self):
        self.save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        self.save_shortcut.setEnabled(False)
        self.save_shortcut.activated.connect(self._on_save_shortcut)

        self.edit_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.edit_shortcut.setEnabled(False)
        self.edit_shortcut.activated.connect(self._on_edit_shortcut)

        self.open_shortcut = QShortcut(QKeySequence.StandardKey.Open, self)
        self.open_shortcut.setEnabled(False)
        self.open_shortcut.activated.connect(self._load_character_file)

    @property
    def focused(self) -> bool:
        return super().focused

    @focused.setter
    def focused(self, value: bool):
        super(TFPcCard, self.__class__).focused.fset(self, value)
        self.save_shortcut.setEnabled(value)
        self.edit_shortcut.setEnabled(value)
        self.open_shortcut.setEnabled(value)

    def _on_save_shortcut(self):
        if self.toggle_edit_action.isChecked():
            self.toggle_edit_action.trigger()

    def _on_edit_shortcut(self):
        if not self.toggle_edit_action.isChecked():
            self.toggle_edit_action.trigger()

    def closeEvent(self, event):
        edit_action = self.menu_button.actions[MenuSection.CUSTOM][1]
        if edit_action.isChecked() and self.has_unsaved_changes:
            response = self.app.show_question(
                "Save Changes?",
                "Do you want to save the changes you made?",
                buttons=["Save", "Don't Save", "Cancel"]
            )
            if response == "Cancel":
                event.ignore()
                return
            elif response == "Save":
                try:
                    if not self._save_current_data():
                        event.ignore()
                        return
                except Exception as e:
                    self.app.show_error("Save Error", f"Failed to save: {str(e)}")
                    event.ignore()
                    return

        self.closed.emit(self)
        super().closeEvent(event)

class PCInfoPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        metadata_widget = self._create_metadata_section()
        main_layout.addWidget(metadata_widget)

        main_layout.addWidget(TFSeparator.horizontal())

        basic_stats_widget = self._create_basic_stats_section()
        main_layout.addWidget(basic_stats_widget)

        main_layout.addStretch()
    
    def _create_metadata_section(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        fields = [
            ("Player Name:", "player_name"),
            ("Campaign Date:", "campaign_date"),
            ("Era:", "era"),
            ("Created At:", "created_at"),
            ("Updated At:", "updated_at")
        ]
        
        for label_text, field_name in fields:
            entry = TFValueEntry(label_text=label_text, label_size=100, value_size=120, object_name=f"edit_{field_name}", alignment=Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(entry)
        
        return widget
    
    def _create_basic_stats_section(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        stats = [
            ("STR", "strength"), ("CON", "constitution"),
            ("SIZ", "size"), ("DEX", "dexterity"),
            ("APP", "appearance"), ("INT", "intelligence"),
            ("POW", "power"), ("EDU", "education"),
            ("LUK", "luck"), (None, None)
        ]
        
        for i in range(0, len(stats), 2):
            row_layout = QHBoxLayout()
            
            if stats[i][0] is not None:
                entry1 = TFValueEntry(
                    label_text=stats[i][0], 
                    label_size=40, 
                    value_size=50, 
                    object_name=f"edit_{stats[i][1]}",
                    number_only=True,
                    allow_decimal=False
                )
                row_layout.addWidget(entry1)
                row_layout.addSpacing(20)
            
            if i + 1 < len(stats) and stats[i + 1][0] is not None:
                entry2 = TFValueEntry(
                    label_text=stats[i + 1][0], 
                    label_size=40, 
                    value_size=50, 
                    object_name=f"edit_{stats[i + 1][1]}",
                    number_only=True,
                    allow_decimal=False
                )
                row_layout.addWidget(entry2)
            
            row_layout.addStretch()
            layout.addLayout(row_layout)
        
        return widget
    
    def update_data(self, pc_data):
        metadata = pc_data.get('metadata', {})
        
        for field in ['player_name', 'era']:
            edit = self.findChild(QLineEdit, f"edit_{field}")
            if edit:
                edit.setText(str(metadata.get(field, '')))
        
        campaign_date = self.findChild(QLineEdit, "edit_campaign_date")
        if campaign_date:
            date_str = metadata.get('campaign_date', '')
            campaign_date.setText(format_datetime(date_str,input_format="%Y-%m-%d",default_value=date_str))
        
        created_at = self.findChild(QLineEdit, "edit_created_at")
        if created_at:
            created_at.setText(format_datetime(metadata.get('created_at', ''), show_time=True))
        
        updated_at = self.findChild(QLineEdit, "edit_updated_at")
        if updated_at:
            updated_at.setText(format_datetime(metadata.get('updated_at', ''), show_time=True))
        
        basic_stats = pc_data.get('basic_stats', {})
        for stat in ['strength', 'constitution',
                    'size', 'dexterity',
                    'appearance', 'intelligence',
                    'power', 'education',
                    'luck']:
            edit = self.findChild(QLineEdit, f"edit_{stat}")
            if edit:
                edit.setText(str(basic_stats.get(stat, '')))

class LeftInfoPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        main_layout.addWidget(self._create_avatar_section())
        main_layout.addWidget(TFSeparator.horizontal())
        main_layout.addWidget(self._create_personal_info_section())

    def _create_avatar_section(self):
        widget = QFrame()
        widget.setFixedHeight(150)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        image_container = QLabel()
        image_container.setObjectName("image_container")
        image_container.setFixedSize(130, 130)
        image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image_label = QLabel(image_container)
        image_label.setObjectName("pc_image")
        image_label.setFixedSize(130, 130)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setScaledContents(True)

        layout.addWidget(image_container, alignment=Qt.AlignmentFlag.AlignCenter)
        return widget

    def _create_personal_info_section(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        fields = [
            ("Name:", "name"),
            ("Age:", "age"),
            ("Occupation:", "occupation"),
            ("Residence:", "residence"),
            ("Birthplace:", "birthplace"),
            ("Nationality:", "nationality")
        ]
        
        for label_text, field_name in fields:
            if label_text != 'Age':
                entry = TFValueEntry(
                    label_text=label_text, 
                    label_size=100, 
                    value_size=160, 
                    object_name=f"edit_{field_name}", 
                    alignment=Qt.AlignmentFlag.AlignLeft
                )
            else:
                entry = TFValueEntry(
                    label_text=label_text, 
                    label_size=100, 
                    value_size=160, 
                    object_name=f"edit_{field_name}", 
                    alignment=Qt.AlignmentFlag.AlignLeft,
                    number_only=True,
                    allow_decimal=False
                )
            layout.addWidget(entry)
        
        return widget

    def update_data(self, pc_data):
        personal_info = pc_data.get('personal_info', {})
        for field in ['name', 'age', 'occupation', 
                    'residence', 'birthplace', 
                    'nationality']:
            edit = self.findChild(QLineEdit, f"edit_{field}")
            if edit:
                edit.setText(str(personal_info.get(field, '')))

class LowerPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        self.setObjectName("section_frame")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setObjectName("transparent_scroll")
        scroll_area.viewport().setObjectName("transparent_viewport")
        
        container = QWidget()
        container.setObjectName("transparent_container")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(10)
        
        self.status_bar = StatusBar()
        container_layout.addWidget(self.status_bar)
        
        self.skills_grid = SkillsGrid(self)
        container_layout.addWidget(self.skills_grid)
        
        self.items_panel = ItemsPanel(self)
        container_layout.addWidget(self.items_panel)
        
        self.notes_panel = NotesPanel(self)
        container_layout.addWidget(self.notes_panel)
        
        container_layout.addStretch()
        
        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)
    
    def update_data(self, pc_data):
        self.status_bar.update_data(pc_data.get('status', {}))
        self.skills_grid.update_skills(pc_data.get('skills', {}))
        self.items_panel.update_items(pc_data.get('items', {}))
        self.notes_panel.update_notes(pc_data.get('notes', ''))

class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(536)
        self.setFixedHeight(40)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        stats = [
            ("HP", "hp"), ("MP", "mp"), ("SAN", "san"),
            ("Move", "movement_rate"), ("DB", "damage_bonus"), ("Build", "build")
        ]
        
        for i, (label_text, base_name) in enumerate(stats):
            container = QWidget()
            if label_text in ["HP", "MP", "SAN"]:
                self._create_combined_stat(container, label_text, base_name)
            else:
                self._create_single_stat(container, label_text, base_name)
            
            main_layout.addWidget(container, 0, i)
    
    def _create_combined_stat(self, container, label_text, base_name):
        layout = QHBoxLayout(container)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(2)

        label = QLabel(label_text)
        label.setFont(LABEL_FONT)
        label.setFixedWidth(24)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        current = TFNumberReceiver(text="", alignment=Qt.AlignmentFlag.AlignCenter, font=EDIT_FONT, allow_decimal=False, allow_negative=False)
        current.setObjectName(f"edit_{base_name}_current")
        current.setFixedWidth(26)
        current.setStyleSheet("QLineEdit { padding: 1px; }")
        current.setEnabled(False)

        separator = QLabel("/")
        separator.setFont(LABEL_FONT)
        separator.setFixedWidth(5)
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)

        maximum = TFNumberReceiver(text="", alignment=Qt.AlignmentFlag.AlignCenter, font=EDIT_FONT, allow_decimal=False, allow_negative=False)
        maximum.setObjectName(f"edit_{base_name}_max")
        maximum.setFixedWidth(26)
        maximum.setStyleSheet("QLineEdit { padding: 1px; }")
        maximum.setEnabled(False)

        layout.addWidget(label)
        layout.addWidget(current)
        layout.addWidget(separator)
        layout.addWidget(maximum)
        layout.addStretch()

    def _create_single_stat(self, container, label_text, field_name):
        layout = QHBoxLayout(container)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(2)
        if label_text != 'DB':
            entry = TFValueEntry(
                label_text=label_text, 
                label_size=40, 
                value_size=40, 
                object_name=f"edit_{field_name}",
                number_only=True,
                allow_decimal=False,
            )
        elif label_text == 'Build':
            entry = TFValueEntry(
                label_text=label_text, 
                label_size=40, 
                value_size=40, 
                object_name=f"edit_{field_name}",
                number_only=True,
                allow_decimal=False,
                allow_negative=True
            )
        else:
            entry = TFValueEntry(
                label_text=label_text, 
                label_size=40, 
                value_size=40, 
                object_name=f"edit_{field_name}"
            )
        
        layout.addWidget(entry)

    def update_data(self, status_data):
        for base in ['hp', 'mp', 'san']:
            current = self.findChild(QLineEdit, f"edit_{base}_current")
            maximum = self.findChild(QLineEdit, f"edit_{base}_max")
            if current and maximum:
                current.setText(str(status_data.get(f'{base}_current', '')))
                maximum.setText(str(status_data.get(f'{base}_max', '')))

        for field in ['movement_rate', 'damage_bonus', 'build']:
            edit = self.findChild(QLineEdit, f"edit_{field}")
            if edit:
                edit.setText(str(status_data.get(field, '')))

class SkillsGrid(QFrame):
    SKILL_ABBREVIATIONS = {
        'electrical_repair': 'Elec Repair',
        'mechanical_repair': 'Mech Repair',
        'operate_heavy_machinery': 'Op Heavy Mach',
        'library_use': 'Library',
        'credit_rating': 'Credit',
        'natural_world': 'Nature',
        'spot_hidden': 'Spot',
        'sleight_of_hand': 'Sleight',
        'drive_auto': 'Drive'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.original_skill_names = {} 
        self.show_all = False 
        self.toggle_button = None
        self.modified_skills = {}
        self.setup_ui()
    
    def setup_ui(self):
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setHorizontalSpacing(15)
        self.main_layout.setVerticalSpacing(4)

    def _get_skill_base(self, skill_name):
        return skill_name.split(':')[0] if ':' in skill_name else skill_name

    def _is_grouped_skill(self, skill_name):
        return self._get_skill_base(skill_name) in GROUPED_SKILLS

    def _is_special_skill(self, skill_name):
        return self._get_skill_base(skill_name) in SPECIAL_SKILLS
    
    def _organize_skills(self, skills_data):
        organized = {}
        used_groups = set()

        for skill, value in skills_data.items():
            base = self._get_skill_base(skill)
            
            if base == 'language':
                if ':' not in skill:
                    organized[skill] = value
                else:
                    organized[skill] = value
                used_groups.add(base)
                continue

            if self._is_grouped_skill(skill):
                organized[skill] = value
                used_groups.add(base)
            else:
                organized[skill] = value

        for group in used_groups:
            if group in GROUPED_SKILLS or group == 'language':
                others_key = f"{group}:others"
                others_value = (1 if group == 'language' else 
                            DEFAULT_SKILLS.get(f"{group}:all", 0))
                organized[others_key] = others_value

        return organized

    def _get_skills_to_display(self, modified_skills):
        if not self.show_all:
            return self._organize_skills(modified_skills)

        display_skills = {}
        used_groups = set()
        
        for skill, value in modified_skills.items():
            base = self._get_skill_base(skill)
            if base in GROUPED_SKILLS or base == 'language':
                display_skills[skill] = value
                used_groups.add(base)
            else:
                display_skills[skill] = value

        for group in used_groups:
            if any(skill.startswith(f"{group}:") and not skill.endswith('all') 
                  for skill in modified_skills.keys()):
                others_key = f"{group}:others"
                others_value = DEFAULT_SKILLS.get(f"{group}:all", 1)
                display_skills[others_key] = others_value

        for skill, value in DEFAULT_SKILLS.items():
            if skill.endswith(':all'):
                continue
            
            if skill not in display_skills:
                display_skills[skill] = value

        all_groups = GROUPED_SKILLS.copy()
        all_groups.add('language')
        
        for group in all_groups:
            if group not in used_groups:
                all_skill = f"{group}:all"
                display_skills[all_skill] = DEFAULT_SKILLS.get(all_skill, 1)

        def sort_key(item):
            skill_name = item[0]
            base = skill_name.split(':')[0]
            
            is_grouped = base in GROUPED_SKILLS or base == 'language'
            is_others = skill_name.endswith('others')
            is_all = skill_name.endswith('all')
            
            return (
                is_grouped,
                is_all,
                is_others,
                skill_name 
            )

        return dict(sorted(display_skills.items(), key=sort_key))

    def _format_skill_name(self, original_skill_name):
        if ':all' in original_skill_name:
            base = original_skill_name.split(':')[0].capitalize()
            display_name = f"{base} - All"
        elif original_skill_name in self.SKILL_ABBREVIATIONS:
            display_name = self.SKILL_ABBREVIATIONS[original_skill_name]
        else:
            if ':' in original_skill_name:
                if original_skill_name.endswith('others'):
                    base = original_skill_name.split(':')[0].capitalize()
                    display_name = f"{base} - Others"
                else:
                    base_name = original_skill_name.split(':')[1]
                    words = base_name.split('_')
                    display_name = ' '.join(word.capitalize() for word in words)
            elif '_' in original_skill_name:
                parts = original_skill_name.split('_')
                display_name = ' '.join(part.capitalize() for part in parts)
            else:
                display_name = original_skill_name.capitalize()
        
        self.original_skill_names[display_name.lower()] = original_skill_name
        return display_name
    
    def set_edit_mode(self, enabled: bool):
        if hasattr(self, 'add_skill_button'):
            self.add_skill_button.setEnabled(enabled)
        if hasattr(self, 'delete_skill_button'):
            self.delete_skill_button.setEnabled(enabled)
        for line_edit in self.findChildren(QLineEdit):
            line_edit.setEnabled(enabled)
    
    def update_skills(self, skills_data, preserve_edit_state=False):
        is_editing = False
        if preserve_edit_state:
            is_editing = self.parent.parent.toggle_edit_action.isChecked()
            
        self.modified_skills = skills_data.copy()
        
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        display_skills = self._get_skills_to_display(skills_data)
        
        for index, (skill_name, skill_value) in enumerate(display_skills.items()):
            row = index // 4
            col = index % 4

            font = QFont("Inconsolata SemiCondensed")
            
            display_name = self._format_skill_name(skill_name)
            
            is_special = skill_name.endswith(('all', 'others'))
            
            if is_special:
                special_edit_callback = lambda s=display_name, v=skill_value: self._show_special_input_dialog(s, v)
            else:
                special_edit_callback = None

            skill_entry = TFValueEntry(
                label_text=display_name,
                value_text=skill_value,
                label_size=75,
                custom_label_font=font,
                number_only=True,
                allow_decimal=False,
                special_edit=special_edit_callback if is_special else None
            )
            
            skill_entry.value_changed.connect(lambda val, name=skill_name: self._on_skill_value_changed(name, val))
            
            if is_editing:
                skill_entry.value_field.setEnabled(True)
                
            self.main_layout.addWidget(skill_entry, row, col)

        last_row = (len(display_skills) - 1) // 4
        button_row = last_row + 1
        
        self.toggle_button = self._create_toggle_button()
        self.add_skill_button = self._create_add_button()
        self.delete_skill_button = self._create_delete_button()
        
        self.main_layout.addWidget(self.toggle_button, button_row, 0)
        self.main_layout.addWidget(self.add_skill_button, button_row, 1)
        self.main_layout.addWidget(self.delete_skill_button, button_row, 2)
        
        spacer = QWidget()
        self.main_layout.addWidget(spacer, button_row, 3)
        
        if preserve_edit_state:
            self.set_edit_mode(is_editing)

    def _create_toggle_button(self):
        button = QPushButton("Show All" if not self.show_all else "Show Modified")
        button.setFixedWidth(100) 
        button.setFont(QFont("Inconsolata SemiCondensed"))
        button.clicked.connect(self._toggle_skills_display)
        return button

    def _create_add_button(self):
        button = QPushButton("Add Skill")
        button.setFixedWidth(100)
        button.setFont(QFont("Inconsolata SemiCondensed"))
        button.clicked.connect(self._handle_add_skill)
        button.setEnabled(False)
        return button
    
    def _create_delete_button(self):
        button = QPushButton("Delete Skill")
        button.setFixedWidth(100) 
        button.setFont(QFont("Inconsolata SemiCondensed"))
        button.clicked.connect(self._handle_delete_skill)
        button.setEnabled(False)
        return button

    def _toggle_skills_display(self):
        self.show_all = not self.show_all
        if hasattr(self, 'modified_skills'):
            self.update_skills(self.modified_skills, preserve_edit_state=True)
    
    def _handle_add_skill(self):
        confirmed, result = SkillAddDialog.get_skill_input(self)
        if not confirmed:
            return
            
        skill_name, skill_value = result
        
        if skill_name in self.modified_skills:
            for skill_entry in self.findChildren(TFValueEntry):
                entry_name = self._convert_display_to_storage_name(skill_entry.label.text().lower())
                if entry_name == skill_name:
                    skill_entry.set_value(str(skill_value))
                    self._highlight_widget(skill_entry)
                    return
                    
        base_skill = skill_name.split(':')[0] if ':' in skill_name else skill_name
        if base_skill in GROUPED_SKILLS:
            default_value = DEFAULT_SKILLS.get(f"{base_skill}:all", 0)
            if skill_value == default_value:
                self.parent.parent.app.show_message(f"No need to create this skill. You can use {base_skill.capitalize()} - All instead.", 3000, 'yellow')
                return
        
        self._update_single_skill(skill_name, skill_value)

    def _handle_delete_skill(self):
        print("Yo!")

    def _highlight_widget(self, widget):
        current_style = widget.styleSheet()
        widget.setStyleSheet(current_style + "border: 2px solid #FFD700;")
        
        QTimer.singleShot(3000, lambda: widget.setStyleSheet(current_style))

    def _on_skill_value_changed(self, skill_name, new_value):
            try:
                value = int(new_value) if new_value.strip() else 0
                base_skill = skill_name.split(':')[0] if ':' in skill_name else skill_name
                default_value = (DEFAULT_SKILLS.get(f"{base_skill}:all", 0)
                            if self._is_grouped_skill(skill_name)
                            else DEFAULT_SKILLS.get(skill_name, 0))
                
                if value != default_value:
                    self.modified_skills[skill_name] = value
                elif skill_name in self.modified_skills:
                    if skill_name.endswith(':all'):
                        del self.modified_skills[skill_name]
                        self.update_skills(self.modified_skills, preserve_edit_state=True)
                    else:
                        self._update_single_skill(skill_name, value)
                        
            except ValueError:
                pass

    def _show_special_input_dialog(self, skill_name: str, current_value: int) -> None:
        is_all = "all" in skill_name.lower()
        skill_type = "All" if is_all else "Others"
        base_name = skill_name.split(' - ')[0].lower()
        
        confirmed, result = SkillInputDialog.get_skill_input(
            self,
            skill_type,
            base_name,
            current_value,
            self.modified_skills
        )
        
        if not confirmed:
            return
            
        new_skill_name, new_value = result
        
        self._update_single_skill(new_skill_name, new_value)

    def _update_single_skill(self, skill_name: str, value: int):
        try:
            base_skill = skill_name.split(':')[0]
            default_value = DEFAULT_SKILLS.get(f"{base_skill}:all", 0)
            
            if value == default_value:
                remaining_skills = [s for s in self.modified_skills.keys() 
                                  if s.startswith(f"{base_skill}:") and 
                                  not s.endswith(('all', 'others')) and
                                  s != skill_name]
                
                if not remaining_skills:
                    self.parent.parent.app.show_message(
                        f"Using default value. Converting to {base_skill.capitalize()} - All.",
                        3000,
                        'yellow'
                    )
                    self._convert_others_to_all(base_skill)
                else:
                    self.parent.parent.app.show_message(
                        f"Using default value. Skill removed.",
                        3000,
                        'yellow'
                    )
                    with open(self.parent.parent.current_file_path, 'r+', encoding='utf-8') as file:
                        data = json.load(file)
                        if skill_name in data['skills']:
                            data['skills'].pop(skill_name)
                        if skill_name in self.modified_skills:
                            self.modified_skills.pop(skill_name)
                        file.seek(0)
                        json.dump(data, file, indent=4, ensure_ascii=False)
                        file.truncate()
                    
                    self.update_skills(self.modified_skills, preserve_edit_state=True)
                    return
            else:
                with open(self.parent.parent.current_file_path, 'r+', encoding='utf-8') as file:
                    data = json.load(file)
                    data['skills'][skill_name] = value
                    self.modified_skills[skill_name] = value
                    file.seek(0)
                    json.dump(data, file, indent=4, ensure_ascii=False)
                    file.truncate()
                
                self.update_skills(self.modified_skills, preserve_edit_state=True)
                
                for skill_entry in self.findChildren(TFValueEntry):
                    entry_name = self._convert_display_to_storage_name(skill_entry.label.text().lower())
                    if entry_name == skill_name:
                        self._highlight_widget(skill_entry)
                        break
                
                self.parent.parent.app.show_message("Skill updated successfully", 2000, 'green')
            
        except Exception as e:
            self.parent.parent.app.show_error("Update Error", f"Failed to update skill: {str(e)}")

    def _convert_others_to_all(self, base_skill: str):
        try:
            with open(self.parent.parent.current_file_path, 'r+', encoding='utf-8') as file:
                data = json.load(file)
                
                data['skills'] = {k: v for k, v in data['skills'].items() 
                                if not k.startswith(f"{base_skill}:")}
                self.modified_skills = {k: v for k, v in self.modified_skills.items() 
                                      if not k.startswith(f"{base_skill}:")}
                
                all_skill = f"{base_skill}:all"
                all_value = DEFAULT_SKILLS.get(all_skill, 1)
                data['skills'][all_skill] = all_value
                self.modified_skills[all_skill] = all_value
                
                file.seek(0)
                json.dump(data, file, indent=4, ensure_ascii=False)
                file.truncate()
                
            self.update_skills(self.modified_skills, preserve_edit_state=True)
            
        except Exception as e:
            self.parent.parent.app.show_error("Update Error", f"Failed to convert to All: {str(e)}")

    def _convert_display_to_storage_name(self, display_name):
            original_name = self.original_skill_names.get(display_name.lower())
            if original_name:
                return original_name
            
            for storage_name, abbr in self.SKILL_ABBREVIATIONS.items():
                if abbr.lower() == display_name.lower():
                    return storage_name
            
            return display_name.lower().replace(' ', '_')

class ItemsPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Box)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(4)
        
        self.items_grid = QGridLayout()
        self.items_grid.setHorizontalSpacing(10)
        self.items_grid.setVerticalSpacing(4)
        self.layout.addLayout(self.items_grid)

    def update_items(self, items_data):
        while self.items_grid.count():
            item = self.items_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        row = 0
        
        weapons = items_data.get('weapons', {})
        for weapon_id, weapon_data in weapons.items():
            display_name = ' '.join(word.capitalize() for word in weapon_id.split('_'))
            
            font = QFont("Inconsolata SemiCondensed")
            font.setWeight(QFont.Weight.Bold)
            
            item_entry = TFValueEntry(
                label_text=display_name,
                value_text=weapon_data.get('notes', ''),
                alignment=Qt.AlignmentFlag.AlignLeft,
                label_size=75,
                value_size=450,
                custom_label_font=font
            )
            
            self.items_grid.addWidget(item_entry, row, 0)
            row += 1
        
        armours = items_data.get('armours', {})
        for armour_id, armour_data in armours.items():
            display_name = ' '.join(word.capitalize() for word in armour_id.split('_'))
            
            item_entry = TFValueEntry(
                label_text=display_name,
                value_text=armour_data.get('notes', ''),
                alignment=Qt.AlignmentFlag.AlignLeft,
                label_size=75,
                value_size=450,
                custom_label_font=QFont("Inconsolata SemiCondensed")
            )
            
            self.items_grid.addWidget(item_entry, row, 0)
            row += 1
        
        others = items_data.get('others', {})
        for item_id, item_data in others.items():
            display_name = ' '.join(word.capitalize() for word in item_id.split('_'))
            
            item_entry = TFValueEntry(
                label_text=display_name,
                value_text=item_data.get('notes', ''),
                alignment=Qt.AlignmentFlag.AlignLeft,
                label_size=75,
                value_size=450,
                custom_label_font=QFont("Inconsolata SemiCondensed")
            )
            
            self.items_grid.addWidget(item_entry, row, 0)
            row += 1

class NotesPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Box)
        self.setup_ui()
    
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(4)
        
        title = QLabel("Notes")
        title_font = QFont("Inconsolata", 10)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        self.layout.addWidget(title)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setFont(QFont("Inconsolata", 10))
        self.notes_edit.setFixedHeight(200)
        self.notes_edit.setEnabled(False)
        self.layout.addWidget(self.notes_edit)
    
    def update_notes(self, notes_text):
        self.notes_edit.setText(notes_text)
    
    def set_edit_enabled(self, enabled):
        self.notes_edit.setEnabled(enabled)

class CharacterRules:
    @staticmethod
    def create_rules() -> Dict[str, TFValidationRule]:
        rules = {}
        
        rules.update({
            'metadata.player_name': TFValidationRule(
                type_=str,
                required=True,
                max_val=50,
                error_messages={'required': 'Player name is required'}
            ),
            'metadata.era': TFValidationRule(
                type_=str,
                required=True,
                choices=['1920s', 'Modern'],
                error_messages={'choices': 'Era must be either 1920s or Modern'}
            ),
            'metadata.campaign_date': TFValidationRule(
                type_=str,
                required=True,
                pattern=r'^\d{4}-\d{2}-\d{2}$',
                error_messages={'pattern': 'Date must be in YYYY-MM-DD format'}
            )
        })
        
        # Personal info rules
        rules.update({
            'personal_info.name': TFValidationRule(
                type_=str,
                required=True,
                max_val=50,
                error_messages={'required': 'Investigator name is required'}
            ),
            'personal_info.age': TFValidationRule(
                type_=int,
                required=True,
                min_val=15,
                max_val=90,
                error_messages={
                    'required': 'Age is required',
                    'min': 'Age cannot be less than 15',
                    'max': 'Age cannot exceed 90'
                }
            ),
            'personal_info.occupation': TFValidationRule(
                type_=str,
                required=True,
                max_val=50,
                error_messages={'required': 'Occupation is required'}
            )
        })
        
        # Basic statistics rules
        for stat in ['strength', 'constitution', 'size', 'dexterity',
                    'appearance', 'intelligence', 'power', 'education']:
            rules[f'basic_stats.{stat}'] = TFValidationRule(
                type_=int,
                required=True,
                min_val=1,
                max_val=99,
                error_messages={
                    'required': f'{stat.upper()} is required',
                    'min': 'Characteristic cannot be less than 1',
                    'max': 'Characteristic cannot exceed 99'
                }
            )
        
        # Luck special rule
        rules['basic_stats.luck'] = TFValidationRule(
            type_=int,
            required=True,
            min_val=1,
            max_val=99,
            error_messages={
                'required': 'LUCK is required',
                'min': 'LUCK cannot be less than 1',
                'max': 'LUCK cannot exceed 99'
            }
        )
        
        # Status values rules
        for stat in ['hp', 'mp', 'san']:
            rules[f'status.{stat}_current'] = TFValidationRule(
                type_=int,
                required=True,
                min_val=0,
                error_messages={
                    'required': f'Current {stat.upper()} is required',
                    'min': f'Current {stat.upper()} cannot be negative'
                }
            )
            rules[f'status.{stat}_max'] = TFValidationRule(
                type_=int,
                required=True,
                min_val=1,
                error_messages={
                    'required': f'Maximum {stat.upper()} is required',
                    'min': f'Maximum {stat.upper()} must be greater than 0'
                }
            )
        
        # MOV special rule
        rules['status.movement_rate'] = TFValidationRule(
            type_=int,
            required=True,
            min_val=2,
            max_val=9,
            error_messages={
                'required': 'MOV is required',
                'min': 'MOV cannot be less than 2',
                'max': 'MOV cannot exceed 9'
            }
        )
        
        # DB rule
        rules['status.damage_bonus'] = TFValidationRule(
            type_=str,
            required=True,
            pattern=r'^([+-]?\d+d\d+|[+-]?\d+|0)$',
            error_messages={
                'required': 'DB is required',
                'pattern': 'Invalid DB format (e.g., -1d6, +1d4, 0)'
            }
        )
        
        # BUILD rule
        rules['status.build'] = TFValidationRule(
            type_=int,
            required=True,
            min_val=-2,
            max_val=2,
            error_messages={
                'required': 'Build is required',
                'min': 'Build cannot be less than -2',
                'max': 'Build cannot exceed 2'
            }
        )
        
        # Skills rule
        rules['skills._any_'] = TFValidationRule(
            type_=int,
            required=True,
            min_val=1,
            max_val=99,
            error_messages={
                'min': 'Skill value cannot be less than 1',
                'max': 'Skill value cannot exceed 99'
            }
        )
        
        return rules
    
    @staticmethod
    def validate_hp_san_relation(current: int, max_: int, field: str) -> Tuple[bool, str]:
        if current > max_:
            return False, f"Current {field} cannot exceed maximum value"
        return True, ""

    @staticmethod
    def validate_db_build_relation(db_str: str, build: int) -> Tuple[bool, str]:
        build_db_map = {
            -2: "-2",
            -1: "-1",
            0: "0",
            1: "+1d4",
            2: "+1d6"
        }
        if build in build_db_map and db_str != build_db_map[build]:
            return False, f"Build {build} should have DB of {build_db_map[build]}"
        return True, ""

class SkillInputDialog(TFComputingDialog):
    def __init__(self, skill_type: str, base_skill: str, current_value: int, 
                current_skills: dict, parent=None):
        self.skill_type = skill_type
        self.base_skill = base_skill
        self.current_value = current_value
        self.current_skills = current_skills
        super().__init__("Skill Input", parent)
        self.setup_content()
        
    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        skill_label = QLabel(self.base_skill.capitalize())
        skill_label.setFont(QFont("Inconsolata", 11, QFont.Weight.Bold))
        layout.addWidget(skill_label)
        
        input_frame = self._create_input_section()
        layout.addWidget(input_frame)
        
        self.setFixedSize(300, 150)
        
    def _create_input_section(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.NoFrame)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        subtype_layout = QHBoxLayout()
        subtype_label = QLabel("Subtype:")
        subtype_label.setFont(QFont("Inconsolata", 10))
        subtype_label.setFixedWidth(60)
        self.subtype_input = QLineEdit()
        self.subtype_input.setFont(QFont("Inconsolata", 10))
        subtype_layout.addWidget(subtype_label)
        subtype_layout.addWidget(self.subtype_input)
        layout.addLayout(subtype_layout)
        
        value_layout = QHBoxLayout()
        value_label = QLabel("Value:")
        value_label.setFont(QFont("Inconsolata", 10))
        value_label.setFixedWidth(60)
        self.value_input = TFNumberReceiver(
            text="",
            alignment=Qt.AlignmentFlag.AlignLeft,
            font=QFont("Inconsolata", 10),
            allow_decimal=False,
            allow_negative=False
        )
        value_layout.addWidget(value_label)
        value_layout.addWidget(self.value_input)
        layout.addLayout(value_layout)
        
        return frame

    def compute_result(self) -> tuple[bool, str]:
        subtype = self.subtype_input.text().strip().lower()
        value = self.value_input.text().strip()
        
        if not subtype:
            return False, "Please enter the skill subtype."
            
        if not value:
            return False, "Please enter the skill value."
            
        try:
            value_int = int(value)
            if value_int < 1 or value_int > 99:
                return False, "Skill value must be between 1 and 99."
        except ValueError:
            return False, "Please enter a valid number."
            
        skill_name = f"{self.base_skill}:{subtype}"
            
        return True, (skill_name, value_int)

    @classmethod
    def get_skill_input(cls, parent, skill_type: str, base_skill: str, 
                       current_value: int, current_skills: dict) -> tuple[bool, tuple[str, int]]:
        dialog = cls(skill_type, base_skill, current_value, current_skills, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return True, dialog.get_result()
        return False, ("", 0)

class SkillAddDialog(TFComputingDialog):
    def __init__(self, parent=None):
        self.all_grouped_skills = GROUPED_SKILLS | {'language'} | SPECIAL_SKILLS
        super().__init__("Add Skill", parent)
        self.parent = parent
        self.setup_content()
        
    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        category_label = QLabel("Skill Category:")
        category_label.setFont(QFont("Inconsolata", 10, QFont.Weight.Bold))
        layout.addWidget(category_label)
        
        self.parent_combo = QComboBox()
        self.parent_combo.setFont(QFont("Inconsolata", 10))
        self.parent_combo.setFixedWidth(200)
        self.parent_combo.addItem("None")
        
        for skill in sorted(self.all_grouped_skills):
            if skill == 'firearms':
                display_name = 'Firearms'
            else:
                display_name = skill.capitalize()
            self.parent_combo.addItem(display_name)
            
        layout.addWidget(self.parent_combo)
        
        layout.addWidget(TFSeparator.horizontal())
        
        self.name_entry = TFValueEntry(
            label_text="Skill Name:",
            value_text="",
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=100,
            value_size=180,
            custom_label_font=QFont("Inconsolata", 10, QFont.Weight.Bold),
            custom_edit_font=QFont("Inconsolata", 10)
        )
        self.name_entry.value_field.setEnabled(True)
        self.name_entry.value_field.setValidator(
            QRegularExpressionValidator(QRegularExpression("[a-zA-Z ]+"))
        )
        layout.addWidget(self.name_entry)
        
        self.value_entry = TFValueEntry(
            label_text="Skill Value:",
            value_text="",
            label_size=100,
            value_size=180,
            custom_label_font=QFont("Inconsolata", 10, QFont.Weight.Bold),
            custom_edit_font=QFont("Inconsolata", 10),
            number_only=True,
            allow_decimal=False
        )
        self.value_entry.value_field.setEnabled(True)
        layout.addWidget(self.value_entry)
        
        layout.addStretch()
        
        self.setFixedSize(350, 250)

    def compute_result(self) -> tuple[bool, str]:
        parent_skill = self.parent_combo.currentText().lower()
        skill_name = self.name_entry.get_value().strip()
        value = self.value_entry.get_value().strip()
        
        if not skill_name:
            return False, "Please enter the skill name."
            
        if not value:
            return False, "Please enter the skill value."

        try:
            value_int = int(value)
            if value_int < 1 or value_int > 99:
                return False, "Skill value must be between 1 and 99."
        except ValueError:
            return False, "Please enter a valid number."
        
        if parent_skill == "none":
            final_name = skill_name.lower().replace(" ", "_")
        else:
            final_name = f"{parent_skill}:{skill_name.lower().replace(' ', '_')}"
            
        return True, (final_name, value_int)

    @classmethod
    def get_skill_input(cls, parent) -> tuple[bool, tuple[str, int]]:
        dialog = cls(parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return True, dialog.get_result()
        return False, ("", 0)
    