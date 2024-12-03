import json
from pathlib import Path

from PyQt6.QtWidgets import QHBoxLayout, QGridLayout, QScrollArea, QFrame
from PyQt6.QtCore import Qt

from implements.components.base_card import BaseCard
from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication
from utils.helper import resource_path


class Card2(BaseCard):
    SKILL_NAME_MAPPING = {
        "图书馆使用": "图书馆",
        # 其他映射...
    }
    def __init__(self, parent=None):
        self.showing_all = False
        self.default_skills = {}
        self.current_skills = {}
        self._load_default_skills()
        super().__init__(parent=parent)

    def _setup_content(self):
        self.skills_frame = SkillsFrame(self)
        self.buttons_frame = ButtonsFrame(self)

        self.add_child('skills_frame', self.skills_frame)
        self.add_child('buttons_frame', self.buttons_frame)

        self.buttons_frame.expand_collapse_button.clicked.connect(self._toggle_skills_display)

    def _load_default_skills(self):
        try:
            with open(resource_path('implements/data/default_skills.json'), 'r', encoding='utf-8') as f:
                self.default_skills = json.load(f)
        except Exception as e:
            TFApplication.instance().show_message(str(e), 5000, 'yellow')

    def _toggle_skills_display(self):
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
            total_point = skill_data.get('total_point', 0)
            
            entry = self.skills_frame.content_widget.create_value_entry(
                name=skill_name,
                label_text=self.SKILL_NAME_MAPPING.get(name, name) + ':',
                value_text=str(total_point),
                value_size=24,
                label_size=56,
                number_only=True,
                allow_decimal=False,
                max_digits=2,
                enable=False
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

    def save_data(self, p_data):
        pass

    def enable_edit(self):
        pass


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
            on_clicked=self._on_expand_collapse_clicked
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

    def _on_expand_collapse_clicked(self):
        pass

    def _on_add_clicked(self):
        pass

    def _on_delete_clicked(self):
        pass
