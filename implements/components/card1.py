import os
import shutil
from pathlib import Path

from PyQt6.QtWidgets import QHBoxLayout, QGridLayout, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from implements.components.base_card import BaseCard
from ui.components.tf_base_dialog import TFBaseDialog
from ui.components.tf_base_frame import TFBaseFrame
from ui.components.tf_number_receiver import TFNumberReceiver
from ui.components.tf_font import NotoSerifNormal
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
            'mov': 'MOV',
            'db': 'DB',
            'build': 'BUILD'
        }
        
        basic_stats = p_data.get('basic_stats', {})
        missing_stats = []
        stats_values = {}

        for stat in ['hp', 'mp', 'san']:
            stats_values[f'{stat}_current'] = basic_stats[f'curr_{stat}']
            stats_values[f'{stat}_max'] = basic_stats[stat]

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

    def enable_edit(self):
        self.upper_frame.avatar_frame.upload_button.show()
        
        basic_info = self.upper_frame.basic_info_frame
        for key in ['PL', '姓名', '母语', '护甲']:
            if key in basic_info._components:
                basic_info._components[key].set_enable(True)
        
        basic_info.background_button.setEnabled(True)
        basic_info.potrait_button.setEnabled(True)
        
        stats = self.stats_frame
        for key in ['hp', 'mp', 'san']:
            stats._components[f'{key}_current'].parent().setEnabled(True)
        
        for key in [
            'str', 'con', 'siz', 'dex', 'app', 'int', 'pow', 'edu', 'luk',
            'mov', 'db', 'build'
        ]:
            if key in stats._components:
                stats._components[key].set_enable(True)

    def save_data(self, p_data):
        basic_info = self.upper_frame.basic_info_frame
        values = basic_info.get_values()
        
        p_data['player_info']['player_name'] = values['PL']
        p_data['character_info']['char_name'] = values['姓名']
        p_data['character_info']['language_own'] = values['母语']
        
        if 'armour' not in p_data['loadout']:
            p_data['loadout']['armour'] = {}
        p_data['loadout']['armour']['point'] = int(values['护甲'])

        avatar_values = self.upper_frame.avatar_frame.get_values()
        if 'avatar_path' in avatar_values:
            p_data['character_info']['avatar_path'] = avatar_values['avatar_path']

        stats = self.stats_frame
        stats_values = stats.get_values()

        stats_mapping = {
            'str': 'str', 'con': 'con', 'siz': 'siz',
            'dex': 'dex', 'app': 'app', 'int': 'int',
            'pow': 'pow', 'edu': 'edu', 'luk': 'luk',
            'mov': 'mov', 'db': 'db', 'build': 'build'
        }
        for ui_key, json_key in stats_mapping.items():
            p_data['basic_stats'][json_key] = int(stats_values[ui_key])

        for stat in ['hp', 'mp', 'san']:
            p_data['basic_stats'][f'curr_{stat}'] = int(stats_values[f'{stat}_current'])
            p_data['basic_stats'][stat] = int(stats_values[f'{stat}_max'])

        self.upper_frame.avatar_frame.upload_button.hide()
        
        for key in ['PL', '姓名', '母语', '护甲']:
            if key in basic_info._components:
                basic_info._components[key].set_enable(False)
        
        for key in ['hp', 'mp', 'san']:
            stats._components[f'{key}_current'].parent().setEnabled(False)
        
        for key in [
            'str', 'con', 'siz', 'dex', 'app', 'int', 'pow', 'edu', 'luk',
            'mov', 'db', 'build'
        ]:
            if key in stats._components:
                stats._components[key].set_enable(False)


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
            on_clicked=self._on_background_clicked
        )
        self.main_layout.addSpacing(15)
        self.main_layout.addWidget(self.background_button)

        self.potrait_button = self.create_button(
            name='potrait',
            text='人物特质',
            height=24,
            width=90,
            on_clicked=self._on_potrait_clicked
        )
        self.main_layout.addSpacing(3)
        self.main_layout.addWidget(self.potrait_button)

    def _on_background_clicked(self):
        pc_card = self.parent.parent.parent
        if pc_card.p_data == {}:
            TFApplication.instance().show_message('请先加载人物卡', 5000, 'yellow')
            return

        dialog = BackgroundDialog(
            parent=self,
            p_data=pc_card.p_data,
            edit_mode=pc_card.edit_mode
        )
        
        if dialog.exec() == TFBaseDialog.DialogCode.Accepted and pc_card.edit_mode:
            TFApplication.instance().show_message('角色背景故事已保存', 5000, 'green')

    def _on_potrait_clicked(self):
        pc_card = self.parent.parent.parent
        if pc_card.p_data == {}:
            TFApplication.instance().show_message('请先加载人物卡', 5000, 'yellow')
            return

        dialog = PortraitDialog(
            parent=self,
            p_data=pc_card.p_data,
            edit_mode=pc_card.edit_mode
        )
        
        if dialog.exec() == TFBaseDialog.DialogCode.Accepted and pc_card.edit_mode:
            TFApplication.instance().show_message('角色特质已保存', 5000, 'green')


class StatsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, layout_type=QGridLayout, parent=parent)

    def _setup_content(self):
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        standard_stats = [
            'STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK',
            'MOV', 'DB', 'BUILD'
        ]
        
        dynamic_stats = ['HP', 'MP', 'SAN']
        for i, stat in enumerate(dynamic_stats):
            row = i // 3
            col = i % 3
            entry = self.create_dual_number_receiver(
                label_text=stat,
                current_value=0,
                max_value=0
            )
            self.main_layout.addWidget(entry, row, col)
        
        for i, key in enumerate(standard_stats):
            row = (i // 3) + 1
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

    def create_dual_number_receiver(self, label_text: str, current_value: int, max_value: int) -> None:
        entry_container = TFBaseFrame(level=1, layout_type=QHBoxLayout, parent=self)
        entry_container.main_layout.setSpacing(0)
        entry_container.main_layout.setContentsMargins(0, 0, 0, 0)
        
        label = entry_container.create_label(
            text=label_text,
            fixed_width=40,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            height=24
        )
        label.setFont(NotoSerifNormal)
        
        current_receiver = TFNumberReceiver(
            text=str(current_value),
            alignment=Qt.AlignmentFlag.AlignCenter,
            width=22,
            height=24,
            allow_decimal=False,
            max_digits=2,
            parent=entry_container
        )
        
        separator = entry_container.create_label(
            text="/",
            alignment=Qt.AlignmentFlag.AlignCenter,
            height=24
        )
        
        max_receiver = TFNumberReceiver(
            text=str(max_value),
            alignment=Qt.AlignmentFlag.AlignCenter,
            width=22,
            height=24,
            allow_decimal=False,
            max_digits=2,
            parent=entry_container
        )
        
        entry_container.main_layout.addWidget(label)
        entry_container.main_layout.addWidget(current_receiver)
        entry_container.main_layout.addSpacing(1)
        entry_container.main_layout.addWidget(separator)
        entry_container.main_layout.addSpacing(1)
        entry_container.main_layout.addWidget(max_receiver)
        entry_container.main_layout.addStretch()

        entry_container.setEnabled(False)

        stat_lower = label_text.lower()
        self._register_component(f'{stat_lower}_current', current_receiver)
        self._register_component(f'{stat_lower}_max', max_receiver)

        return entry_container


class BackgroundDialog(TFBaseDialog):
    def __init__(self, parent=None, p_data=None, edit_mode=False):
        self.p_data = p_data
        self.edit_mode = edit_mode
        self.original_text = p_data.get('background', {}).get('background', '')
        super().__init__(
            title="背景故事",
            parent=parent,
            button_config=[
                {"text": "确定", "callback": self._on_ok_clicked},
                {"text": "取消", "callback": self.reject, "role": "reject"}
            ]
        )
        self.resize(600, 400)

    def _setup_content(self) -> None:
        self.text_edit = self.create_text_edit(
            name="background_text",
            text=self.original_text,
            width=580,
            height=360,
            read_only=not self.edit_mode,
            word_wrap=True
        )
        
        self.main_layout.addWidget(self.text_edit)

    def get_validated_data(self) -> str:
        return self.text_edit.toPlainText()

    def _on_ok_clicked(self) -> None:
        if self.edit_mode:
            self._result = self.get_validated_data()
            if self.p_data and 'background' in self.p_data:
                self.p_data['background']['background'] = self._result
        self.accept()


class PortraitEntryFrame(TFBaseFrame):
    def __init__(self, title: str, content: str, edit_mode: bool = False, parent=None):
        self.title = title
        self.content = content
        self.edit_mode = edit_mode
        super().__init__(parent=parent)

    def _setup_content(self) -> None:
        self.title_label = self.create_label(
            text=self.title,
            height=24,
            serif=True
        )
        
        self.text_edit = self.create_text_edit(
            name=f"portrait_{self.title}",
            text=self.content,
            width=580,
            height=60,
            read_only=not self.edit_mode,
            word_wrap=True
        )
        
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.text_edit)

    def get_content(self) -> str:
        return self.text_edit.toPlainText()
    

class PortraitDialog(TFBaseDialog):
    def __init__(self, parent=None, p_data=None, edit_mode=False):
        self.p_data = p_data
        self.edit_mode = edit_mode
        self.portrait_frames = {}
        self.original_data = p_data.get('background', {}).get('portraits', {}).copy()
        
        super().__init__(
            title="人物特质",
            parent=parent,
            button_config=[
                {"text": "确定", "callback": self._on_ok_clicked},
                {"text": "取消", "callback": self.reject, "role": "reject"}
            ]
        )
        self.resize(600, 600)

    def _setup_content(self) -> None:
        portraits_data = self.p_data.get('background', {}).get('portraits', {})
        
        for title, content in portraits_data.items():
            entry_frame = PortraitEntryFrame(
                title=title,
                content=content,
                edit_mode=self.edit_mode,
                parent=self
            )
            self.portrait_frames[title] = entry_frame
            self.main_layout.addWidget(entry_frame)

    def get_validated_data(self) -> dict:
        return {
            title: frame.get_content()
            for title, frame in self.portrait_frames.items()
        }

    def _on_ok_clicked(self) -> None:
        if self.edit_mode:
            self._result = self.get_validated_data()
            if self.p_data and 'background' in self.p_data:
                self.p_data['background']['portraits'] = self._result
        self.accept()
