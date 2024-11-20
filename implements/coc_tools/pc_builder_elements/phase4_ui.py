import random
from typing import Tuple, Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QScrollArea, QFrame, QHBoxLayout, QWidget

from implements.coc_tools.pc_builder_elements.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_elements.phase_status import PhaseStatus
from implements.coc_tools.pc_builder_elements.phase_ui import BasePhaseUI
from implements.coc_tools.coc_data.dialogs import CommonListDialog
from ui.components.tf_base_button import TFPreviousButton, TFBaseButton
from ui.components.tf_group_box import TFGroupBox
from ui.components.tf_text_group_box import TFTextGroupBox
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_font import LABEL_FONT
from utils.validator.tf_validator import TFValidator


class PortraitGroup(TFGroupBox):
    def __init__(self, parent):
        self.common_lists = {
            "Ideology/Beliefs": [
                "Religious Faith - There is a higher power that you worship and pray to (Vishnu, Jesus Christ, Haile Selassie I)",
                "Secular Humanism - Mankind can do fine without religions (atheist, humanist, secularist)",
                "Scientific Devotion - Science has all the answers (evolution, cryogenics, space exploration)",
                "Fatalistic Beliefs - A belief in fate (karma, class system, superstitious)",
                "Society Membership - Member of a society or secret society (Freemason, Women's Institute, Anonymous)",
                "Moral Crusader - There is evil in society that should be rooted out (drugs, violence, racism)",
                "Occult Interest - The occult (astrology, spiritualism, tarot)",
                "Political Conviction - Politics (conservative, socialist, liberal)",
                "Material Ambition - Money is power, and I'm going to get all I can (greedy, enterprising, ruthless)",
                "Social Activism - Campaigner/Activist (feminism, gay rights, union power)"
            ],
            "Significant People": [
                "Parent (e.g. mother, father, stepmother)",
                "Grandparent (e.g. maternal grandmother, paternal grandfather)",
                "Sibling (e.g. brother, half-brother, stepsister)",
                "Child (e.g. son or daughter)",
                "Partner (e.g. spouse, fiancé, lover)",
                "Person who taught you your highest occupational skill",
                "Childhood Friend (e.g. classmate, neighbor, imaginary friend)",
                "A famous person. Your idol or hero",
                "A fellow investigator in your game",
                "A non-player character (NPC) in the game"
            ],
            "Meaningful Locations": [
                "Your seat of learning (e.g. school, university, apprenticeship)",
                "Your hometown (e.g. rural village, market town, busy city)",
                "The place you met your first love (e.g. a music concert, on holiday, a bomb shelter)",
                "A place for quiet contemplation (e.g. the library, country walks on your estate, fishing)",
                "A place for socializing (e.g. gentlemen's club, local bar, uncle's house)",
                "A place connected with your ideology/belief (e.g. parish church, Mecca, Stonehenge)",
                "The grave of a significant person (e.g. a parent, a child, a lover)",
                "Your family home (e.g. a country estate, a rented flat, the orphanage)",
                "The place you were happiest in your life (e.g. park bench of first kiss, university, grandmother's home)",
                "Your workplace (e.g. the office, library, bank)"
            ],
            "Treasured Possessions": [
                "An item connected with your highest skill (e.g. expensive suit, false ID, brass knuckles)",
                "An essential item for your occupation (e.g. doctor's bag, car, lock picks)",
                "A memento from your childhood (e.g. comics, pocketknife, lucky coin)",
                "A memento of a departed person (e.g. jewelry, photograph in wallet, letter)",
                "Something given to you by your Significant Person (e.g. ring, diary, map)",
                "Your collection (e.g. bus tickets, stuffed animals, records)",
                "Something mysterious you found and seek answers about (e.g. unknown letter, curious pipe, strange silver ball)",
                "A sporting item (e.g. cricket bat, signed baseball, fishing rod)",
                "A weapon (e.g. service revolver, hunting rifle, hidden boot knife)",
                "A pet (e.g. dog, cat, tortoise)"
            ],
            "Character Traits": [
                "Generous (e.g. generous tipper, helps those in need, philanthropist)",
                "Good with Animals (e.g. loves cats, grew up on a farm, good with horses)",
                "Dreamer (e.g. given to flights of fancy, visionary, highly creative)",
                "Hedonist (e.g. life of the party, entertaining drunk, live fast and die young)",
                "Gambler and risk-taker (e.g. poker-faced, try anything once, lives on the edge)",
                "Good Cook (e.g. wonderful baker, resourceful chef, refined palate)",
                "Ladies' man/seductress (e.g. suave, charming voice, enchanting eyes)",
                "Loyal (e.g. stands by friends, never breaks promises, would die for beliefs)",
                "Good reputation (e.g. best speaker, most pious, fearless in danger)",
                "Ambitious (e.g. to achieve a goal, to become the boss, to have it all)"
            ],
            "Injuries/Scars": [
                "A distinctive facial scar (e.g. across eyebrow, on cheek, split lip)",
                "War wound (e.g. limp from bullet wound, shrapnel scars, burn marks)",
                "Childhood accident (e.g. crooked finger, knee injury, small burn scar)",
                "Work-related injury (e.g. chemical burns, missing fingertip, back pain)",
                "Sports injury (e.g. boxer's nose, cricket injury, old football wound)",
                "Surgery scar (e.g. appendix removal, heart operation, knee replacement)",
                "Animal attack marks (e.g. dog bite scar, claw marks, snake bite)",
                "Accident trauma (e.g. car crash injury, falling debris wound, fire burns)",
                "Fight memento (e.g. broken nose, knife scar, brass knuckle marks)",
                "Mystery scar (e.g. unexplained mark, ritualistic scar, forgotten wound)"
            ]
        }
        self.mythos_entries: Dict[str, TFValueEntry] = {}
        self.entries: Dict[str, Tuple[TFValueEntry, TFBaseButton, TFBaseButton]] = {}

        super().__init__("Portraits", parent=parent)

    def _setup_content(self):
        details = [
            ("Ideology/Beliefs", "Common List"),
            ("Significant People", "Common List"),
            ("Meaningful Locations", "Common List"),
            ("Treasured Possessions", "Common List"),
            ("Character Traits", "Common List"),
            ("Injuries/Scars", "Common List")
        ]

        mythos_details = [
            "Mythos Tomes Read",
            "Mythos Entities Encountered",
            "Phobias",
            "Manias"
        ]

        for label in mythos_details:
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(5)

            entry = TFValueEntry(
                label_text=label,
                label_size=210,
                value_size=275,
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
                value_size=205,
                alignment=Qt.AlignmentFlag.AlignLeft,
                custom_label_font=LABEL_FONT,
                custom_edit_font=LABEL_FONT
            )

            select_button = TFBaseButton(
                text=button_text,
                width=80,
                height=24,
                on_clicked=lambda _, e=entry: self._on_select_clicked(e)
            )

            roll_button = TFBaseButton(
                text="Roll",
                width=50,
                height=24,
                on_clicked=lambda _, e=entry: self._on_roll_clicked(e)
            )

            container_layout.addWidget(entry)
            container_layout.addWidget(select_button)
            container_layout.addWidget(roll_button)
            container_layout.addStretch()

            self.layout.addWidget(container)
            self.entries[label] = (entry, select_button, roll_button)

    def _on_select_clicked(self, entry: TFValueEntry):
        label = entry.label.text()
        items = self.common_lists[label]
        
        if label == "Significant People":
            display_items = items.copy()
            display_items.extend([
                "", 
                "WHY - For reference only:",
                "1. You are indebted to them (e.g. financially, they protected you through hard times, got you your first job)",
                "2. They taught you something (e.g. a skill, to love, to be a man)",
                "3. They give your life meaning (e.g. you aspire to be like them, you seek to be with them)",
                "4. You wronged them and seek reconciliation (e.g. stole money, informed police, refused to help)",
                "5. Shared experience (e.g. lived through hard times together, grew up together, served in war together)",
                "6. You seek to prove yourself to them (e.g. by getting a good job, finding a good spouse)",
                "7. You idolize them (e.g. for their fame, their beauty, their work)",
                "8. A feeling of regret (e.g. should have died in their place, fell out over something)",
                "9. You wish to prove yourself better than them (e.g. their flaw: lazy, drunk, unloving)",
                "10. They have crossed you and you seek revenge (e.g. death of loved one, financial ruin)"
            ])
            dialog = CommonListDialog(f"Common {label}", display_items, self)
        else:
            dialog = CommonListDialog(f"Common {label}", items, self)
        dialog.exec()

    def _on_roll_clicked(self, entry: TFValueEntry):
        label = entry.label.text()
        if label in self.common_lists:
            random_item = random.choice(self.common_lists[label])
            entry.set_value(random_item)

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

        self.background_group = TFTextGroupBox(
            "Background",
            "Enter character background here...",
            parent=self
        )
        self.background_scroll.setWidget(self.background_group)

        self.lower_group = QFrame(self)
        self.lower_group.setObjectName("section_frame")
        self.lower_group.layout = QHBoxLayout(self.lower_group)
        self.lower_group.layout.setContentsMargins(0, 0, 0, 0)
        self.lower_group.setStyleSheet("QFrame#section_frame { border: none; }")

        self.portrait_group = PortraitGroup(self)
        self.lower_right_group = QFrame(self)
        self.lower_right_group.setObjectName("section_frame")
        self.lower_right_group.layout = QVBoxLayout(self.lower_right_group)
        self.lower_right_group.layout.setContentsMargins(0, 0, 0, 0)
        self.lower_right_group.setStyleSheet("QFrame#section_frame { border: none; }")

        self.inner_relation_group = TFTextGroupBox(
            "Inner Relations",
            "Enter your party connections here, separate multiple entries with commas...",
            parent=self
        )
        self.outside_relation_group = TFTextGroupBox(
            "Outside Relations",
            "Enter your social connections here, separate different relationships with commas...",
            parent=self
        )
        self.lower_right_group.layout.addWidget(self.inner_relation_group, 1)
        self.lower_right_group.layout.addWidget(self.outside_relation_group, 1)

        self.lower_group.layout.addWidget(self.portrait_group, 5)
        self.lower_group.layout.addWidget(self.lower_right_group, 3)

        content_layout.addWidget(self.background_scroll, 2)
        content_layout.addWidget(self.lower_group, 3)

        self.content_area.setLayout(content_layout)

    def _setup_phase_buttons(self, button_layout):
        self.complete_button = TFBaseButton(
            "Complete",
            self,
            height=30,
            on_clicked=self._on_complete_clicked
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

    def _on_complete_clicked(self):
        self.next_button.setEnabled(True)
        self.main_window.set_phase_status(self.phase, PhaseStatus.COMPLETED)

    def _on_previous_clicked(self):
        self.main_window._on_phase_selected(PCBuilderPhase.PHASE2)

    def _reset_content(self):
        super()._reset_content()

        if 'personal_background' in self.main_window.pc_data:
            del self.main_window.pc_data['personal_background']

        self.background_group.reset()
        self.portrait_group.reset()
        self.inner_relation_group.reset()
        self.outside_relation_group.reset()

        self.complete_button.setEnabled(True)
        self.next_button.setEnabled(False)

        self.main_window.set_phase_status(self.phase, PhaseStatus.NOT_START)

    def on_enter(self):
        super().on_enter()

    def on_exit(self):
        if 'personal_background' not in self.main_window.pc_data:
            self.main_window.pc_data['personal_background'] = {}
            
        background_data = {}
        
        background_data['main_text'] = self.background_group.get_text()
        
        mythos_data = {}
        for key, entry in self.portrait_group.mythos_entries.items():
            mythos_data[key] = entry.get_value()
        background_data['mythos'] = mythos_data
        
        portraits_data = {}
        for key, (entry, _, _) in self.portrait_group.entries.items():
            portraits_data[key] = entry.get_value()
        background_data['portraits'] = portraits_data
        
        background_data['inner_relations'] = self.inner_relation_group.get_text()
        
        background_data['outside_relations'] = self.outside_relation_group.get_text()
        
        self.main_window.pc_data['personal_background'] = background_data
