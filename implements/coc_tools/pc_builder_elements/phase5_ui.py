from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QFrame, QScrollArea

from implements.coc_tools.pc_builder_elements.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_elements.phase_ui import BasePhaseUI
from ui.components.tf_base_button import TFPreviousButton, TFBaseButton
from ui.components.tf_group_box import TFGroupBox
from ui.components.tf_text_group_box import TFTextGroupBox
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_font import LABEL_FONT
from utils.validator.tf_validator import TFValidator


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
            label_size=40,
            value_size=80,
            height=30,
            object_name="spell_name"
        )

        self.pow_cost_entry = TFValueEntry(
            label_text="POW",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=35,
            value_size=50,
            height=30,
            object_name="pow_cost"
        )

        self.mag_cost_entry = TFValueEntry(
            label_text="MAG",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=35,
            value_size=50,
            height=30,
            object_name="mag_cost"
        )

        self.san_cost_entry = TFValueEntry(
            label_text="SAN",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=35,
            value_size=50,
            height=30,
            object_name="san_cost"
        )

        self.casting_time_entry = TFValueEntry(
            label_text="Time",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=35,
            value_size=70,
            height=30,
            object_name="casting_time"
        )

        self.description_entry = TFValueEntry(
            label_text="Description",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=80,
            value_size=350,
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


class ExpPackageGroup(TFGroupBox):
    def __init__(self, parent=None):
        super().__init__("Experience Package Selection", parent=parent)

    def _setup_content(self):
        pass


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

        self.spell_group = SpellGroup()
        self.exp_package_group = ExpPackageGroup()
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
        print("[Phase5UI] _on_finish_clicked called.")

    def _on_previous_clicked(self):
        self.main_window.current_phase = PCBuilderPhase.PHASE4
        self.main_window.load_phase_ui()

    def _reset_content(self):
        print("[Phase5UI] _reset_content called.")

    def on_exit(self):
        print("[Phase5UI] on_exit called.")

    def on_enter(self):
        print("[Phase5UI] on_enter called.")
