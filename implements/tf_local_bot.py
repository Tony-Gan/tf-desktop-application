from core.windows.tf_draggable_window import TFDraggableWindow
from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication
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
        self.chat_frame = ChatFrame(self)
        self.button_frame = ButtonFrame(self)
        TFApplication.instance().show_message("还没做完呢，别测这个了", 5000, "green")


class ChatFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        self.dice_result_frame = None
        self.selected_stats_index = -1
        super().__init__(radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass


class ButtonFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        self.dice_result_frame = None
        self.selected_stats_index = -1
        super().__init__(radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass
