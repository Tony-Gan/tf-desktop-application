from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout

from implements.components.base_phase import BasePhase
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_frame import TFBaseFrame


class Phase3(BasePhase):
    def _setup_content(self) -> None:
        super()._setup_content()

        self.show_weapon_type_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="武器类型列表", 
            height=35,
            width=120, 
            on_clicked=self._on_show_weapon_type_clicked
        )

        self.custom_weapon_type_button = TFBaseButton(
            parent=self.buttons_frame, 
            text="自定义武器", 
            height=35,
            width=120, 
            on_clicked=self._on_custom_weapon_type_clicked
        )

        self.buttons_frame.add_custom_button(self.show_weapon_type_button)
        self.buttons_frame.add_custom_button(self.custom_weapon_type_button)

        self.custom_weapon_type_button.hide()

        self.contents_frame.setLayout(QHBoxLayout())

        self.left_frame = LeftFrame(self)
        self.right_frame = RightFrame(self)

        self.contents_frame.add_child('left_frame', self.left_frame)
        self.contents_frame.add_child('right_frame', self.right_frame)

    def reset_contents(self):
        pass

    def initialize(self):
        self.check_dependencies()

    def save_state(self):
        pass

    def check_dependencies(self):
        self.allow_mythos = self.config['general']['allow_mythos']
        self.allow_custom_weapon_type = self.config['general']['custom_weapon_type']
        self.complete_mode = self.config['general']['conmplete_mode']

        if self.allow_custom_weapon_type:
            self.custom_weapon_type_button.show()

    def validate(self):
        pass

    def _on_show_weapon_type_clicked(self):
        pass

    def _on_custom_weapon_type_clicked(self):
        pass


class LeftFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass


class RightFrame(TFBaseFrame):
    def __init__(self,  parent=None):
        super().__init__(QVBoxLayout, level=1, radius=10, parent=parent)

    def _setup_content(self) -> None:
        pass