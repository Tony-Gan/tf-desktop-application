from PyQt6.QtWidgets import QVBoxLayout

from ui.components.tf_base_frame import TFBaseFrame


class Card1(TFBaseFrame):

    def __init__(self, parent=None, layout=QVBoxLayout):
        self.parent = parent
        self.layout = layout

        super().__init__(radius=5, parent=parent)

    def _setup_content(self):
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        pass
