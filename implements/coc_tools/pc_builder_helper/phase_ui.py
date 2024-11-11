from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget

from ui.components.tf_base_button import TFNextButton, TFResetButton
from implements.coc_tools.pc_builder_helper.pc_builder_phase import PCBuilderPhase


class BasePhaseUI(QFrame):
    def __init__(self, phase: PCBuilderPhase, main_window, parent=None):
        super().__init__(parent)
        self.phase = phase
        self.main_window = main_window
        
        self.content_area = None
        self.button_container = None
        self.reset_button = None
        self.next_button = None
        
        self._setup_base_ui()
        self._setup_ui()
        
    def _setup_base_ui(self):
        """Setup the base UI structure"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Content area - without layout
        self.content_area = QFrame()
        main_layout.addWidget(self.content_area, 9)
        
        # Button container
        self.button_container = QFrame()
        button_layout = QHBoxLayout()  # Create layout first
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        self.reset_button = TFResetButton(
            self,
            on_clicked=self._on_reset_clicked
        )
        self.next_button = TFNextButton(
            self,
            enabled=False,
            on_clicked=self._on_next_clicked
        )
        
        button_layout.addWidget(self.reset_button)
        self._setup_phase_buttons(button_layout)
        button_layout.addStretch()
        button_layout.addWidget(self.next_button)
        
        self.button_container.setLayout(button_layout)  # Set layout after configuration
        main_layout.addWidget(self.button_container, 1)

    def _setup_content_area(self):
        """Setup the content area with a clean layout"""
        # Clear old layout if exists
        if self.content_area.layout():
            while self.content_area.layout().count():
                item = self.content_area.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(self.content_area.layout())
        
        # Create new layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        self.content_area.setLayout(content_layout)
        
        return content_layout  # Return layout for child classes to use
    
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
            self._perform_reset()
    
    def _perform_reset(self):
        raise NotImplementedError("Child classes must implement _perform_reset")
    
    def _on_next_clicked(self):
        if self.main_window.can_proceed_to_next_phase():
            self.main_window.proceed_to_next_phase()
    
    def enable_next_button(self, enable: bool = True):
        self.next_button.setEnabled(enable)

    def get_content_layout(self) -> QVBoxLayout:
        return self.content_area.layout()

class Phase2UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        super().__init__(PCBuilderPhase.PHASE2, main_window, parent)


class Phase3UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        super().__init__(PCBuilderPhase.PHASE3, main_window, parent)


class Phase4UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        super().__init__(PCBuilderPhase.PHASE4, main_window, parent)


class Phase5UI(BasePhaseUI):
    def __init__(self, main_window, parent=None):
        super().__init__(PCBuilderPhase.PHASE5, main_window, parent)
