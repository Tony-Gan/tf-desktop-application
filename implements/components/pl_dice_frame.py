from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt

from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication
from implements.components.websocket_client import WebSocketClient
from utils.helper import get_current_datetime


class PLFrame(TFBaseFrame):
    def __init__(self, parent=None):
        self.ws_client = None
        self.my_name = ""
        super().__init__(layout_type=QHBoxLayout, parent=parent)

    def _setup_content(self):
        self.left_panel = TFBaseFrame(layout_type=QVBoxLayout, parent=self)
        self.left_panel.setFixedWidth(300)
        self.add_child("left_panel", self.left_panel)

        self.player_name_entry = self.create_button_entry(
            name="player_name_entry",
            label_text="PL",
            button_text="修改",
            entry_text="",
            button_callback=self._on_player_name_update,
            button_tooltip="修改PL名称",
            label_size=80,
            entry_size=80,
            button_size=50,
            height=24,
        )
        self.left_panel.layout().addWidget(self.player_name_entry)

        self.enter_room_entry = self.create_button_entry(
            name="enter_room_entry",
            label_size=80,
            label_text="房间ID",
            button_text="进入",
            entry_text="",
            button_callback=self._on_enter_room,
            button_tooltip="你的KP没告诉你房间号吗？",
            button_size=50,
            height=24,
        )
        self.left_panel.layout().addWidget(self.enter_room_entry)

        self.pc_data_entry = self.create_button_entry(
            name="pc_data_entry",
            label_text="PC信息卡",
            label_size=80,
            button_text="上传",
            entry_text="",
            button_callback=self._on_pc_data_upload,
            button_tooltip="上传你的PC信息卡",
            button_size=50,
            height=24,
        )
        self.left_panel.layout().addWidget(self.pc_data_entry)

        self.left_panel.main_layout.addStretch()

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
            read_only=True,
            scroll_policy=(Qt.ScrollBarPolicy.ScrollBarAlwaysOff, Qt.ScrollBarPolicy.ScrollBarAlwaysOn),
            enable_rich_text=True
        )
        self.right_panel.layout().addWidget(self.dice_result_text_edit)

    def _on_player_name_update(self):
        new_name = self.player_name_entry.entry_field.text().strip()
        if not new_name:
            TFApplication.instance().show_message("名字不能为空", 5000, 'yellow')
            return
            
        old_name = self.my_name
        self.my_name = new_name
        
        time_str = get_current_datetime(show_time=True, show_seconds=True)
        self._add_debug_message(f"本地名称已更新: {old_name} → {new_name}", 'info')
        TFApplication.instance().show_message(f"名字已更新为：{new_name}", 3000, 'green')
        
        if self.ws_client and self.ws_client.sid:
            self._add_debug_message(f"发送名称更新请求到服务器...", 'info')
            self.ws_client.send_message({
                "type": "name_update",
                "old_name": old_name,
                "new_name": new_name,
                "sid": self.ws_client.sid,
                "token": self.ws_client.room_id
            })

    def _on_enter_room(self):
        room_id = self.enter_room_entry.entry_field.text().strip().upper()
        display_name = self._get_display_name()

        if not room_id:
            TFApplication.instance().show_message("房间号为空", 5000, 'yellow')
            return

        self._add_debug_message(f"尝试进入房间: {room_id}")
        self._add_debug_message(f"服务器地址: ws://127.0.0.1:8765")

        self.enter_room_entry.button.setEnabled(False)
        self.enter_room_entry.entry_field.setEnabled(False)

        if self.ws_client:
            if self.ws_client.isRunning():
                self._add_debug_message("关闭现有连接...", 'warning')
                self.ws_client.stop()
                self.ws_client.quit()
                self.ws_client.wait()
            self.ws_client = None

        self._add_debug_message("创建新的连接...")
        self.ws_client = WebSocketClient(
            room_id=room_id,
            role="player",
            display_name=self.my_name or self.player_name_entry.entry_field.text().strip(),
            parent=self
        )
        self.ws_client.connection_error.connect(self._on_connection_error)
        self.ws_client.joined_room.connect(self._on_joined_room)
        self.ws_client.user_joined.connect(self._on_user_joined)
        self.ws_client.user_left.connect(self._on_user_left)
        self.ws_client.admin_closed.connect(self._on_admin_closed)
        self.ws_client.disconnected.connect(self._on_disconnected)
        self.ws_client.name_update_confirmed.connect(self.handle_name_update_confirm)
        self.ws_client.dice_result_received.connect(self._on_dice_result_received)
        self.ws_client.start()

        self.my_name = display_name

    def _on_dice_result_received(self, dice_text: str):
        self._add_dice_result(dice_text)
    
    def _on_pc_data_upload(self):
        pass

    def _get_display_name(self):
        pl_name = self.player_name_entry.entry_field.text().strip()
        pc_name = 'placeholder'
        
        if pl_name and pc_name:
            return f"[{pl_name}] - [{pc_name}]"
        elif pl_name:
            return f"[{pl_name}] - [OB]"
        elif pc_name:
            return f"[未命名] - [{pc_name}]"
        return self.my_name

    def _on_placeholder_clicked(self):
        old_text = self.get_component_value("dice_result_text_edit") or ""
        new_text = old_text + "\n[Placeholder Button] Action triggered!"
        self.update_component_value("dice_result_text_edit", new_text)

    def _on_connection_error(self, err_msg: str):
        self._add_debug_message(f"连接错误: {err_msg}", 'error')
        TFApplication.instance().show_message(f"连接错误: {err_msg}", 5000, 'red')
        
        self._enable_input_fields()
        
        if self.ws_client:
            if self.ws_client.isRunning():
                self.ws_client.stop()
                self.ws_client.quit()
                self.ws_client.wait()
            self.ws_client = None

    def _on_joined_room(self, sid: str):
        self._add_debug_message(f"成功加入房间！(SID: {sid})")
        if not self.my_name:
            self.my_name = sid

    def _on_user_joined(self, user_sid: str, display_name: str):
        self.other_pls[user_sid] = display_name or user_sid

        time_str = get_current_datetime(show_time=True, show_seconds=True)
        join_text = f'<span style="color: #008000">[{time_str}] - {display_name} 加入了房间</span>'
        self._add_dice_result(join_text)

        TFApplication.instance().show_message(f"{display_name} 加入了房间！", 3000, 'green')

    def _on_user_left(self, user_sid: str, display_name: str):
        name_to_show = display_name or self.other_pls.get(user_sid, user_sid)

        if user_sid in self.other_pls:
            del self.other_pls[user_sid]

        time_str = get_current_datetime(show_time=True, show_seconds=True)
        leave_text = f'<span style="color: #FFA500">[{time_str}] - {name_to_show} 离开了房间</span>'
        self._add_dice_result(leave_text)

        TFApplication.instance().show_message(f"{name_to_show} 离开了房间", 3000, 'yellow')

    def _on_admin_closed(self):
        TFApplication.instance().show_message("KP离开了房间，链接断开", 5000, 'yellow')

    def _on_disconnected(self):
        self._add_debug_message("与服务器断开连接", 'warning')
        TFApplication.instance().show_message("与服务器断开连接", 3000, 'yellow')

        self._enable_input_fields()

        self.ws_client = None
        self.my_name = ""

    def _add_debug_message(self, message: str, level='info'):
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if level == 'error':
            color = '#FF0000'
        elif level == 'warning':
            color = '#FFA500'
        else:
            color = '#000000'
            
        message = f'<div style="color: {color}">[{timestamp}] {message}</div>'
        
        old_text = self.dice_result_text_edit.toHtml()
        new_text = message + (old_text if old_text else "")
        self.dice_result_text_edit.setHtml(new_text)

    def _enable_input_fields(self):
        self.enter_room_entry.button.setEnabled(True)
        self.enter_room_entry.entry_field.setEnabled(True)
        self.player_name_entry.entry_field.setEnabled(True)
        self.player_name_entry.button.setEnabled(True)

    def handle_name_update_confirm(self, old_name: str, new_name: str):
        time_str = get_current_datetime(show_time=True, show_seconds=True)
        update_text = f'<span style="color: #008000">[{time_str}] - 你的PL名称已更新：{old_name} → {new_name}</span>'
        self._add_dice_result(update_text)

    def _add_dice_result(self, text: str):
        current_text = self.dice_result_text_edit.toHtml()
        new_text = text + "<br><br>" + (current_text if current_text else "")
        self.dice_result_text_edit.setHtml(new_text)

    def closeEvent(self, event):
        try:
            if self.ws_client and self.ws_client.isRunning():
                self.ws_client.send_message({"type": "leave"})
                self.ws_client.wait(100)
                self.ws_client.stop()
                self.ws_client.quit()
                self.ws_client.wait()
        except:
            pass
        event.accept()
