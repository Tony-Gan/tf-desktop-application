from typing import List

from PyQt6.QtWidgets import QHBoxLayout, QStackedWidget, QFrame

from core.windows.tf_draggable_window import TFDraggableWindow
from implements.components.phase2 import Phase2
from ui.components.tf_base_frame import TFBaseFrame
from utils.registry.tf_tool_matadata import TFToolMetadata
from implements.components.phase0 import Phase0
from implements.components.phase1 import Phase1


class TFPcBuilderV2(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="角色构筑器v2",
        window_title="角色构筑器v2",
        window_size=(1080, 640),
        description="PC builder",
        max_instances=1
    )

    def __init__(self, parent=None):
        self.p_data = {}
        self.config = {}
        self.frames: List[TFBaseFrame] = []
        self.stacked_widget = None

        super().__init__(parent)

        self._setup_menu()
        self._setup_shortcut()

    def initialize_window(self):
        main_layout = QHBoxLayout(self.content_container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setObjectName("section_frame")
        self.stacked_widget.setFrameShape(QFrame.Shape.NoFrame)
        
        self.create_frames()

        self.stacked_widget.setCurrentIndex(0)
        self.frames[0].on_enter()

        self.progress_bar = ProgressFrame()

        self.stacked_widget.setFixedWidth(900)
        self.progress_bar.setFixedWidth(165)

        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.stacked_widget)

    def _setup_menu(self):
        pass

    def _setup_shortcut(self):
        pass

    def create_frames(self):
        phase0 = Phase0(self.p_data, self.config, self.stacked_widget)
        phase1 = Phase1(self.p_data, self.config, self.stacked_widget)
        phase2 = Phase2(self.p_data, self.config, self.stacked_widget)
        self.stacked_widget.addWidget(phase0)
        self.stacked_widget.addWidget(phase1)
        self.stacked_widget.addWidget(phase2)
        self.frames = [phase0, phase1, phase2]


class ProgressFrame(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(radius=5, parent=parent)

    def _setup_content(self) -> None:
        self.phase1 = ProgressEntry("Basic", self)
        self.phase2 = ProgressEntry("Skills", self)
        self.phase3 = ProgressEntry("Loadout", self)
        self.phase4 = ProgressEntry("Background", self)

        self.add_child("phase1", self.phase1)
        self.add_child("phase2", self.phase2)
        self.add_child("phase3", self.phase3)
        self.add_child("phase4", self.phase4)
    

class ProgressEntry(TFBaseFrame):

    def __init__(self, text: str, parent=None):
        self.text = text
        super().__init__(radius=5, parent=parent)

    def _setup_content(self) -> None:
        self.label = self.create_label(
            text=self.text,
            fixed_width=150,
            serif=True
        )

        self.status = self.create_label(
            text="Not Start",
            fixed_width=150,
        )

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.status)
        self.main_layout.addStretch()
