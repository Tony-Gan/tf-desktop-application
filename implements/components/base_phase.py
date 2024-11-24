from typing import Dict

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QStackedWidget, QHBoxLayout

from ui.components.tf_base_button import TFPreviousButton, TFResetButton, TFNextButton
from ui.components.tf_base_frame import TFBaseFrame


class BasePhase(TFBaseFrame):

    navigate = pyqtSignal(int)

    def __init__(self, p_data: Dict, config: Dict, parent: QStackedWidget):
        self.parent = parent
        self.p_data = p_data
        self.config = config

        super().__init__(radius=5, parent=parent)
        self.initialized = False
        self.dependencies = []
        self.saved_state = {}

    def _setup_content(self) -> None:
        self.contents_frame = ContentsFrame(self.p_data, self.config, self)
        self.buttons_frame = ButtonsFrame(self)
        self.buttons_frame.setFixedHeight(40)

        self.main_layout.addWidget(self.contents_frame)
        self.main_layout.addWidget(self.buttons_frame)

    def on_enter(self):
        if not self.initialized:
            self.initialize()
            self.initialized = True
        else:
            self.restore_state()
            self.check_dependencies()

    def on_exit(self):
        self.save_state()

    def reset_contents(self):
        pass

    def initialize(self):
        pass

    def save_state(self):
        pass

    def restore_state(self):
        pass

    def check_dependencies(self):
        pass


class ContentsFrame(TFBaseFrame):

    def __init__(self, p_data: Dict, config: Dict, parent=None):
        self.p_data = p_data
        self.config = config
        super().__init__(level=0, radius=0, parent=parent)

    def _setup_content(self) -> None:
        pass


class ButtonsFrame(TFBaseFrame):

    def __init__(self, parent=None):
        super().__init__(layout_type=QHBoxLayout, level=0, radius=0, parent=parent)

    def _setup_content(self) -> None:
        self.main_layout.setSpacing(40)

        self.prev_button = TFPreviousButton(self, height=35, on_clicked=self.go_previous)
        self.reset_button = TFResetButton(self, height=35, on_clicked=self.on_reset)
        self.next_button = TFNextButton(self, height=35, on_clicked=self.go_next)

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.prev_button)
        self.main_layout.addWidget(self.reset_button)
        self.main_layout.addWidget(self.next_button)

    def go_next(self):
        current_index = self.parent.parent.currentIndex()
        if current_index < self.parent.parent.count() - 1:
            self.navigate.emit(current_index + 1)

    def go_previous(self):
        current_index = self.parent.parent.currentIndex()
        if current_index > 0:
            self.navigate.emit(current_index - 1)

    def on_reset(self):
        self.parent.reset_contents()
