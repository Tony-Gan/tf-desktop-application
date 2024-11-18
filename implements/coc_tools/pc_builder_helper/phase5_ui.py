from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout

from implements.coc_tools.pc_builder_helper.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_helper.phase_ui import BasePhaseUI
from ui.components.tf_base_button import TFPreviousButton, TFBaseButton
from utils.validator.tf_validator import TFValidator


class Phase5UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        self.config = main_window.config
        self.main_window = main_window

        self.check_button = None
        self.previous_button = None

        super().__init__(PCBuilderPhase.PHASE5, main_window, parent)

        self.validator = TFValidator()
        self._setup_validation_rules()
        self.main_window.config_updated.connect(self._on_config_updated)

    def _setup_ui(self):
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

    def _setup_phase_buttons(self, button_layout):
        self.occupation_list_button = TFBaseButton(
            "Occupation List",
            self,
            height=30,
            on_clicked=self._on_occupation_list_clicked
        )
        self.check_button = TFBaseButton(
            "Check",
            self,
            height=30,
            on_clicked=self._on_check_clicked
        )
        self.previous_button = TFPreviousButton(
            self,
            height=30,
            on_clicked=self._on_previous_clicked
        )

        button_layout.addWidget(self.check_button)
        button_layout.addWidget(self.previous_button)

    def _setup_validation_rules(self):
        pass

    def _on_occupation_list_clicked(self):
        print("[Phase5UI] on_occupation_list_clicked called.")

    def _on_check_clicked(self):
        print("[Phase5UI] _on_check_clicked called.")

    def _on_previous_clicked(self):
        self.main_window.current_phase = PCBuilderPhase.PHASE4
        self.main_window.load_phase_ui()

    def _on_next_clicked(self):
        print("[Phase5UI] _on_next_clicked called.")

    def _reset_content(self):
        print("[Phase5UI] _reset_content called.")
