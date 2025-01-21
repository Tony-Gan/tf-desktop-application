from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt

from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication
from implements.components.websocket_client import WebSocketClient


class PLFrame(TFBaseFrame):
    def __init__(self, parent=None):
        self.ws_client = None
        self.my_name = ""
        super().__init__(layout_type=QHBoxLayout, parent=parent)

    def _setup_content(self):
        self.left_panel = TFBaseFrame(layout_type=QVBoxLayout, parent=self)
        self.left_panel.setFixedWidth(300)
        self.add_child("left_panel", self.left_panel)

        self.player_name_entry = self.create_value_entry(
            name="player_name_entry",
            label_text="PL",
            value_text="",
            height=24,
            label_size=75,
            value_size=150,
        )
        self.left_panel.layout().addWidget(self.player_name_entry)

        self.pc_name_entry = self.create_value_entry(
            name="pc_name_entry",
            label_text="PC",
            value_text="",
            height=24,
            label_size=75,
            value_size=150,
        )
        self.left_panel.layout().addWidget(self.pc_name_entry)

        self.enter_room_entry = self.create_button_entry(
            name="enter_room_entry",
            label_size=75,
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
            label_size=75,
            button_text="上传",
            entry_text="",
            button_callback=self._on_pc_data_upload,
            button_tooltip="上传你的PC信息卡",
            button_size=50,
            height=24,
        )
        self.left_panel.layout().addWidget(self.pc_data_entry)

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
            width=480,
            height=250,
            placeholder_text="掷骰结果和信息会出现在这里...",
            read_only=True,
            scroll_policy=(Qt.ScrollBarPolicy.ScrollBarAlwaysOff, Qt.ScrollBarPolicy.ScrollBarAlwaysOn),
            enable_rich_text=True
        )
        self.right_panel.layout().addWidget(self.dice_result_text_edit)

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
        
        self.player_name_entry.value_field.setEnabled(False)
        self.pc_name_entry.value_field.setEnabled(False)

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
            display_name=display_name,
            parent=self
        )
        self.ws_client.connection_error.connect(self._on_connection_error)
        self.ws_client.joined_room.connect(self._on_joined_room)
        self.ws_client.user_joined.connect(self._on_user_joined)
        self.ws_client.user_left.connect(self._on_user_left)
        self.ws_client.admin_closed.connect(self._on_admin_closed)
        self.ws_client.disconnected.connect(self._on_disconnected)
        self.ws_client.start()

        self.my_name = display_name
    
    def _on_pc_data_upload(self):
        pass

    def _get_display_name(self):
        pl_name = self.player_name_entry.value_field.text().strip()
        pc_name = self.pc_name_entry.value_field.text().strip()
        
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

    def _on_user_joined(self, user_sid: str):
        pass

    def _on_user_left(self, user_sid: str):
        pass

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
        self.player_name_entry.value_field.setEnabled(True)
        self.pc_name_entry.value_field.setEnabled(True)

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
