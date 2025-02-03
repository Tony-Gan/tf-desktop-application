from core.windows.tf_draggable_window import TFDraggableWindow
from ui.components.tf_base_frame import TFBaseFrame
from utils.registry.tf_tool_matadata import TFToolMetadata


class TFDiceRoller(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="DeepSeek-R1",
        window_title="机器人儿",
        window_size=(800, 600),
        description="AI Robot",
        max_instances=1
    )

    def __init__(self, parent=None):
        super().__init__(parent)

    def initialize_window(self):
        self.chat_frame = TFChatFrame(self)
        self.button_frame = TFButtonFrame(self)


class TFChatFrame(TFBaseFrame):
    pass


class TFButtonFrame(TFBaseFrame):
    pass
