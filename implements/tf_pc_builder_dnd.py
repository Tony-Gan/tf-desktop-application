from typing import List

from PyQt6.QtWidgets import QHBoxLayout

from core.windows.tf_draggable_window import TFDraggableWindow
from ui.components.tf_base_frame import TFBaseFrame
from utils.registry.tf_tool_matadata import TFToolMetadata


class TFDnDPcBuilder(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="DnD建卡器v1",
        window_title="DnD5E 角色构筑器",
        window_size=(960, 800),
        description="DnD5E PC builder",
        max_instances=1
    )

    def __init__(self, parent=None):
        self.p_data = {}
        self.config = {}
        self.frames: List[TFBaseFrame] = []
        self.stacked_widget = None

        super().__init__(parent)

    def initialize_window(self):
        main_layout = QHBoxLayout(self.content_container)