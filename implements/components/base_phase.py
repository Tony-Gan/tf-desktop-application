from typing import Dict, List, Tuple

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QStackedWidget, QHBoxLayout, QFrame

from ui.components.if_state_controll import IStateController
from ui.components.tf_base_button import TFPreviousButton, TFResetButton, TFNextButton
from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication


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
        self.buttons_frame.setFixedHeight(50)

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
        print(self.p_data)

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

    def validate(self) -> List[Tuple[IStateController, str]]:
        return []
        
    def reset_validation_state(self) -> None:
        def reset_state(widget):
            for child in widget.findChildren(QFrame):
                reset_state(child)
                
        reset_state(self.contents_frame)


    def try_go_next(self):
        self.reset_validation_state()
        
        invalid_items = self.validate()
        if not invalid_items:
            self.go_next()
        else:
            message = []
            for _, error_msg in invalid_items:
                message.append(error_msg)
            TFApplication.instance().show_message("\n".join(message), 5000, "yellow")

    def go_next(self):
        current_index = self.parent.currentIndex()
        if current_index < self.parent.count() - 1:
            self.on_exit()
            self.parent.setCurrentIndex(current_index + 1)
            next_phase = self.parent.widget(current_index + 1)
            next_phase.on_enter()
            self.navigate.emit(current_index + 1)

    def go_previous(self):
        current_index = self.parent.currentIndex()
        if current_index > 0:
            self.on_exit()
            self.parent.setCurrentIndex(current_index - 1)
            prev_phase = self.parent.widget(current_index - 1)
            prev_phase.on_enter()
            self.navigate.emit(current_index - 1)

    def on_reset(self):
        self.reset_contents()


class ContentsFrame(TFBaseFrame):

    def __init__(self, p_data: Dict, config: Dict, parent=None):
        self.p_data = p_data
        self.config = config
        super().__init__(level=0, radius=0, parent=parent)

    def _setup_content(self) -> None:
        pass


class ButtonsFrame(TFBaseFrame):

    def __init__(self, parent=None):
        self.left_layout = QHBoxLayout()
        self.right_layout = QHBoxLayout()
        self.left_layout.setSpacing(40)
        self.right_layout.setSpacing(40)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        super().__init__(layout_type=QHBoxLayout, level=0, radius=0, parent=parent)

    def _setup_content(self) -> None:
        left_widget = QFrame()
        left_widget.setLayout(self.left_layout)
        self.main_layout.addWidget(left_widget)

        self.main_layout.addStretch()

        right_widget = QFrame()
        right_widget.setLayout(self.right_layout)
        self.main_layout.addWidget(right_widget)

        self.prev_button = TFPreviousButton(self, font_family=QFont("Noto Serif SC"), height=35, on_clicked=self.parent.go_previous)
        self.reset_button = TFResetButton(self, font_family=QFont("Noto Serif SC"), height=35, on_clicked=self.parent.on_reset)
        self.next_button = TFNextButton(self, font_family=QFont("Noto Serif SC"), height=35, on_clicked=self.parent.try_go_next, enabled=True)

        self.right_layout.addStretch()
        self.right_layout.addWidget(self.prev_button)
        self.right_layout.addWidget(self.reset_button)
        self.right_layout.addWidget(self.next_button)

    def add_custom_button(self, button):
        self.left_layout.addWidget(button)
