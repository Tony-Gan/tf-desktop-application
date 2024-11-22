from typing import List

from PyQt6.QtWidgets import QHBoxLayout, QStackedWidget, QFrame

from core.windows.tf_draggable_window import TFDraggableWindow
from ui.components.tf_base_frame import TFBaseFrame
from utils.registry.tf_tool_matadata import TFToolMetadata


class TFPcBuilderV2(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="pc_builder_v2",
        menu_path="Tools/COC",
        menu_title="Add PC Builder V2",
        window_title="PC Builder V2",
        window_size=(1080, 640),
        description="PC builder",
        max_instances=1
    )

    def __init__(self, parent=None):
        self.p_data = {}
        self.frames: List[TFBaseFrame] = []
        self.stacked_widget = None

        super().__init__(parent)

        self._setup_menu()
        self._setup_shortcut()

    def initialize_window(self):
        main_layout = QHBoxLayout(self.content_container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setObjectName("section_frame")
        self.stacked_widget.setFrameShape(QFrame.Shape.Box)

        self.frames = []
        self.create_frames()

        self.stacked_widget.setCurrentIndex(0)
        self.frames[0].on_enter()
        main_layout.addWidget(self.stacked_widget)

    def _setup_menu(self):
        pass

    def _setup_shortcut(self):
        pass

    def create_frames(self):
        pass
