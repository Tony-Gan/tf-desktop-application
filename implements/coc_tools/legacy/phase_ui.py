from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget

from ui.components.tf_base_button import TFNextButton, TFResetButton
from implements.coc_tools.coc_data.data_reader import load_occupations_from_json
from implements.coc_tools.pc_builder_elements.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_elements.phase_status import PhaseStatus
from utils.helper import resource_path


class BasePhaseUI(QWidget):
    def __init__(self, phase: PCBuilderPhase, main_window, parent=None):
        super().__init__(parent)
        self.phase = phase
        self.main_window = main_window

        self.content_area = None
        self.button_container = None
        self.reset_button = None
        self.next_button = None

        self.has_activated = False
        self.occupation_list = load_occupations_from_json(resource_path("implements/coc_tools/coc_data/occupations.json"))

        self._setup_base_ui()
        self._setup_ui()

    def on_enter(self):
        """Called when the phase becomes active"""
        if not self.has_activated:
            self.has_activated = True
            self.main_window.set_phase_status(self.phase, PhaseStatus.COMPLETING)

    def on_exit(self):
        """Called when the phase becomes inactive"""
        pass

    def _setup_base_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setObjectName("main_layout")
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        self.content_area = QFrame()
        self.content_area.setObjectName("content_area")
        main_layout.addWidget(self.content_area, 15)

        self.button_container = QFrame()
        self.button_container.setObjectName("button_container")
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 20, 0)
        button_layout.setSpacing(20)

        self.reset_button = TFResetButton(
            self,
            on_clicked=self._on_reset_clicked
        )
        self.next_button = TFNextButton(
            self,
            enabled=False,
            on_clicked=self._on_next_clicked
        )

        button_layout.addStretch(1)
        button_layout.addWidget(self.reset_button)
        self._setup_phase_buttons(button_layout)
        button_layout.addWidget(self.next_button)

        self.button_container.setLayout(button_layout)
        main_layout.addWidget(self.button_container, 1)
    
    def _setup_phase_buttons(self, button_layout: QHBoxLayout):
        pass
    
    def _setup_ui(self):
        raise NotImplementedError("Child classes must implement _setup_ui")

    def _on_reset_clicked(self):
        response = self.main_window.app.show_warning(
            "Reset Confirmation",
            f"This will reset all data in Phase {self.phase.value}. Are you sure?",
            buttons=["Yes", "No"]
        )
        if response == "Yes":
            self.main_window.set_phase_status(self.phase, PhaseStatus.NOT_START)
            self._reset_content()

    def _reset_content(self):
        self.reset_all()
    
    def reset_all(self):
        instantiated_phases = sorted(self.main_window.phase_uis.keys(), key=lambda phase: phase.value, reverse=True)

        current_phase = self.phase

        for phase in instantiated_phases:
            if phase.value > current_phase.value:
                print(f"Calling reset for {phase}")
                self.main_window.phase_uis[phase]._reset_content()
    
    def _on_next_clicked(self):
        phase_list = list(PCBuilderPhase)
        current_idx = phase_list.index(self.phase)
        if current_idx < len(phase_list) - 1:
            next_phase = phase_list[current_idx + 1]
            self.main_window._on_phase_selected(next_phase)
    
    def enable_next_button(self, enable: bool = True):
        self.next_button.setEnabled(enable)

    def get_content_layout(self) -> QVBoxLayout:
        return self.content_area.layout()
