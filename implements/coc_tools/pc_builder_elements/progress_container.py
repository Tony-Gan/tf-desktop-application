from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel

from implements.coc_tools.pc_builder_elements.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_elements.phase_progress_item import PhaseProgressItem
from implements.coc_tools.pc_builder_elements.phase_status import PhaseStatus
from ui.components.tf_separator import TFSeparator


class ProgressContainer(QFrame):
    phase_selected = pyqtSignal(PCBuilderPhase)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("progress_container")

        self.phase_items = {}
        self._setup_ui()

    def _setup_ui(self):
        self.setFrameShape(QFrame.Shape.Box)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(20)

        title = QLabel("Progress")
        title_font = QFont("Inconsolata")
        title_font.setPointSize(14)
        title.setFont(title_font)
        title.setFixedHeight(50)
        layout.addWidget(title)

        layout.addWidget(TFSeparator("horizontal"))

        for phase in PCBuilderPhase:
            item = PhaseProgressItem(phase, self)
            item.clicked.connect(self.phase_selected.emit)
            self.phase_items[phase] = item
            layout.addWidget(item)

        layout.addStretch()

    def update_status(self, phase: PCBuilderPhase, status: PhaseStatus):
        if phase in self.phase_items:
            self.phase_items[phase].set_status(status)

    def set_active_phase(self, phase: PCBuilderPhase):
        for p, item in self.phase_items.items():
            item.set_active(p == phase)
