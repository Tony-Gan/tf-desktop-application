from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout

from ui.components.tf_base_frame import TFBaseFrame
from ui.components.tf_option_entry import TFOptionEntry
from ui.tf_application import TFApplication
from implements.components.websocket_client import WebSocketClient


class KPFrame(TFBaseFrame):

    def __init__(self, parent=None):
        self.room_id = WebSocketClient.generate_room_id().upper()
        self.current_pl_count = 0
        self.player_list = []

        super().__init__(layout_type=QHBoxLayout, parent=parent)

        self.ws_client = WebSocketClient(room_id=self.room_id, role="admin", parent=self)
        self.ws_client.connection_error.connect(self._on_connection_error)
        self.ws_client.joined_room.connect(self._on_joined_room)
        self.ws_client.user_joined.connect(self._on_user_joined)
        self.ws_client.user_left.connect(self._on_user_left)
        self.ws_client.admin_closed.connect(self._on_admin_closed)
        self.ws_client.disconnected.connect(self._on_disconnected)
        self.ws_client.start()

    def _setup_content(self):
        self.left_panel = TFBaseFrame(layout_type=QVBoxLayout, parent=self)
        self.left_panel.setFixedWidth(300)
        self.add_child("left_panel", self.left_panel)

        self.room_id_entry = self.create_button_entry(
            name="room_id_entry",
            label_text="房间ID",
            label_size=75,
            button_text="复制",
            entry_text=self.room_id,
            button_callback=self._on_copy_room_id,
            button_tooltip="PL通过此ID进入相同房间",
            button_size=50,
            height=24,
        )
        self.room_id_entry.entry_field.setEnabled(False)
        self.left_panel.layout().addWidget(self.room_id_entry)

        self.current_pl_entry = self.create_value_entry(
            name="current_pl",
            label_text="当前PL列表",
            value_text="0",
            height=24,
            label_size=75,
            value_size=150,
        )
        self.left_panel.layout().addWidget(self.current_pl_entry)

        self.players_text_edit = self.create_text_edit(
            name="players_text_edit",
            text="",
            width=480,
            height=150,
            placeholder_text="还没有PL哦",
            read_only=True
        )
        self.left_panel.layout().addWidget(self.players_text_edit)

        self.right_panel = TFBaseFrame(layout_type=QVBoxLayout, parent=self)
        self.add_child("right_panel", self.right_panel)

        self.dice_panel = DicePanelFrame(parent=self)
        self.right_panel.layout().addWidget(self.dice_panel)

        self.dice_result_text_edit = self.create_text_edit(
            name="dice_result_text_edit",
            text="",
            width=400,
            height=250,
            placeholder_text="掷骰结果和信息会出现在这里...",
            read_only=True
        )
        self.right_panel.layout().addWidget(self.dice_result_text_edit)

    def _on_copy_room_id(self):
        room_id = self.room_id_entry.get_text()
        if room_id:
            TFApplication.clipboard().setText(room_id)
            TFApplication.instance().show_message(f"房间号已复制到剪贴板：{room_id}", 5000)

    def _on_placeholder_clicked(self):
        old_text = self.get_component_value("dice_result_text_edit") or ""
        new_text = old_text + "\n[Placeholder Button] Action triggered!"
        self.update_component_value("dice_result_text_edit", new_text)

    def _on_connection_error(self, err_msg: str):
        TFApplication.instance().show_message(f"KP Error: {err_msg}", 5000, 'red')

    def _on_joined_room(self, sid: str):
        pass

    def _on_user_joined(self, user_sid: str):
        self.current_pl_count += 1
        self.update_component_value("current_pl", str(self.current_pl_count))

        self.player_list.append(user_sid)
        self._refresh_player_list_display()
        self.dice_panel.update_player_list(self.player_list)

        TFApplication.instance().show_message(f"PL - {user_sid}来了！", 3000, 'green')

    def _on_user_left(self, user_sid: str):
        if user_sid in self.player_list:
            self.player_list.remove(user_sid)
            self.current_pl_count -= 1
            self.update_component_value("current_pl", str(self.current_pl_count))
            self._refresh_player_list_display()
            self.dice_panel.update_player_list(self.player_list)

            TFApplication.instance().show_message(f"PL - {user_sid} 跑了！", 3000, 'yellow')

    def _on_admin_closed(self):
        TFApplication.instance().show_message("KP关闭了房间", 3000, 'yellow')

    def _on_disconnected(self):
        pass

    def _refresh_player_list_display(self):
        text = "\n".join(self.player_list)
        self.update_component_value("players_text_edit", text)


class DicePanelFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(layout_type=QVBoxLayout, parent=parent)

    def _setup_content(self):
        self.dice_type = self.create_option_entry(
            name="dice_type",
            label_text="掷骰类型",
            options=["自定义掷骰", "设定掷骰"],
            current_value="自定义掷骰",
            label_size=80,
            value_size=120
        )
        self.layout().addWidget(self.dice_type)
        self.dice_type.value_changed.connect(self._on_dice_type_changed)

        self.content_panel = TFBaseFrame(layout_type=QVBoxLayout, parent=self)
        self.layout().addWidget(self.content_panel)

        self.roll_button = self.create_button(
            name="roll_button",
            text="掷骰",
            width=100,
            on_clicked=self._on_roll_clicked
        )
        self.layout().addWidget(self.roll_button)
        self.layout().addStretch()

        self._setup_custom_dice_panel()

    def _setup_custom_dice_panel(self):
        self._clear_content_panel()

        self.dice_command = self.create_value_entry(
            name="dice_command",
            label_text="掷骰指令",
            label_size=80,
            value_size=200
        )
        self.content_panel.layout().addWidget(self.dice_command)

        self.dice_info = self.create_line_edit(
            name="dice_info",
            width=300,
        )
        self.content_panel.layout().addWidget(self.dice_info)

    def _setup_preset_dice_panel(self):
        self._clear_content_panel()

        self.preset_type = self.create_option_entry(
            name="preset_type",
            label_text="掷骰类型",
            options=["标准掷骰", "技能掷骰", "对抗掷骰", "暗骰"],
            current_value="标准掷骰",
            label_size=80,
            value_size=120
        )
        self.content_panel.layout().addWidget(self.preset_type)
        self.preset_type.value_changed.connect(self._on_preset_type_changed)

        self._setup_standard_dice_panel()

    def _setup_standard_dice_panel(self):
        self.roll_target = self.create_option_entry(
            name="roll_target",
            label_text="掷骰对象",
            options=[],
            current_value="",
            label_size=80,
            value_size=120,
            enable_filter=False
        )
        self.content_panel.layout().addWidget(self.roll_target)

        self.standard_value = self.create_value_entry(
            name="standard_value",
            label_text="标准值",
            label_size=80,
            value_size=120,
            number_only=True,
            allow_decimal=False,
            allow_negative=False
        )
        self.content_panel.layout().addWidget(self.standard_value)

        self.advantage = self.create_value_entry(
            name="advantage",
            label_text="优势/劣势",
            label_size=80,
            value_size=120,
            number_only=True,
            allow_decimal=False,
            allow_negative=True
        )
        self.content_panel.layout().addWidget(self.advantage)

        self.roll_info = self.create_line_edit(
            name="roll_info",
            width=300,
        )
        self.content_panel.layout().addWidget(self.roll_info)

    def _setup_skill_dice_panel(self):
        self.skill_roll_target = self.create_option_entry(
            name="skill_roll_target",
            label_text="掷骰对象",
            options=[],
            current_value="",
            label_size=80,
            value_size=120,
            enable_filter=True
        )
        self.content_panel.layout().addWidget(self.skill_roll_target)

        skill_level_frame = TFBaseFrame(layout_type=QHBoxLayout, parent=self)
        self.content_panel.layout().addWidget(skill_level_frame)

        self.skill = self.create_option_entry(
            name="skill",
            label_text="掷骰技能",
            options=[],
            current_value="",
            label_size=80,
            value_size=120,
            enable_filter=True
        )
        skill_level_frame.layout().addWidget(self.skill)

        self.skill_level = self.create_value_entry(
            name="skill_level",
            label_text="技能等级",
            label_size=80,
            value_size=80,
            number_only=True,
            allow_decimal=False,
            allow_negative=False
        )
        skill_level_frame.layout().addWidget(self.skill_level)

        self.skill_advantage = self.create_value_entry(
            name="skill_advantage",
            label_text="优势/劣势",
            label_size=80,
            value_size=120,
            number_only=True,
            allow_decimal=False,
            allow_negative=True
        )
        self.content_panel.layout().addWidget(self.skill_advantage)

        self.skill_roll_info = self.create_line_edit(
            name="skill_roll_info",
            width=300
        )
        self.content_panel.layout().addWidget(self.skill_roll_info)

    def _setup_vs_dice_panel(self):
        targets_frame = TFBaseFrame(layout_type=QHBoxLayout, parent=self)
        self.content_panel.layout().addWidget(targets_frame)

        self.vs_roll_target1 = self.create_option_entry(
            name="vs_roll_target1",
            label_text="掷骰对象1",
            options=[],
            current_value="",
            label_size=80,
            value_size=120,
            enable_filter=True
        )
        targets_frame.layout().addWidget(self.vs_roll_target1)

        self.vs_roll_target2 = self.create_option_entry(
            name="vs_roll_target2",
            label_text="掷骰对象2",
            options=[],
            current_value="",
            label_size=80,
            value_size=120,
            enable_filter=True
        )
        targets_frame.layout().addWidget(self.vs_roll_target2)

        skills_frame = TFBaseFrame(layout_type=QHBoxLayout, parent=self)
        self.content_panel.layout().addWidget(skills_frame)

        self.vs_skill1 = self.create_option_entry(
            name="vs_skill1",
            label_text="技能1",
            options=[],
            current_value="",
            label_size=60,
            value_size=100,
            enable_filter=True
        )
        skills_frame.layout().addWidget(self.vs_skill1)

        self.vs_skill_level1 = self.create_value_entry(
            name="vs_skill_level1",
            label_text="等级1",
            label_size=60,
            value_size=60,
            number_only=True,
            allow_decimal=False,
            allow_negative=False
        )
        skills_frame.layout().addWidget(self.vs_skill_level1)

        self.vs_skill2 = self.create_option_entry(
            name="vs_skill2",
            label_text="技能2",
            options=[],
            current_value="",
            label_size=60,
            value_size=100,
            enable_filter=True
        )
        skills_frame.layout().addWidget(self.vs_skill2)

        self.vs_skill_level2 = self.create_value_entry(
            name="vs_skill_level2",
            label_text="等级2",
            label_size=60,
            value_size=60,
            number_only=True,
            allow_decimal=False,
            allow_negative=False
        )
        skills_frame.layout().addWidget(self.vs_skill_level2)

        advantage_frame = TFBaseFrame(layout_type=QHBoxLayout, parent=self)
        self.content_panel.layout().addWidget(advantage_frame)

        self.vs_advantage1 = self.create_value_entry(
            name="vs_advantage1",
            label_text="优势/劣势1",
            label_size=80,
            value_size=80,
            number_only=True,
            allow_decimal=False,
            allow_negative=True
        )
        advantage_frame.layout().addWidget(self.vs_advantage1)

        self.vs_advantage2 = self.create_value_entry(
            name="vs_advantage2",
            label_text="优势/劣势2",
            label_size=80,
            value_size=80,
            number_only=True,
            allow_decimal=False,
            allow_negative=True
        )
        advantage_frame.layout().addWidget(self.vs_advantage2)

        self.strict_vs = self.create_check_with_label(
            name="strict_vs",
            label_text="严格对抗",
            checked=False
        )
        self.content_panel.layout().addWidget(self.strict_vs)

    def _setup_hidden_dice_panel(self):
        pass

    def _clear_content_panel(self):
        for i in reversed(range(self.content_panel.layout().count())): 
            widget = self.content_panel.layout().itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def _on_dice_type_changed(self, value):
        # 先保存第一行的选择组件
        dice_type = self.dice_type
        previous_layout = self.layout()
        
        # 创建新的内容面板
        old_content_panel = self.content_panel
        self.content_panel = TFBaseFrame(layout_type=QVBoxLayout, parent=self)
        
        # 设置新的内容
        if value == "自定义掷骰":
            self._setup_custom_dice_panel()
        else:
            self._setup_preset_dice_panel()
        
        # 替换旧的内容面板
        previous_layout.replaceWidget(old_content_panel, self.content_panel)
        old_content_panel.deleteLater()

    def _on_preset_type_changed(self, value):
        # 保存第2行的选择组件
        preset_type = self.preset_type
        previous_layout = self.content_panel.layout()
        
        # 清除第2行后的内容
        while previous_layout.count() > 1:
            item = previous_layout.itemAt(1)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    previous_layout.removeWidget(widget)
                    widget.deleteLater()
        
        # 根据选择设置不同的面板
        if value == "标准掷骰":
            self._setup_standard_dice_panel()
        elif value == "技能掷骰":
            self._setup_skill_dice_panel()
        elif value == "对抗掷骰":
            self._setup_vs_dice_panel()
        elif value == "暗骰":
            self._setup_hidden_dice_panel()

    def _on_roll_clicked(self):
        print("掷骰按钮被点击")

    def update_player_list(self, player_list):
        components_to_update = [
            "roll_target", "skill_roll_target", 
            "vs_roll_target1", "vs_roll_target2"
        ]
        
        for name in components_to_update:
            component = self._components.get(name)
            if component and isinstance(component, TFOptionEntry):
                component.update_options(player_list)
