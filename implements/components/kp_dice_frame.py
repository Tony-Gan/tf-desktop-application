from typing import Dict
from PyQt6.QtWidgets import QHBoxLayout, QScrollArea, QFrame
from PyQt6.QtCore import Qt

from ui.components.tf_base_frame import TFBaseFrame



class KPFrame(TFBaseFrame):
    def __init__(self, parent=None):
        self.p_data: Dict[str, Dict] = {}
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
        super().__init__(level=0, radius=5, parent=parent)

    def _setup_content(self):
        self.setFixedHeight(200)

        self.room_number_entry = self.create_button_entry(
            name="room_number",
            label_text="当前房间号:",
            label_size=80,
            button_text="复制",
            button_size=50,
            button_callback=self._copy_room_number,
            entry_size=80,
            height=24,
            show_tooltip=True,
            tooltip_text="当前房间号，在PL模式下可输入此房间号进入当前房间"
        )

        self.number_of_pl = self.create_value_entry(
            name='number_of_pl',
            label_text='当前PL',
            label_size=80,
            height=24,
            enable=False,
            value_size=20
        )

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.pl_frame = TFBaseFrame(level=1, parent=scroll)
        self.pl_frame.main_layout.setSpacing(3)
        self.pl_frame.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.pl_frame.main_layout.setContentsMargins(2, 2, 2, 2)
        scroll.setWidget(self.pl_frame)

        self.main_layout.addWidget(self.room_number_entry)
        self.main_layout.addWidget(self.number_of_pl)
        self.main_layout.addWidget(scroll)

    def _copy_room_number(self):
        print('Yo!')

    def _on_add_pl(self, name, sid):
        label = self.create_label(
            text=f'{name} - {sid}',
            fixed_width=150,
            height=24,
            serif=True
        )
        self.pl_frame.main_layout.addWidget(label)


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
