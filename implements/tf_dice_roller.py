import socketio

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt

from core.windows.tf_draggable_window import TFDraggableWindow
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication
from utils.registry.tf_tool_matadata import TFToolMetadata


class TFDiceRoller(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="骰子",
        window_title="骰子",
        window_size=(500, 400),
        description="Dice Roller",
        max_instances=1
    )

    def __init__(self, parent=None):
        super().__init__(parent)

    def initialize_window(self):
        main_layout = QVBoxLayout(self.content_container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(40)

        self.kp_button = TFBaseButton(
            text="KP模式",
            parent=self,
            width=200,
            height=40,
            font_size=14,
            enabled=True,
            border_radius=5,
            tooltip="进入KP模式"
        )
        self.kp_button.clicked.connect(self._on_kp_mode_clicked)

        self.pl_button = TFBaseButton(
            text="PL模式",
            parent=self,
            width=200,
            height=40,
            font_size=14,
            enabled=True,
            border_radius=5,
            tooltip="进入PL模式"
        )
        self.pl_button.clicked.connect(self._on_pl_mode_clicked)

        self.stacked_widget = QStackedWidget()
        self.keeper_frame = TFKeeperFrame(self)
        self.player_frame = TFPlayerFrame(self)

        self.stacked_widget.addWidget(self.keeper_frame)
        self.stacked_widget.addWidget(self.player_frame)
        self.stacked_widget.hide()

        main_layout.addStretch()
        main_layout.addWidget(self.kp_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(self.pl_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(self.stacked_widget)
        main_layout.addStretch()

    def _on_kp_mode_clicked(self):
        self.kp_button.hide()
        self.pl_button.hide()
        self.stacked_widget.setCurrentWidget(self.keeper_frame)
        self.stacked_widget.show()

    def _on_pl_mode_clicked(self):
        self.kp_button.hide()
        self.pl_button.hide()
        self.stacked_widget.setCurrentWidget(self.player_frame)
        self.stacked_widget.show()

    def closeEvent(self, event):
        self.keeper_frame.cleanup()
        self.player_frame.cleanup()
        super().closeEvent(event)


class TFKeeperFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(layout_type=QHBoxLayout, parent=parent)
        self.sio = socketio.Client()
        self._setup_socket()
        try:
            self.sio.connect('http://localhost:5000')
        except Exception as e:
            TFApplication.instance().show_message(f"连接错误: {str(e)}", 3000, "red")

    def _setup_socket(self):
        if self.sio is None:
            self.sio = socketio.Client()
            @self.sio.on('connect')
            def on_connect():
                self.sio.emit('register_admin', {}, callback=self._on_admin_registered)

            @self.sio.on('user_joined')
            def on_user_joined(data):
                current_text = self.connected_users.toPlainText()
                self.connected_users.setText(f"{current_text}User {data['sid']} joined\n")

            @self.sio.on('user_disconnected')
            def on_user_disconnected(data):
                current_text = self.connected_users.toPlainText()
                self.connected_users.setText(f"{current_text}User {data['sid']} disconnected\n")

            try:
                self.sio.connect('http://localhost:5000')
            except Exception as e:
                TFApplication.instance().show_message(f"连接错误: {str(e)}", 3000, "red")

    def _setup_content(self):
        left_frame = TFBaseFrame(parent=self)
        left_frame.main_layout.setContentsMargins(10, 10, 10, 10)
        left_frame.main_layout.setSpacing(10)

        self.token_button = self.create_button(
            name="token_button",
            text="生成Token",
            width=150,
            height=24,
            border_radius=5,
            tooltip="生成并复制Token到剪贴板"
        )
        self.token_button.clicked.connect(self._copy_token)

        self.connected_users = self.create_text_edit(
            name="connected_users",
            text="Connected Users:\n",
            width=150,
            height=200,
            read_only=True
        )

        left_frame.main_layout.addWidget(self.token_button)
        left_frame.main_layout.addWidget(self.connected_users)
        left_frame.main_layout.addStretch()

        self.message_edit = self.create_text_edit(
            name="message_edit",
            width=280,
            height=350,
            placeholder_text="在此输入消息..."
        )
        self.message_edit.textChanged.connect(self._on_message_changed)

        self.main_layout.addWidget(left_frame)
        self.main_layout.addWidget(self.message_edit)

    def _on_admin_registered(self, data):
        if 'token' in data:
            TFApplication.instance().clipboard().setText(data['token'])
            TFApplication.instance().show_message("Token已复制到剪贴板", 3000)

    def _copy_token(self):
        self._setup_socket()
        if self.sio and self.sio.connected:
            self.sio.emit('register_admin', {}, callback=self._on_admin_registered)

    def _on_message_changed(self):
        if self.sio and self.sio.connected:
            message = self.message_edit.toPlainText()
            self.sio.emit('admin_message', {'message': message})

    def cleanup(self):
        if self.sio:
            self.sio.disconnect()
            self.sio = None


class TFPlayerFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(layout_type=QHBoxLayout, parent=parent)
        self.sio = socketio.Client()
        self._setup_socket()
        try:
            self.sio.connect('http://localhost:5000')
        except Exception as e:
            TFApplication.instance().show_message(f"连接错误: {str(e)}", 3000, "red")

    def _setup_socket(self):
        if self.sio is None:
            self.sio = socketio.Client()
            @self.sio.on('message')
            def on_message(data):
                self.message_display.setText(data['message'])

            @self.sio.on('admin_disconnected')
            def on_admin_disconnected():
                TFApplication.instance().show_message("管理员已断开连接", 3000, "yellow")
                self.message_display.clear()

            try:
                self.sio.connect('http://localhost:5000')
            except Exception as e:
                TFApplication.instance().show_message(f"连接错误: {str(e)}", 3000, "red")

    def _setup_content(self):
        left_frame = TFBaseFrame(parent=self)

        self.token_entry = self.create_button_entry(
            name="token_entry",
            label_text="Token:",
            entry_size=80,
            button_text="确认",
            button_size=80,
            tooltip_text="输入Token并确认",
            button_callback=self._on_token_confirm
        )

        left_frame.main_layout.setContentsMargins(10, 10, 10, 10)
        left_frame.main_layout.addWidget(self.token_entry)
        left_frame.main_layout.addStretch()

        self.message_display = self.create_text_edit(
            name="message_display",
            width=280,
            height=350,
            read_only=True,
            placeholder_text="等待消息..."
        )

        self.main_layout.addWidget(left_frame)
        self.main_layout.addWidget(self.message_display)

    def _on_token_confirm(self):
        self._setup_socket()
        if self.sio and self.sio.connected:
            token = self.token_entry.get_value()
            self.sio.emit('join_room', {'token': token}, callback=self._on_join_response)

    def _on_join_response(self, response):
        if response.get('status') == 'success':
            TFApplication.instance().show_message("成功连接到房间", 3000, "green")
        else:
            TFApplication.instance().show_message(
                response.get('message', "连接失败"),
                3000,
                "red"
            )

    def cleanup(self):
        if self.sio:
            self.sio.disconnect()
            self.sio = None

