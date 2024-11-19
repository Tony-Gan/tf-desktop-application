from typing import Tuple, Dict

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QVBoxLayout, QScrollArea, QFrame, QHBoxLayout, QGroupBox, QTextEdit, QWidget

from implements.coc_tools.pc_builder_elements.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_elements.phase_ui import BasePhaseUI
from ui.components.tf_base_button import TFPreviousButton, TFBaseButton
from ui.components.tf_value_entry import TFValueEntry
from utils.validator.tf_validator import TFValidator

LABEL_FONT = QFont("Inconsolata SemiCondensed")
LABEL_FONT.setPointSize(10)


class BackgroundGroup(QGroupBox):
    def __init__(self, parent):
        super().__init__("Background", parent)
        self.parent = parent
        self.setObjectName("section_frame")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self._setup_content()

    def _setup_content(self):
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont(LABEL_FONT))
        self.text_edit.setPlaceholderText("Enter character background here...")

        self.layout.addWidget(self.text_edit)

    def get_text(self) -> str:
        return self.text_edit.toPlainText().strip()

    def set_text(self, text: str):
        self.text_edit.setText(text)

    def reset(self):
        self.text_edit.clear()


class PortraitGroup(QGroupBox):
    def __init__(self, parent):
        super().__init__("Portraits", parent)
        self.parent = parent
        self.setObjectName("section_frame")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.mythos_entries: Dict[str, TFValueEntry] = {}
        self.entries: Dict[str, Tuple[TFValueEntry, TFBaseButton, TFBaseButton]] = {}

        self._setup_content()

    def _setup_content(self):
        details = [
            ("Significant People", "Select Person"),
            ("Meaningful Locations", "Select Location"),
            ("Important Possessions", "Select Possession"),
            ("Character Traits", "Select Trait"),
            ("Injuries/Scars", "Select Injury"),
            ("Phobias", "Select Phobia"),
            ("Manias", "Select Mania")
        ]

        mythos_details = [
            "Mythos Tomes Read",
            "Mythos Entities Encountered"
        ]

        for label in mythos_details:
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(5)

            entry = TFValueEntry(
                label_text=label,
                label_size=240,
                value_size=250,
                alignment=Qt.AlignmentFlag.AlignLeft,
                custom_label_font=LABEL_FONT,
                custom_edit_font=LABEL_FONT
            )

            container_layout.addWidget(entry)
            container_layout.addStretch()

            self.layout.addWidget(container)
            self.mythos_entries[label] = entry

        self.layout.addSpacing(10)

        for label, button_text in details:
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(5)

            entry = TFValueEntry(
                label_text=label,
                label_size=140,
                value_size=180,
                alignment=Qt.AlignmentFlag.AlignLeft,
                custom_label_font=LABEL_FONT,
                custom_edit_font=LABEL_FONT
            )

            select_button = TFBaseButton(
                text=button_text,
                width=110,
                height=24,
                on_clicked=lambda checked, e=entry: self._on_select_clicked(e)
            )

            roll_button = TFBaseButton(
                text="Roll",
                width=50,
                height=24,
                on_clicked=lambda checked, e=entry: self._on_roll_clicked(e)
            )

            container_layout.addWidget(entry)
            container_layout.addWidget(select_button)
            container_layout.addWidget(roll_button)
            container_layout.addStretch()

            self.layout.addWidget(container)
            self.entries[label] = (entry, select_button, roll_button)

    def _on_select_clicked(self, entry: TFValueEntry):
        print(f"Select button clicked for entry: {entry.label.text()}")

    def _on_roll_clicked(self, entry: TFValueEntry):
        print(f"Roll button clicked for entry: {entry.label.text()}")

    def get_values(self) -> Dict[str, str]:
        values = {
            key: entry.get_value()
            for key, entry in self.mythos_entries.items()
        }
        values.update({
            key: entry.get_value()
            for key, (entry, _, _) in self.entries.items()
        })
        return values

    def set_values(self, values: Dict[str, str]):
        for key, value in values.items():
            if key in self.mythos_entries:
                self.mythos_entries[key].set_value(value)
            elif key in self.entries:
                self.entries[key][0].set_value(value)

    def reset(self):
        for entry in self.mythos_entries.values():
            entry.set_value("")
        for entry, _, _ in self.entries.values():
            entry.set_value("")


class SpellGroup(QGroupBox):
    def __init__(self, parent):
        super().__init__("Spells", parent)
        self.parent = parent
        self.setObjectName("section_frame")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self._setup_content()

    def _setup_content(self):
        pass


class Phase4UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        self.config = main_window.config
        self.main_window = main_window

        super().__init__(PCBuilderPhase.PHASE4, main_window, parent)

        self.validator = TFValidator()
        self._setup_validation_rules()

    def _setup_ui(self):
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        self.background_scroll = QScrollArea()
        self.background_scroll.setWidgetResizable(True)
        self.background_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.background_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.background_scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.background_group = BackgroundGroup(self)
        self.background_scroll.setWidget(self.background_group)

        self.lower_group = QFrame(self)
        self.lower_group.setObjectName("section_frame")
        self.lower_group.layout = QHBoxLayout(self.lower_group)
        self.lower_group.layout.setContentsMargins(0, 0, 0, 0)

        self.portrait_group = PortraitGroup(self)
        self.spell_group = SpellGroup(self)

        self.lower_group.layout.addWidget(self.portrait_group, 4)
        self.lower_group.layout.addWidget(self.spell_group, 3)

        content_layout.addWidget(self.background_scroll, 2)
        content_layout.addWidget(self.lower_group, 3)

        self.content_area.setLayout(content_layout)

    def _setup_phase_buttons(self, button_layout):
        self.complete_button = TFBaseButton(
            "Complete",
            self,
            height=30,
            on_clicked=self._on_check_clicked
        )
        self.previous_button = TFPreviousButton(
            self,
            height=30,
            on_clicked=self._on_previous_clicked
        )

        button_layout.addWidget(self.complete_button)
        button_layout.addWidget(self.previous_button)

    def _setup_validation_rules(self):
        pass

    def _on_check_clicked(self):
        print("[Phase4UI] _on_check_clicked called.")

    def _on_previous_clicked(self):
        self.main_window._on_phase_selected(PCBuilderPhase.PHASE2)

    def _reset_content(self):
        print("[Phase4UI] _reset_content called.")

    def on_enter(self):
        print(self.main_window.pc_data)
        super().on_enter()

    def on_exit(self):
        super().on_exit()
