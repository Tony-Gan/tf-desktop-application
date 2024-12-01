from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QScrollArea, QFrame, QLineEdit, QGroupBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from implements.components.base_phase import BasePhase
from implements.components.data_reader import load_skills_from_json, load_occupations_from_json
from implements.components.data_type import Occupation, Skill
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_dialog import TFBaseDialog
from ui.components.tf_base_frame import TFBaseFrame
from ui.components.tf_radio_group import TFRadioGroup
from ui.components.tf_font import NotoSerifNormal
from ui.tf_application import TFApplication
from utils.helper import resource_path


class Phase2(BasePhase):

    def _setup_content(self) -> None:
        self.selected_occupation = None
        super()._setup_content()

        self.show_occupation_list_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="职业列表", 
            height=35,
            width=120, 
            on_clicked=self._on_occupation_list_clicked
        )

        self.custom_occupation_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="自定义职业", 
            height=35,
            width=120, 
            on_clicked=self._on_custom_occupation_clicked
        )

        self.buttons_frame.add_custom_button(self.show_occupation_list_button)
        self.buttons_frame.add_custom_button(self.custom_occupation_button)

        self.custom_occupation_button.hide()

        self.upper_frame = UpperFrame(self)
        self.skills_frame = SkillsFrame(self)

        self.contents_frame.add_child("upper_frame", self.upper_frame)
        self.contents_frame.add_child("skill_frame", self.skills_frame)

    def reset_contents(self):
        self.selected_occupation = None
        basic_info = self.upper_frame.basic_info_frame
        basic_info.occupation_entry.set_text("")
        basic_info.occupation_points_entry.set_value("0")
        
        if hasattr(self, 'skills'):
            for skill in self.skills:
                skill.occupation_point = 0
                skill.interest_point = 0
                skill.is_occupation = False
                if skill.name == '信誉':
                    skill.is_occupation = True
        
        if hasattr(self.skills_frame, 'skill_entries'):
            for entry in self.skills_frame.skill_entries.values():
                entry.reset()
        
        occupation_skills_frame = self.upper_frame.occupation_skills_frame
        if hasattr(occupation_skills_frame, 'skill_entries'):
            for entry in occupation_skills_frame.skill_entries:
                occupation_skills_frame.main_layout.removeWidget(entry)
                entry.deleteLater()
            occupation_skills_frame.skill_entries.clear()
        
        basic_info.update_points_information()
        
        self.skills_frame.refresh_skill_display()

    def initialize(self):
        self.check_dependencies()

    def save_state(self):
        if 'character_info' not in self.p_data:
            self.p_data['character_info'] = {}
            
        if self.selected_occupation:
            self.p_data['character_info']['occupation'] = self.selected_occupation.name
            
        if 'skills' not in self.p_data:
            self.p_data['skills'] = {}
        
        for skill in self.skills:
            if skill.total_point > skill.default_point or skill.name == '母语' or skill.name == '闪避':
                self.p_data['skills'][skill.full_name] = skill.total_point

    def check_dependencies(self):
        self.allow_mythos = self.config['general']['allow_mythos']

        if self.config['general']['custom_occupation']:
            self.custom_occupation_button.show()

        nine_stats = ['str', 'con', 'siz', 'dex', 'app', 'int', 'pow', 'edu', 'luk']
        self.basic_stats = {k.upper(): int(self.p_data["basic_stats"][k]) for k in nine_stats}

        self.skills = load_skills_from_json(self.basic_stats["DEX"], self.basic_stats["EDU"])
        self.occupations = load_occupations_from_json()

        self.upper_frame.basic_info_frame.init_points_information()
        self.skills_frame.refresh_skill_display()

    def validate(self) -> List[Tuple[Any, str]]:
        invalid_items = []
        
        if not self.selected_occupation:
            invalid_items.append((
                self.upper_frame.basic_info_frame.occupation_entry,
                "请选择一个职业"
            ))
            return invalid_items

        occupation_limit = self.config['general']['occupation_skill_limit']
        interest_limit = self.config['general']['interest_skill_limit']
        
        credit_min = self.selected_occupation.get_credit_rating_min()
        credit_max = self.selected_occupation.get_credit_rating_max()
        
        for skill in self.skills:
            total_points = skill.total_point
            
            if skill.name == '母语':
                if total_points > occupation_limit:
                    invalid_items.append((
                        self.skills_frame.skill_entries[skill.full_name],
                        f"母语技能不能超过职业技能上限 {occupation_limit}"
                    ))
                continue
                
            if skill.name == '信誉':
                if total_points < credit_min or total_points > credit_max:
                    invalid_items.append((
                        self.skills_frame.skill_entries[skill.full_name],
                        f"信誉值必须在职业规定的范围内 ({credit_min}-{credit_max})"
                    ))
                continue
                
            if skill.is_occupation:
                if total_points > occupation_limit:
                    invalid_items.append((
                        self.skills_frame.skill_entries[skill.full_name],
                        f"职业技能 {skill.display_name} 不能超过上限 {occupation_limit}"
                    ))
            else:
                if total_points > interest_limit:
                    invalid_items.append((
                        self.skills_frame.skill_entries[skill.full_name],
                        f"兴趣技能 {skill.display_name} 不能超过上限 {interest_limit}"
                    ))
        
        return invalid_items

    def go_next(self):
        remaining_occupation = int(self.upper_frame.basic_info_frame.occupation_points_entry.get_value())
        remaining_interest = int(self.upper_frame.basic_info_frame.interest_points_entry.get_value())
        
        if remaining_occupation > 0 or remaining_interest > 0:
            warning_message = "你还有未分配的点数：\n"
            if remaining_occupation > 0:
                warning_message += f"职业点数：{remaining_occupation}\n"
            if remaining_interest > 0:
                warning_message += f"兴趣点数：{remaining_interest}\n"
            warning_message += "\n是否确定要继续？"
            
            result = TFApplication.instance().show_warning(
                "未分配点数",
                warning_message,
                ["确定", "取消"]
            )
            
            if result == "取消":
                return
                
        super().go_next()

    def _on_occupation_list_clicked(self):
        self.upper_frame.basic_info_frame._on_occupation_select()

    def _on_custom_occupation_clicked(self):
        success, custom_occupation = CustomOccupationDialog.get_input(self)
        if success and custom_occupation:
            self.occupations.append(custom_occupation)
            
            self.reset_contents()
            self.selected_occupation = custom_occupation
            
            basic_info = self.upper_frame.basic_info_frame
            basic_info.occupation_entry.set_text(custom_occupation.name)
            basic_info.occupation_points_entry.set_value(
                str(custom_occupation.calculate_skill_points(self.basic_stats))
            )
            
            for skill in custom_occupation.occupation_skills:
                if isinstance(skill, Skill):
                    for s in self.skills:
                        if s == skill:
                            s.is_occupation = True
                            break
        
            self.upper_frame.occupation_skills_frame.update_occupation_skills()
            self.skills_frame.refresh_skill_display()
            
            for entry in [
                basic_info.occupation_points_entry,
                basic_info.interest_points_entry
            ]:
                entry.value_field.setStyleSheet("color: #3498DB;")
                
            TFApplication.instance().show_message(
                f"自定义职业 '{custom_occupation.name}' 已创建并选择",
                5000,
                "green"
            )


class UpperFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedHeight(160)

        self.basic_info_frame = BasicInformationFrame(self)
        self.occupation_skills_frame = OccupationSkillsFrame(self)

        self.add_child("basic_info", self.basic_info_frame)
        self.add_child("occupation_skills", self.occupation_skills_frame)


class BasicInformationFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QGridLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedWidth(390)
        self.occupation_entry = self.create_button_entry(
            name="occupation",
            label_text="职业:",
            label_size=90,
            button_text="选择",
            button_callback=self._on_occupation_select,
            button_size=75,
            entry_size=160,
            border_radius=5,
            height=24
        )
        self.occupation_entry.set_entry_enabled(False)
        self.occupation_entry.label.setStyleSheet("color: #FFB700;")

        self.occupation_points_entry = self.create_value_entry(
            name="occupation_points",
            label_text="职业点数:",
            label_size=100,
            value_size=40,
            enable=False,
            height=24
        )

        self.interest_points_entry = self.create_value_entry(
            name="interest_points",
            label_text="兴趣点数:",
            label_size=100,
            value_size=40,
            enable=False,
            height=24
        )

        self.limit_entry = self.create_value_entry(
            name="point_limit",
            label_text="职业/兴趣上限:",
            label_size=100,
            value_size=40,
            enable=False,
            height=24,
        )

        self.allow_mix_point_entry = self.create_value_entry(
            name="mix_point",
            label_text="允许混点:",
            label_size=100,
            value_size=40,
            enable=False,
            height=24
        )

        self.main_layout.addWidget(self.occupation_entry, 0, 0, 1, 2)
        self.main_layout.addWidget(self.occupation_points_entry, 1, 0)
        self.main_layout.addWidget(self.interest_points_entry, 1, 1)
        self.main_layout.addWidget(self.limit_entry, 2, 0)
        self.main_layout.addWidget(self.allow_mix_point_entry, 2, 1)

    def init_points_information(self):
        config = self.parent.parent.config
        p_data = self.parent.parent.p_data
        self.interest_points_entry.set_value(str(int(p_data['basic_stats']['int']) * 2))

        points_limit = str(config["general"]["occupation_skill_limit"]) + "/" + str(config["general"]["interest_skill_limit"])
        self.limit_entry.set_value(points_limit)
        self.allow_mix_point_entry.set_value("是" if config["general"]["allow_mix_points"] else "否")

    def update_points_information(self):
        occupation_points_used = sum(skill.occupation_point for skill in self.parent.parent.skills)
        interest_points_used = sum(skill.interest_point for skill in self.parent.parent.skills)
        
        max_occupation_points = self.parent.parent.selected_occupation.calculate_skill_points(self.parent.parent.basic_stats) if self.parent.parent.selected_occupation else 0
        remaining_occupation_points = max_occupation_points - occupation_points_used
        self.occupation_points_entry.set_value(str(remaining_occupation_points))
        
        max_interest_points = int(self.parent.parent.p_data["basic_stats"]["int"]) * 2
        remaining_interest_points = max_interest_points - interest_points_used
        self.interest_points_entry.set_value(str(remaining_interest_points))
        
        for entry, points in [
            (self.occupation_points_entry, remaining_occupation_points),
            (self.interest_points_entry, remaining_interest_points)
        ]:
            if points > 0:
                entry.value_field.setStyleSheet("color: #3498DB;")
            elif points < 0:
                entry.value_field.setStyleSheet("color: #FF6B6B;")
            else:
                entry.value_field.setStyleSheet("color: #2ECC71;")

    def _on_occupation_select(self):
        success, selected_occupation = OccupationListDialog.get_input(
            self,
            occupations=self.parent.parent.occupations,
            basic_stats=self.parent.parent.basic_stats
        )
        if success and selected_occupation:
            self.occupation_entry.label.setStyleSheet("")
            self.parent.parent.reset_contents()
            self.parent.parent.selected_occupation = selected_occupation

            self.occupation_entry.set_text(selected_occupation.name)
            self.occupation_points_entry.set_value(selected_occupation.calculate_skill_points(self.parent.parent.basic_stats))

            for s in self.parent.parent.skills:
                s.is_occupation = False
                if s.name == '信誉':
                    s.is_occupation = True

            for s1 in selected_occupation.occupation_skills:
                if isinstance(s1, Skill):
                    if not s1.is_abstract:
                        for s2 in self.parent.parent.skills:
                            if s1 == s2:
                                s2.is_occupation = True
                                break

            self.parent.occupation_skills_frame.update_occupation_skills()
            self.parent.parent.skills_frame.refresh_skill_display()

            if '信誉' in self.parent.parent.skills_frame.skill_entries:
                self.parent.parent.skills_frame.skill_entries['信誉']._update_label_color()

            for entry in [
                self.occupation_points_entry,
                self.interest_points_entry
            ]:
                entry.value_field.setStyleSheet("color: #3498DB;")


class OccupationSkillsFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        self.skill_entries = []
        super().__init__(QGridLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

    def update_occupation_skills(self):
        for entry in self.skill_entries:
            self.main_layout.removeWidget(entry)
            entry.deleteLater()
        self.skill_entries.clear()

        selected_occupation = self.parent.parent.selected_occupation
        if not selected_occupation:
            return

        for i, skill_item in enumerate(selected_occupation.occupation_skills):
            row = i // 3
            col = i % 3
            
            if isinstance(skill_item, Skill):
                entry = OccupationSkillEntry(
                    skill_text=skill_item.display_name,
                    is_abstract=skill_item.is_abstract,
                    parent=self
                )
            else:
                entry = OccupationSkillEntry(
                    skill_text=skill_item.format_display(),
                    is_abstract=True,
                    parent=self
                )
            
            self.main_layout.addWidget(entry, row, col)
            self.skill_entries.append(entry)

        credit_entry = OccupationSkillEntry(
            skill_text=f"信誉范围: {selected_occupation.credit_rating}",
            is_abstract=False,
            parent=self
        )
        row = len(selected_occupation.occupation_skills) // 3
        col = len(selected_occupation.occupation_skills) % 3
        self.main_layout.addWidget(credit_entry, row, col)
        self.skill_entries.append(credit_entry)


class OccupationSkillEntry(TFBaseFrame):
    def __init__(self, skill_text: str, is_abstract: bool = False, parent=None):
        self.skill_text = skill_text
        self.is_abstract = is_abstract
        self.selected_skill = None
        super().__init__(QHBoxLayout, level=2, radius=5, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedHeight(30)
        self.main_layout.setContentsMargins(5, 0, 5, 0)
        
        self.skill_label = self.create_label(
            text=self.skill_text,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            height=24,
            serif=True
        )
        if self.is_abstract:
            self.skill_label.setStyleSheet("color: #FFB700;")
        self.main_layout.addWidget(self.skill_label)
        
        if self.is_abstract:
            self.select_button = self.create_button(
                name="select",
                text="",
                width=24,
                height=24,
                icon_path=resource_path("resources/images/icons/down-arrow.png"),
                on_clicked=self._on_select_clicked
            )
            self.main_layout.addWidget(self.select_button)
        else:
            self.main_layout.addStretch()

    def _on_select_clicked(self):
        if '/' in self.skill_text:
            skill_texts = [s.strip() for s in self.skill_text.split('/')]
            dialog = CombinationSkillSelectDialog(skill_texts, parent=self)
        elif self.skill_text == "交涉技能 - 任意":
            dialog = SimpleSkillSelectDialog("选择交涉技能", "交涉技能", parent=self)
        elif self.skill_text == "任意技能":
            dialog = GroupedSkillSelectDialog(parent=self)
        elif ':任意' in self.skill_text or self.is_abstract:
            skill_type = self.skill_text.split('-')[0].strip()
            dialog = SimpleSkillSelectDialog(f"选择{skill_type}技能", skill_type, parent=self)
            
        dialog.exec()

    def handle_skill_selection(self, selected_skill: Skill):
        if self.selected_skill:
            self.selected_skill.is_occupation = False

        self.selected_skill = selected_skill
        self.skill_label.setText(selected_skill.display_name)
        self.skill_label.setStyleSheet("")
        selected_skill.is_occupation = True
        self.parent.parent.parent.skills_frame.refresh_skill_display()



class SkillsFrame(TFBaseFrame):
    PARENT_SKILL_DEFAULTS = {
        "技艺": 5,
        "格斗": 5,
        "火器": 10,
        "语言": 1,
        "驾驶": 1,
        "科学": 1,
        "生存": 10,
    }
    def __init__(self,  parent=None):
        self.skill_entries = {}
        super().__init__(QGridLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(2, 2, 2, 2)

    def _on_expand_skill(self, skill_type: str):
        dialog = SkillExpandDialog(
            skill_type=skill_type,
            title=f"{skill_type}",
            parent=self
        )
        dialog.exec()

    def _on_add_new_skill(self):
        success, result = NewSkillDialog.get_input(self)
        if success and result:
            skill_name, base_value = result
            
            if ':' in skill_name:
                super_name, name = skill_name.split(':')
            else:
                super_name, name = None, skill_name
                
            new_skill = Skill(
                name=name,
                super_name=super_name,
                default_point=base_value
            )
            
            self.parent.skills.append(new_skill)
            self.refresh_skill_display()

            TFApplication.instance().show_message(f"技能{new_skill.display_name}已添加", 5000, 'green')

    def refresh_skill_display(self):
        for entry in self.skill_entries.values():
            self.main_layout.removeWidget(entry)
            entry.deleteLater()
        self.skill_entries.clear()

        mythos = self.parent.allow_mythos

        if hasattr(self, 'buttons_frame'):
            self.main_layout.removeWidget(self.buttons_frame)
            self.buttons_frame.deleteLater()

        skills = self.parent.skills if hasattr(self.parent, 'skills') else []
        row = 0
        col = 0
        
        for skill in sorted(skills, key=lambda x: x.display_name):
            if not skill.super_name:
                if not mythos and skill.name == '克苏鲁神话':
                    continue
                entry = SkillEntry(skill, parent=self)
                self.skill_entries[skill.full_name] = entry
                
                self.main_layout.addWidget(entry, row, col)
                
                col += 1
                if col == 4:
                    col = 0
                    row += 1

        button_row = row + (1 if col > 0 else 0)
        
        self.buttons_frame = TFBaseFrame(QHBoxLayout, level=1, radius=5, parent=self)
        self.buttons_frame.main_layout.setContentsMargins(5, 5, 5, 5)
        self.buttons_frame.main_layout.setSpacing(5)
        
        for skill_type in self.PARENT_SKILL_DEFAULTS:
            def create_callback(skill_type=skill_type):
                return lambda: self._on_expand_skill(skill_type)
            
            has_occupation_skill = False
            for skill in self.parent.skills:
                if (skill.super_name == skill_type and 
                    skill.is_occupation):
                    has_occupation_skill = True
                    break
                
            btn = self.create_button(
                name=f"expand_{skill_type}",
                text=f"{skill_type}",
                height=24,
                width=90,
                on_clicked=create_callback()
            )

            if has_occupation_skill:
                btn._text_color = QColor("#3498DB")
                btn.update()

            self.buttons_frame.main_layout.addWidget(btn)
            
        self.create_skill_btn = self.create_button(
            name="create_skill",
            text="新增技能",
            height=24,
            width=90,
            on_clicked=self._on_add_new_skill
        )
        self.buttons_frame.main_layout.addWidget(self.create_skill_btn)
        
        self.main_layout.addWidget(self.buttons_frame, button_row, 0, 1, 4)

    def reset_all_skills(self):
        for entry in self.skill_entries.values():
            entry.reset()


class SkillEntry(TFBaseFrame):
    def __init__(self, skill: Skill, level=1, expand=False, parent=None):
        self.skill = skill
        self.expand = expand
        self.parent = parent
        super().__init__(QHBoxLayout, level=level, radius=5, parent=parent)
        self.setFixedHeight(24)
        
    def _setup_content(self) -> None:
        self.main_layout.setContentsMargins(5, 0, 5, 0)
        self.main_layout.setSpacing(10)
        
        self.skill_label = self.create_label(
            text=self.skill.display_name,
            alignment= Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            fixed_width=60 if not self.expand else 110,
            height=24,
            serif=True
        )
        self._update_label_color()
        
        self.occupation_points = self.create_number_receiver(
            name="occupation_points",
            text="0",
            alignment=Qt.AlignmentFlag.AlignCenter,
            width=22,
            max_digits=2
        )
        self.occupation_points.setEnabled(self.skill.is_occupation)
        self.occupation_points.textChanged.connect(self._on_points_changed)
        
        self.interest_points = self.create_number_receiver(
            name="interest_points",
            text="0",
            alignment=Qt.AlignmentFlag.AlignCenter,
            width=22,
            max_digits=2
        )
        self.interest_points.textChanged.connect(self._on_points_changed)
        
        self.default_points = self.create_number_receiver(
            name="default_points",
            text=str(self.skill.default_point),
            alignment=Qt.AlignmentFlag.AlignCenter,
            width=22
        )
        self.default_points.setEnabled(False)
        
        self.total_points = self.create_number_receiver(
            name="total_points",
            text=str(self.skill.default_point),
            alignment=Qt.AlignmentFlag.AlignCenter,
            width=22
        )
        self.total_points.setEnabled(False)
        
        self.main_layout.addWidget(self.skill_label)
        self.main_layout.addWidget(self.occupation_points)
        self.main_layout.addWidget(self.interest_points)
        self.main_layout.addWidget(self.default_points)
        self.main_layout.addWidget(self.total_points)
        self.main_layout.addStretch()

    def _find_phase2_parent(self):
        current = self.parent
        while current and not isinstance(current, Phase2):
            current = current.parent
        return current

    def _update_label_color(self):
        phase2 = self._find_phase2_parent()
        if not phase2:
            return
            
        occupation_limit = phase2.config['general']['occupation_skill_limit']
        interest_limit = phase2.config['general']['interest_skill_limit']

        if self.skill.name == '信誉':
            if phase2.selected_occupation:
                min_credit = phase2.selected_occupation.get_credit_rating_min()
                max_credit = phase2.selected_occupation.get_credit_rating_max()
                total_points = self.skill.total_point
                if total_points < min_credit or total_points > max_credit:
                    self.skill_label.setStyleSheet("color: #FF6B6B;")
                    return
        
        if self.skill.is_occupation:
            if self.skill.total_point > occupation_limit:
                self.skill_label.setStyleSheet("color: #FF6B6B;")
            else:
                self.skill_label.setStyleSheet("color: #3498DB;")
        elif self.skill.interest_point > 0:
            if self.skill.total_point > interest_limit:
                self.skill_label.setStyleSheet("color: #FF6B6B;")
            else:
                self.skill_label.setStyleSheet("color: #2ECC71;")
        else:
            self.skill_label.setStyleSheet("")

    def _on_points_changed(self):
        self.skill.occupation_point = int(self.occupation_points.text() or 0)
        self.skill.interest_point = int(self.interest_points.text() or 0)
        self.total_points.setText(str(self.skill.total_point))
        self._update_label_color()
        
        self.parent.parent.upper_frame.basic_info_frame.update_points_information()
            
    def reset(self):
        self.occupation_points.setText("0")
        self.interest_points.setText("0")
        self._update_label_color()
        self.total_points.setText(str(self.skill.default_point))


class OccupationListDialog(TFBaseDialog):

    def __init__(self, parent=None, occupations: List[Occupation] = None, basic_stats: Dict[str, str] = None):
        self.occupations = occupations
        self.basic_stats = basic_stats
        
        self.categories = set()
        for occupation in occupations:
            self.categories.update(occupation.category)
        self.categories = sorted(list(self.categories))
        
        self._selected_occupation = None
        self._entry_widgets = []

        super().__init__(title="选择职业", layout_type=QVBoxLayout, parent=parent, button_config=[])

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
        self.name_filter.setPlaceholderText("根据名称筛选...")
        self.name_filter.textChanged.connect(self._debounce_filter)
        
        category_options = ["None"] + self.categories
        self.category_filter = self.create_option_entry(
            name="category_filter",
            label_text="类型:",
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
        self.skill_filter.setPlaceholderText("根据技能筛选... (WIP)")
        
        self.reset_button = self.create_button(
            name="reset_filter",
            text="重置筛选",
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
        name_filter = self.name_filter.text()
        category_filter = self.category_filter.get_value()

        for entry in self._entry_widgets:
            show = True
            
            if name_filter and name_filter not in entry.occupation.name:
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
        font = QFont("Noto Serif SC Light")
        font.setPointSize(10)

        title_font = QFont("Noto Serif SC")
        title_font.setPointSize(12)

        name_label = self.create_label(
            self.occupation.name,
            fixed_width=None,
            height=30
        )
        name_label.setFont(title_font)
        self.main_layout.addWidget(name_label)

        formula_label = self.create_label(
            f"职业点计算：{self.occupation.format_formula_for_display()}",
            height=24,
            serif=True
        )
        formula_label.setFont(font)
        self.main_layout.addWidget(formula_label)

        calculated_points = self.occupation.calculate_skill_points(self.basic_stats)
        points_entry = self.create_value_entry(
            name="points",
            label_text="可用职业点:",
            value_text=str(calculated_points),
            label_size=70,
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
            f"职业技能：{self.occupation.format_skills()}",
            height=24,
            serif=True
        )
        skills_label.setFont(font)
        self.main_layout.addWidget(skills_label)

        categories_label = self.create_label(
            f"类型：{', '.join(self.occupation.category)}",
            height=24,
            serif=True
        )
        categories_label.setFont(font)
        self.main_layout.addWidget(categories_label)

        credit_label = self.create_label(
            f"信用范围：{self.occupation.credit_rating}",
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


class SkillExpandDialog(TFBaseDialog):
    def __init__(self, skill_type: str, title: str, parent=None):
        self.skill_type = skill_type
        self.parent = parent
        self.skill_entries = {}
        super().__init__(
            title=title,
            layout_type=QVBoxLayout,
            parent=parent,
            button_config=[]
        )
        
    def _setup_content(self) -> None:
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(20)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_content = TFBaseFrame(QVBoxLayout, parent=scroll)
        scroll.setWidget(scroll_content)
        
        skills = sorted(
            [s for s in self.parent.parent.skills if s.super_name == self.skill_type],
            key=lambda x: x.name
        )
        
        for skill in skills:
            entry = SkillEntry(skill, level=0, expand=True, parent=self)
            scroll_content.main_layout.addWidget(entry)
            self.skill_entries[skill.name] = entry
            
        buttons_frame = TFBaseFrame(QHBoxLayout, level=0, parent=scroll_content)
        
        add_btn = self.create_button(
            name="add_skill",
            text="+",
            width=24,
            height=24,
            on_clicked=self._on_add_clicked
        )
        
        remove_btn = self.create_button(
            name="remove_skill",
            text="-",
            width=24,
            height=24,
            on_clicked=self._on_remove_clicked
        )
        
        buttons_frame.main_layout.addWidget(add_btn)
        buttons_frame.main_layout.addWidget(remove_btn)
        buttons_frame.main_layout.addStretch()
        
        scroll_content.main_layout.addWidget(buttons_frame)
        scroll_content.main_layout.addStretch()
        
        self.main_layout.addWidget(scroll)
        
    def _on_add_clicked(self):
        input_field = self.create_line_edit(
            name="new_skill_input",
            height=30
        )
        input_field.setPlaceholderText("输入技能名...")
        
        scroll_content = self.content_frame.findChild(TFBaseFrame)
        buttons_frame = scroll_content.findChild(TFBaseFrame)
        index = scroll_content.main_layout.indexOf(buttons_frame)
        scroll_content.main_layout.insertWidget(index, input_field)
        
        input_field.setFocus()
        input_field.focusOutEvent = lambda e: self._on_input_focus_lost(e, input_field)
        
    def _on_input_focus_lost(self, event, input_field: QLineEdit):
        skill_name = input_field.text().strip()
        if skill_name:
            if any(s.name == skill_name and s.super_name == self.skill_type
                   for s in self.parent.parent.skills):
                TFApplication.instance().show_message("技能已经存在", 5000,"yellow")
                input_field.deleteLater()
                return
            
            new_skill = Skill(
                name=skill_name,
                super_name=self.skill_type,
                default_point=self.parent.PARENT_SKILL_DEFAULTS.get(self.skill_type, 1)
            )
            
            self.parent.parent.skills.append(new_skill)
            
            entry = SkillEntry(new_skill, level=0, expand=True, parent=self)
            self.skill_entries[new_skill.name] = entry
            
            scroll_content = self.content_frame.findChild(TFBaseFrame)
            buttons_frame = scroll_content.findChild(TFBaseFrame)
            index = scroll_content.main_layout.indexOf(buttons_frame)
            scroll_content.main_layout.insertWidget(index, entry)
            
        input_field.deleteLater()
        
    def _on_remove_clicked(self):
        scroll_content = self.content_frame.findChild(TFBaseFrame)
        buttons_frame = scroll_content.findChild(TFBaseFrame)
        index = scroll_content.main_layout.indexOf(buttons_frame) - 1
        
        if index >= 0:
            widget = scroll_content.main_layout.itemAt(index).widget()
            if isinstance(widget, SkillEntry):
                self.parent.parent.skills.remove(widget.skill)
                widget.deleteLater()
                if widget.skill.name in self.skill_entries:
                    del self.skill_entries[widget.skill.name]


class BaseSkillSelectDialog(TFBaseDialog):
    def __init__(self, title: str, parent=None):
        self.parent = parent
        super().__init__(
            title=title,
            layout_type=QGridLayout,
            parent=parent,
            button_config=[]
        )
        
    def _setup_content(self) -> None:
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

    def _on_selection_changed(self, selected_skill: Skill):
        self.parent.handle_skill_selection(selected_skill)
        self.accept()

    def _disable_occupied_skills(self, radio_group: TFRadioGroup, skill_map: Dict[str, Skill]) -> None:
        for radio_with_label in radio_group.radio_buttons:
            text = radio_with_label.get_text()
            if text and text in skill_map and skill_map[text].is_occupation:
                radio_with_label.setEnabled(False)
        
    def get_result(self) -> Optional[Skill]:
        return self._result
    

class SimpleSkillSelectDialog(BaseSkillSelectDialog):
    def __init__(self, title: str, skill_type: str = None, parent=None):
        self.skills = parent.parent.parent.parent.skills
        self.skill_type = skill_type
        super().__init__(title=title, parent=parent)

    def _setup_content(self) -> None:
        super()._setup_content()
        available_skills = (
            [skill for skill in self.skills if skill.name in ["取悦", "话术", "恐吓", "说服"]]
            if self.skill_type == "交涉技能"
            else [skill for skill in self.skills if skill.super_name == self.skill_type]
        )
        available_skills.sort(key=lambda x: x.display_name)
        
        self.skill_map = {skill.display_name: skill for skill in available_skills}
        
        self.radio_group = self.create_radio_group(
            name="skill_options",
            options=[skill.display_name for skill in available_skills],
            spacing=10
        )
        
        for i, radio in enumerate(self.radio_group.radio_buttons):
            row = i // 4
            col = i % 4
            self.main_layout.addWidget(radio, row, col)
        
        self._disable_occupied_skills(self.radio_group, self.skill_map)
        
        self.radio_group.value_changed.connect(lambda x: self._on_selection_changed(self.skill_map[x]))
    

class GroupedSkillSelectDialog(BaseSkillSelectDialog):
    def __init__(self, parent=None):
        self.skills = parent.parent.parent.parent.skills
        self.skill_map = {}
        super().__init__(title="选择技能", parent=parent)
        
    def _setup_content(self) -> None:
        super()._setup_content()
        frame = TFBaseFrame(QVBoxLayout, parent=self)
        
        independent_skills = sorted([s for s in self.skills if not s.super_name], 
                                key=lambda x: x.display_name)
            
        if independent_skills:
            independent_group = QGroupBox("独立技能", parent=frame)
            group_layout = QGridLayout(independent_group)
            
            self.skill_map.update({skill.display_name: skill for skill in independent_skills})
            if self.parent.parent.parent.parent.config['general']['allow_mythos']:
                options = [skill.display_name for skill in independent_skills]
            else:
                options = [skill.display_name for skill in independent_skills if skill.name != '克苏鲁神话']
            radio_group = self.create_radio_group(
                name="independent_skills",
                options=options,
                layout_type=QGridLayout,
                spacing=10
            )
            
            for i, radio in enumerate(radio_group.radio_buttons):
                row = i // 4
                col = i % 4
                group_layout.addWidget(radio, row, col)
            
            self._disable_occupied_skills(radio_group, self.skill_map)
            radio_group.value_changed.connect(lambda x: self._on_selection_changed(self.skill_map[x]))
            frame.main_layout.addWidget(independent_group)
        
        parent_types = sorted(set(
            skill.super_name for skill in self.skills
            if skill.super_name is not None
        ))
        
        for parent_type in parent_types:
            skills = sorted([s for s in self.skills if s.super_name == parent_type],
                          key=lambda x: x.display_name)
            if skills:
                type_group = QGroupBox(parent_type, parent=frame)
                group_layout = QGridLayout(type_group)
                
                self.skill_map.update({skill.display_name: skill for skill in skills})
                radio_group = self.create_radio_group(
                    name=f"group_{parent_type}",
                    options=[skill.display_name for skill in skills],
                    layout_type=QGridLayout,
                    spacing=10
                )
                
                for i, radio in enumerate(radio_group.radio_buttons):
                    row = i // 4
                    col = i % 4
                    group_layout.addWidget(radio, row, col)
                
                self._disable_occupied_skills(radio_group, self.skill_map)
                radio_group.value_changed.connect(lambda x: self._on_selection_changed(self.skill_map[x]))
                frame.main_layout.addWidget(type_group)
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(frame)
        
        self.main_layout.addWidget(scroll)
        self.resize(840, 800)


class CombinationSkillSelectDialog(BaseSkillSelectDialog):
    def __init__(self, skill_texts: List[str], parent=None):
        self.skills = parent.parent.parent.parent.skills
        self.skill_texts = skill_texts
        super().__init__(title="选择一项技能", parent=parent)
        
    def _setup_content(self) -> None:
        super()._setup_content()
        available_skills = []
        
        for skill_text in self.skill_texts:
            if '任意' in skill_text:
                skill_type = skill_text.split('-')[0].strip()
                skills = [s for s in self.skills if s.super_name == skill_type]
                available_skills.extend(skills)
            else:
                skill = next(
                    (s for s in self.skills 
                    if s.name == skill_text or 
                    (s.super_name and f"{s.super_name} - {s.name}" == skill_text)),
                    None
                )
                if skill:
                    available_skills.append(skill)
        
        available_skills.sort(key=lambda x: x.display_name)
        
        self.skill_map = {skill.display_name: skill for skill in available_skills}
        self.radio_group = self.create_radio_group(
            name="skill_options",
            options=[skill.display_name for skill in available_skills],
            layout_type=QGridLayout, 
            spacing=10
        )
        
        self._disable_occupied_skills(self.radio_group, self.skill_map)
        
        self.radio_group.value_changed.connect(lambda x: self._on_selection_changed(self.skill_map[x]))
        self.main_layout.addWidget(self.radio_group)


class NewSkillDialog(TFBaseDialog):
    def __init__(self, parent=None):
        self.parent = parent
        self.all_grouped_skills = set(s.super_name for s in parent.parent.skills if s.super_name)
        super().__init__(title="新增技能", parent=parent, button_config=[{"text": "确定", "callback": self._on_ok_clicked}])

    def _setup_content(self) -> None:
        self.resize(350, 250)
        self.main_layout.setSpacing(15)

        options = ["独立技能"]
        for skill in sorted(self.all_grouped_skills):
            options.append(skill)
            
        self.skill_category = self.create_option_entry(
            name="category",
            label_text="技能类别:",
            options=options,
            current_value="独立技能",
            label_size=70,
            value_size=150
        )
        
        self.skill_name = self.create_value_entry(
            name="name",
            label_text="技能名称:",
            label_size=70,
            value_size=150
        )
        
        self.base_value = self.create_value_entry(
            name="base_value",
            label_text="基础值:",
            label_size=70,
            value_size=150,
            value_text="0",
            number_only=True,
            allow_decimal=False,
            max_digits=2
        )

        self.main_layout.addWidget(self.skill_category)
        self.main_layout.addWidget(self.skill_name)
        self.main_layout.addWidget(self.base_value)
        self.main_layout.addStretch()

    def validate(self) -> List[Tuple[Any, str]]:
        invalid_items = []
        
        name = self.skill_name.get_value().strip()
        if not name:
            invalid_items.append((self.skill_name, "技能名称不能为空"))
            
        try:
            base_value = int(self.base_value.get_value())
            if base_value < 0:
                invalid_items.append((self.base_value, "基础值不能为负数"))
            elif base_value > 99:
                invalid_items.append((self.base_value, "基础值不能超过99"))
        except ValueError:
            invalid_items.append((self.base_value, "请输入有效的基础值"))
            
        category = self.skill_category.get_value()
        if category == "独立技能":
            super_name = None
        else:
            super_name = category
            
        skill_name = name.lower().replace(" ", "_")
        existing_skill = next(
            (s for s in self.parent.parent.skills 
             if s.name == skill_name and s.super_name == super_name),
            None
        )
        
        if existing_skill:
            parent_name = "独立技能" if super_name is None else super_name
            invalid_items.append(
                (self.skill_name, 
                 f"在{parent_name}下已存在名为'{name}'的技能。请使用其他名称。")
            )
            
        return invalid_items

    def get_validated_data(self) -> Tuple[str, int]:
        category = self.skill_category.get_value()
        base_value = int(self.base_value.get_value())
        
        if category == "独立技能":
            final_name = self.skill_name.get_value()
        else:
            final_name = f"{category}:{self.skill_name.get_value()}"
            
        return final_name, base_value


class CustomSkillSelectDialog(BaseSkillSelectDialog):
    def __init__(self, parent=None, skills=None):
        self.parent_dialog = parent
        self.skills = skills
        self.skill_map = {}
        super().__init__(title="选择职业技能", parent=parent)

    def _setup_content(self) -> None:
        super()._setup_content()
        
        add_new_btn = self.create_button(
            name="add_new_skill",
            text="新增技能",
            width=100,
            height=24,
            on_clicked=self._on_add_new_skill
        )
        self.layout.insertWidget(0, add_new_btn)
        
        frame = TFBaseFrame(QVBoxLayout, parent=self)
        
        independent_skills = sorted(
            [s for s in self.skills if not s.super_name],
            key=lambda x: x.display_name
        )
            
        if independent_skills:
            independent_group = QGroupBox("独立技能", parent=frame)
            group_layout = QGridLayout(independent_group)
            
            self.skill_map.update({skill.display_name: skill for skill in independent_skills})
            if self.parent.parent.config['general']['allow_mythos']:
                options = [skill.display_name for skill in independent_skills]
            else:
                options = [skill.display_name for skill in independent_skills if skill.name != '克苏鲁神话']
                
            radio_group = self.create_radio_group(
                name="independent_skills",
                options=options,
                layout_type=QGridLayout,
                spacing=10
            )
            
            for i, radio in enumerate(radio_group.radio_buttons):
                row = i // 4
                col = i % 4
                group_layout.addWidget(radio, row, col)
            
            radio_group.value_changed.connect(
                lambda x: self._on_selection_changed(self.skill_map[x])
            )
            frame.main_layout.addWidget(independent_group)
        
        parent_types = sorted(set(
            skill.super_name for skill in self.skills
            if skill.super_name is not None
        ))
        
        for parent_type in parent_types:
            skills = sorted(
                [s for s in self.skills if s.super_name == parent_type],
                key=lambda x: x.display_name
            )
            if skills:
                type_group = QGroupBox(parent_type, parent=frame)
                group_layout = QGridLayout(type_group)
                
                self.skill_map.update({skill.display_name: skill for skill in skills})
                radio_group = self.create_radio_group(
                    name=f"group_{parent_type}",
                    options=[skill.display_name for skill in skills],
                    layout_type=QGridLayout,
                    spacing=10
                )
                
                for i, radio in enumerate(radio_group.radio_buttons):
                    row = i // 4
                    col = i % 4
                    group_layout.addWidget(radio, row, col)
                
                radio_group.value_changed.connect(
                    lambda x: self._on_selection_changed(self.skill_map[x])
                )
                frame.main_layout.addWidget(type_group)
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(frame)
        
        self.main_layout.addWidget(scroll)
        self.resize(840, 800)

    def _on_selection_changed(self, selected_skill: Skill):
        self._result = selected_skill
        self.accept()

    def _on_add_new_skill(self):
        success, result = NewSkillDialog.get_input(self)
        if success and result:
            skill_name, base_value = result
            
            if ':' in skill_name:
                super_name, name = skill_name.split(':')
            else:
                super_name, name = None, skill_name
                
            new_skill = Skill(
                name=name,
                super_name=super_name,
                default_point=base_value
            )
            
            self.skills.append(new_skill)
            self._result = new_skill
            self.accept()


class CustomOccupationDialog(TFBaseDialog):
    def __init__(self, parent=None):
        self.parent = parent
        self.skills = parent.skills
        self.basic_stats = parent.basic_stats
        self.occupation_skills = []
        super().__init__(
            title="自定义职业",
            parent=parent,
            button_config=[{"text": "确定", "callback": self._on_ok_clicked}]
        )

    def _setup_content(self) -> None:
        self.resize(600, 380)
        self.main_layout.setSpacing(20)

        basic_info = TFBaseFrame(QGridLayout, parent=self)
        
        self.name_entry = self.create_value_entry(
            name="occupation_name",
            label_text="职业名称:",
            label_size=75,
            value_size=200
        )
        basic_info.main_layout.addWidget(self.name_entry, 0, 0, 1, 2)

        self.calc_type = self.create_option_entry(
            name="calc_type",
            label_text="计算方式:",
            options=["单一属性", "复合属性"],
            current_value="单一属性",
            label_size=75,
            value_size=200
        )
        self.calc_type.value_changed.connect(self._on_calc_type_changed)
        basic_info.main_layout.addWidget(self.calc_type, 1, 0, 1, 2)

        stats = ["STR", "CON", "SIZ", "DEX", "APP", "INT", "POW", "EDU"]
        self.stat1 = self.create_option_entry(
            name="stat1",
            label_text="计算属性:",
            options=stats,
            label_size=75,
            value_size=100
        )
        self.stat2 = self.create_option_entry(
            name="stat2",
            label_text="第二属性:",
            options=stats,
            label_size=75,
            value_size=100
        )
        basic_info.main_layout.addWidget(self.stat1, 2, 0)
        basic_info.main_layout.addWidget(self.stat2, 2, 1)
        self.stat2.setVisible(False)

        self.points_display = self.create_value_entry(
            name="available_points",
            label_text="可用技能点:",
            label_size=75,
            value_size=100,
            enable=False
        )
        basic_info.main_layout.addWidget(self.points_display, 3, 0)
        
        credit_frame = TFBaseFrame(QHBoxLayout, parent=self)
        self.credit_min = self.create_value_entry(
            name="credit_min",
            label_text="信用范围:",
            label_size=75,
            value_size=50,
            number_only=True,
            value_text="0"
        )
        self.credit_max = self.create_value_entry(
            name="credit_max",
            label_text="到",
            label_size=30,
            value_size=50,
            number_only=True,
            value_text="0"
        )
        credit_frame.main_layout.addWidget(self.credit_min)
        credit_frame.main_layout.addWidget(self.credit_max)
        basic_info.main_layout.addWidget(credit_frame, 4, 0)

        self.main_layout.addWidget(basic_info)

        skills_frame = TFBaseFrame(QVBoxLayout, parent=self)
        skills_header = TFBaseFrame(QHBoxLayout, parent=skills_frame)
        
        label = self.create_label("职业技能:", fixed_width=60)
        label.setFont(NotoSerifNormal)
        skills_header.main_layout.addWidget(label)
        
        self.add_skill_btn = self.create_button(
            name="add_skill",
            text="+",
            width=24,
            height=24,
            on_clicked=self._add_skill_entry
        )
        skills_header.main_layout.addWidget(self.add_skill_btn)
        skills_header.main_layout.addStretch()
        
        skills_frame.main_layout.addWidget(skills_header)
        
        self.skills_container = TFBaseFrame(QVBoxLayout, parent=skills_frame)
        skills_frame.main_layout.addWidget(self.skills_container)
        
        self.main_layout.addWidget(skills_frame)
        
        self._add_skill_entry()
        
        self._update_points_display()

    def _on_calc_type_changed(self, value: str):
        self.stat2.setVisible(value == "复合属性")
        self._update_points_display()

    def _add_skill_entry(self):
        if len(self.occupation_skills) >= 8:
            return
            
        skill_entry = TFBaseFrame(QHBoxLayout, parent=self.skills_container)
        
        skill_label = self.create_value_entry(
            name=f"skill_{len(self.occupation_skills)}",
            label_text=f"技能 {len(self.occupation_skills) + 1}:",
            label_size=60,
            value_size=200,
            enable=False
        )
        
        select_btn = self.create_button(
            name=f"select_{len(self.occupation_skills)}",
            text="选择",
            width=60,
            on_clicked=lambda: self._select_skill(skill_label)
        )
        
        remove_btn = self.create_button(
            name=f"remove_{len(self.occupation_skills)}",
            text="-",
            width=24,
            on_clicked=lambda: self._remove_skill_entry(skill_entry)
        )
        
        skill_entry.main_layout.addWidget(skill_label)
        skill_entry.main_layout.addWidget(select_btn)
        skill_entry.main_layout.addWidget(remove_btn)
        
        self.skills_container.main_layout.addWidget(skill_entry)
        self.occupation_skills.append(None)
        
        if len(self.occupation_skills) >= 8:
            self.add_skill_btn.setEnabled(False)

    def _remove_skill_entry(self, entry):
        index = self.skills_container.main_layout.indexOf(entry)
        if index >= 0:
            self.skills_container.main_layout.itemAt(index).widget().deleteLater()
            self.occupation_skills.pop(index)
            self.add_skill_btn.setEnabled(True)
            self._update_skill_labels()

    def _update_skill_labels(self):
        for i, entry in enumerate(self._iter_skill_entries()):
            label = entry.main_layout.itemAt(0).widget()
            label.label.setText(f"技能 {i + 1}:")

    def _iter_skill_entries(self):
        for i in range(self.skills_container.main_layout.count()):
            widget = self.skills_container.main_layout.itemAt(i).widget()
            if isinstance(widget, TFBaseFrame):
                yield widget

    def _select_skill(self, label_widget):
        dialog = CustomSkillSelectDialog(self, self.skills)
        if dialog.exec() == self.DialogCode.Accepted:
            selected_skill = dialog.get_result()
            if selected_skill:
                for entry in self._iter_skill_entries():
                    if entry.main_layout.itemAt(0).widget() == label_widget:
                        index = self.skills_container.main_layout.indexOf(entry)
                        self.occupation_skills[index] = selected_skill
                        label_widget.set_value(selected_skill.display_name)
                        break

    def _update_points_display(self):
        if not hasattr(self, 'stat1'):
            return
            
        stat1_val = self.basic_stats.get(self.stat1.get_value(), 0)
        points = stat1_val * 4
        
        if self.calc_type.get_value() == "复合属性":
            stat2_val = self.basic_stats.get(self.stat2.get_value(), 0)
            points = (stat1_val + stat2_val) * 2
            
        self.points_display.set_value(str(points))

    def validate(self) -> List[Tuple[Any, str]]:
        invalid_items = []
        
        name = self.name_entry.get_value().strip()
        if not name:
            invalid_items.append((self.name_entry, "职业名称不能为空"))
        elif any(o.name == name for o in self.parent.occupations):
            invalid_items.append((self.name_entry, "该职业名称已存在"))
            
        if not any(skill is not None for skill in self.occupation_skills):
            invalid_items.append((self.add_skill_btn, "至少需要选择一个职业技能"))
            
        try:
            credit_min = int(self.credit_min.get_value())
            credit_max = int(self.credit_max.get_value())
            if credit_min >= credit_max:
                invalid_items.append((self.credit_min, "信用最小值必须小于最大值"))
            if credit_min < 0 or credit_max > 99:
                invalid_items.append((self.credit_min, "信用范围必须在0-99之间"))
        except ValueError:
            invalid_items.append((self.credit_min, "请输入有效的信用范围"))
            
        return invalid_items

    def get_validated_data(self) -> Occupation:
        name = self.name_entry.get_value().strip()
        
        if self.calc_type.get_value() == "单一属性":
            formula = f"{self.stat1.get_value()}*4"
        else:
            formula = f"{self.stat1.get_value()}*2+{self.stat2.get_value()}*2"
            
        skills = [skill for skill in self.occupation_skills if skill is not None]
        
        credit_range = f"{self.credit_min.get_value()}-{self.credit_max.get_value()}"
        
        return Occupation(
            name=name,
            skill_points_formula=formula,
            occupation_skills=skills,
            category=["自定义"],
            credit_rating=credit_range
        )
    
