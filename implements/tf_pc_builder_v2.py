from typing import List

from PyQt6.QtWidgets import QHBoxLayout, QStackedWidget, QFrame, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPixmap

from core.windows.tf_draggable_window import TFDraggableWindow
from ui.components.tf_base_frame import TFBaseFrame
from utils.helper import resource_path
from utils.registry.tf_tool_matadata import TFToolMetadata
from implements.coc_components.base_phase import BasePhase
from implements.coc_components.phase0 import Phase0
from implements.coc_components.phase1 import Phase1
from implements.coc_components.phase2 import Phase2
from implements.coc_components.phase3 import Phase3
from implements.coc_components.phase4 import Phase4


class TFPcBuilderV2(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="CoC建卡器v2",
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

    def initialize_window(self):
        main_layout = QHBoxLayout(self.content_container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        self.progress_bar = ProgressFrame(self)

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setObjectName("section_frame")
        self.stacked_widget.setFrameShape(QFrame.Shape.NoFrame)
        
        self.create_frames()

        self.stacked_widget.setCurrentIndex(0)
        self.frames[0].on_enter()

        self.stacked_widget.setFixedWidth(940)
        self.progress_bar.setFixedWidth(125)

        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.stacked_widget)

    def create_frames(self):
        phase0 = Phase0(self.p_data, self.config, self.stacked_widget)
        phase1 = Phase1(self.p_data, self.config, self.stacked_widget)
        phase2 = Phase2(self.p_data, self.config, self.stacked_widget)
        phase3 = Phase3(self.p_data, self.config, self.stacked_widget, layout=QHBoxLayout)
        phase4 = Phase4(self.p_data, self.config, self.stacked_widget)
        self.stacked_widget.addWidget(phase0)
        self.stacked_widget.addWidget(phase1)
        self.stacked_widget.addWidget(phase2)
        self.stacked_widget.addWidget(phase3)
        self.stacked_widget.addWidget(phase4)
        self.frames = [phase0, phase1, phase2, phase3, phase4]

        for phase in self.frames:
            self.progress_bar.connect_to_phase(phase)


class ProgressFrame(TFBaseFrame):
    def __init__(self, parent=None):
        self.current_phase = 0
        self.completed_phases = set()
        super().__init__(radius=5, parent=parent)

    def _setup_content(self) -> None:
        self.setFixedWidth(130)
        self.setStyleSheet("""
            ProgressFrame {
                background-color: #1E2228;
                border-radius: 5px;
            }
        """)

        self.main_layout.setContentsMargins(0, 20, 0, 20)
        self.main_layout.setSpacing(10)
        
        phases = ["基础设定", "人物设置", "技能分配", "背景设置", "其他设置"]
        self.entries = []
        
        for i, phase_text in enumerate(phases):
            entry = ProgressEntry(i, phase_text, self)
            entry.setFixedHeight(60)
            self.entries.append(entry)
            self.add_child(f"phase_{i}", entry)
            
        self._update_states()

    def _update_states(self):
        for i, entry in enumerate(self.entries):
            entry.is_active = (i == self.current_phase)
            entry.is_completed = i in self.completed_phases
            entry.update()

    def connect_to_phase(self, phase: BasePhase):
        phase.navigate.connect(self._handle_phase_change)

    def _handle_phase_change(self, phase_index: int):
        if phase_index > self.current_phase:
            self.completed_phases.add(self.current_phase)
        self.current_phase = phase_index
        self._update_states()
    

class ProgressEntry(TFBaseFrame):
    def __init__(self, phase_index: int, text: str, parent=None):
        self.phase_index = phase_index
        self.text = text
        self.is_active = False 
        self.is_completed = False
        super().__init__(radius=0, parent=parent)

    def _setup_content(self) -> None:
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(15)
        
        self.icon = QLabel()
        self.icon.setFixedSize(24, 24)
        self._update_icon()
        
        self.label = self.create_label(
            text=self.text,
            serif=True,
            alignment=Qt.AlignmentFlag.AlignVCenter
        )
        
        layout.addWidget(self.icon)
        layout.addWidget(self.label)
        layout.addStretch()
        
        self.main_layout.addLayout(layout)
       
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.is_active:
            painter.fillRect(self.rect(), QColor(40, 44, 52))
            
        self.label.setStyleSheet(f"color: {('#FFFFFF' if self.is_active else '#9E9E9E')}")

    def update(self):
        self._update_icon()
        super().update()

    def _update_icon(self):
        icon_state = "_completed" if self.is_completed else "_ongoing" if self.is_active else ""
        icon_path = resource_path(f"resources/images/icons/phase{self.phase_index}{icon_state}.png")
        self.icon.setPixmap(QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
