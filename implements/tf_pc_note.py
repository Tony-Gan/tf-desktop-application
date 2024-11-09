import json
from datetime import datetime, timezone

from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QFileDialog, QWidget, QLineEdit, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont

from core.windows.tf_draggable_window import TFDraggableWindow
from utils.registry.tf_tool_matadata import TFToolMetadata
from ui.components.tf_settings_widget import MenuSection
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_separator import TFSeparator
from ui.components.tf_number_receiver import TFNumberReceiver
from utils.helper import format_datetime

LABEL_FONT = QFont("Inconsolata")
LABEL_FONT.setWeight(QFont.Weight.DemiBold)
LABEL_FONT.setPointSize(10)

EDIT_FONT = QFont("Inconsolata")
EDIT_FONT.setWeight(QFont.Weight.Normal)
EDIT_FONT.setPointSize(10)

class TFPcNote(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="pc_note",
        menu_path="Tools/COC",
        window_title="PC Note",
        menu_title="Add PC Note",
        window_size=(600, 1080),
        description="PC information note",
        max_instances=6
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pc_data = None
        self.current_file_path = None
        self.has_unsaved_changes = False
        self._setup_menu()

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

        self.lower_panel = LowerPanel()
        self.lower_panel.setObjectName("section_frame")
        self.lower_panel.setFrameShape(QFrame.Shape.Box)
        main_layout.addWidget(self.lower_panel)

    def _setup_menu(self):
        self.menu_button.add_action(
            "Load Character", 
            self._load_character_file, 
            MenuSection.CUSTOM
        )
        self.menu_button.add_action(
            "Toggle Editing",
            self._toggle_editing,
            MenuSection.CUSTOM,
            checkable=True
        )

    def _load_character_file(self):
        edit_action = self.menu_button.actions[MenuSection.CUSTOM][1]
        if edit_action.isChecked() and self.has_unsaved_changes:
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
        
        if edit_action.isChecked():
            self._disconnect_change_signals()
            edit_action.setChecked(False)
            self._update_panel_edit_state(self.left_info_panel, False)
            self._update_panel_edit_state(self.pc_info_panel, False)
            self._update_panel_edit_state(self.lower_panel, False)
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Character File",
            "resources/data/coc/pcs/",
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
        action = self.menu_button.actions[MenuSection.CUSTOM][1]
        
        if self.pc_data is None:
            action.setChecked(False)
            self.app.show_message("Please load a character file first", 2000, 'yellow')
            return

        is_editing = action.isChecked()
        if not is_editing and self.has_unsaved_changes:
            self._save_current_data()
        
        self._update_panel_edit_state(self.left_info_panel, is_editing)
        self._update_panel_edit_state(self.pc_info_panel, is_editing)
        self._update_panel_edit_state(self.lower_panel, is_editing)
        
        if is_editing:
            self._connect_change_signals()
        else:
            self._disconnect_change_signals()
            self.has_unsaved_changes = False
        
        message = "Editing mode enabled" if is_editing else "Editing mode disabled, data saved."
        self.app.show_message(message, 2000, 'green')

    def _on_text_changed(self):
        self.has_unsaved_changes = True

    def _connect_change_signals(self):
        for panel in [self.left_info_panel, self.pc_info_panel, self.lower_panel]:
            for line_edit in panel.findChildren(QLineEdit):
                line_edit.textChanged.connect(self._on_text_changed)

    def _disconnect_change_signals(self):
        for panel in [self.left_info_panel, self.pc_info_panel, self.lower_panel]:
            for line_edit in panel.findChildren(QLineEdit):
                try:
                    line_edit.textChanged.disconnect()
                except TypeError:
                    pass

    def _update_panel_edit_state(self, panel, enabled):
        for line_edit in panel.findChildren(QLineEdit):
            line_edit.setEnabled(enabled)

    def _save_current_data(self):
        try:
            metadata_fields = {
                'player_name': str,
                'era': str,
                'campaign_date': str
            }
            for field, type_conv in metadata_fields.items():
                edit = self.pc_info_panel.findChild(QLineEdit, f"edit_{field}")
                if edit:
                    self.pc_data['metadata'][field] = type_conv(edit.text())
            
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
                if edit:
                    value = edit.text()
                    if value:
                        try:
                            self.pc_data['personal_info'][field] = type_conv(value)
                        except ValueError as e:
                            self.app.show_error(
                                "Invalid Input",
                                f"Invalid value for {field}: {str(e)}"
                            )
                            return
            
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
                if edit:
                    value = edit.text()
                    if value:
                        try:
                            self.pc_data['basic_stats'][stat] = type_conv(value)
                        except ValueError as e:
                            self.app.show_error(
                                "Invalid Input",
                                f"Invalid value for {stat}: {str(e)}"
                            )
                            return
            
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
                if edit:
                    value = edit.text()
                    if value:
                        try:
                            self.pc_data['status'][field] = type_conv(value)
                        except ValueError as e:
                            self.app.show_error(
                                "Invalid Input",
                                f"Invalid value for {field}: {str(e)}"
                            )
                            return
            
            for skill_entry in self.lower_panel.skills_grid.findChildren(TFValueEntry):
                skill_name = skill_entry.label.text().lower()
                skill_name = self._convert_display_to_storage_name(skill_name)
                value = skill_entry.get_value()
                if value:
                    try:
                        self.pc_data['skills'][skill_name] = int(value)
                    except ValueError as e:
                        self.app.show_error(
                            "Invalid Input",
                            f"Invalid value for skill {skill_name}: {str(e)}"
                        )
                        return
            
            self.pc_data['metadata']['updated_at'] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            with open(self.current_file_path, 'w', encoding='utf-8') as file:
                json.dump(self.pc_data, file, indent=4, ensure_ascii=False)
                
            self.has_unsaved_changes = False
            self.app.show_message("Character data saved successfully", 2000, 'green')
            
        except IOError as e:
            self.app.show_error("Save Error", f"Failed to write file: {str(e)}")
        except Exception as e:
            self.app.show_error("Save Error", f"Unexpected error while saving: {str(e)}")

    def _convert_display_to_storage_name(self, display_name):
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
        avatar_path = self.pc_data.get('metadata', {}).get('avatar_file')
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
                    self._save_current_data()
                    if self.has_unsaved_changes:
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
        
        self.skills_grid = SkillsGrid()
        container_layout.addWidget(self.skills_grid)
        
        bottom_placeholder = QFrame()
        container_layout.addWidget(bottom_placeholder)
        
        container_layout.addStretch()
        
        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)
    
    def update_data(self, pc_data):
        self.status_bar.update_data(pc_data.get('status', {}))
        self.skills_grid.update_skills(pc_data.get('skills', {}))

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

        current = TFNumberReceiver(text="", alignment=Qt.AlignmentFlag.AlignRight, font=EDIT_FONT, allow_decimal=False, allow_negative=False)
        current.setObjectName(f"edit_{base_name}_current")
        current.setFixedWidth(26)
        current.setStyleSheet("QLineEdit { padding: 1px; }")
        current.setEnabled(False)

        separator = QLabel("/")
        separator.setFont(LABEL_FONT)
        separator.setFixedWidth(5)
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)

        maximum = TFNumberReceiver(text="", alignment=Qt.AlignmentFlag.AlignLeft, font=EDIT_FONT, allow_decimal=False, allow_negative=False)
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
                allow_decimal=False
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
        "credit_rating": "Credit R.",
        "spot_hidden": "Spot",
        "craft:knife_skills": "Knife"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.setup_ui()
    
    def setup_ui(self):
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setHorizontalSpacing(10)
        self.main_layout.setVerticalSpacing(4)

    def _format_skill_name(self, skill_name):
        if skill_name in self.SKILL_ABBREVIATIONS:
            return self.SKILL_ABBREVIATIONS[skill_name]
        
        if ':' in skill_name:
            skill_name = skill_name.split(':')[1]
        
        if '_' in skill_name:
            parts = skill_name.split('_')
            return ' '.join(part.capitalize() for part in parts)
        
        return skill_name.capitalize()
    
    def update_skills(self, skills_data):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for index, (skill_name, skill_value) in enumerate(skills_data.items()):
            row = index // 4
            col = index % 4
            
            skill_entry = TFValueEntry(
                label_text=self._format_skill_name(skill_name),
                value_text=skill_value,
                number_only=True,
                allow_decimal=False
            )
            
            self.main_layout.addWidget(skill_entry, row, col)
