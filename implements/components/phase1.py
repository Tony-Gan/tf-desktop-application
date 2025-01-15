import os
import math
import random
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QFileDialog, QVBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QFont

from implements.components.base_phase import BasePhase
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_dialog import TFBaseDialog
from ui.components.tf_base_frame import TFBaseFrame
from ui.components.tf_font import NotoSerifNormal
from ui.tf_application import TFApplication
from utils.helper import resource_path


class Phase1(BasePhase):

    def _setup_content(self) -> None:
        super()._setup_content()

        self.buttons_frame.prev_button.hide()
        self.buttons_frame.complete_button.hide()

        self.show_character_description_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="角色信息", 
            height=35,
            width=120,
            font_family=QFont("Noto Serif SC"),
            on_clicked=self._on_show_character_description_clicked
        )
        self.age_reduction_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="年龄修正", 
            height=35,
            width=120,
            font_family=QFont("Noto Serif SC"),
            on_clicked=self._on_age_reduction_clicked
        )
        self.stats_exchange_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="属性交换", 
            height=35,
            width=120,
            font_family=QFont("Noto Serif SC"),
            on_clicked=self._on_stats_exchange_clicked
        )
        self.buttons_frame.add_custom_button(self.show_character_description_button)
        self.buttons_frame.add_custom_button(self.age_reduction_button)
        self.buttons_frame.add_custom_button(self.stats_exchange_button)

        self.stats_exchange_button.hide()

        self.upper_frame = UpperFrame(self)
        self.lower_frame = LowerFrame(self)

        self.contents_frame.add_child("upper_frame", self.upper_frame)
        self.contents_frame.add_child("lower_frame", self.lower_frame)

    def reset_contents(self):
        self.upper_frame.avatar_frame.avatar_label.clear()
        if hasattr(self.upper_frame.avatar_frame, '_current_avatar_path'):
            delattr(self.upper_frame.avatar_frame, '_current_avatar_path')
            
        player_info = self.upper_frame.player_info_group
        player_info.player_name_entry.set_value("")
        player_info.era_entry.set_value("None")
        
        char_info = self.upper_frame.character_info_group
        char_info.char_name_entry.set_value("")
        char_info.age_entry.set_value("")
        char_info.age_entry.set_enable(True)
        char_info.gender_entry.set_value("None")
        char_info.natinality_entry.set_value("")
        char_info.residence_entry.set_value("")
        char_info.birthpalce_entry.set_value("")
        char_info.language_own_entry.set_text("")

        self.age_reduction_button.setEnabled(True)

        mode = self.config.get("mode")
        if mode == "天命":
            if self.lower_frame.middle_stack:
                stats_entries = self.lower_frame.basic_stats_group.stats_entries
                for entry in stats_entries.values():
                    entry.set_value("0")
                    entry.set_enable(True)
                self.lower_frame.basic_stats_group._update_derived_stats()
                self.lower_frame.basic_stats_group.hide()
                self.lower_frame.dice_result_frame.show()
                self.lower_frame.middle_stack.setCurrentWidget(self.lower_frame.dice_result_frame)
        elif mode == "购点":
            if self.lower_frame.middle_stack:
                self.lower_frame.middle_stack.setCurrentWidget(self.lower_frame.basic_stats_group)
                stats = self.lower_frame.basic_stats_group.stats_entries
                for entry in stats.values():
                    entry.set_value("0")
                    entry.set_enable(True)
                self.lower_frame.basic_stats_group._update_derived_stats()

    def initialize(self):
        self.check_dependencies()

    def save_state(self):
        if 'player_info' not in self.p_data:
            self.p_data['player_info'] = {}
        player_info_values = self.upper_frame.player_info_group.get_values()
        self.p_data['player_info'].update(player_info_values)
        
        if 'character_info' not in self.p_data:
            self.p_data['character_info'] = {}
        character_info_values = self.upper_frame.character_info_group.get_values()
        character_info_values['language_own'] = self.upper_frame.character_info_group.language_own_entry.get_text()
        self.p_data['character_info'].update(character_info_values)
        
        avatar_values = self.upper_frame.avatar_frame.get_values()
        if avatar_values.get('avatar_path'):
            self.p_data['character_info']['avatar_path'] = avatar_values['avatar_path']
            
        if 'basic_stats' not in self.p_data:
            self.p_data['basic_stats'] = {}
            
        basic_stats = {}
        for stat, entry in self.lower_frame.basic_stats_group.stats_entries.items():
            basic_stats[stat.lower()] = entry.get_value()
        
        for key, entry in self.lower_frame.basic_stats_group.derived_entries.items():
            if entry.get_value() != "N/A":
                basic_stats[key.lower()] = entry.get_value()
                if key.lower() in ["hp", "mp", "san"]:
                    extra_key = "curr_" + key.lower()
                    basic_stats[extra_key] = entry.get_value()
                
        self.p_data['basic_stats'].update(basic_stats)

    def restore_state(self):
        pass

    def check_dependencies(self):
        mode = self.config.get("mode", "天命")
        self.lower_frame.stats_info_group.update_from_config(self.config)
        self.lower_frame.handle_mode_change(mode, self.config)

        if mode == "天命":
            destiny_config = self.config.get("destiny", {})
            allow_exchange = destiny_config.get("allow_exchange", False)
            self.stats_exchange_button.setVisible(allow_exchange)
        else:
            self.stats_exchange_button.hide()

    def validate(self):
        invalid_items = []
        
        player_info = self.upper_frame.player_info_group
        if not player_info.player_name_entry.get_value():
            invalid_items.append((player_info.player_name_entry, "玩家姓名不能为空"))
        if player_info.era_entry.get_value() == "未选择":
            invalid_items.append((player_info.era_entry, "请选择一个时代"))
            
        char_info = self.upper_frame.character_info_group
        if not char_info.char_name_entry.get_value():
            invalid_items.append((char_info.char_name_entry, "角色姓名不能为空"))
        if not char_info.age_entry.get_value():
            invalid_items.append((char_info.age_entry, "年龄不能为空"))
        elif int(char_info.age_entry.get_value()) < 15 or int(char_info.age_entry.get_value()) > 90:
            invalid_items.append((char_info.age_entry, "年龄应设置在 15 到 90 之间"))
        if char_info.gender_entry.get_value() == "未选择":
            invalid_items.append((char_info.gender_entry, "请选择性别"))
        if not char_info.natinality_entry.get_value():
            invalid_items.append((char_info.natinality_entry, "国籍不能为空"))
        if not char_info.residence_entry.get_value():
            invalid_items.append((char_info.residence_entry, "居住地不能为空"))
        if not char_info.birthpalce_entry.get_value():
            invalid_items.append((char_info.birthpalce_entry, "出生地不能为空"))
        if not char_info.language_own_entry.get_text():
            invalid_items.append((char_info.language_own_entry, "请选择你的母语"))

        mode = self.config.get("mode")
        if mode == "天命":
            if not self.lower_frame.basic_stats_group.isVisible():
                invalid_items.append((
                    self.lower_frame.dice_result_frame, 
                    "请选择一组骰子结果"
                ))
        elif mode == "购点":
            points_config = self.config.get("points", {})
            lower_limit = points_config.get("lower_limit", 30)
            upper_limit = points_config.get("upper_limit", 80)
            
            basic_stats = self.lower_frame.basic_stats_group
            for stat, entry in basic_stats.stats_entries.items():
                try:
                    value = int(entry.get_value())
                    if value < lower_limit:
                        invalid_items.append((
                            entry,
                            f"{stat} 至少需要 {lower_limit}（当前值：{value}）"
                        ))
                    elif value > upper_limit:
                        invalid_items.append((
                            entry,
                            f"{stat} 不能超过 {upper_limit}（当前值：{value}）"
                        ))
                except ValueError:
                    invalid_items.append((entry, f"{stat} 的值无效"))
        
        return invalid_items

    def _on_show_character_description_clicked(self):
        for stat, entry in self.lower_frame.basic_stats_group.stats_entries.items():
            if not entry.get_value() or int(entry.get_value()) == 0:
                TFApplication.instance().show_message("请先设置所有属性后再查看角色描述", 5000, "yellow")
                return
        
        stats = {}
        for stat, entry in self.lower_frame.basic_stats_group.stats_entries.items():
            stats[stat] = int(entry.get_value())
            
        CharacterDescriptionDialog.get_input(self, stats=stats)

    def _on_age_reduction_clicked(self):
        mode = self.lower_frame.stats_info_group.entries["dice_mode"].get_value()

        if not self.upper_frame.character_info_group.age_entry.get_value().isdigit():
            TFApplication.instance().show_message("请先输入年龄后再进行年龄修正操作。", 5000, "yellow")
            return
        
        if not self.lower_frame.basic_stats_group.isVisible():
            TFApplication.instance().show_message("请选择基本属性后再继续。", 5000, "yellow")
            return

        if mode == "购点":
            if not int(self.lower_frame.stats_info_group.entries["points_available"].get_value()) == 0:
                TFApplication.instance().show_message("请分配完所有点数后再继续。", 5000, "yellow")
                return

        modifications = []
        stats_group = self.lower_frame.basic_stats_group

        age = int(self.upper_frame.character_info_group.get_values()["age"])

        total_reduction, reduction_stats = self._calculate_total_reduction(age)
        if total_reduction != 0:
            current_stats = {
                stat: int(self.lower_frame.basic_stats_group.stats_entries[stat].get_value())
                for stat in reduction_stats
            }
            success, results = AgeReductionDialog.get_input(
                self,
                reduction_stats=reduction_stats,
                total_reduction=total_reduction,
                current_stats=current_stats
            )
            
            if not success:
                return
            
            for stat, reduction in results.items():
                if reduction > 0:
                    old_value = int(stats_group.stats_entries[stat].get_value())
                    new_value = max(1, old_value - reduction)
                    stats_group.stats_entries[stat].set_value(str(new_value))
                    modifications.append(f"{stat} 减少了 {reduction} 点（{old_value} → {new_value}）")


        edu_message = self._process_edu_improvement(age, stats_group)
        app_message = self._process_app_reduction(age, stats_group)
        if age < 20 and mode == "天命" or (mode == "购点" and not self.config["points"]["custom_luck"]):
            dice_result = sum(random.randint(1, 6) for _ in range(3)) * 5
            curr_luk = int(self.lower_frame.basic_stats_group.stats_entries["LUK"].get_value())
            if dice_result > curr_luk:
                self.lower_frame.basic_stats_group.stats_entries["LUK"].set_value(str(dice_result))
                modifications.append(f"LUK 从 {curr_luk} 提高到 {dice_result}")

        if edu_message:
            modifications.extend(edu_message)
        if app_message:
            modifications.extend(app_message)


        self.age_reduction_button.setEnabled(False)
        self.upper_frame.character_info_group.age_entry.set_enable(False)
        self.lower_frame.basic_stats_group.setEnabled(False)
        if modifications:
            TFApplication.instance().show_message("\n".join(modifications), 5000, "green")

        stats_group._update_derived_stats()
        stats_group._update_radar_stats()

    def _on_stats_exchange_clicked(self):
        if not self.lower_frame.basic_stats_group.isVisible():
            TFApplication.instance().show_message("请先选择基本属性后再进行交换", 5000, "yellow")
            return
        
        current_stats = {}
        for stat, entry in self.lower_frame.basic_stats_group.stats_entries.items():
            if stat != 'LUK':
                current_stats[stat] = int(entry.get_value() or '0')
                
        destiny_config = self.config.get("destiny", {})
        exchange_count = int(destiny_config.get("exchange_count", "1"))
        
        success, result = StatExchangeDialog.get_input(
            self,
            remaining_times=exchange_count,
            current_stats=current_stats
        )
        
        if success and result:
            stat1, stat2 = result
            val1 = self.lower_frame.basic_stats_group.stats_entries[stat1].get_value()
            val2 = self.lower_frame.basic_stats_group.stats_entries[stat2].get_value()
            self.lower_frame.basic_stats_group.stats_entries[stat1].set_value(val2)
            self.lower_frame.basic_stats_group.stats_entries[stat2].set_value(val1)
            
            destiny_config["exchange_count"] = str(exchange_count - 1)
            if int(destiny_config["exchange_count"]) == 0:
                self.stats_exchange_button.setEnabled(False)
                
            self.lower_frame.basic_stats_group._update_derived_stats()
            self.lower_frame.basic_stats_group._update_radar_stats()

    def _calculate_total_reduction(self, age: int):
        if age >= 80:
            total_reduction = 80
            reduction_stats = ['STR', 'CON', 'DEX']
        elif age >= 70:
            total_reduction = 40
            reduction_stats = ['STR', 'CON', 'DEX']
        elif age >= 60:
            total_reduction = 20
            reduction_stats = ['STR', 'CON', 'DEX']
        elif age >= 50:
            total_reduction = 10
            reduction_stats = ['STR', 'CON', 'DEX']
        elif age >= 40:
            total_reduction = 5
            reduction_stats = ['STR', 'CON', 'DEX']
        elif age < 20:
            total_reduction = 5
            reduction_stats = ['STR', 'SIZ']
        else:
            total_reduction = 0
            reduction_stats = []

        return total_reduction, reduction_stats
    
    def _process_edu_improvement(self, age: int, stats_group):
        edu_message = []

        if age >= 70:
            edu_checks = 4
        elif age >= 60:
            edu_checks = 3
        elif age >= 50:
            edu_checks = 2
        elif age >= 40:
            edu_checks = 1
        else:
            edu_checks = 0

        old_edu = int(stats_group.stats_entries['EDU'].get_value())
        curr_edu = old_edu
        for _ in range(edu_checks):
            check = random.randint(1, 100)
            if check > curr_edu:
                improvement = random.randint(1, 10)
                curr_edu = min(99, curr_edu + improvement)

        if edu_checks:
            stats_group.stats_entries['EDU'].set_value(str(curr_edu))
            if curr_edu > old_edu:
                edu_message.append(f"EDU 从 {old_edu} 提高到 {curr_edu}")

        return edu_message
    
    def _process_app_reduction(self, age: int, stats_group):
        app_message = []

        if age >= 80:
            app_reduction = 25
        elif age >= 70:
            app_reduction = 15
        elif age >= 60:
            app_reduction = 10
        elif age >= 50:
            app_reduction = 10
        elif age >= 40:
            app_reduction = 5
        else:
            app_reduction = 0

        if app_reduction > 0:
            old_app = int(stats_group.stats_entries['APP'].get_value())
            new_app = max(1, old_app - app_reduction)
            stats_group.stats_entries['APP'].set_value(str(new_app))
            app_message.append(f"APP 因年龄减少了 {app_reduction} 点（{old_app} → {new_app}）")

        return app_message

    def try_go_next(self):
        if self.age_reduction_button.isEnabled():
            self._on_age_reduction_clicked()
            
        super().try_go_next()


class UpperFrame(TFBaseFrame):

    def __init__(self,  parent=None):
        super().__init__(QHBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedHeight(200)

        self.avatar_frame = AvatarFrame(self)
        self.player_info_group = PlayerInfoGroup(self)
        self.character_info_group = CharacterInfoGroup(self)

        self.add_child("avatar_entry", self.avatar_frame)
        self.add_child("player_info_entry", self.player_info_group)
        self.add_child("character_info_entry", self.character_info_group)


class LowerFrame(TFBaseFrame):

    def __init__(self,  parent=None):
        self.dice_result_frame = None
        self.selected_stats_index = -1
        super().__init__(QHBoxLayout, radius=10, parent=parent)

    def _setup_content(self) -> None:
        self.middle_stack = QStackedWidget(self)
        self.stats_info_group = StatsInformationGroup(self)
        self.basic_stats_group = BasicStatsGroup(self)
        self.radar_graph = RadarGraph(self)

        self.middle_stack.addWidget(self.basic_stats_group)

        self.add_child("stats_info", self.stats_info_group)
        self.main_layout.addWidget(self.middle_stack)
        self.add_child("radar_graph", self.radar_graph)

    def handle_mode_change(self, mode: str, config: dict) -> None:
        if mode == "购点":
            self.middle_stack.setCurrentWidget(self.basic_stats_group)
            points_config = config.get("points", {})
            allow_custom_luck = points_config.get("custom_luck", False)
            available_points = points_config.get("available", 480)

            self.basic_stats_group.total_points = available_points

            for stat, entry in self.basic_stats_group.stats_entries.items():
                entry.set_enable(True)
                entry.set_value("0")
                if stat == 'LUK' and not allow_custom_luck:
                    entry.set_enable(False)
                    dice_result = sum(random.randint(1, 6) for _ in range(3)) * 5
                    entry.set_value(str(dice_result))
                    self.basic_stats_group.total_points += dice_result
                    self.basic_stats_group._update_points_available()
                    TFApplication.instance().show_message(f"LUK 骰子结果：{dice_result}", 5000, "green")

        elif mode == "天命":
            dice_count = int(config.get("destiny", {}).get("dice_count", 3))
            if not self.dice_result_frame:
                self.dice_result_frame = DiceResultFrame(dice_count, self)
                self.dice_result_frame.values_changed.connect(self._handle_dice_result_confirmed)
                self.middle_stack.addWidget(self.dice_result_frame)
            else:
                self.dice_result_frame.update_dice_count(dice_count)
            self.middle_stack.setCurrentWidget(self.dice_result_frame)

    def _handle_dice_result_confirmed(self, values: dict) -> None:
        selected_stats = values.get("selected_stats", {})
        if selected_stats:
            self.selected_stats_index = next(
                (i for i, stats in enumerate(self.dice_result_frame.rolls_data)
                 if stats == selected_stats),
                -1
            )
            
            self.dice_result_frame.hide()
            self.basic_stats_group.show()
            
            for stat, value in selected_stats.items():
                entry = self.basic_stats_group.stats_entries.get(stat)
                if entry:
                    entry.set_value(str(value))
                    entry.set_enable(False)
                    
            self.basic_stats_group._update_derived_stats()


class AvatarFrame(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(layout_type=QVBoxLayout, radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedWidth(160)

        self.avatar_label = self.create_label(
            text="",
            alignment=Qt.AlignmentFlag.AlignCenter,
            height=100
        )
        self.avatar_label.setFixedWidth(100)
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

    def update_component_value(self, name: str, value: str) -> None:
        super().update_component_value(name, value)
        if name == 'avatar_path' and value:
            self._current_avatar_path = value
            self._update_avatar_display(value)


class PlayerInfoGroup(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedWidth(210)

        self.player_name_entry = self.create_value_entry(
            name="player_name",
            label_text="Player(PL):",
            label_size=80,
            value_size=70,
            height=24,
            show_tooltip=True,
            tooltip_text="玩家的称呼（非你所创建的角色的称呼）"
        )
        self.player_name_entry.value_changed.connect(self._update_label_colors)

        self.era_entry = self.create_option_entry(
            name="era",
            label_text="时代:",
            options=["1920s", "现代"],
            current_value="现代",
            label_size=80,
            value_size=70,
            height=24
        )

        self.main_layout.addWidget(self.player_name_entry)
        self.main_layout.addWidget(self.era_entry)

        self._update_label_colors()

    def _update_label_colors(self) -> None:
        if not self.player_name_entry.get_value():
            self.player_name_entry.label.setStyleSheet("color: #FFB700;")
        else:
            self.player_name_entry.label.setStyleSheet("")


class CharacterInfoGroup(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(layout_type=QGridLayout, radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        self.char_name_entry = self.create_value_entry(
            name="char_name",
            label_text="姓名:",
            label_size=50,
            value_size=75,
            height=24
        )
        self.char_name_entry.value_changed.connect(self._update_label_colors)

        self.age_entry = self.create_value_entry(
            name="age",
            label_text="年龄:",
            label_size=50,
            value_size=75,
            height=24,
            number_only=True,
            allow_decimal=False,
            max_digits=2
        )
        self.age_entry.value_changed.connect(self._update_label_colors)

        self.gender_entry = self.create_option_entry(
            name="gender",
            label_text="性别:",
            options=["未选择", "男性", "女性", "其他"],
            current_value="未选择",
            label_size=50,
            value_size=75,
            height=24
        )
        self.gender_entry.value_changed.connect(self._update_label_colors)

        self.natinality_entry = self.create_value_entry(
            name="nationality",
            label_text="国籍:",
            label_size=50,
            value_size=75,
            height=24
        )
        self.natinality_entry.value_changed.connect(self._update_label_colors)

        self.residence_entry = self.create_value_entry(
            name="residence",
            label_text="现居地:",
            label_size=60,
            value_size=75,
            height=24
        )
        self.residence_entry.value_changed.connect(self._update_label_colors)

        self.birthpalce_entry = self.create_value_entry(
            name="birthplace",
            label_text="出生地:",
            label_size=60,
            value_size=75,
            height=24
        )
        self.birthpalce_entry.value_changed.connect(self._update_label_colors)

        self.language_own_entry = self.create_button_entry(
            name="language_own",
            label_text="母语:",
            label_size=50,
            button_text="选择",
            button_callback=self._on_language_select,
            button_size=75,
            entry_size=75,
            border_radius=5
        )
        self.language_own_entry.set_entry_enabled(False)
        self.language_own_entry.text_changed.connect(self._language_update_callback)

        self.main_layout.addWidget(self.char_name_entry, 0, 0)
        self.main_layout.addWidget(self.age_entry, 0, 1)
        self.main_layout.addWidget(self.gender_entry, 1, 1)
        self.main_layout.addWidget(self.natinality_entry, 1, 0)
        self.main_layout.addWidget(self.residence_entry, 0, 2)
        self.main_layout.addWidget(self.birthpalce_entry, 1, 2)
        self.main_layout.addWidget(self.language_own_entry, 2, 0, 1, 2)

        self._update_label_colors()

    def _on_language_select(self):
        success, selected_language = LanguageSelectionDialog.get_input(self)
        if success and selected_language:
            self.language_own_entry.set_text(selected_language)

    def _language_update_callback(self):
        self._update_label_colors()

    def _update_label_colors(self) -> None:
        validations = {
            self.char_name_entry: not self.char_name_entry.get_value(),
            self.age_entry: not self.age_entry.get_value(),
            self.natinality_entry: not self.natinality_entry.get_value(),
            self.residence_entry: not self.residence_entry.get_value(),
            self.birthpalce_entry: not self.birthpalce_entry.get_value(),
            self.gender_entry: self.gender_entry.get_value() == "未选择",
            self.language_own_entry: not self.language_own_entry.get_text()
        }

        for entry, is_invalid in validations.items():
            if is_invalid:
                entry.label.setStyleSheet("color: #FFB700;")
            else:
                entry.label.setStyleSheet("")


class StatsInformationGroup(TFBaseFrame):

    def __init__(self, parent=None):
        self.entries = {}
        super().__init__(radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedWidth(140)
    
        self.entries['dice_mode'] = self.create_value_entry(
            name="dice_mode",
            label_text="模式:",
            label_size=65,
            value_size=50,
            height=24,
            enable=False
        )
        self.main_layout.addWidget(self.entries['dice_mode'])

    def update_from_config(self, config: dict) -> None:
        for name, entry in list(self.entries.items()):
            if name != 'dice_mode':
                try:
                    entry.blockSignals(True)
                    if name in self._components:
                        del self._components[name]
                    self.main_layout.removeWidget(entry)
                    del self.entries[name]
                    entry.deleteLater()
                except RuntimeError:
                    continue

        mode = config.get("mode", "天命")
        self.entries['dice_mode'].blockSignals(True)
        self.entries['dice_mode'].set_value(mode)
        self.entries['dice_mode'].blockSignals(False)

        if mode == "购点":
            points_config = config.get("points", {})
            available_points = points_config.get("available", 480)
            self.parent.basic_stats_group.total_points = available_points
            
            self.entries['points_available'] = self.create_value_entry(
                name="points_available",
                label_text="可用点数:",
                label_size=65,
                value_text=str(available_points),
                value_size=50,
                height=24,
                enable=False
            )

            stats_range = f"{points_config.get('lower_limit', 30)}-{points_config.get('upper_limit', 80)}"
            self.entries['stats_range'] = self.create_value_entry(
                name="stats_range",
                label_text="属性范围:",
                label_size=65,
                value_size=50,
                value_text=stats_range,
                height=24,
                enable=False
            )

            custom_luck = "是" if points_config.get("custom_luck", False) else "否"
            self.entries['allow_custom_luck'] = self.create_value_entry(
                name="allow_custom_luck",
                label_text="自定义LUK:",
                label_size=65,
                value_size=50,
                value_text=custom_luck,
                height=24,
                enable=False
            )

            self.main_layout.addWidget(self.entries['points_available'])
            self.main_layout.addWidget(self.entries['stats_range'])
            self.main_layout.addWidget(self.entries['allow_custom_luck'])

        elif mode == "天命":
            destiny_config = config.get("destiny", {})
            
            self.entries['dice_count'] = self.create_value_entry(
                name="dice_count",
                label_text="骰子数量:",
                label_size=65,
                value_size=50,
                value_text=str(destiny_config.get("dice_count", "3")),
                height=24,
                enable=False
            )

            allow_exchange = destiny_config.get("allow_exchange", False)
            self.entries['allow_exchange'] = self.create_value_entry(
                name="allow_stats_exchange",
                label_text="属性交换:",
                label_size=65,
                value_size=50,
                value_text="允许" if allow_exchange else "禁止",
                height=24,
                enable=False
            )

            exchange_count = destiny_config.get("exchange_count", "1") if allow_exchange else "N/A"
            self.entries['exchange_count'] = self.create_value_entry(
                name="exchange_count",
                label_text="交换次数:",
                label_size=65,
                value_size=50,
                value_text=exchange_count,
                height=24,
                enable=False
            )

            self.main_layout.addWidget(self.entries['dice_count'])
            self.main_layout.addWidget(self.entries['allow_exchange'])
            self.main_layout.addWidget(self.entries['exchange_count'])


class BasicStatsGroup(TFBaseFrame):
    
    def __init__(self, parent=None):
        self.stats_entries = {}
        self.derived_entries = {}
        self.total_points = 0
        super().__init__(layout_type=QGridLayout, radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK']
        for i, stat in enumerate(stats):
            row = i // 3
            col = i % 3
            entry = self.create_value_entry(
                name=stat.lower(),
                label_text=f"{stat}:",
                value_text="0",
                value_size=30,
                label_size=40,
                number_only=True,
                allow_decimal=False,
                max_digits=2
            )
            entry.value_changed.connect(self._update_derived_stats)
            entry.value_changed.connect(self._update_points_available)
            entry.value_changed.connect(self._update_radar_stats)
            self.stats_entries[stat] = entry
            self.main_layout.addWidget(entry, row, col)


        derived_stats = [
            ('HP', 'HP'),
            ('MP', 'MP'),
            ('SAN', 'San'),
            ('MOV', 'Mv.'),
            ('DB', 'DB'),
            ('Build', 'Bd.')
        ]

        for i, (stat_key, label_text) in enumerate(derived_stats):
            row = i // 2
            col = 3 + (i % 2)
            entry = self.create_value_entry(
                name=label_text.lower(),
                label_text=label_text + ":",
                value_text="N/A",
                value_size=30,
                label_size=40,
                number_only=True,
                enable=False
            )
            self.derived_entries[stat_key] = entry
            self.main_layout.addWidget(entry, row, col)

    def _get_stat_value(self, stat: str) -> int:
        try:
            value = self.stats_entries[stat].get_value()
            return int(value) if value else 0
        except (ValueError, KeyError):
            return 0
        
    def _update_derived_stats(self) -> None:
        str_val = self._get_stat_value('STR')
        con_val = self._get_stat_value('CON')
        siz_val = self._get_stat_value('SIZ')
        dex_val = self._get_stat_value('DEX')
        pow_val = self._get_stat_value('POW')

        if self.stats_entries['CON'].get_value() and self.stats_entries['SIZ'].get_value():
            hp = (con_val + siz_val) // 10
            self.derived_entries['HP'].set_value(str(hp))
        else:
            self.derived_entries['HP'].set_value("N/A")

        if self.stats_entries['POW'].get_value():
            mp = pow_val // 5
            self.derived_entries['MP'].set_value(str(mp))
        else:
            self.derived_entries['MP'].set_value("N/A")

        if self.stats_entries['POW'].get_value():
            self.derived_entries['SAN'].set_value(str(pow_val))
        else:
            self.derived_entries['SAN'].set_value("N/A")

        if (self.stats_entries['STR'].get_value() and 
            self.stats_entries['DEX'].get_value() and 
            self.stats_entries['SIZ'].get_value()):
            mov = self._calculate_mov(str_val, dex_val, siz_val)
            self.derived_entries['MOV'].set_value(mov)
        else:
            self.derived_entries['MOV'].set_value("N/A")

        if self.stats_entries['STR'].get_value() and self.stats_entries['SIZ'].get_value():
            db, build = self._calculate_db_and_build(str_val, siz_val)
            self.derived_entries['DB'].set_value(db)
            self.derived_entries['Build'].set_value(build)
        else:
            self.derived_entries['DB'].set_value("N/A")
            self.derived_entries['Build'].set_value("N/A")

    def _calculate_mov(self, str_val: int, dex_val: int, siz_val: int) -> str:
        if not all([str_val, dex_val, siz_val]):
            return "N/A"
            
        if str_val >= siz_val and dex_val >= siz_val:
            return "9"
        elif str_val <= siz_val and dex_val <= siz_val:
            return "7"
        else:
            return "8"
        
    def _calculate_db_and_build(self, str_val: int, siz_val: int) -> tuple[str, str]:
        if not all([str_val, siz_val]):
            return "N/A", "N/A"
            
        total = str_val + siz_val
        
        if total < 65:
            return "-2", "-2"
        elif total < 85:
            return "-1", "-1"
        elif total < 125:
            return "0", "0"
        elif total < 165:
            return "+1d4", "+1"
        elif total < 205:
            return "+1d6", "+2"
        elif total < 285:
            return "+2d6", "+3"
        elif total < 365:
            return "+3d6", "+4"
        elif total < 445:
            return "+4d6", "+5"
        else:
            return "+5d6", "+6"
        
    def _update_points_available(self) -> None:
        if self.parent.stats_info_group.entries['dice_mode'].get_value() != "购点":
            return
            
        total_used = sum(self._get_stat_value(stat) for stat in self.stats_entries)
        
        points_remaining = self.total_points - total_used
        points_entry = self.parent.stats_info_group.entries.get('points_available')
        points_entry.set_value(str(points_remaining))

    def _update_radar_stats(self) -> None:
        stats = {}
        for stat, entry in self.stats_entries.items():
            value = entry.get_value()
            stats[stat.upper()] = float(value) if value else 0

        self.parent.radar_graph.update_stats(stats)


class DiceResultFrame(TFBaseFrame):
    
    def __init__(self, dice_count: int, parent=None):
        self.dice_count = dice_count
        self.rolls_data: List[Dict[str, int]] = []
        super().__init__(QVBoxLayout, radius=10, level=1, parent=parent)

    def _setup_content(self) -> None:
        self.rolls_data = self._generate_rolls()
        
        options = []
        for _, roll in enumerate(self.rolls_data, 1):
            base_stats = []
            total_without_luck = 0
            for stat, value in roll.items():
                if stat != 'LUK':
                    base_stats.append(f"{stat}:{value}")
                    total_without_luck += value
            total_with_luck = total_without_luck + roll['LUK']
            
            base_stats_text = " ".join(base_stats)
            stats_text = f"{base_stats_text}\n总计（基础值/含幸运值）：{total_without_luck}/{total_with_luck}"
            options.append(stats_text)

        self.radio_group = self.create_radio_group(
            name="dice_results",
            options=options,
            label_font=NotoSerifNormal,
            height=48,
            spacing=5
        )
        
        for btn in self.radio_group.radio_buttons:
            btn.value_changed.connect(self._on_selection_changed)
        
        self.main_layout.addWidget(self.radio_group)

    def update_dice_count(self, new_count: int) -> None:
        old_count = len(self.rolls_data)
        if new_count <= old_count:
            self.rolls_data = self.rolls_data[:new_count]
        else:
            additional_count = new_count - old_count
            self.rolls_data.extend(self._generate_additional_rolls(additional_count))
            
        options = []
        for roll in self.rolls_data:
            base_stats = []
            total_without_luck = 0
            for stat, value in roll.items():
                if stat != 'LUK':
                    base_stats.append(f"{stat}:{value}")
                    total_without_luck += value
            total_with_luck = total_without_luck + roll['LUK']
            
            base_stats_text = " ".join(base_stats)
            stats_text = f"{base_stats_text}\n总计（基础值/含幸运值）：{total_without_luck}/{total_with_luck}"
            options.append(stats_text)
            
        old_selection = next(
            (i for i, btn in enumerate(self.radio_group.radio_buttons) if btn.is_checked()),
            -1
        )
        
        self.radio_group.setParent(None)
        self.radio_group.deleteLater()
        
        self.radio_group = self.create_radio_group(
            name="dice_results",
            options=options,
            label_font=NotoSerifNormal,
            height=48,
            spacing=5
        )
        
        for btn in self.radio_group.radio_buttons:
            btn.value_changed.connect(self._on_selection_changed)
            
        if old_selection >= 0 and old_selection < len(options):
            self.radio_group.radio_buttons[old_selection].set_checked(True)
            
        self.main_layout.addWidget(self.radio_group)
        
    def _generate_additional_rolls(self, count: int) -> List[Dict[str, int]]:
        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK']
        rolls = []
        
        for _ in range(count):
            roll = {}
            for stat in stats:
                roll[stat] = self._roll_stat(stat)
            rolls.append(roll)
            
        return rolls

    def _on_selection_changed(self, checked: bool) -> None:
        if checked:
            selected_index = self.radio_group.radio_buttons.index(
                self.sender()
            )
            selected_stats = self.rolls_data[selected_index]
            self.values_changed.emit({"selected_stats": selected_stats})

    def _generate_rolls(self) -> List[Dict[str, int]]:
        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK']
        rolls = []
        
        for _ in range(self.dice_count):
            roll = {}
            for stat in stats:
                roll[stat] = self._roll_stat(stat)
            rolls.append(roll)
            
        return rolls

    def _roll_stat(self, stat_type: str) -> int:
        if stat_type in ['SIZ', 'INT', 'EDU']:
            result = (sum(random.randint(1, 6) for _ in range(2)) + 6) * 5
        else:
            result = sum(random.randint(1, 6) for _ in range(3)) * 5
        return result
        
    def _on_confirm_clicked(self) -> None:
        selected_index = self.radio_group.radio_buttons.index(
            next(btn for btn in self.radio_group.radio_buttons if btn.is_checked())
        )
        if selected_index >= 0:
            selected_stats = self.rolls_data[selected_index]
            self.values_changed.emit({"selected_stats": selected_stats})

    def get_values(self) -> dict:
        values = super().get_values()
        if hasattr(self, 'radio_group'):
            selected_index = next(
                (i for i, btn in enumerate(self.radio_group.radio_buttons) if btn.is_checked()),
                -1
            )
            if selected_index >= 0:
                values["selected_stats"] = self.rolls_data[selected_index]
        return values
    

class RadarGraph(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=10, parent=parent)
        self.stats = {}
        self.stats_order = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUK']
        
        self.grid_color = QColor("#3A414D")
        self.stat_color = QColor("#4E5666")
        self.text_color = QColor("#FFFFFF")
        
    def _setup_content(self) -> None:
        self.setFixedWidth(300)
        
    def update_stats(self, stats: dict) -> None:
        self.stats = stats
        self.update()
        
    def paintEvent(self, event):
        if not self.stats:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 40
        
        self._draw_grid(painter, center_x, center_y, radius)
        
        self._draw_stats(painter, center_x, center_y, radius)
        
        self._draw_labels(painter, center_x, center_y, radius)
        
    def _draw_grid(self, painter: QPainter, center_x: float, center_y: float, radius: float) -> None:
        grid_pen = QPen(self.grid_color)
        grid_pen.setWidth(1)
        
        for i in range(5):
            current_radius = radius * (i + 1) / 5
            points = []
            for j in range(9):
                angle = j * 2 * math.pi / 9 - math.pi / 2
                x = center_x + current_radius * math.cos(angle)
                y = center_y + current_radius * math.sin(angle)
                points.append((x, y))
            
            painter.setPen(grid_pen)
            
            for j in range(9):
                painter.drawLine(
                    int(points[j][0]), 
                    int(points[j][1]), 
                    int(points[(j + 1) % 9][0]), 
                    int(points[(j + 1) % 9][1])
                )
            
            if i < 4:
                value = (i + 1) * 20
                text_pen = QPen(self.text_color)
                painter.setPen(text_pen)
                painter.drawText(
                    int(center_x - 10), 
                    int(center_y - current_radius - 5),
                    str(value)
                )
                
        painter.setPen(grid_pen)
        for i in range(9):
            angle = i * 2 * math.pi / 9 - math.pi / 2
            end_x = center_x + radius * math.cos(angle)
            end_y = center_y + radius * math.sin(angle)
            painter.drawLine(
                int(center_x),
                int(center_y),
                int(end_x),
                int(end_y)
            )
            
    def _draw_stats(self, painter: QPainter, center_x: float, center_y: float, radius: float) -> None:
        stat_pen = QPen(self.stat_color)
        stat_pen.setWidth(2)
        painter.setPen(stat_pen)
        
        points = []
        for i, stat in enumerate(self.stats_order):
            value = float(self.stats.get(stat, 0))
            value = min(value, 100)
            current_radius = radius * value / 100
            angle = i * 2 * math.pi / 9 - math.pi / 2
            x = center_x + current_radius * math.cos(angle)
            y = center_y + current_radius * math.sin(angle)
            points.append((x, y))
        
        for i in range(len(points)):
            painter.drawLine(
                int(points[i][0]),
                int(points[i][1]),
                int(points[(i + 1) % 9][0]),
                int(points[(i + 1) % 9][1])
            )
            
    def _draw_labels(self, painter: QPainter, center_x: float, center_y: float, radius: float) -> None:
        text_pen = QPen(self.text_color)
        painter.setPen(text_pen)
        
        font = NotoSerifNormal
        font.setPointSize(9)
        painter.setFont(font)
        
        for i, stat in enumerate(self.stats_order):
            value = float(self.stats.get(stat, 0))
            value = min(value, 100)
            angle = i * 2 * math.pi / 9 - math.pi / 2
            
            label_radius = radius + 20
            label_x = center_x + label_radius * math.cos(angle)
            label_y = center_y + label_radius * math.sin(angle)
            
            text = f"{stat}:{int(value)}"
            painter.drawText(
                int(label_x - 20), 
                int(label_y + 5), 
                text
            )
            
    def get_values(self) -> dict:
        return self.stats
        
    def update_component_value(self, name: str, value: str) -> None:
        if name in self.stats_order:
            try:
                self.stats[name] = float(value)
                self.update()
            except (ValueError, TypeError):
                self.stats[name] = 0


class LanguageSelectionDialog(TFBaseDialog):
    def __init__(self, parent=None):
        super().__init__(
            title="选择语言", 
            layout_type=QGridLayout, 
            parent=parent,
            button_config=[
                {"text": "确定", "callback": self._on_ok_clicked}
                ]
        )

    def _setup_content(self) -> None:
        languages = [
            "汉语", "英语", "日语", "法语", "韩语",
            "泰语", "俄罗斯语", "西班牙语", "阿拉伯语", "葡萄牙语",
            "希伯来语", "越南语", "印地语", "其他"
        ]

        self.language_group = self.create_radio_group(
            name="language_selection",
            options=languages[:30],
            height=24,
            spacing=10
        )

        for i, radio in enumerate(self.language_group.radio_buttons):
            row = i // 5
            if row >= 2:
                row += 1
            col = i % 5
            self.main_layout.addWidget(radio, row, col)

    def validate(self) -> List[Tuple[Any, str]]:
        if not self.language_group.get_value():
            return [(self.language_group, "请选择母语")]
        return []

    def get_validated_data(self) -> Optional[str]:
        return self.language_group.get_value()
    

class AgeReductionDialog(TFBaseDialog):
    def __init__(self, parent=None, reduction_stats: List[str] = None, 
                 total_reduction: int = 0, current_stats: Dict[str, int] = None):
        self.total_reduction = total_reduction
        self.reduction_stats = reduction_stats or []
        self.current_stats = current_stats or {}
        self.stat_entries = {}
        
        super().__init__(
            title=f"年龄修正",
            parent=parent,
            button_config=[
                {"text": "确定", "callback": self._on_ok_clicked},
                {"text": "取消", "callback": self.reject, "role": "reject"}
            ]
        )

    def _setup_content(self) -> None:
        self.info_label = self.create_value_entry(
            name="info",
            label_text="请将以下点数进行分配：",
            value_text=str(self.total_reduction),
            label_size=150,
            value_size=50,
            enable=False
        )
        self.main_layout.addWidget(self.info_label)

        self.stat_entries = {}
        for stat in self.reduction_stats:
            current_value = self.current_stats.get(stat, 0)
            entry = self.create_value_entry(
                name=f"deduct_{stat.lower()}",
                label_text=f"{stat}（当前: {current_value}）:",
                value_text="0",
                label_size=150,
                value_size=50,
                number_only=True,
                allow_decimal=False,
                allow_negative=False,
                max_digits=2
            )
            entry.value_changed.connect(self._update_remaining)
            self.stat_entries[stat] = entry
            self.main_layout.addWidget(entry)

    def _update_remaining(self) -> None:
        total_allocated = sum(
            int(entry.get_value() or '0')
            for entry in self.stat_entries.values()
        )
        remaining = max(0, self.total_reduction - total_allocated)
        self.info_label.set_value(str(remaining))

    def validate(self) -> List[Tuple[Any, str]]:
        errors = []
        total = 0

        for stat, entry in self.stat_entries.items():
            try:
                value = int(entry.get_value() or '0')
                current_value = self.current_stats.get(stat, 0)
                
                if value < 0:
                    errors.append((entry, f"{stat} 的减少值不能为负数"))
                elif current_value - value < 1:
                    errors.append((entry, f"{stat} 不能减少到小于 1（当前值：{current_value}）"))
                total += value
            except ValueError:
                errors.append((entry, f"{stat} 的值无效"))

        if total != self.total_reduction:
            errors.append((
                self.info_label,
                f"总减少值必须等于 {self.total_reduction}（当前：{total}）"
            ))

        return errors

    def get_validated_data(self) -> Dict[str, int]:
        return {
            stat: int(entry.get_value() or '0')
            for stat, entry in self.stat_entries.items()
        }


class CharacterDescriptionDialog(TFBaseDialog):
    def __init__(self, parent=None, stats: Dict[str, int] = None):
        self.stats = stats or {}
        super().__init__(
            title="角色信息",
            layout_type=QGridLayout,
            parent=parent,
            button_config=[{"text": "确定", "callback": self.accept}]
        )
        self.resize(800, 600)

    def _setup_content(self) -> None:
        descriptions = {
            'STR': ('力量', self._get_str_description),
            'CON': ('体质', self._get_con_description),
            'SIZ': ('体型', self._get_siz_description),
            'DEX': ('敏捷', self._get_dex_description),
            'APP': ('外貌', self._get_app_description),
            'INT': ('智力', self._get_int_description),
            'POW': ('信仰', self._get_pow_description),
            'EDU': ('教育', self._get_edu_description),
            'LUK': ('幸运', self._get_luck_description),
        }

        for idx, (stat, (full_name, desc_func)) in enumerate(descriptions.items()):
            stat_frame = TFBaseFrame(parent=self)
            
            header = stat_frame.create_label(
                text=f"{stat} ({full_name}): {self.stats[stat]}",
                height=24
            )
            
            description = stat_frame.create_label(
                text=desc_func(self.stats[stat]),
                height=48,
            )
            
            stat_frame.main_layout.addWidget(header)
            stat_frame.main_layout.addWidget(description)
            
            row = idx // 2
            col = idx % 2
            self.main_layout.addWidget(stat_frame, row, col)

    def _get_str_description(self, value: int) -> str:
        if value <= 15:
            return "几乎没有力量，连拧开瓶盖或提起椅子都显得吃力"
        elif value <= 40:
            return "明显偏弱，搬重物或长时间体力活让人感到吃不消"
        elif value <= 60:
            return "普通人的平均力量，可以胜任一般的日常体力活动"
        elif value <= 80:
            return "强壮有力，能够轻松完成体能挑战，比如举重或短跑"
        else:
            return "非凡的力量，举重、破门而入甚至搬动家具都不在话下"

    def _get_con_description(self, value: int) -> str:
        if value <= 20:
            return "体弱多病，稍微受凉就可能卧床不起"
        elif value <= 40:
            return "身体较差，经常生病或感到疲惫"
        elif value <= 60:
            return "健康水平一般，能应付日常但抗压力较弱"
        elif value <= 80:
            return "身体强壮，少有生病，能快速恢复"
        else:
            return "铁打的体格，几乎百毒不侵，无惧严酷环境"

    def _get_siz_description(self, value: int) -> str:
        if value <= 20:
            return "身材瘦小，甚至看起来像个未成年的孩子"
        elif value <= 40:
            return "个头不高，身形纤细，通常在群体中不显眼"
        elif value <= 60:
            return "标准体型，普通人的平均身材"
        elif value <= 80:
            return "高大威猛或体格魁梧，在人群中常常显得突出"
        elif value <= 100:
            return "身材庞大，无论身高还是体型都令人印象深刻"
        else:
            return "巨人般的身材，可能需要特制的衣物或家具"

    def _get_dex_description(self, value: int) -> str:
        if value <= 20:
            return "动作迟缓，常常打翻物品或被简单的运动绊住"
        elif value <= 40:
            return "动作笨拙，缺乏流畅的肢体协调性"
        elif value <= 60:
            return "协调性普通，可以完成一般的体育活动"
        elif value <= 80:
            return "动作灵活，具备优秀的反应速度和身体控制能力"
        else:
            return "灵活性惊人，像体操运动员或特技演员般敏捷"

    def _get_app_description(self, value: int) -> str:
        if value <= 20:
            return "外貌怪异或令人不适，可能被社会视为异类"
        elif value <= 40:
            return "长相平凡，容易被忽略，不会引起特别的关注"
        elif value <= 60:
            return "中等外貌，符合大众审美标准"
        elif value <= 80:
            return "吸引人的外貌，能轻松赢得别人的好感"
        else:
            return "美得惊艳或英俊得无法忽视，如明星般光彩夺目"

    def _get_int_description(self, value: int) -> str:
        if value <= 20:
            return "思维迟缓，可能无法理解复杂概念"
        elif value <= 40:
            return "智力偏低，但能应付基本的逻辑和任务"
        elif value <= 60:
            return "普通水平的智力，足以理解日常问题"
        elif value <= 80:
            return "聪明机智，擅长分析问题和理解抽象概念"
        else:
            return "天才般的头脑，往往能以超乎常人的视角解决问题"

    def _get_pow_description(self, value: int) -> str:
        if value <= 20:
            return "意志薄弱，容易被恐惧或压力击垮"
        elif value <= 40:
            return "心志不够坚韧，面对挫折常常退缩"
        elif value <= 60:
            return "意志力普通，能应对正常的生活压力"
        elif value <= 80:
            return "坚定的意志力，难以被外界轻易动摇"
        else:
            return "超凡的意志力，几乎无惧任何挑战或心理打击"

    def _get_edu_description(self, value: int) -> str:
        if value <= 20:
            return "接受的教育极为有限，基本的知识水平"
        elif value <= 40:
            return "初等教育程度，了解一些基础的文化和技能"
        elif value <= 60:
            return "中等教育水平，具备广泛的基础知识"
        elif value <= 80:
            return "高等教育背景，拥有丰富的知识储备"
        else:
            return "学术造诣深厚，几乎在某些领域达到专家级水平"

    def _get_luck_description(self, value: int) -> str:
        if value <= 20:
            return "霉运缠身，经常遇到倒霉事"
        elif value <= 40:
            return "偶尔不走运，但也不是完全的倒霉鬼"
        elif value <= 60:
            return "普通的运气，既没有太多好运也没有太多霉运"
        elif value <= 80:
            return "好运常伴，经常在关键时刻扭转局势"
        else:
            return "福星高照，无论做什么事情似乎总能成功"


class StatExchangeDialog(TFBaseDialog):
    def __init__(self, parent=None, remaining_times: int = 0, current_stats: Dict[str, int] = None):
        self.remaining_times = remaining_times
        self.current_stats = current_stats or {}
        self.stat_entries = {}
        
        super().__init__(
            title="Exchange Stats",
            parent=parent,
            button_config=[
                {"text": "交换", "callback": self._on_ok_clicked},
                {"text": "取消", "callback": self.reject, "role": "reject"}
            ]
        )

    def _setup_content(self) -> None:
        times_label = self.create_label(
            text=f"剩余交换次数：{self.remaining_times}",
            height=24
        )
        self.main_layout.addWidget(times_label)
        
        stats = ['STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU']
        for stat in stats:
            checkbox = self.create_check_with_label(
                name=stat,
                label_text=f"{stat}: {self.current_stats.get(stat, 0)}",
                height=24
            )
            self.stat_entries[stat] = checkbox
            self.main_layout.addWidget(checkbox)

    def validate(self) -> List[Tuple[Any, str]]:
        selected = [
            stat for stat, entry in self.stat_entries.items()
            if entry.get_value()
        ]
        
        if len(selected) != 2:
            return [(self.stat_entries[selected[0]] if selected else None,
                    "请选择恰好两个属性进行交换")]
        return []

    def get_validated_data(self) -> Tuple[str, str]:
        selected = [
            stat for stat, entry in self.stat_entries.items()
            if entry.get_value()
        ]
        return tuple(selected)
    
