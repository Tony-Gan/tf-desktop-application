from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout
from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication
from implements.components.websocket_client import WebSocketClient


class PLFrame(TFBaseFrame):
    """
    PL Mode Frame
    Two columns (horizontal):
      Left panel (vertical):
        - A value entry for player's name
        - A button entry to enter a room
      Right panel (vertical):
        - (Same as KP) A function area with placeholders
        - A large text field for dice rolls or messages
    """

    def __init__(self, parent=None):
        self.ws_client = None
        self.my_name = ""  # if user doesn't provide a name, we use sid
        super().__init__(layout_type=QHBoxLayout, parent=parent)
        self._setup_content()

    def _setup_content(self):
        """
        Construct left and right panels.
        """
        # Left panel
        self.left_panel = TFBaseFrame(layout_type=QVBoxLayout, parent=self)
        self.add_child("left_panel", self.left_panel)

        # 1) Player Name
        self.player_name_entry = self.create_value_entry(
            name="player_name_entry",
            label_text="Player Name",
            value_text="",
            height=30,
            label_size=100,
            value_size=150,
        )
        self.left_panel.layout().addWidget(self.player_name_entry)

        # 2) Enter Room
        self.enter_room_entry = self.create_button_entry(
            name="enter_room_entry",
            label_text="Room ID",
            button_text="Enter",
            entry_text="",
            button_callback=self._on_enter_room,
            button_tooltip="Enter the specified room",
            height=30,
        )
        self.left_panel.layout().addWidget(self.enter_room_entry)

        # Right panel
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
            placeholder_text="Dice results or messages will appear here.",
            read_only=True
        )
        self.right_panel.layout().addWidget(self.dice_result_text_edit)

    def _on_enter_room(self):
        """
        Connect to the room specified in the enter_room_entry.
        """
        room_id = self.enter_room_entry.entry_field.text().strip().upper()
        name = self.player_name_entry.value_field.text().strip()

        if not room_id:
            TFApplication.instance().show_message("Room ID is empty!", 5000, 'yellow')
            return

        # 1) Create a WebSocketClient if not already
        if self.ws_client:
            # Already connected once? Possibly close or do nothing
            self.ws_client.close()
            self.ws_client = None

        self.ws_client = WebSocketClient(room_id=room_id, role="player", parent=self)
        self.ws_client.connection_error.connect(self._on_connection_error)
        self.ws_client.joined_room.connect(self._on_joined_room)
        self.ws_client.user_joined.connect(self._on_user_joined)       # Probably not needed for PL
        self.ws_client.user_left.connect(self._on_user_left)           # Might not matter for PL
        self.ws_client.admin_closed.connect(self._on_admin_closed)
        self.ws_client.disconnected.connect(self._on_disconnected)
        self.ws_client.start()

        # 2) If user didn't enter a name, we fill it later in _on_joined_room using sid
        self.my_name = name if name else ""  

    def _on_placeholder_clicked(self):
        """
        Placeholder for future functionality, e.g. sending a dice roll.
        """
        old_text = self.get_component_value("dice_result_text_edit") or ""
        new_text = old_text + "\n[Placeholder Button] Action triggered!"
        self.update_component_value("dice_result_text_edit", new_text)

    # ------------------------------------------------------------------------------------
    # -------------------------- WebSocket Events & Handlers -----------------------------
    # ------------------------------------------------------------------------------------
    def _on_connection_error(self, err_msg: str):
        """
        Possibly "Room not exists" or something else. Show message in yellow
        and do not proceed with the connection.
        """
        TFApplication.instance().show_message(err_msg, 5000, 'yellow')

    def _on_joined_room(self, sid: str):
        """
        The server assigned us a sid. If we had no name, we use sid as default name.
        """
        if not self.my_name:
            self.my_name = sid
        # Optionally, you can send a "typing" or "set_name" event so that KP knows your name.

        old_text = self.get_component_value("dice_result_text_edit") or ""
        new_text = old_text + f"\nYou joined room as '{self.my_name}' (sid: {sid})."
        self.update_component_value("dice_result_text_edit", new_text)

    def _on_user_joined(self, user_sid: str):
        """
        Not as relevant for a single PL, but you could show e.g., "Another player joined".
        """
        pass

    def _on_user_left(self, user_sid: str):
        """
        Another user left the room. Possibly not relevant for a single PL
        unless you want to show a message.
        """
        pass

    def _on_admin_closed(self):
        """
        The KP closed the room. We are forcibly disconnected. Show a message to PL.
        """
        TFApplication.instance().show_message("KP closed the room; you are disconnected.", 5000, 'yellow')

    def _on_disconnected(self):
        """
        Our connection was closed. Possibly admin closed or we left.
        Show a message or do nothing.
        """
        old_text = self.get_component_value("dice_result_text_edit") or ""
        new_text = old_text + "\nDisconnected from the server."
        self.update_component_value("dice_result_text_edit", new_text)
