from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout

from ui.components.tf_base_frame import TFBaseFrame
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

        self.placeholder_button = self.create_button(
            name="placeholder_button",
            text="Placeholder",
            tooltip="This is just a placeholder button",
            width=150,
            on_clicked=self._on_placeholder_clicked
        )
        self.right_panel.layout().addWidget(self.placeholder_button)

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

        TFApplication.instance().show_message(f"PL - {user_sid}来了！", 3000, 'green')

    def _on_user_left(self, user_sid: str):
        if user_sid in self.player_list:
            self.player_list.remove(user_sid)
            self.current_pl_count -= 1
            self.update_component_value("current_pl", str(self.current_pl_count))
            self._refresh_player_list_display()

            TFApplication.instance().show_message(f"PL - {user_sid} 跑了！", 3000, 'yellow')

    def _on_admin_closed(self):
        TFApplication.instance().show_message("KP关闭了房间", 3000, 'yellow')

    def _on_disconnected(self):
        pass

    def _refresh_player_list_display(self):
        text = "\n".join(self.player_list)
        self.update_component_value("players_text_edit", text)
