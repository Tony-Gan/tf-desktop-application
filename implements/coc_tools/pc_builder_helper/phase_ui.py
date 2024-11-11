from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout

from ui.components.tf_base_button import TFBaseButton
from implements.coc_tools.pc_builder_helper.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_helper.phase_status import PhaseStatus


class BasePhaseUI(QFrame):
    def __init__(self, phase: PCBuilderPhase, main_window: 'TFPcBuilder', parent=None):
        super().__init__(parent)
        self.phase = phase
        self.main_window = main_window
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        content_area = QFrame(self)
        content_layout = QVBoxLayout(content_area)
        content_layout.addWidget(QLabel(f"Phase {self.phase.value}"))
        layout.addWidget(content_area, 9)

        button_container = QFrame(self)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        for _ in range(5):
            button = TFBaseButton(
                "PlaceHolder",
                parent=self
            )
            button_layout.addWidget(button)

        layout.addWidget(button_container, 1)

    def mousePressEvent(self, event):
        if self.main_window:
            self.main_window.set_phase_status(self.phase, PhaseStatus.COMPLETED)


class Phase1UI(BasePhaseUI):
    def __init__(self, main_window: 'TFPcBuilder', parent=None):
        super().__init__(PCBuilderPhase.PHASE1, main_window, parent)


class Phase2UI(BasePhaseUI):
    def __init__(self, main_window: 'TFPcBuilder', parent=None):
        super().__init__(PCBuilderPhase.PHASE2, main_window, parent)


class Phase3UI(BasePhaseUI):
    def __init__(self, main_window: 'TFPcBuilder', parent=None):
        super().__init__(PCBuilderPhase.PHASE3, main_window, parent)


class Phase4UI(BasePhaseUI):
    def __init__(self, main_window: 'TFPcBuilder', parent=None):
        super().__init__(PCBuilderPhase.PHASE4, main_window, parent)


class Phase5UI(BasePhaseUI):
    def __init__(self, main_window: 'TFPcBuilder', parent=None):
        super().__init__(PCBuilderPhase.PHASE5, main_window, parent)
