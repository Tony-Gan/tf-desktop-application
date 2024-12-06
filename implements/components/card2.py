import json
from typing import Any, List, Tuple

from PyQt6.QtWidgets import QHBoxLayout, QGridLayout, QScrollArea, QFrame
from PyQt6.QtCore import Qt

from implements.components.base_card import BaseCard
from ui.components.tf_base_dialog import TFBaseDialog
from ui.components.tf_base_frame import TFBaseFrame
from utils.helper import resource_path


class Card2(BaseCard):
    SKILL_NAME_MAPPING = {
        "图书馆使用": "图书馆",
        "计算机科学": "计算科学",
        "克苏鲁神话": "克苏鲁",
        "火焰喷射器": "炎喷射器",
    }
    def __init__(self, parent=None):
        self.showing_all = False
        self.default_skills = {}
        self.current_skills = {}
        self.default_skills = self._load_default_skills()
        super().__init__(parent=parent)

    def _setup_content(self):
        self.skills_frame = SkillsFrame(self)
        self.buttons_frame = ButtonsFrame(self)

        self.add_child('skills_frame', self.skills_frame)
        self.add_child('buttons_frame', self.buttons_frame)

    def _load_default_skills(self):
        with open(resource_path('implements/data/default_skills.json'), 'r', encoding='utf-8') as f:
            return json.load(f)

    def toggle_skills_display(self):
        layout = self.skills_frame.content_widget.main_layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.showing_all = not self.showing_all
        if self.showing_all:
            self.buttons_frame.expand_collapse_button.setText("显示修改")
            self._show_all_skills()
        else:
            self.buttons_frame.expand_collapse_button.setText("显示全部")
            self._show_modified_skills()

    def _show_modified_skills(self):
        self._display_skills(self.current_skills)

    def _show_all_skills(self):
        all_skills = {}
        all_skills.update(self.current_skills)
        
        for skill_name, default_value in self.default_skills.items():
            if skill_name not in self.current_skills:
                all_skills[skill_name] = {
                    'total_point': default_value,
                    'is_default': True
                }
        
        self._display_skills(all_skills)

    def _display_skills(self, skills):
        layout = self.skills_frame.content_widget.main_layout 
        row = 0
        col = 0
        
        for skill_name, skill_data in skills.items():
            name = skill_name.split(':')[-1]
            total_point = skill_data.get('total_point', 0) + skill_data.get('extra_point', 0)
            
            entry = self.skills_frame.content_widget.create_value_entry(
                name=skill_name,
                label_text=self.SKILL_NAME_MAPPING.get(name, name) + ':',
                value_text=str(total_point),
                value_size=24,
                label_size=60,
                number_only=True,
                allow_decimal=False,
                max_digits=2,
                enable=self.parent.edit_mode
            )
            entry.value_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            layout.addWidget(entry, row, col)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def load_data(self, p_data):
        self.showing_all = False
        self.buttons_frame.expand_collapse_button.setText("显示全部")
        self.current_skills = p_data.get('skills', {})
        self._show_modified_skills()

        self.buttons_frame.expand_collapse_button.setEnabled(True)

    def enable_edit(self):
        layout = self.skills_frame.content_widget.main_layout
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if hasattr(widget, 'set_enable'): 
                widget.set_enable(True)
                
        self.buttons_frame.add_button.show()
        self.buttons_frame.delete_button.show()
        self.buttons_frame.add_button.setEnabled(True)
        self.buttons_frame.delete_button.setEnabled(True)

    def save_data(self, p_data):
        layout = self.skills_frame.content_widget.main_layout
        current_values = {}
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if hasattr(widget, 'get_value'):
                label_text = widget.label.text().rstrip(':')
                reverse_mapping = {v: k for k, v in self.SKILL_NAME_MAPPING.items()}
                display_name = reverse_mapping.get(label_text, label_text)
                
                original_skill_name = None
                for skill_name in self.default_skills.keys():
                    base_name = skill_name.split(':')[-1]
                    if base_name == display_name:
                        original_skill_name = skill_name
                        break
                
                if original_skill_name is None and display_name in self.default_skills:
                    original_skill_name = display_name
                    
                if original_skill_name is None:
                    continue
                    
                current_value = int(widget.get_value())
                default_value = self.default_skills.get(original_skill_name, 0)
                
                if current_value != default_value:
                    current_values[original_skill_name] = current_value
        
        for skill_name, current_value in current_values.items():
            if skill_name in self.current_skills:
                old_skill_data = self.current_skills[skill_name]
                old_total = old_skill_data.get('total_point', 0) + old_skill_data.get('extra_point', 0)
                value_diff = current_value - old_total
                
                if 'extra_point' not in p_data['skills'][skill_name]:
                    p_data['skills'][skill_name]['extra_point'] = 0
                p_data['skills'][skill_name]['extra_point'] += value_diff
                
            else:
                default_value = self.default_skills.get(skill_name, 0)
                extra_point = current_value - default_value
                
                p_data['skills'][skill_name] = {
                    'occupation_point': 0,
                    'interest_point': 0,
                    'extra_point': extra_point,
                    'total_point': default_value,
                    'is_occupation': False,
                    'growth_signal': False
                }

        self.buttons_frame.add_button.hide()
        self.buttons_frame.delete_button.hide()
        
        layout = self.skills_frame.content_widget.main_layout
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if hasattr(widget, 'set_enable'):
                widget.value_field.setEnabled(False)


class SkillsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, layout_type=QGridLayout, parent=parent)

    def _setup_content(self):
        self.setFixedHeight(360)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.content_widget = TFBaseFrame(level=1, layout_type=QGridLayout, parent=scroll)
        self.content_widget.main_layout.setSpacing(10)
        self.content_widget.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.content_widget)

        self.main_layout.addWidget(scroll)


class ButtonsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(radius=5, layout_type=QHBoxLayout, parent=parent)

    def _setup_content(self):
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(30)

        self.expand_collapse_button = self.create_button(
            name='expand_collapse',
            text='显示全部',
            height=30,
            width=90,
            enabled=False,
            on_clicked=self.parent.toggle_skills_display
        )

        self.add_button = self.create_button(
            name='add',
            text='增加技能',
            height=30,
            width=90,
            enabled=False,
            on_clicked=self._on_add_clicked
        )

        self.delete_button = self.create_button(
            name='delete',
            text='删除技能',
            height=30,
            width=90,
            enabled=False,
            on_clicked=self._on_delete_clicked
        )

        self.main_layout.addWidget(self.expand_collapse_button)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.add_button)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.delete_button)

        self.add_button.hide()
        self.delete_button.hide()

    def _on_add_clicked(self):
        card = self.parent
        dialog = AddSkillDialog(
            parent=self,
            current_skills=card.current_skills,
            default_skills=card.default_skills
        )
        
        while True:
            if dialog.exec() == TFBaseDialog.DialogCode.Rejected:
                break
                
            skill_name, base_value = dialog.get_validated_data()
            
            card.current_skills[skill_name] = {
                'occupation_point': 0,
                'interest_point': 0,
                'extra_point': 0,
                'total_point': base_value,
                'is_occupation': False,
                'growth_signal': False
            }
            
            if not card.showing_all:
                card._show_modified_skills()
            else:
                card._show_all_skills()
                
            break

    def _on_delete_clicked(self):
        card = self.parent
        dialog = DeleteSkillDialog(
            parent=self,
            current_skills=card.current_skills
        )
        
        if dialog.exec() == TFBaseDialog.DialogCode.Accepted:
            skills_to_delete = dialog.get_validated_data()
            
            if skills_to_delete:
                for skill_name in skills_to_delete:
                    if skill_name in card.current_skills:
                        del card.current_skills[skill_name]
                
                layout = card.skills_frame.content_widget.main_layout
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                if card.showing_all:
                    all_skills = {}
                    all_skills.update(card.current_skills)
                    for skill_name, default_value in card.default_skills.items():
                        if skill_name not in card.current_skills:
                            all_skills[skill_name] = {
                                'total_point': default_value,
                                'is_default': True
                            }
                    card._display_skills(all_skills)
                else:
                    card._display_skills(card.current_skills)


class AddSkillDialog(TFBaseDialog):
    def __init__(self, parent=None, current_skills=None, default_skills=None):
        self.current_skills = current_skills or {}
        self.default_skills = default_skills or {}
        
        self.categories = {"独立技能"}
        for skill in self.default_skills.keys():
            if ':' in skill:
                category = skill.split(':')[0]
                self.categories.add(category)
        
        super().__init__(
            title="新增技能",
            parent=parent,
            button_config=[
                {"text": "确定", "callback": self._on_ok_clicked},
                {"text": "取消", "callback": self.reject, "role": "reject"}
            ]
        )

    def _setup_content(self) -> None:
        self.resize(350, 200)
        self.main_layout.setSpacing(15)

        self.category = self.create_option_entry(
            name="category",
            label_text="技能类别:",
            options=sorted(self.categories),
            current_value="独立技能",
            label_size=70,
            value_size=150
        )
        
        self.skill_name = self.create_value_entry(
            name="skill_name",
            label_text="技能名称:",
            label_size=70,
            value_size=150
        )

        self.main_layout.addWidget(self.category)
        self.main_layout.addWidget(self.skill_name)
        self.main_layout.addStretch()

    def validate(self) -> List[Tuple[Any, str]]:
        category = self.category.get_value()
        name = self.skill_name.get_value().strip()
        
        if not name:
            return [(self.skill_name, "技能名称不能为空")]
        
        full_skill_name = name if category == "独立技能" else f"{category}:{name}"
        
        if full_skill_name in self.current_skills:
            return [(self.skill_name, "此技能已存在")]
        
        return []

    def get_validated_data(self) -> tuple:
        category = self.category.get_value()
        name = self.skill_name.get_value().strip()
        
        full_skill_name = name if category == "独立技能" else f"{category}:{name}"
        
        base_value = self.default_skills.get(full_skill_name, 1)
        
        return full_skill_name, base_value
    

class DeleteSkillDialog(TFBaseDialog):
    def __init__(self, parent=None, current_skills=None):
        self.current_skills = current_skills or {}
        self.skill_checks = {}
        
        self.categorized_skills = {}
        for skill_name in self.current_skills.keys():
            if ':' in skill_name:
                category, name = skill_name.split(':', 1)
            else:
                category = '独立技能'
                name = skill_name
            
            if category not in self.categorized_skills:
                self.categorized_skills[category] = []
            self.categorized_skills[category].append((name, skill_name))
        
        super().__init__(
            title="删除技能",
            layout_type=QGridLayout,
            parent=parent,
            button_config=[
                {"text": "确定", "callback": self._on_ok_clicked},
                {"text": "取消", "callback": self.reject, "role": "reject"}
            ]
        )

    def _setup_content(self) -> None:
        self.resize(600, 400)
        row = 0
        
        for category, skills in sorted(self.categorized_skills.items()):
            category_label = self.create_label(
                text=f"【{category}】",
                serif=True,
                height=30
            )
            self.main_layout.addWidget(category_label, row, 0, 1, 4)
            row += 1
            
            col = 0
            for name, full_name in sorted(skills):
                check = self.create_check_with_label(
                    name=full_name,
                    label_text=name,
                    checked=False,
                    height=24
                )
                self.skill_checks[full_name] = check
                self.main_layout.addWidget(check, row, col)
                
                col += 1
                if col >= 4:
                    col = 0
                    row += 1
            
            if col != 0:
                row += 1

    def get_validated_data(self) -> List[str]:
        return [
            skill_name
            for skill_name, check in self.skill_checks.items()
            if check.get_value()
        ]
    
