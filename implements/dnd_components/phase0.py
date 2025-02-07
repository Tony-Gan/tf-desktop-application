from PyQt6.QtGui import QFont

from implements.coc_components.base_phase import BasePhase
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_frame import TFBaseFrame


class Phase0(BasePhase):
    def _setup_content(self) -> None:
        super()._setup_content()

        self.buttons_frame.prev_button.hide()
        self.buttons_frame.complete_button.hide()

        self.contents_frame.main_layout.setContentsMargins(10, 10, 10, 10)
        self.contents_frame.main_layout.setSpacing(40)

        self.race_intro_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="种族介绍", 
            height=35,
            width=120,
            font_family=QFont("Noto Serif SC"),
            on_clicked=self._on_race_intro_button_clicked
        )
        self.buttons_frame.add_custom_button(self.race_intro_button)

        self.race_frame = RaceFrame(self)
        self.detail_frame = DetailFrame(self)

        self.contents_frame.add_child("race_frame", self.race_frame)
        self.contents_frame.add_child("detail_frame", self.detail_frame)

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

    def validate(self):
        pass

    def _on_race_intro_button_clicked(self):
        pass


class RaceFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass


class DetailFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass
