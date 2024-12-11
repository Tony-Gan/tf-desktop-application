from ui.components.tf_base_frame import TFBaseFrame

from PyQt6.QtWidgets import QHBoxLayout


class PLFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(layout_type=QHBoxLayout, level=0, radius=5, parent=parent)

    def _setup_content(self):
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(10)

        self.information_frame = InformationFrame(self)
        self.right_frame = RightFrame(self)

        self.add_child('information_frame', self.information_frame)
        self.add_child('right_frame', self.right_frame)


class InformationFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(layout_type=QHBoxLayout, level=0, radius=5, parent=parent)

    def _setup_content(self):
        pass


class RightFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        self.roll_frame = RollFrame(self)
        self.message_frame = MessageFrame(self)
        
        self.add_child('roll_frame', self.roll_frame)
        self.add_child('message_frame', self.message_frame)


class RollFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        pass


class MessageFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        pass
