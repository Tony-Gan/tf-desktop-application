from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout

from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication
from implements.components.websocket_client import WebSocketClient


class KPFrame(TFBaseFrame):
    """
    KP Mode Frame
    Two columns (horizontal):
      Left panel (vertical):
        - A button entry showing the current room id with a button 'copy'
        - A value entry labeled 'current pl', initially empty
        - An empty text field for displaying all players in the room with their IDs
      Right panel (vertical):
        - A function area with many buttons, for now only a placeholder
        - A large text field to display dice rolls or messages
    """

    def __init__(self, parent=None):
        # 1) Generate a new room_id for this session
        self.room_id = WebSocketClient.generate_room_id().upper()
        self.current_pl_count = 0
        self.player_list = []  # store sids or names

        super().__init__(layout_type=QHBoxLayout, parent=parent)

        # 2) Start the WebSocket client with role=admin
        self.ws_client = WebSocketClient(room_id=self.room_id, role="admin", parent=self)
        self.ws_client.connection_error.connect(self._on_connection_error)
        self.ws_client.joined_room.connect(self._on_joined_room)
        self.ws_client.user_joined.connect(self._on_user_joined)
        self.ws_client.user_left.connect(self._on_user_left)
        self.ws_client.admin_closed.connect(self._on_admin_closed)   # not typically triggered on admin side
        self.ws_client.disconnected.connect(self._on_disconnected)
        self.ws_client.start()

        self._setup_content()

    def _setup_content(self):
        """
        Construct left and right panels.
        """
        # Left panel
        self.left_panel = TFBaseFrame(layout_type=QVBoxLayout, parent=self)
        self.add_child("left_panel", self.left_panel)

        # 1) current room id with copy button
        #    Put the newly generated self.room_id in the entry_text
        self.room_id_entry = self.create_button_entry(
            name="room_id_entry",
            label_text="Room ID",
            button_text="Copy",
            entry_text=self.room_id,
            button_callback=self._on_copy_room_id,
            button_tooltip="Copy the current room ID to clipboard",
            height=30,
        )
        self.left_panel.layout().addWidget(self.room_id_entry)

        # 2) current pl
        self.current_pl_entry = self.create_value_entry(
            name="current_pl",
            label_text="Current PL",
            value_text="0",
            height=30,
            label_size=80,
            value_size=150,
        )
        self.left_panel.layout().addWidget(self.current_pl_entry)

        # 3) text field to display players
        self.players_text_edit = self.create_text_edit(
            name="players_text_edit",
            text="",
            width=300,
            height=150,
            placeholder_text="No players yet",
            read_only=True
        )
        self.left_panel.layout().addWidget(self.players_text_edit)

        # Right panel
        self.right_panel = TFBaseFrame(layout_type=QVBoxLayout, parent=self)
        self.add_child("right_panel", self.right_panel)

        # Placeholder for future function area
        self.placeholder_button = self.create_button(
            name="placeholder_button",
            text="Placeholder",
            tooltip="This is just a placeholder button",
            width=150,
            on_clicked=self._on_placeholder_clicked
        )
        self.right_panel.layout().addWidget(self.placeholder_button)

        # Big text field for dice result or message
        self.dice_result_text_edit = self.create_text_edit(
            name="dice_result_text_edit",
            text="",
            width=400,
            height=250,
            placeholder_text="Dice results or messages will appear here.",
            read_only=True
        )
        self.right_panel.layout().addWidget(self.dice_result_text_edit)

    def _on_copy_room_id(self):
        """
        Copy the current room ID to clipboard.
        """
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        room_id = self.get_component_value("room_id_entry")
        if room_id:
            clipboard.setText(room_id)
            TFApplication.instance().show_message(
                f"Room ID '{room_id}' copied!", 3000, 'green'
            )

    def _on_placeholder_clicked(self):
        """
        Placeholder for future functionality, e.g., sending a dice roll.
        """
        old_text = self.get_component_value("dice_result_text_edit") or ""
        new_text = old_text + "\n[Placeholder Button] Action triggered!"
        self.update_component_value("dice_result_text_edit", new_text)

    # ------------------------------------------------------------------------------------
    # -------------------------- WebSocket Events & Handlers -----------------------------
    # ------------------------------------------------------------------------------------
    def _on_connection_error(self, err_msg: str):
        """
        Called when we fail to connect or get an error from the server.
        e.g., if server is not running or an 'error' message arrived.
        """
        TFApplication.instance().show_message(f"KP Error: {err_msg}", 5000, 'red')

    def _on_joined_room(self, sid: str):
        """
        The server assigned us an admin sid. We don't do much with it, but store it if needed.
        """
        # Not strictly needed, but you can store it
        # or show a message that the KP is in the room.
        pass

    def _on_user_joined(self, user_sid: str):
        """
        A new PL joined the room. Increase count, add to text field, etc.
        """
        self.current_pl_count += 1
        self.update_component_value("current_pl", str(self.current_pl_count))

        # Add to players list
        self.player_list.append(user_sid)
        self._refresh_player_list_display()

        # Optionally show a message
        TFApplication.instance().show_message(
            f"Player {user_sid} joined!", 3000, 'green'
        )

    def _on_user_left(self, user_sid: str):
        """
        A PL left the room. Decrease count, remove from text field, etc.
        """
        if user_sid in self.player_list:
            self.player_list.remove(user_sid)
            self.current_pl_count -= 1
            self.update_component_value("current_pl", str(self.current_pl_count))
            self._refresh_player_list_display()

            TFApplication.instance().show_message(
                f"Player {user_sid} left the room!", 3000, 'yellow'
            )

    def _on_admin_closed(self):
        """
        If we somehow get a 'disconnect' reason=admin closed on admin side.
        Usually won't happen, but just in case.
        """
        TFApplication.instance().show_message("Admin closed the room", 3000, 'yellow')

    def _on_disconnected(self):
        """
        The server or connection has closed. Possibly on window close or server gone.
        """
        # You can show a message or just do nothing
        pass

    def _refresh_player_list_display(self):
        """
        Refresh the multiline text with each player SID on a new line.
        """
        text = "\n".join(self.player_list)
        self.update_component_value("players_text_edit", text)
