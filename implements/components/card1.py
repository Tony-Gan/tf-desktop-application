import os
import shutil
from pathlib import Path

from PyQt6.QtWidgets import QHBoxLayout, QGridLayout, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from implements.components.base_card import BaseCard
from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication
from utils.helper import resource_path


class Card1(BaseCard):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def _setup_content(self):
        self.upper_frame = UpperFrame(self)
        self.stats_frame = StatsFrame(self)

        self.add_child('upper_frame', self.upper_frame)
        self.add_child('stats_frame', self.stats_frame)

    def load_data(self, p_data):
        avatar_path = p_data.get('character_info', {}).get('avatar_path')
        if avatar_path:
            full_path = resource_path(avatar_path)
            self.upper_frame.avatar_frame._update_avatar_display(full_path)
            self.upper_frame.avatar_frame._current_avatar_path = avatar_path

        required_fields = {
            'player_name': ('player_info', 'PL'),
            'char_name': ('character_info', '姓名'),
            'language_own': ('character_info', '母语')
        }
        
        missing_basic_info = []
        basic_info_values = {
            'PL': 'N/A',
            '姓名': '未命名角色',
            '母语': 'N/A',
            '护甲': p_data.get('loadout', {}).get('armour', {}).get('point', 0)
        }

        for field, (section, display_name) in required_fields.items():
            value = p_data.get(section, {}).get(field)
            if value is None:
                missing_basic_info.append(display_name)
            else:
                basic_info_values[display_name] = value

        if missing_basic_info:
            missing_fields = ", ".join(missing_basic_info)
            TFApplication.instance().show_message(f"文件不完整：缺少以下基本信息 {missing_fields}", 5000, 'yellow')

        self.upper_frame.basic_info_frame.update_components_from_values(basic_info_values)

        stats_mapping = {
            'str': 'STR',
            'con': 'CON',
            'siz': 'SIZ',
            'dex': 'DEX',
            'app': 'APP',
            'int': 'INT',
            'pow': 'POW',
            'edu': 'EDU',
            'luk': 'LUK',
            'hp': 'HP',
            'mp': 'MP',
            'san': 'SAN',
            'mov': 'MOV',
            'db': 'DB',
            'build': 'BUILD'
        }
        
        stats_values = {}
        basic_stats = p_data.get('basic_stats', {})
        missing_stats = []

        for json_key, ui_key in stats_mapping.items():
            value = basic_stats.get(json_key)
            if value is None:
                missing_stats.append(ui_key)
            stats_values[ui_key.lower()] = value if value is not None else "0"

        if missing_stats:
            missing_fields = ", ".join(missing_stats)
            TFApplication.instance().show_message(f"文件不完整：缺少以下属性值 {missing_fields}", 5000, 'yellow')
            
        self.stats_frame.update_components_from_values(stats_values)
        
        char_name = basic_info_values['姓名']
        if self.parent:
            self.parent.title = f"{char_name}"

    def save_data(self, p_data):
        pass

    def enable_edit(self):
        pass


class UpperFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=0, radius=5, layout_type=QHBoxLayout, parent=parent)

    def _setup_content(self):
        self.setFixedHeight(220)
        self.main_layout.setSpacing(30)

        self.avatar_frame = AvatarFrame(self)
        self.basic_info_frame = BasicInfoFrame(self)

        self.add_child('avatar_frame', self.avatar_frame)
        self.add_child('basic_info_frame', self.basic_info_frame)


class AvatarFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=0, radius=5, parent=parent)

    def _setup_content(self):
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.setFixedWidth(150)

        self.avatar_label = self.create_label(
            text="",
            alignment=Qt.AlignmentFlag.AlignCenter,
            height=130
        )
        self.avatar_label.setFixedWidth(130)
        self.avatar_label.setObjectName("avatar_label")
        self.avatar_label.setStyleSheet("""
            QLabel#avatar_label {
                border: 1px solid #666666;
                background-color: #242831;
                border-radius: 5px;
            }
        """)

        self.upload_button = self.create_button(
            name="avatar_upload",
            text="上传头像",
            width=120,
            height=24,
            font_size=10,
            enabled=True,
            tooltip="点击进行头像上传",
            border_radius=5,
            on_clicked=self._on_avatar_upload
        )

        self.upload_button.hide()

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.upload_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addStretch()

    def _on_avatar_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择头像图片",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if not file_path:
            return
        
        try:
            file_size = os.path.getsize(file_path)
            max_size = 2 * 1024 * 1024
            if file_size > max_size:
                TFApplication.instance().show_message("文件大小超过2MB限制，请选择更小的文件。", 5000, "yellow")
                return
        except Exception as e:
            TFApplication.instance().show_message(f"无法检查文件大小: {str(e)}", 5000, "yellow")
            return

        try:
            avatar_dir = Path(resource_path("resources/data/coc/pcs/avatars"))
            avatar_dir.mkdir(parents=True, exist_ok=True)

            avatar_filename = os.path.basename(file_path)
            avatar_path = avatar_dir / avatar_filename

            if avatar_path.exists():
                base, ext = os.path.splitext(avatar_filename)
                counter = 1
                while avatar_path.exists():
                    avatar_filename = f"{base}_{counter}{ext}"
                    avatar_path = avatar_dir / avatar_filename
                    counter += 1

            shutil.copy2(file_path, avatar_path)

            self._update_avatar_display(str(avatar_path))
            
            self._current_avatar_path = str(avatar_path.relative_to(Path.cwd()))
            self._emit_values_changed()
            
        except Exception as e:
            TFApplication.instance().show_message(str(e), 5000, "yellow")

    def _update_avatar_display(self, image_path: str):
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(
            self.avatar_label.size(),
            aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
            transformMode=Qt.TransformationMode.SmoothTransformation
        )
        self.avatar_label.setPixmap(scaled_pixmap)

    def get_values(self) -> dict:
        values = super().get_values()
        if hasattr(self, '_current_avatar_path'):
            values['avatar_path'] = self._current_avatar_path
        return values


class BasicInfoFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=0, radius=5, parent=parent)

    def _setup_content(self):
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        for key in ['PL', '姓名', '母语', '护甲']:
            entry = self.create_value_entry(
                name=key,
                label_text=key + ':',
                value_text="N/A",
                value_size=90,
                label_size=50,
                enable=False,
                show_tooltip=True if key == 'PL' else False
            )
            self.main_layout.addWidget(entry)
        self.background_button = self.create_button(
            name='background',
            text='背景故事',
            height=24,
            width=90,
            enabled=False,
            on_clicked=self._on_background_clicked
        )
        self.main_layout.addSpacing(15)
        self.main_layout.addWidget(self.background_button)

        self.potrait_button = self.create_button(
            name='potrait',
            text='人物特质',
            height=24,
            width=90,
            enabled=False,
            on_clicked=self._on_potrait_clicked
        )
        self.main_layout.addSpacing(3)
        self.main_layout.addWidget(self.potrait_button)

    def _on_background_clicked(self):
        pass

    def _on_potrait_clicked(self):
        pass


class StatsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, layout_type=QGridLayout, parent=parent)

    def _setup_content(self):
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        for i, key in enumerate([
            'STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK',
            'HP', 'MP', 'SAN', 'MOV', 'DB', 'BUILD'
        ]):
            row = i // 3
            col = i % 3
            entry = self.create_value_entry(
                name=key.lower(),
                label_text=key,
                value_text="N/A",
                value_size=40,
                label_size=50,
                number_only=True,
                allow_decimal=False,
                max_digits=2,
                enable=False
            )
            self.main_layout.addWidget(entry, row, col)
