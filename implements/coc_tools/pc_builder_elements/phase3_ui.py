from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QVBoxLayout, QFrame, QHBoxLayout, QWidget, QLabel,
                             QGridLayout, QGroupBox, QScrollArea, QLineEdit)

from implements.coc_tools.coc_data.dialogs import DeleteItemDialog, CombatSkillListDialog, WeaponTypeListDialog
from implements.coc_tools.coc_data.data_enum import Category
from implements.coc_tools.coc_data.data_reader import load_weapon_types_from_json, load_combat_skills_from_json
from implements.coc_tools.pc_builder_elements.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_elements.phase_ui import BasePhaseUI
from implements.coc_tools.pc_builder_elements.phase_status import PhaseStatus
from ui.components.tf_base_button import TFPreviousButton, TFBaseButton
from ui.components.tf_group_box import TFGroupBox
from ui.components.tf_option_entry import TFOptionEntry
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_font import LABEL_FONT
from utils.validator.tf_validator import TFValidator
from utils.helper import resource_path


class WeaponGroup(TFGroupBox):
    MAX_WEAPONS = 5

    def __init__(self, parent):
        self.weapon_entries = []
        super().__init__("Weapons", parent=parent)

    def _setup_content(self):
        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(5)

        self.add_button = TFBaseButton(
            "Add Weapon",
            width=100,
            height=30,
            enabled=True,
            object_name="add_weapon_button",
            tooltip="Add a new weapon entry",
            on_clicked=self._add_weapon
        )

        self.delete_button = TFBaseButton(
            "Delete Weapon",
            width=100,
            height=30,
            enabled=False,
            object_name="delete_weapon_button",
            tooltip="Delete the last weapon entry",
            on_clicked=self._delete_weapon
        )

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addStretch()

        self.layout.addStretch()
        self.layout.addWidget(self.button_container)

    def _add_weapon(self):
        if len(self.weapon_entries) >= self.MAX_WEAPONS:
            return

        entry = WeaponEntry(self)
        self.layout.insertWidget(len(self.weapon_entries), entry)
        self.weapon_entries.append(entry)

        self._update_button_states()

    def _delete_weapon(self):
        if self.weapon_entries:
            entry = self.weapon_entries.pop()
            self.layout.removeWidget(entry)
            entry.deleteLater()

            self._update_button_states()

    def _update_button_states(self):
        current_count = len(self.weapon_entries)
        self.add_button.setEnabled(current_count < self.MAX_WEAPONS)
        self.delete_button.setEnabled(current_count > 0)
        self.parent.adjust_status()

    def reset(self):
        while self.weapon_entries:
            self._delete_weapon()


class WeaponEntry(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.categories = ["None"] + [category.value for category in Category]
        if isinstance(self.parent, WeaponGroup):
            self.weapon_types = self.parent.parent.weapon_types

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
            object_name="name"
        )

        self.category_selector = TFOptionEntry(
            label_text="Cate.",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            options=self.categories,
            current_value="None",
            label_size=35,
            value_size=100,
            height=30,
            object_name="weapon_category",
            extra_value_width=60
        )
        self.category_selector.value_field.setEditable(True)
        self.category_selector.value_field.setPlaceholderText("None")

        self.type_selector = TFOptionEntry(
            label_text="Type",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            options=["None"],
            label_size=35,
            value_size=120,
            height=30,
            object_name="weapon_type",
            extra_value_width=80
        )
        self.type_selector.value_field.setEnabled(False)
        self.type_selector.value_field.setEditable(True)
        self.type_selector.value_field.setPlaceholderText("None")

        self.skill_entry = TFValueEntry(
            label_text="Skill",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=35,
            value_size=80,
            height=30,
            object_name="weapon_skill"
        )

        self.damage_entry = TFValueEntry(
            label_text="Damage",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=40,
            value_size=70,
            height=30,
            object_name="weapon_damage"
        )

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_layout.setSpacing(0)

        self.expand_button = TFBaseButton(
            text="Expand",
            width=80,
            height=24,
            object_name="expand_button",
            on_clicked=self._toggle_expand
        )

        button_layout.addWidget(self.expand_button)

        self.range_entry = TFValueEntry(
            label_text="Range",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=40,
            value_size=30,
            height=30,
            object_name="weapon_range"
        )

        self.penetration_entry = TFValueEntry(
            label_text="Pen.",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=35,
            value_size=30,
            height=30,
            object_name="weapon_penetration"
        )

        self.rof_entry = TFValueEntry(
            label_text="RoF",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=35,
            value_size=30,
            height=30,
            object_name="weapon_rof"
        )

        self.ammo_entry = TFValueEntry(
            label_text="Ammo",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=35,
            value_size=30,
            height=30,
            object_name="weapon_ammo"
        )

        self.malfunction_entry = TFValueEntry(
            label_text="Malf",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=40,
            value_size=30,
            height=30,
            object_name="weapon_malfunction"
        )

        self.layout.addWidget(self.name_entry, 0, 0)
        self.layout.addWidget(self.category_selector, 0, 1)
        self.layout.addWidget(self.type_selector, 0, 2)
        self.layout.addWidget(self.skill_entry, 0, 3)
        self.layout.addWidget(self.damage_entry, 0, 4)
        self.layout.addWidget(button_container, 0, 5)
        self.layout.addWidget(self.range_entry, 1, 0)
        self.layout.addWidget(self.penetration_entry, 1, 1)
        self.layout.addWidget(self.rof_entry, 1, 2)
        self.layout.addWidget(self.ammo_entry, 1, 3)
        self.layout.addWidget(self.malfunction_entry, 1, 4)

        self._hide_second_row()

        self.category_selector.value_field.currentTextChanged.connect(self._on_category_changed)
        self.type_selector.value_field.currentTextChanged.connect(self._on_type_changed)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)
        self.layout.setColumnStretch(4, 1)

        self.name_entry.value_field.textChanged.connect(self._on_value_changed)
        self.category_selector.value_field.currentTextChanged.connect(self._on_value_changed)
        self.type_selector.value_field.currentTextChanged.connect(self._on_value_changed)
        self.skill_entry.value_field.textChanged.connect(self._on_value_changed)
        self.damage_entry.value_field.textChanged.connect(self._on_value_changed)
        self.range_entry.value_field.textChanged.connect(self._on_value_changed)
        self.penetration_entry.value_field.textChanged.connect(self._on_value_changed)
        self.rof_entry.value_field.textChanged.connect(self._on_value_changed)
        self.ammo_entry.value_field.textChanged.connect(self._on_value_changed)
        self.malfunction_entry.value_field.textChanged.connect(self._on_value_changed)

    def _on_value_changed(self):
        if isinstance(self.parent, WeaponGroup) and isinstance(self.parent.parent, Phase3UI):
            self.parent.parent.adjust_status()

    def _on_category_changed(self, category: str):
        if category == "None":
            self.type_selector.setEnabled(False)
            self.type_selector.set_options(["None"])
            self.type_selector.set_value("None")
            return

        self.type_selector.value_field.setEnabled(True)

        filtered_types = ["None"] + [wt.name for wt in self.weapon_types
                                     if wt.category.value == category]

        current_text = self.type_selector.get_value()
        self.type_selector.set_options(filtered_types)

        if current_text in filtered_types:
            self.type_selector.set_value(current_text)
        else:
            self.type_selector.set_value("None")

    def _on_type_changed(self, weapon_type: str):
        if weapon_type == "None":
            return

        selected_type = next((wt for wt in self.weapon_types
                              if wt.name == weapon_type), None)
        if selected_type:
            self.skill_entry.set_value(selected_type.skill.standard_text) or "N/A"
            self.damage_entry.set_value(selected_type.damage.standard_text) or "N/A"
            self.range_entry.set_value(selected_type.range.standard_text) or "N/A"
            self.penetration_entry.set_value(selected_type.penetration.value) or "N/A"
            self.rof_entry.set_value(selected_type.rate_of_fire) or "N/A"
            self.ammo_entry.set_value(selected_type.ammo if selected_type.ammo else "N/A")
            self.malfunction_entry.set_value(selected_type.malfunction if selected_type.malfunction else "N/A")

    def _hide_second_row(self):
        self.range_entry.hide()
        self.penetration_entry.hide()
        self.rof_entry.hide()
        self.ammo_entry.hide()
        self.malfunction_entry.hide()

    def _show_second_row(self):
        self.range_entry.show()
        self.penetration_entry.show()
        self.rof_entry.show()
        self.ammo_entry.show()
        self.malfunction_entry.show()

    def _toggle_expand(self):
        if self.range_entry.isVisible():
            self._hide_second_row()
            self.expand_button.setText("Expand")
        else:
            self._show_second_row()
            self.expand_button.setText("Collapse")


class CombatSkillGroup(TFGroupBox):
    def __init__(self, parent):
        self.skills = ["None"] + [cs.name for cs in parent.combat_skills]
        super().__init__("Combat Skills", parent=parent)

    def _setup_content(self):
        upper_layout = QHBoxLayout()
        self.combat_skill_selector = TFOptionEntry(
            label_text="Combat Skill",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            options=self.skills,
            current_value="None",
            label_size=80,
            value_size=120,
            height=30,
            object_name="coverage_selector"
        )
        self.combat_skill_selector.value_field.setEditable(True)

        self.damage_entry = TFValueEntry(
            label_text="Damage",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=50,
            value_size=50,
            height=30,
            object_name="damage"
        )
        self.damage_entry.value_field.setText("1D3+DB")

        self.combat_skill_entry = TFValueEntry(
            label_text="Skills",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=80,
            value_size=180,
            height=30,
            object_name="name"
        )
        self.combat_skill_entry.value_field.setText("N/A")

        self.combat_skill_selector.value_field.currentTextChanged.connect(self._on_combat_skill_changed)

        upper_layout.addWidget(self.combat_skill_selector)
        upper_layout.addWidget(self.damage_entry)
        self.layout.addLayout(upper_layout)
        self.layout.addWidget(self.combat_skill_entry)

        self.combat_skill_selector.value_field.currentTextChanged.connect(
            lambda: self.parent.adjust_status())
        self.damage_entry.value_field.textChanged.connect(
            lambda: self.parent.adjust_status())
        self.combat_skill_entry.value_field.textChanged.connect(
            lambda: self.parent.adjust_status())

    def _on_combat_skill_changed(self, combat_skill: str):
        if combat_skill == "None":
            self.combat_skill_entry.value_field.setText("N/A")
            self.damage_entry.value_field.setText("1D3")
            return

        selected_skill = next((cs for cs in self.parent.combat_skills if cs.name == combat_skill), None)
        if selected_skill:
            techniques_keys = ", ".join(selected_skill.techniques.keys())
            self.combat_skill_entry.value_field.setText(techniques_keys)
            self.damage_entry.value_field.setText(selected_skill.damage)
        else:
            self.combat_skill_entry.value_field.setText("N/A")
            self.damage_entry.value_field.setText("1D3")

    def reset(self):
        self.combat_skill_selector.value_field.setCurrentText("None")

        self.combat_skill_entry.value_field.setText("N/A")
        self.damage_entry.value_field.setText("1D3")


class ArmourGroup(TFGroupBox):
    def __init__(self, parent):
        super().__init__("Armour", layout_type=QGridLayout, parent=parent)

    def _setup_content(self):
        self.name_entry = TFValueEntry(
            label_text="Name",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=60,
            value_size=90,
            height=30,
            object_name="name"
        )
        self.name_entry.value_field.setText("N/A")

        self.type_entry = TFValueEntry(
            label_text="Type",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=60,
            value_size=90,
            height=30,
            object_name="armour_type"
        )
        self.type_entry.value_field.setText("N/A")

        self.points_entry = TFValueEntry(
            label_text="Points",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=60,
            value_size=90,
            height=30,
            object_name="points"
        )
        self.points_entry.value_field.setText("N/A")

        self.coverage_selector = TFOptionEntry(
            label_text="Coverage",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            options=["None", "Head", "Torso", "Upper Arm", "Lower Arm", "Thighs", "Lower Legs", "Hands", "Feet", "Neck", "Groin"],
            current_value="None",
            label_size=60,
            value_size=90,
            height=30,
            object_name="coverage_selector",
        )
        self.coverage_selector.value_field.setEditable(True)

        self.layout.addWidget(self.name_entry, 0, 0)
        self.layout.addWidget(self.type_entry, 0, 1)
        self.layout.addWidget(self.points_entry, 1, 0)
        self.layout.addWidget(self.coverage_selector, 1, 1)

        self.name_entry.value_field.textChanged.connect(
            lambda: self.parent.adjust_status())
        self.type_entry.value_field.textChanged.connect(
            lambda: self.parent.adjust_status())
        self.points_entry.value_field.textChanged.connect(
            lambda: self.parent.adjust_status())
        self.coverage_selector.value_field.currentTextChanged.connect(
            lambda: self.parent.adjust_status())

    def reset(self):
        self.name_entry.value_field.setText("N/A")
        self.type_entry.value_field.setText("N/A")
        self.points_entry.value_field.setText("N/A")

        self.coverage_selector.value_field.setCurrentText("None")


class CreditGroup(TFGroupBox):
    def __init__(self, parent):
        super().__init__("Credits", parent=parent)

    def _setup_content(self):
        self.cash_entry = TFValueEntry(
            label_text="Cash",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=60,
            value_size=80,
            height=30,
            object_name="cash",
            enabled=False
        )

        self.deposit_entry = TFValueEntry(
            label_text="Deposit",
            custom_label_font=LABEL_FONT,
            custom_edit_font=LABEL_FONT,
            alignment=Qt.AlignmentFlag.AlignLeft,
            label_size=60,
            value_size=80,
            height=30,
            object_name="deposit",
            enabled=False
        )
        credit_rate = self.parent.main_window.pc_data.get('skills', {}).get('credit_rate', 25)
        era = self.parent.main_window.pc_data.get('metadata', {}).get('era', 'Modern')
        cash, deposit = self._calculate_credits(credit_rate, era)

        self.cash_entry.value_field.setText("${:,}".format(cash))
        self.deposit_entry.value_field.setText("${:,}".format(deposit))

        self.layout.addWidget(self.cash_entry)
        self.layout.addWidget(self.deposit_entry)

    def _calculate_credits(self, credit_rate: int, era: str) -> tuple[int, int]:
        era_multipliers = {
            "Medieval": (0.5, 5),
            "1890s": (1, 10),
            "1920s": (2, 20),
            "Modern": (20, 200),
            "Near Future": (50, 500),
            "Future": (100, 1000)
        }

        cash_multiplier, deposit_multiplier = era_multipliers.get(era, (20, 200))

        if credit_rate == 0:
            cash = 0.5 * cash_multiplier
            deposit = 0
        elif 1 <= credit_rate <= 9:
            cash = credit_rate * 1 * cash_multiplier
            deposit = credit_rate * 10 * deposit_multiplier
        elif 10 <= credit_rate <= 49:
            cash = credit_rate * 2 * cash_multiplier
            deposit = credit_rate * 50 * deposit_multiplier
        elif 50 <= credit_rate <= 89:
            cash = credit_rate * 5 * cash_multiplier
            deposit = credit_rate * 500 * deposit_multiplier
        elif 90 <= credit_rate <= 98:
            cash = credit_rate * 20 * cash_multiplier
            deposit = credit_rate * 2000 * deposit_multiplier
        elif credit_rate == 99:
            cash = 1_000_000
            deposit = 100_000_000
        else:
            cash = 1_000_000
            deposit = 100_000_000

        return cash, deposit
    
    def reset(self):
        credit_rate = self.parent.main_window.pc_data.get('skills', {}).get('credit_rate', 25)
        era = self.parent.main_window.pc_data.get('metadata', {}).get('era', 'Modern')

        cash, deposit = self._calculate_credits(credit_rate, era)

        self.cash_entry.value_field.setText("${:,}".format(cash))
        self.deposit_entry.value_field.setText("${:,}".format(deposit))


class ItemBaseGroup(TFGroupBox):
    def __init__(self, parent, title):
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("""
            QWidget {
                border: 1px solid rgba(224, 224, 224, 0.05);
            }
            QLineEdit {
                border: 1px solid rgba(204, 204, 204, 0.05);
            }
            QLabel {
                border: 1px solid rgba(224, 224, 224, 0.05);
            }
        """)

        self.content_vertical_layout = QVBoxLayout(self.content_widget)
        self.content_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.content_vertical_layout.setSpacing(0)

        self.grid_widget = QWidget()
        self.content_layout = QGridLayout(self.grid_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(1)

        self.content_vertical_layout.addWidget(self.grid_widget)
        self.content_vertical_layout.addStretch(1)

        self.items = []
        self.current_row = 0
        self.COLS_PER_ROW = 3

        self.placeholder_widgets = []

        super().__init__(title, parent=parent)
        self._setup_first_row()

    def _setup_content(self):
        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(5)

        self.add_button = TFBaseButton(
            "Add Item",
            width=100,
            height=30,
            enabled=True,
            object_name="add_item_button",
            tooltip="Add a new item",
            on_clicked=self._add_item
        )

        self.delete_button = TFBaseButton(
            "Delete Item",
            width=100,
            height=30,
            enabled=False,
            object_name="delete_item_button",
            tooltip="Delete the last item",
            on_clicked=self._delete_item
        )

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addStretch()

        self.layout.addWidget(self.content_widget, 1)
        self.layout.addWidget(self.button_container, 0)

    def _setup_first_row(self):
        for col in range(self.COLS_PER_ROW):
            placeholder = QWidget()
            placeholder.setFixedHeight(24)
            self.content_layout.addWidget(placeholder, 0, col)
            self.placeholder_widgets.append((placeholder, 0, col))

    def _add_item(self):
        unconfirmed_line_edit = None
        for widget, row, col in self.items:
            if isinstance(widget, QLineEdit):
                unconfirmed_line_edit = (widget, row, col)
                break
        
        if unconfirmed_line_edit:
            line_edit, row, col = unconfirmed_line_edit
            text = line_edit.text().strip()
            if not text:
                self.content_layout.removeWidget(line_edit)
                line_edit.deleteLater()
                self.items.remove(unconfirmed_line_edit)
            else:
                self._convert_to_label(line_edit, row, col)

        next_pos = len(self.items)
        row = next_pos // self.COLS_PER_ROW
        col = next_pos % self.COLS_PER_ROW

        if col == 0 and row == len(self.placeholder_widgets) // self.COLS_PER_ROW:
            for c in range(self.COLS_PER_ROW):
                placeholder = QWidget()
                placeholder.setFixedHeight(24)
                self.content_layout.addWidget(placeholder, row, c)
                self.placeholder_widgets.append((placeholder, row, c))

        line_edit = QLineEdit()
        line_edit.setFont(LABEL_FONT)
        line_edit.setFixedHeight(24)
        line_edit.setFixedWidth(131)
        
        for widget, r, c in self.placeholder_widgets:
            if r == row and c == col:
                widget.hide()
                break

        self.content_layout.addWidget(line_edit, row, col)
        self.items.append((line_edit, row, col))
        
        line_edit.editingFinished.connect(lambda: self._convert_to_label(line_edit, row, col))
        line_edit.focusOutEvent = lambda e: self._convert_to_label(line_edit, row, col)
        
        line_edit.setFocus()
        self.delete_button.setEnabled(True)
        self.parent.parent.adjust_status()
        self.delete_button.setEnabled(bool(self.items))

    def _convert_to_label(self, line_edit, row, col):
        if not line_edit.isVisible():
            return
            
        text = line_edit.text().strip()
        if text:
            label = QLabel(text)
            label.setFont(LABEL_FONT)
            label.setFixedHeight(24)
            
            label.mousePressEvent = lambda e: self._on_label_clicked(label, row, col)
            
            self.content_layout.removeWidget(line_edit)
            line_edit.deleteLater()
            self.content_layout.addWidget(label, row, col)
            
            for i, (widget, r, c) in enumerate(self.items):
                if widget == line_edit:
                    self.items[i] = (label, row, col)
                    break

            if isinstance(self.parent, LowerGroup) and isinstance(self.parent.parent, Phase3UI):
                self.parent.parent.adjust_status()

    def _on_label_clicked(self, label, row, col):
        unconfirmed_line_edit = None
        for widget, r, c in self.items:
            if isinstance(widget, QLineEdit):
                unconfirmed_line_edit = (widget, r, c)
                break
        
        if unconfirmed_line_edit:
            line_edit, r, c = unconfirmed_line_edit
            text = line_edit.text().strip()
            if text:
                self._convert_to_label(line_edit, r, c)
            else:
                self.content_layout.removeWidget(line_edit)
                line_edit.deleteLater()
                self.items.remove(unconfirmed_line_edit)

        line_edit = QLineEdit(label.text())
        line_edit.setFont(LABEL_FONT)
        line_edit.setFixedHeight(24)
        line_edit.setFixedWidth(100)
        
        line_edit.editingFinished.connect(lambda: self._convert_to_label(line_edit, row, col))
        line_edit.focusOutEvent = lambda e: self._convert_to_label(line_edit, row, col)
        
        self.content_layout.removeWidget(label)
        label.deleteLater()
        self.content_layout.addWidget(line_edit, row, col)
        
        for i, (widget, r, c) in enumerate(self.items):
            if widget == label:
                self.items[i] = (line_edit, row, col)
                break
        
        line_edit.setFocus()
        line_edit.selectAll()

    def _delete_item(self):
        confirmed_items = [(w, r, c) for w, r, c in self.items if isinstance(w, QLabel)]
        if not confirmed_items:
            return
            
        confirmed, items_to_delete = DeleteItemDialog.get_input(self, items=self.items)
        if not confirmed or not items_to_delete:
            return
            
        for text in items_to_delete:
            for widget, row, col in self.items[:]:
                if isinstance(widget, QLabel) and widget.text() == text:
                    self.content_layout.removeWidget(widget)
                    widget.deleteLater()
                    self.items.remove((widget, row, col))
        
        remaining_items = [(w, r, c) for w, r, c in self.items]
        self.items.clear() 
        
        for p_widget, _, _ in self.placeholder_widgets:
            p_widget.hide()
        
        for i, (widget, _, _) in enumerate(remaining_items):
            new_row = i // self.COLS_PER_ROW
            new_col = i % self.COLS_PER_ROW
            
            self.content_layout.addWidget(widget, new_row, new_col)
            self.items.append((widget, new_row, new_col))
            
            if new_col == 0 and new_row >= len(self.placeholder_widgets) // self.COLS_PER_ROW:
                for c in range(self.COLS_PER_ROW):
                    if not any(p_row == new_row and p_col == c for _, p_row, p_col in self.placeholder_widgets):
                        placeholder = QWidget()
                        placeholder.setFixedHeight(24)
                        self.content_layout.addWidget(placeholder, new_row, c)
                        self.placeholder_widgets.append((placeholder, new_row, c))
                        placeholder.hide()
        
        last_pos = len(self.items)
        last_row = last_pos // self.COLS_PER_ROW
        last_col = last_pos % self.COLS_PER_ROW
        
        for p_widget, p_row, p_col in self.placeholder_widgets:
            if p_row == last_row and p_col >= last_col:
                p_widget.show()
        
        if not self.items:
            self.delete_button.setEnabled(False)
        
        if isinstance(self.parent, LowerGroup) and isinstance(self.parent.parent, Phase3UI):
            self.parent.parent.adjust_status()

    def reset(self):
        for widget, _, _ in self.items:
            self.content_layout.removeWidget(widget)
            widget.deleteLater()
        
        for widget, _, _ in self.placeholder_widgets:
            self.content_layout.removeWidget(widget)
            widget.deleteLater()
        
        self.items.clear()
        self.placeholder_widgets.clear()
        
        self._setup_first_row()
        
        self.delete_button.setEnabled(False)


class ItemGroup(ItemBaseGroup):
    def __init__(self, parent=None):
        super().__init__(parent, title="Items")
        self.add_button.setText("Add Item")
        self.delete_button.setText("Delete Item")


class DepositGroup(ItemBaseGroup):
    def __init__(self, parent=None):
        super().__init__(parent, title="Deposits")
        self.add_button.setText("Add Deposit")
        self.delete_button.setText("Delete Deposit")


class LowerGroup(QFrame):
    def __init__(self, parent:'Phase3UI'):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("section_frame")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self._setup_content()

    def _setup_content(self):
        self.item_group = ItemGroup(self)
        self.deposit_group = DepositGroup(self)

        self.layout.addWidget(self.item_group, 1)
        self.layout.addWidget(self.deposit_group, 1)


class Phase3UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        self.config = main_window.config
        self.main_window = main_window

        self.weapon_types = load_weapon_types_from_json(resource_path("implements/coc_tools/coc_data/weapon_types.json"))
        self.combat_skills = load_combat_skills_from_json(resource_path("implements/coc_tools/coc_data/combat_skills.json"))
        self.weapon_scroll_area = None

        super().__init__(PCBuilderPhase.PHASE3, main_window, parent)

        self.validator = TFValidator()
        self._setup_validation_rules()

    def _setup_ui(self):
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        self.weapon_scroll = QScrollArea()
        self.weapon_scroll.setWidgetResizable(True)
        self.weapon_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.weapon_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.weapon_scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.weapon_group = WeaponGroup(self)
        self.weapon_scroll.setWidget(self.weapon_group)

        self.armour_group = ArmourGroup(self)
        self.combat_skill_group = CombatSkillGroup(self)
        self.credit_group = CreditGroup(self)

        self.mid_group = QFrame(self)
        self.mid_group.layout = QHBoxLayout(self.mid_group)
        self.mid_group.layout.setContentsMargins(0, 0, 0, 0)

        self.mid_group.layout.addWidget(self.armour_group, 3)
        self.mid_group.layout.addWidget(self.combat_skill_group, 3)
        self.mid_group.layout.addWidget(self.credit_group, 1)

        self.lower_group = LowerGroup(self)

        content_layout.addWidget(self.weapon_scroll, 2)
        content_layout.addWidget(self.mid_group, 1)
        content_layout.addWidget(self.lower_group, 2)

        self.content_area.setLayout(content_layout)

    def _setup_phase_buttons(self, button_layout):
        self.show_combat_skills_button = TFBaseButton(
            "Combat Skills",
            self,
            height=30,
            on_clicked=self._on_show_combat_skills_clicked
        )
        self.show_weapon_list_button = TFBaseButton(
            "Weapons List",
            self,
            height=30,
            on_clicked=self._on_show_weapon_list_clicked
        )
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

        button_layout.addWidget(self.show_combat_skills_button)
        button_layout.addWidget(self.show_weapon_list_button)
        button_layout.addWidget(self.complete_button)
        button_layout.addWidget(self.previous_button)

    def _setup_validation_rules(self):
        def validate_weapon_entry(entry: WeaponEntry) -> tuple[bool, str]:
            fields = {
                "Name": entry.name_entry.get_value(),
                "Category": entry.category_selector.get_value(),
                "Type": entry.type_selector.get_value(),
                "Skill": entry.skill_entry.get_value(),
                "Damage": entry.damage_entry.get_value(),
                "Range": entry.range_entry.get_value(),
                "Penetration": entry.penetration_entry.get_value(),
                "Rate of Fire": entry.rof_entry.get_value(),
                "Ammunition": entry.ammo_entry.get_value(),
                "Malfunction": entry.malfunction_entry.get_value()
            }

            empty_fields = [field for field, value in fields.items()
                            if not value or value == "None"]

            if empty_fields:
                return False, f"In weapon entry: {', '.join(empty_fields)} cannot be empty"

            return True, ""

        self.validator.add_custom_validator('weapon_entry', validate_weapon_entry)

    def _on_show_combat_skills_clicked(self):
        dialog = CombatSkillListDialog(self, self.combat_skills)
        dialog.exec()

    def _on_show_weapon_list_clicked(self):
        dialog = WeaponTypeListDialog(self, self.weapon_types)
        dialog.exec()

    def _on_complete_clicked(self):
        error_messages = []

        if self.weapon_group.weapon_entries:
            for entry in self.weapon_group.weapon_entries:
                is_valid, message = self.validator._custom_validators['weapon_entry'](entry)
                if not is_valid:
                    error_messages.append(message)

            if error_messages:
                self.main_window.app.show_warning(
                    "Validation Error",
                    "\n".join(error_messages),
                    buttons=["OK"]
                )
                return False

        self.complete_button.setEnabled(False)
        self.next_button.setEnabled(True)
        self.main_window.set_phase_status(self.phase, PhaseStatus.COMPLETED)

    def _on_previous_clicked(self):
        self.main_window._on_phase_selected(PCBuilderPhase.PHASE2)

    def _reset_content(self):
        super()._reset_content()

        if 'loadout' in self.main_window.pc_data:
            del self.main_window.pc_data['loadout']

        self.weapon_group.reset()
        
        self.armour_group.reset()
        self.combat_skill_group.reset()
        self.credit_group.reset()
        
        self.lower_group.item_group.reset()
        self.lower_group.deposit_group.reset()

        self.complete_button.setEnabled(True)
        self.next_button.setEnabled(False)

        self.main_window.set_phase_status(self.phase, PhaseStatus.NOT_START)

    def adjust_status(self):
        if self.main_window.get_phase_status(self.phase) == PhaseStatus.NOT_START:
            self.main_window.set_phase_status(self.phase, PhaseStatus.COMPLETING)
        if self.main_window.get_phase_status(self.phase) == PhaseStatus.COMPLETED:
            self.main_window.set_phase_status(self.phase, PhaseStatus.COMPLETING)
            self.complete_button.setEnabled(True)
            self.enable_next_button(False)

    def on_enter(self):
        super().on_enter()

    def on_exit(self):
        if 'loadout' not in self.main_window.pc_data:
            self.main_window.pc_data['loadout'] = {}
            
        loadout_data = {}

        weapons_data = {}
        for entry in self.weapon_group.weapon_entries:
            weapon_name = entry.name_entry.get_value()
            if weapon_name != "N/A":
                weapons_data[weapon_name] = {
                    "name": weapon_name,
                    "skill": entry.skill_entry.get_value(),
                    "damage": entry.damage_entry.get_value(),
                    "range": entry.range_entry.get_value(),
                    "penetration": entry.penetration_entry.get_value(),
                    "rate_of_fire": entry.rof_entry.get_value(),
                    "ammo": entry.ammo_entry.get_value() if entry.ammo_entry.get_value() != "N/A" else None,
                    "malfunction": entry.malfunction_entry.get_value() if entry.malfunction_entry.get_value() != "N/A" else None,
                    "category": entry.category_selector.get_value(),
                    "notes": ""
                }
        loadout_data['weapons'] = weapons_data

        combat_skill_name = self.combat_skill_group.combat_skill_selector.get_value()
        if combat_skill_name != "None":
            combat_skill_text = self.combat_skill_group.combat_skill_entry.get_value()
            loadout_data['combat_skill'] = {
                "name": combat_skill_name,
                "combat_skill": [s.strip() for s in combat_skill_text.split(",") if s.strip() != "N/A"],
                "notes": ""
            }

        armour_name = self.armour_group.name_entry.get_value()
        if armour_name != "N/A":
            armours_data = {
                armour_name: {
                    "type": self.armour_group.type_entry.get_value(),
                    "points": self.armour_group.points_entry.get_value(),
                    "coverage": self.armour_group.coverage_selector.get_value(),
                    "notes": ""
                }
            }
            loadout_data['armours'] = armours_data

        belongings_data = {}
        for widget, _, _ in self.lower_group.item_group.items:
            if isinstance(widget, QLabel):
                belongings_data[widget.text()] = {"notes": ""}
        if belongings_data:
            loadout_data['personal_belongings'] = belongings_data

        deposit_data = {}
        for widget, _, _ in self.lower_group.deposit_group.items:
            if isinstance(widget, QLabel):
                deposit_data[widget.text()] = {"notes": ""}
        if deposit_data:
            loadout_data['deposit'] = deposit_data
        
        self.main_window.pc_data['loadout'] = loadout_data
