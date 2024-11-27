from typing import Dict, List, Optional
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QScrollArea, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from implements.components.base_phase import BasePhase
from implements.components.data_reader import load_skills_from_json, load_occupations_from_json
from implements.components.data_type import Occupation
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_dialog import TFBaseDialog
from ui.components.tf_base_frame import TFBaseFrame


class Phase2(BasePhase):

    def _setup_content(self) -> None:
        self.selected_occupation = None
        super()._setup_content()

        self.show_occupation_list_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="Occ. List", 
            height=35,
            width=120, 
            on_clicked=self._on_occupation_list_clicked
        )

        self.buttons_frame.add_custom_button(self.show_occupation_list_button)

        self.upper_frame = UpperFrame(self)
        self.skills_frame = SkillsFrame(self)

        self.contents_frame.add_child("upper_frame", self.upper_frame)
        self.contents_frame.add_child("skill_frame", self.skills_frame)

    def reset_contents(self):
        pass

    def initialize(self):
        self.check_dependencies()

    def check_dependencies(self):
        curr_dex = int(self.p_data["basic_stats"]["dex"])
        curr_edu = int(self.p_data["basic_stats"]["edu"])
        language_own = self.p_data["character_info"]["language_own"].lower()
        self.skills = load_skills_from_json(curr_dex, curr_edu, language_own)
        self.occupations = load_occupations_from_json()

        self.upper_frame.basic_info_frame.update_points_information()

    def _on_occupation_list_clicked(self):
        pass


class UpperFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.basic_info_frame = BasicInformationFrame(self)
        self.occupation_skills_frame = OccupationSkillsFrame(self)

        self.add_child("basic_info", self.basic_info_frame)
        self.add_child("occupation_skills", self.occupation_skills_frame)


class BasicInformationFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.occupation_entry = self.create_button_entry(
            name="occupation",
            label_text="Occupation:",
            label_size=90,
            button_text="Select",
            button_callback=self._on_occupation_select,
            button_size=75,
            entry_size=75,
            border_radius=5
        )

        self.main_layout.addWidget(self.occupation_entry)

    def update_points_information(self):
        # refresh information
        pass

    def _on_occupation_select(self):
        success, selected_occupation = OccupationListDialog.get_input(
            self,
            occupations=self.parent.parent.occupations,
            basic_stats=self.parent.parent.p_data["basic_stats"]
        )
        if success and selected_occupation:
            self.occupation_entry.set_text(selected_occupation.name)
            self.parent.parent.selected_occupation = selected_occupation
            # TODO: 触发其他需要的更新（预留占位符）


class OccupationSkillsFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QGridLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass


class SkillsFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QGridLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass


class OccupationListDialog(TFBaseDialog):

    def __init__(self, parent=None, occupations: List[Occupation] = None, basic_stats: Dict[str, str] = None):
        self.occupations = occupations
        nine_stats = ['str', 'con', 'siz', 'dex', 'app', 'int', 'pow', 'edu', 'luk']
        self.basic_stats = {k.upper(): int(v) for k, v in basic_stats.items() if k in nine_stats}
        
        self.categories = set()
        for occupation in occupations:
            self.categories.update(occupation.category)
        self.categories = sorted(list(self.categories))
        
        self._selected_occupation = None
        self._entry_widgets = []

        super().__init__(title="Select Occupation", layout_type=QVBoxLayout, parent=parent, button_config=[])

    def _setup_content(self) -> None:
        self.resize(1000, 780)
        self.main_layout.setSpacing(15)

        search_frame = TFBaseFrame(QHBoxLayout, parent=self)
        search_frame.main_layout.setSpacing(30)
        
        self.name_filter = self.create_line_edit(
            name="name_filter",
            text="",
            width=100,
            height=24
        )
        self.name_filter.setPlaceholderText("Filter by name...")
        self.name_filter.textChanged.connect(self._debounce_filter)
        
        category_options = ["None"] + self.categories
        self.category_filter = self.create_option_entry(
            name="category_filter",
            label_text="Category:",
            options=category_options,
            label_size=70,
            value_size=150
        )
        self.category_filter.value_changed.connect(self._apply_filters)
        
        self.skill_filter = self.create_line_edit(
            name="skill_filter",
            text="",
            width=200,
            height=24
        )
        self.skill_filter.setPlaceholderText("Filter by skill... (WIP)")
        
        self.reset_button = self.create_button(
            name="reset_filter",
            text="Reset Filters",
            width=100,
            on_clicked=self._reset_filters
        )

        search_frame.main_layout.addWidget(self.name_filter)
        search_frame.main_layout.addWidget(self.category_filter)
        search_frame.main_layout.addWidget(self.skill_filter)
        search_frame.main_layout.addStretch()
        search_frame.main_layout.addWidget(self.reset_button)
        
        self.main_layout.addWidget(search_frame)
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.scroll_content = TFBaseFrame(QVBoxLayout, parent=scroll)
        scroll.setWidget(self.scroll_content)
        
        for occupation in self.occupations:
            entry = OccupationEntry(occupation, self.basic_stats, parent=self.scroll_content)
            self.scroll_content.main_layout.addWidget(entry)
            self._entry_widgets.append(entry)
            
        self.scroll_content.main_layout.addStretch()
        self.main_layout.addWidget(scroll)

    def _debounce_filter(self):
        if hasattr(self, '_filter_timer'):
            self._filter_timer.stop()
        else:
            self._filter_timer = QTimer()
            self._filter_timer.setSingleShot(True)
            self._filter_timer.timeout.connect(self._apply_filters)
        self._filter_timer.start(500)

    def _apply_filters(self):
        name_filter = self.name_filter.text().lower()
        category_filter = self.category_filter.get_value()

        for entry in self._entry_widgets:
            show = True
            
            if name_filter and name_filter not in entry.occupation.name.lower():
                show = False

            if category_filter and category_filter != "None":
                if category_filter not in entry.occupation.category:
                    show = False
            
            entry.setVisible(show)

    def _reset_filters(self):
        self.name_filter.clear()
        self.category_filter.set_value("None")
        self.skill_filter.clear()
        for entry in self._entry_widgets:
            entry.setVisible(True)

    def accept_occupation(self, occupation: Occupation):
        self._selected_occupation = occupation
        self.accept()
        
    def get_result(self) -> Optional[Occupation]:
        return self._selected_occupation


class OccupationEntry(TFBaseFrame):

    def __init__(self, occupation: Occupation, basic_stats: Dict[str, int], parent=None):
        self.occupation = occupation
        self.basic_stats = basic_stats

        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)
        self.setObjectName("occupationEntry")
        
        self.setMouseTracking(True)
        self.setStyleSheet("""
            #occupationEntry {
                background-color: transparent;
            }
            #occupationEntry:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)

    def _setup_content(self) -> None:
        font = QFont("Merriweather Light")
        font.setPointSize(10)

        title_font = QFont("Merriweather")
        title_font.setPointSize(12)

        name_label = self.create_label(
            self.occupation.name,
            fixed_width=None,
            height=30
        )
        name_label.setFont(title_font)
        self.main_layout.addWidget(name_label)

        formula_label = self.create_label(
            f"Skill Points: {self.occupation.format_formula_for_display()}",
            height=24,
            serif=True
        )
        formula_label.setFont(font)
        self.main_layout.addWidget(formula_label)

        calculated_points = self.occupation.calculate_skill_points(self.basic_stats)
        points_entry = self.create_value_entry(
            name="points",
            label_text="Available Points:",
            value_text=str(calculated_points),
            label_size=110,
            value_size=30,
            enable=False,
            height=24
        )
        
        if calculated_points >= 280:
            color = "rgb(50, 205, 50)"
        elif calculated_points >= 240:
            color = "rgb(100, 149, 237)"
        elif calculated_points <= 160:
            color = "rgb(220, 20, 60)"
        else:
            color = "white"
            
        points_entry.value_field.setStyleSheet(f"color: {color}")
        self.main_layout.addWidget(points_entry)

        skills_label = self.create_label(
            f"Skills: \n{self.occupation.format_skills()}",
            height=60,
            serif=True
        )
        skills_label.setFont(font)
        self.main_layout.addWidget(skills_label)

        categories_label = self.create_label(
            f"Categories: {', '.join(self.occupation.category)}",
            height=24,
            serif=True
        )
        categories_label.setFont(font)
        self.main_layout.addWidget(categories_label)

        credit_label = self.create_label(
            f"Credit Rating: {self.occupation.credit_rating}",
            height=24,
            serif=True
        )
        credit_label.setFont(font)
        self.main_layout.addWidget(credit_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dialog = self.window()
            if isinstance(dialog, OccupationListDialog):
                dialog.accept_occupation(self.occupation)
