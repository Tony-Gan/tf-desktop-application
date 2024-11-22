from typing import Dict

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QStackedWidget

from ui.components.tf_base_button import TFPreviousButton, TFResetButton, TFNextButton
from ui.components.tf_base_frame import TFBaseFrame


class BasePhase(TFBaseFrame):

    navigate = pyqtSignal(int)

    def __init__(self, p_data: Dict, parent: QStackedWidget):
        super().__init__(QVBoxLayout, parent)
        self.parent = parent
        self.p_data = p_data
        self.initialized = False
        self.dependencies = []
        self.saved_state = {}

    def _setup_content(self) -> None:
        self.prev_button = TFPreviousButton(self, on_clicked=self.go_previous)
        self.reset_button = TFResetButton(self, on_clicked=self.reset_contents)
        self.next_button = TFNextButton(self, on_clicked=self.go_next)

    def on_enter(self):
        if not self.initialized:
            self.initialize()
            self.initialized = True
        else:
            self.restore_state()
            self.check_dependencies()

    def on_exit(self):
        self.save_state()

    def initialize(self):
        pass

    def save_state(self):
        pass

    def restore_state(self):
        pass

    def check_dependencies(self):
        pass

    def go_next(self):
        current_index = self.parent.currentIndex()
        if current_index < self.parent.count() - 1:
            self.navigate.emit(current_index + 1)

    def go_previous(self):
        current_index = self.parent.currentIndex()
        if current_index > 0:
            self.navigate.emit(current_index - 1)
