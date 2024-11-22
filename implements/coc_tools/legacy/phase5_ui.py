from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QFrame, 
                             QScrollArea, QLabel, QDialog, QComboBox, QLineEdit, QCheckBox)

from implements.coc_tools.coc_data.dialogs import TextDisplayDialog
from implements.coc_tools.pc_builder_elements.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.legacy.phase_ui import BasePhaseUI
from ui.components.tf_base_button import TFPreviousButton, TFBaseButton
from ui.components.tf_group_box import TFGroupBox
from ui.components.tf_separator import TFSeparator
from ui.components.tf_text_group_box import TFTextGroupBox
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_computing_dialog import TFComputingDialog
from ui.components.tf_font import LABEL_FONT
from utils.validator.tf_validator import TFValidator
from utils.validator.tf_validation_rules import TFValidationRule


class SpellEntry(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)

        self._setup_content()

    def _setup_content(self):
        self.name_entry = TFValueEntry(
            label_text="Name",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=30,
            value_size=80,
            height=30,
            object_name="spell_name"
        )

        self.pow_cost_entry = TFValueEntry(
            label_text="POW",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=30,
            value_size=40,
            height=30,
            object_name="pow_cost"
        )

        self.mag_cost_entry = TFValueEntry(
            label_text="MAG",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=30,
            value_size=40,
            height=30,
            object_name="mag_cost"
        )

        self.san_cost_entry = TFValueEntry(
            label_text="SAN",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=30,
            value_size=40,
            height=30,
            object_name="san_cost"
        )

        self.casting_time_entry = TFValueEntry(
            label_text="Time",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=30,
            value_size=60,
            height=30,
            object_name="casting_time"
        )

        self.description_entry = TFValueEntry(
            label_text="Description",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=70,
            value_size=400,
            height=30,
            object_name="description"
        )

        self.layout.addWidget(self.name_entry, 0, 0)
        self.layout.addWidget(self.pow_cost_entry, 0, 1)
        self.layout.addWidget(self.mag_cost_entry, 0, 2)
        self.layout.addWidget(self.san_cost_entry, 0, 3)
        self.layout.addWidget(self.casting_time_entry, 0, 4)
        self.layout.addWidget(self.description_entry, 1, 0, 1, 5)

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)
        self.layout.setColumnStretch(4, 1)

        if isinstance(self.parent, SpellGroup) and hasattr(self.parent, 'parent'):
            for entry in [self.name_entry, self.pow_cost_entry, self.mag_cost_entry,
                         self.san_cost_entry, self.casting_time_entry, self.description_entry]:
                entry.value_field.textChanged.connect(self._on_value_changed)

    def _on_value_changed(self):
        if isinstance(self.parent, SpellGroup) and hasattr(self.parent, 'parent'):
            self.parent.parent.adjust_status()


class SpellGroup(TFGroupBox):
    MAX_SPELLS = 5

    def __init__(self, parent=None):
        self.spell_entries = []
        super().__init__("Spells", parent=parent)

    def _setup_content(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(2)
        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)

        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(5)

        self.add_button = TFBaseButton(
            "Add Spell",
            width=100,
            height=30,
            enabled=True,
            object_name="add_spell_button",
            tooltip="Add a new spell entry",
            on_clicked=self._add_spell
        )

        self.delete_button = TFBaseButton(
            "Delete Spell",
            width=100,
            height=30,
            enabled=False,
            object_name="delete_spell_button",
            tooltip="Delete the last spell entry",
            on_clicked=self._delete_spell
        )

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addStretch()

        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.button_container)

    def _add_spell(self):
        if len(self.spell_entries) >= self.MAX_SPELLS:
            return

        entry = SpellEntry(self)
        self.scroll_layout.insertWidget(0, entry)
        self.spell_entries.append(entry)

        self._update_button_states()

    def _delete_spell(self):
        if self.spell_entries:
            entry = self.spell_entries.pop()
            self.scroll_layout.removeWidget(entry)
            entry.deleteLater()

            self._update_button_states()

    def _update_button_states(self):
        current_count = len(self.spell_entries)
        self.add_button.setEnabled(current_count < self.MAX_SPELLS)
        self.delete_button.setEnabled(current_count > 0)
        if hasattr(self.parent, 'adjust_status'):
            self.parent.adjust_status()

    def reset(self):
        while self.spell_entries:
            self._delete_spell()


class ExpPackageEntry(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.package_content = {
            "War Experience": {
                'title': 'War Experience Package',
                'paragraphs': [
                    'The investigator has served in one of the Armed Forces during a war—probably the Great War of 1914 to 1918 for 1920s investigators. While benefitting from their experience, they also bear its scars.'
                ],
                'sections': [
                    {
                        'subtitle': 'Required Adjustments',
                        'content': '• Adjust age according to period of war and starting year of the scenario.\n• Deduct 1D10+5 from SAN.\n• Add one of the following to the investigator\'s backstory: Injury/Scar or a Phobia/Mania associated with the war.'
                    },
                    {
                        'subtitle': 'Bonus Skills (70 points)',
                        'content': 'Rank and file soldiers choose from:\nClimb, Fighting (Brawl), Firearms (Rifle/Shotgun), First Aid, Intimidate, Listen, Stealth, Throw, Sleight of Hand, Spot Hidden, Survival.\n\nOfficers choose from:\nClimb, Firearms (Handgun), First Aid, Listen, Navigate, one interpersonal skill (Charm, Persuade, or Intimidate), Stealth, Spot Hidden, Throw.'
                    },
                    {
                        'subtitle': 'Special Note',
                        'content': 'Immune to sanity losses resulting from viewing a corpse or gross injury.'
                    }
                ]
            },
            
            "Police Experience": {
                'title': 'Police Experience Package',
                'paragraphs': [
                    'The investigator has served for a number of years on a police force or has retired from this profession.'
                ],
                'sections': [
                    {
                        'subtitle': 'Required Adjustments',
                        'content': '• Choose a starting age of 25 or over.\n• Deduct 1D10 from SAN.\n• Add one of the following to the investigator\'s backstory: Injury/Scar or a Phobia/Mania associated with their experiences as a police officer.'
                    },
                    {
                        'subtitle': 'Bonus Skills (60 points)',
                        'content': 'Choose from: Climb, Drive Auto, Fighting (Brawl), Firearms (Handgun or Rifle/Shotgun), First Aid, Intimidate, Law, Listen, Other Language, any two interpersonal skills (Charm, Fast Talk, Persuade, or Intimidate), Track.'
                    },
                    {
                        'subtitle': 'Special Note',
                        'content': 'Immune to sanity losses resulting from viewing a corpse.'
                    }
                ]
            },

            "Criminal Experience": {
                'title': 'Organized Crime Experience Package',
                'paragraphs': [
                    'The investigator has spent most, if not all, of their life involved in organized crime.'
                ],
                'sections': [
                    {
                        'subtitle': 'Required Adjustments',
                        'content': '• Choose a starting age of 20 or over.\n• Deduct 1D10 from SAN.\n• Add one of the following to the investigator\'s backstory: Injury/Scar or a Phobia/Mania associated with criminal experience.'
                    },
                    {
                        'subtitle': 'Bonus Skills (60 points)',
                        'content': 'Choose from: Climb, Drive Auto, Fighting (any), Firearms (any), any one interpersonal skill (Charm, Fast Talk, Persuade, or Intimidate), Law, Listen, Locksmith, Psychology, Sleight of Hand, Stealth, Spot Hidden.'
                    },
                    {
                        'subtitle': 'Special Note',
                        'content': 'Immune to sanity losses resulting from viewing a corpse, witnessing or performing a murder, or seeing violence perpetrated against a human being.'
                    }
                ]
            },

            "Medical Experience": {
                'title': 'Medical Experience Package',
                'paragraphs': [
                    'The investigator is a long-serving physician, nurse, or forensic examiner.'
                ],
                'sections': [
                    {
                        'subtitle': 'Required Adjustments',
                        'content': '• Choose a starting age of 30 or over.\n• Deduct 1D10 from SAN.\n• Add a Phobia/Mania associated with medical experience to the investigator\'s backstory.'
                    },
                    {
                        'subtitle': 'Bonus Skills (60 points)',
                        'content': 'Choose from: First Aid, Law, Listen, Medicine, Psychology, Spot Hidden, Science (any two).'
                    },
                    {
                        'subtitle': 'Special Note',
                        'content': 'Immune to sanity losses resulting from viewing a corpse or gross injury.'
                    }
                ]
            },

            "Mythos Experience": {
                'title': 'Mythos Experience Package',
                'paragraphs': [
                    'The investigator has knowledge of the Cthulhu Mythos, either in an academic sense or through tangible experience. Discuss with the Keeper how the investigator is aware of the Cthulhu Mythos—through reading books or experience—and write this into the investigator\'s backstory.'
                ],
                'sections': [
                    {
                        'subtitle': 'Required Adjustments',
                        'content': '• Increase Cthulhu Mythos skill to level agreed with Keeper (suggested 1D10+5).\n• Reduce maximum Sanity in line with Cthulhu Mythos skill.\n• If a believer, deduct SAN equal to amount of Cthulhu Mythos skill gained.\n• Add two of the following to the investigator\'s backstory: Injury/Scar, Phobia/Mania or Encounter with Strange Entity associated with Mythos experience.'
                    },
                    {
                        'subtitle': 'Special Note',
                        'content': 'Spells (only if a believer) with the Keeper\'s permission—the Keeper will determine what spell(s) the investigator has access to.'
                    }
                ]
            }
        }
        self._setup_content()

    def _setup_content(self):
        self.name_label = QLabel()
        self.name_label.setFont(LABEL_FONT)
        self.name_label.setMinimumWidth(80)

        self.view_button = TFBaseButton(
            "View Details",
            width=80,
            height=24,
            enabled=True,
            object_name="view_button",
            on_clicked=self._on_view_clicked
        )

        self.apply_button = TFBaseButton(
            "Apply",
            width=80,
            height=24,
            enabled=True,
            object_name="apply_button",
            on_clicked=self._on_apply_clicked
        )

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.view_button)
        self.layout.addWidget(self.apply_button)
        self.layout.addStretch()

    def _on_view_clicked(self):
            name = self.name_label.text()
            package_name = None
            name_mapping = {
                "War": "War Experience",
                "Police": "Police Experience",
                "Crime": "Criminal Experience",
                "Medical": "Medical Experience",
                "Mythos": "Mythos Experience"
            }
            
            if name in name_mapping:
                package_name = name_mapping[name]
                if package_name in self.package_content:
                    dialog = TextDisplayDialog(
                        f"{package_name} Details",
                        self.package_content[package_name],
                        self.parent
                    )
                    dialog.exec()

    def _on_apply_clicked(self):
            name = self.name_label.text()
            response = self.parent.parent.main_window.app.show_warning(
                "Apply Experience Package",
                f"Are you sure you want to apply the {name} Experience Package?",
                ["Confirm", "Cancel"]
            )
            
            if response != "Confirm":
                return
                
            if name == "War":
                dialog = WarExperienceDialog(self.parent)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    result = dialog.get_result()
                    print("[ExpPackageEntry] War Experience package to be applied:", result)
                
            elif name == "Police":
                dialog = PoliceExperienceDialog(self.parent)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    result = dialog.get_result()
                    print("[ExpPackageEntry] Police Experience package to be applied:", result)
                
            elif name == "Crime":
                dialog = CriminalExperienceDialog(self.parent)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    result = dialog.get_result()
                    print("[ExpPackageEntry] Criminal Experience package to be applied:", result)
                
            elif name == "Medical":
                dialog = MedicalExperienceDialog(self.parent)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    result = dialog.get_result()
                    print("[ExpPackageEntry] Medical Experience package to be applied:", result)
                
            elif name == "Mythos":
                dialog = MythosExperienceDialog(self.parent)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    result = dialog.get_result()
                    print("[ExpPackageEntry] Mythos Experience package to be applied:", result)


class ExpPackageGroup(TFGroupBox):
    def __init__(self, parent=None):
        self.parent = parent
        self.current_selected = None
        self.entries = []
        super().__init__("Experience Package Selection", parent=parent)

    def _setup_content(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(12)
        self.scroll_area.setWidget(self.scroll_content)

        default_packages = [
            "War",
            "Police",
            "Crime",
            "Medical",
            "Mythos"
        ]

        for package_name in default_packages:
            entry = ExpPackageEntry(self)
            entry.name_label.setText(package_name)
            self.scroll_layout.addWidget(entry)
            self.entries.append(entry)

        self.scroll_layout.addStretch()
        self.layout.addWidget(self.scroll_area)

    def _on_package_selected(self, selected_entry: ExpPackageEntry):
        for entry in self.entries:
            if entry == selected_entry:
                entry.select_button.setEnabled(False)
                self.current_selected = entry
            else:
                entry.select_button.setEnabled(True)

        if hasattr(self.parent, 'adjust_status'):
            self.parent.adjust_status()

    def reset(self):
        if self.current_selected:
            self.current_selected.select_button.setEnabled(True)
            self.current_selected = None


class Phase5UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        self.config = main_window.config
        self.main_window = main_window

        super().__init__(PCBuilderPhase.PHASE5, main_window, parent)

        self.validator = TFValidator()
        self._setup_validation_rules()

    def _setup_ui(self):
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        self.spell_group = SpellGroup(self)
        self.exp_package_group = ExpPackageGroup(self)
        self.aspirations_and_drives_group = TFTextGroupBox(
            "Aspirations and Drives",
            "Enter your aspirations and drives here, separate multiple entries with commas...",
            parent=self
        )
        self.talents_and_abilities_group = TFTextGroupBox(
            "Talents and Abilities",
            "Enter your talents and abilities here, separate multiple entries with commas...",
            parent=self
        )
        self.other_notes_group = TFTextGroupBox(
            "Other Notes",
            "Enter any other notes here...",
            parent=self
        )

        self.upper_group = QFrame(self)
        self.upper_group.setObjectName("section_frame")
        self.upper_group.layout = QHBoxLayout(self.upper_group)
        self.upper_group.layout.setContentsMargins(0, 0, 0, 0)
        self.upper_group.setStyleSheet("QFrame#section_frame { border: none; }")

        self.lower_group = QFrame(self)
        self.lower_group.setObjectName("section_frame")
        self.lower_group.layout = QHBoxLayout(self.lower_group)
        self.lower_group.layout.setContentsMargins(0, 0, 0, 0)
        self.lower_group.setStyleSheet("QFrame#section_frame { border: none; }")

        self.upper_group.layout.addWidget(self.spell_group, 2)
        self.upper_group.layout.addWidget(self.exp_package_group, 1)
        self.lower_group.layout.addWidget(self.aspirations_and_drives_group, 1)
        self.lower_group.layout.addWidget(self.talents_and_abilities_group, 1)
        self.lower_group.layout.addWidget(self.other_notes_group, 1)

        content_layout.addWidget(self.upper_group, 1)
        content_layout.addWidget(self.lower_group, 1)

        self.content_area.setLayout(content_layout)

    def _setup_phase_buttons(self, button_layout):
        self.finish_button = TFBaseButton(
            "Finish",
            self,
            height=30,
            on_clicked=self._on_finish_clicked
        )
        self.previous_button = TFPreviousButton(
            self,
            height=30,
            on_clicked=self._on_previous_clicked
        )

        button_layout.addWidget(self.finish_button)
        button_layout.addWidget(self.previous_button)

    def _setup_validation_rules(self):
        pass

    def _on_finish_clicked(self):
        dialog = CharacterSummaryDialog(self.main_window.pc_data, self)
        dialog.exec()

    def _on_previous_clicked(self):
        self.main_window.current_phase = PCBuilderPhase.PHASE4
        self.main_window.load_phase_ui()

    def _reset_content(self):
        print("[Phase5UI] _reset_content called.")

    def on_exit(self):
        print("[Phase5UI] on_exit called.")

    def on_enter(self):
        print("[Phase5UI] on_enter called.")


class WarExperienceDialog(TFComputingDialog):
    def __init__(self, parent=None):
        button_config = [
            {"text": "OK", "callback": self._on_ok_clicked},
            {"text": "Cancel", "role": "reject"}
        ]
        super().__init__("Apply War Experience", parent, button_config)
        self._setup_validation_rules()
        self.setup_content()
        
    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setSpacing(10)

        age_label = self.create_label("1. Please adjust your age appropriately")
        layout.addWidget(age_label)

        san_layout = QHBoxLayout()
        san_label = self.create_label("2. Current SAN will be reduced by")
        self.san_reduction = QLineEdit()
        self.san_reduction.setEnabled(False)
        self.san_reduction.setFixedWidth(50)
        self.roll_button = TFBaseButton(
            "Roll",
            width=60,
            height=24,
            on_clicked=self._on_roll_clicked
        )
        san_layout.addWidget(san_label)
        san_layout.addWidget(self.san_reduction)
        san_layout.addWidget(self.roll_button)
        san_layout.addStretch()
        layout.addLayout(san_layout)

        trauma_layout = QHBoxLayout()
        trauma_label = self.create_label("3. Add war-related Injury/Scar/Phobia/Mania:")
        self.trauma_input = QLineEdit()
        self.trauma_input.setMinimumWidth(200)
        trauma_layout.addWidget(trauma_label)
        trauma_layout.addWidget(self.trauma_input)
        layout.addLayout(trauma_layout)

        identity_layout = QHBoxLayout()
        identity_label = self.create_label("4. Your identity in the war:")
        self.identity_combo = QComboBox()
        self.identity_combo.addItems(["None", "Rank and file soldier", "Officer"])
        self.identity_combo.currentTextChanged.connect(self._on_identity_changed)
        identity_layout.addWidget(identity_label)
        identity_layout.addWidget(self.identity_combo)
        layout.addLayout(identity_layout)

        self.skill_label = self.create_label("Please select your identity first")
        layout.addWidget(self.skill_label)

        note_label = self.create_label("Note on the investigator sheet: Immune to sanity losses resulting from viewing a corpse or gross injury")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)

        layout.addStretch()
        
    def _setup_validation_rules(self):
        rules = {
            'san_reduction': TFValidationRule(
                type_=str,
                required=True,
                error_messages={
                    'required': 'Please roll for SAN reduction'
                }
            ),
            'identity': TFValidationRule(
                type_=str,
                required=True,
                choices=['Rank and file soldier', 'Officer'],
                error_messages={
                    'required': 'Please select your identity',
                    'choices': 'Please select a valid identity'
                }
            )
        }
        self.validator.add_rules(rules)

    def _on_roll_clicked(self):
        from random import randint
        result = randint(1, 10) + 5
        self.san_reduction.setText(str(result))
        self.roll_button.setEnabled(False)

    def _on_identity_changed(self, identity: str):
        if identity == "Rank and file soldier":
            self.skill_label.setText("[Placeholder] Rank and file soldier skills")
        elif identity == "Officer":
            self.skill_label.setText("[Placeholder] Officer skills")
        else:
            self.skill_label.setText("Please select your identity first")

    def get_field_values(self) -> dict:
        return {
            'san_reduction': self.san_reduction.text(),
            'trauma': self.trauma_input.text(),
            'identity': self.identity_combo.currentText()
        }

    def process_validated_data(self, data: dict) -> dict:
        print("[WarExperienceDialog] Processing data:", data)
        return data
    

class PoliceExperienceDialog(TFComputingDialog):
    def __init__(self, parent=None):
        button_config = [
            {"text": "OK", "callback": self._on_ok_clicked},
            {"text": "Cancel", "role": "reject"}
        ]
        super().__init__("Apply Police Experience", parent, button_config)
        self._setup_validation_rules()
        self.setup_content()
        
    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setSpacing(10)

        age_label = self.create_label("1. Ensure your age is 25 or above")
        layout.addWidget(age_label)

        san_layout = QHBoxLayout()
        san_label = self.create_label("2. Current SAN will be reduced by")
        self.san_reduction = QLineEdit()
        self.san_reduction.setEnabled(False)
        self.san_reduction.setFixedWidth(50)
        self.roll_button = TFBaseButton(
            "Roll",
            width=60,
            height=24,
            on_clicked=self._on_roll_clicked
        )
        san_layout.addWidget(san_label)
        san_layout.addWidget(self.san_reduction)
        san_layout.addWidget(self.roll_button)
        san_layout.addStretch()
        layout.addLayout(san_layout)

        trauma_layout = QHBoxLayout()
        trauma_label = self.create_label("3. Add police-related Injury/Scar/Phobia/Mania:")
        self.trauma_input = QLineEdit()
        self.trauma_input.setMinimumWidth(200)
        trauma_layout.addWidget(trauma_label)
        trauma_layout.addWidget(self.trauma_input)
        layout.addLayout(trauma_layout)

        placeholder_label = self.create_label("4. [Placeholder for future content]")
        layout.addWidget(placeholder_label)

        note_label = self.create_label("Note on the investigator sheet: Immune to sanity losses resulting from viewing a corpse.")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)

        layout.addStretch()
        
    def _setup_validation_rules(self):
        rules = {
            'san_reduction': TFValidationRule(
                type_=str,
                required=True,
                error_messages={
                    'required': 'Please roll for SAN reduction'
                }
            )
        }
        self.validator.add_rules(rules)

    def _on_roll_clicked(self):
        from random import randint
        result = randint(1, 10)
        self.san_reduction.setText(str(result))
        self.roll_button.setEnabled(False)

    def get_field_values(self) -> dict:
        return {
            'san_reduction': self.san_reduction.text(),
            'trauma': self.trauma_input.text()
        }

    def process_validated_data(self, data: dict) -> dict:
        print("[PoliceExperienceDialog] Processing data:", data)
        return data


class CriminalExperienceDialog(TFComputingDialog):
    def __init__(self, parent=None):
        button_config = [
            {"text": "OK", "callback": self._on_ok_clicked},
            {"text": "Cancel", "role": "reject"}
        ]
        super().__init__("Apply Criminal Experience", parent, button_config)
        self._setup_validation_rules()
        self.setup_content()
        
    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setSpacing(10)

        age_label = self.create_label("1. Ensure your age is 20 or above")
        layout.addWidget(age_label)

        san_layout = QHBoxLayout()
        san_label = self.create_label("2. Current SAN will be reduced by")
        self.san_reduction = QLineEdit()
        self.san_reduction.setEnabled(False)
        self.san_reduction.setFixedWidth(50)
        self.roll_button = TFBaseButton(
            "Roll",
            width=60,
            height=24,
            on_clicked=self._on_roll_clicked
        )
        san_layout.addWidget(san_label)
        san_layout.addWidget(self.san_reduction)
        san_layout.addWidget(self.roll_button)
        san_layout.addStretch()
        layout.addLayout(san_layout)

        trauma_layout = QHBoxLayout()
        trauma_label = self.create_label("3. Add criminal-related Injury/Scar/Phobia/Mania:")
        self.trauma_input = QLineEdit()
        self.trauma_input.setMinimumWidth(200)
        trauma_layout.addWidget(trauma_label)
        trauma_layout.addWidget(self.trauma_input)
        layout.addLayout(trauma_layout)

        placeholder_label = self.create_label("4. [Placeholder for future content]")
        layout.addWidget(placeholder_label)

        note_label = self.create_label("Note on the investigator sheet: Immune to sanity losses resulting from viewing a corpse, witnessing or performing a murder, or seeing violence perpetrated against a human being.")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)

        layout.addStretch()
        
    def _setup_validation_rules(self):
        rules = {
            'san_reduction': TFValidationRule(
                type_=str,
                required=True,
                error_messages={
                    'required': 'Please roll for SAN reduction'
                }
            )
        }
        self.validator.add_rules(rules)

    def _on_roll_clicked(self):
        from random import randint
        result = randint(1, 10)
        self.san_reduction.setText(str(result))
        self.roll_button.setEnabled(False)

    def get_field_values(self) -> dict:
        return {
            'san_reduction': self.san_reduction.text(),
            'trauma': self.trauma_input.text()
        }

    def process_validated_data(self, data: dict) -> dict:
        print("[CriminalExperienceDialog] Processing data:", data)
        return data


class MedicalExperienceDialog(TFComputingDialog):
    def __init__(self, parent=None):
        button_config = [
            {"text": "OK", "callback": self._on_ok_clicked},
            {"text": "Cancel", "role": "reject"}
        ]
        super().__init__("Apply Medical Experience", parent, button_config)
        self._setup_validation_rules()
        self.setup_content()
        
    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setSpacing(10)

        age_label = self.create_label("1. Ensure your age is 30 or above")
        layout.addWidget(age_label)

        san_layout = QHBoxLayout()
        san_label = self.create_label("2. Current SAN will be reduced by")
        self.san_reduction = QLineEdit()
        self.san_reduction.setEnabled(False)
        self.san_reduction.setFixedWidth(50)
        self.roll_button = TFBaseButton(
            "Roll",
            width=60,
            height=24,
            on_clicked=self._on_roll_clicked
        )
        san_layout.addWidget(san_label)
        san_layout.addWidget(self.san_reduction)
        san_layout.addWidget(self.roll_button)
        san_layout.addStretch()
        layout.addLayout(san_layout)

        trauma_layout = QHBoxLayout()
        trauma_label = self.create_label("3. Add medical-related Phobia/Mania:")
        self.trauma_input = QLineEdit()
        self.trauma_input.setMinimumWidth(200)
        trauma_layout.addWidget(trauma_label)
        trauma_layout.addWidget(self.trauma_input)
        layout.addLayout(trauma_layout)

        placeholder_label = self.create_label("4. [Placeholder for future content]")
        layout.addWidget(placeholder_label)

        note_label = self.create_label("Note on the investigator sheet: Immune to sanity losses resulting from viewing a corpse or gross injury.")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)

        layout.addStretch()
        
    def _setup_validation_rules(self):
        rules = {
            'san_reduction': TFValidationRule(
                type_=str,
                required=True,
                error_messages={
                    'required': 'Please roll for SAN reduction'
                }
            )
        }
        self.validator.add_rules(rules)

    def _on_roll_clicked(self):
        from random import randint
        result = randint(1, 10)
        self.san_reduction.setText(str(result))
        self.roll_button.setEnabled(False)

    def get_field_values(self) -> dict:
        return {
            'san_reduction': self.san_reduction.text(),
            'trauma': self.trauma_input.text()
        }

    def process_validated_data(self, data: dict) -> dict:
        print("[MedicalExperienceDialog] Processing data:", data)
        return data


class MythosExperienceDialog(TFComputingDialog):
    def __init__(self, parent=None):
        button_config = [
            {"text": "OK", "callback": self._on_ok_clicked},
            {"text": "Cancel", "role": "reject"}
        ]
        super().__init__("Apply Mythos Experience", parent, button_config)
        self._setup_validation_rules()
        self.setup_content()
        
    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setSpacing(10)

        mythos_layout = QHBoxLayout()
        mythos_label = self.create_label("1. Cthulhu Mythos skill will be increased by")
        self.mythos_increase = QLineEdit()
        self.mythos_increase.setEnabled(False)
        self.mythos_increase.setFixedWidth(50)
        self.roll_button = TFBaseButton(
            "Roll",
            width=60,
            height=24,
            on_clicked=self._on_roll_clicked
        )
        mythos_layout.addWidget(mythos_label)
        mythos_layout.addWidget(self.mythos_increase)
        mythos_layout.addWidget(self.roll_button)
        mythos_layout.addStretch()
        layout.addLayout(mythos_layout)

        san_max_label = self.create_label("2. Your maximum SAN will be reduced by the amount of Cthulhu Mythos skill points")
        layout.addWidget(san_max_label)

        believer_layout = QHBoxLayout()
        believer_label = self.create_label("3. If a believer, deduct SAN equal to amount of Cthulhu Mythos skill gained.")
        self.believer_checkbox = QCheckBox()
        self.believer_checkbox.stateChanged.connect(self._on_believer_changed)
        believer_layout.addWidget(believer_label)
        believer_layout.addWidget(self.believer_checkbox)
        layout.addLayout(believer_layout)

        trauma_layout1 = QHBoxLayout()
        trauma_label1 = self.create_label("4. Add Injury/Scar, Phobia/Mania or Encounter with Strange Entity:")
        self.trauma_input1 = QLineEdit()
        self.trauma_input1.setMinimumWidth(200)
        trauma_layout1.addWidget(trauma_label1)
        trauma_layout1.addWidget(self.trauma_input1)
        layout.addLayout(trauma_layout1)

        trauma_layout2 = QHBoxLayout()
        trauma_label2 = self.create_label("5. Add another Injury/Scar, Phobia/Mania or Encounter with Strange Entity:")
        self.trauma_input2 = QLineEdit()
        self.trauma_input2.setMinimumWidth(200)
        trauma_layout2.addWidget(trauma_label2)
        trauma_layout2.addWidget(self.trauma_input2)
        layout.addLayout(trauma_layout2)

        self.spell_placeholder = self.create_label("6. [Placeholder for spell content]")
        self.spell_placeholder.hide()
        layout.addWidget(self.spell_placeholder)

        layout.addStretch()
        
    def _setup_validation_rules(self):
        rules = {
            'mythos_increase': TFValidationRule(
                type_=str,
                required=True,
                error_messages={
                    'required': 'Please roll for Mythos increase'
                }
            ),
            'trauma1': TFValidationRule(
                type_=str,
                required=True,
                error_messages={
                    'required': 'Please add first Mythos-related trauma'
                }
            ),
            'trauma2': TFValidationRule(
                type_=str,
                required=True,
                error_messages={
                    'required': 'Please add second Mythos-related trauma'
                }
            )
        }
        self.validator.add_rules(rules)

    def _on_roll_clicked(self):
        from random import randint
        result = randint(1, 10) + 5
        self.mythos_increase.setText(str(result))
        self.roll_button.setEnabled(False)

    def _on_believer_changed(self, state):
        self.spell_placeholder.setVisible(state == Qt.CheckState.Checked.value)

    def get_field_values(self) -> dict:
        return {
            'mythos_increase': self.mythos_increase.text(),
            'is_believer': self.believer_checkbox.isChecked(),
            'trauma1': self.trauma_input1.text(),
            'trauma2': self.trauma_input2.text()
        }

    def process_validated_data(self, data: dict) -> dict:
        print("[MythosExperienceDialog] Processing data:", data)
        return data


class CharacterSummaryDialog(TFComputingDialog):
    def __init__(self, pc_data: dict, parent=None):
        button_config = [
            {"text": "Confirm", "callback": self._on_confirm_clicked},
            {"text": "Cancel", "role": "reject"}
        ]
        super().__init__("Character Summary", parent, button_config)
        self.pc_data = pc_data
        self.setup_content()
        self.resize(600, 800)

    def setup_content(self):
        layout = QVBoxLayout(self.content_frame)
        layout.setSpacing(10)

        hint_label = self.create_label("Click Confirm to create character sheet", bold=True)
        hint_label.setStyleSheet("color: #2196F3;")
        layout.addWidget(hint_label)
        layout.addWidget(TFSeparator.horizontal())

        metadata_label = self.create_label("Basic Information", bold=True)
        layout.addWidget(metadata_label)
        metadata_info = [
            f"Player Name: {self.pc_data['metadata']['player_name']}",
            f"Campaign Date: {self.pc_data['metadata']['campaign_date']}",
            f"Era: {self.pc_data['metadata']['era']}"
        ]
        for info in metadata_info:
            layout.addWidget(self.create_label(info))
        layout.addWidget(TFSeparator.horizontal())

        personal_label = self.create_label("Personal Information", bold=True)
        layout.addWidget(personal_label)
        personal_info = [
            f"Name: {self.pc_data['personal_info']['name']}",
            f"Age: {self.pc_data['personal_info']['age']}",
            f"Occupation: {self.pc_data['personal_info']['occupation']}",
            f"Residence: {self.pc_data['personal_info']['residence']}",
            f"Birthplace: {self.pc_data['personal_info']['birthplace']}",
            f"Nationality: {self.pc_data['personal_info']['nationality']}"
        ]
        for info in personal_info:
            layout.addWidget(self.create_label(info))
        layout.addWidget(TFSeparator.horizontal())

        stats_label = self.create_label("Characteristics", bold=True)
        layout.addWidget(stats_label)
        stats_grid = QGridLayout()
        stats_mapping = {
            'strength': 'STR', 'constitution': 'CON', 'size': 'SIZ',
            'dexterity': 'DEX', 'appearance': 'APP', 'intelligence': 'INT',
            'power': 'POW', 'education': 'EDU', 'luck': 'LUK'
        }
        row = 0
        col = 0
        for key, abbr in stats_mapping.items():
            value = self.pc_data['basic_stats'][key]
            stat_label = self.create_label(f"{abbr}: {value}")
            stats_grid.addWidget(stat_label, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1
        layout.addLayout(stats_grid)
        layout.addWidget(TFSeparator.horizontal())

        status_label = self.create_label("Status", bold=True)
        layout.addWidget(status_label)
        status_grid = QGridLayout()
        status_info = [
            ('HP', 'hp_max'),
            ('MP', 'mp_max'),
            ('SAN', 'san_max'),
            ('MOV', 'movement_rate'),
            ('DB', 'damage_bonus'),
            ('Build', 'build')
        ]
        row = 0
        col = 0
        for label, key in status_info:
            value = self.pc_data['status'][key]
            status_label = self.create_label(f"{label}: {value}")
            status_grid.addWidget(status_label, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1
        layout.addLayout(status_grid)
        layout.addWidget(TFSeparator.horizontal())

        skills_label = self.create_label("Skills", bold=True)
        layout.addWidget(skills_label)
        skills_grid = QGridLayout()
        row = 0
        col = 0
        for skill, value in self.pc_data['skills'].items():
            skill_name = skill.replace('_', ' ').title()
            skill_label = self.create_label(f"{skill_name}: {value}")
            skills_grid.addWidget(skill_label, row, col)
            col += 1
            if col == 2:
                col = 0
                row += 1
        layout.addLayout(skills_grid)

        background_label = self.create_label("Personal Background", bold=True)
        layout.addWidget(background_label)
        
        if self.pc_data['personal_background']['main_text']:
            main_text_label = self.create_label("Background:")
            main_text_content = self.create_label(self.pc_data['personal_background']['main_text'])
            main_text_content.setWordWrap(True)
            layout.addWidget(main_text_label)
            layout.addWidget(main_text_content)
            
        mythos = self.pc_data['personal_background']['mythos']
        if isinstance(mythos, dict):
            mythos_label = self.create_label("Mythos Information:", bold=True)
            layout.addWidget(mythos_label)
            for key, value in mythos.items():
                if value:
                    layout.addWidget(self.create_label(f"{key}: {value}"))
        
        portraits = self.pc_data['personal_background']['portraits']
        if isinstance(portraits, dict):
            portraits_label = self.create_label("Portraits:", bold=True)
            layout.addWidget(portraits_label)
            for key, value in portraits.items():
                if value:
                    layout.addWidget(self.create_label(f"{key}: {value}"))
        
        if self.pc_data['personal_background']['inner_relations']:
            inner_label = self.create_label("Inner Relations:")
            inner_content = self.create_label(self.pc_data['personal_background']['inner_relations'])
            inner_content.setWordWrap(True)
            layout.addWidget(inner_label)
            layout.addWidget(inner_content)
            
        if self.pc_data['personal_background']['outside_relations']:
            outer_label = self.create_label("Outside Relations:")
            outer_content = self.create_label(self.pc_data['personal_background']['outside_relations'])
            outer_content.setWordWrap(True)
            layout.addWidget(outer_label)
            layout.addWidget(outer_content)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        scroll_widget.setLayout(layout)
        scroll_area.setWidget(scroll_widget)

        self.content_frame.setLayout(QVBoxLayout())
        self.content_frame.layout().addWidget(scroll_area)

    def _on_confirm_clicked(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Character Sheet",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
                
            try:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.pc_data, f, indent=4, ensure_ascii=False)
                self.accept()
            except Exception as e:
                self.parent().main_window.app.show_warning(
                    "Save Error",
                    f"Failed to save character sheet: {str(e)}",
                    ["OK"]
                )
