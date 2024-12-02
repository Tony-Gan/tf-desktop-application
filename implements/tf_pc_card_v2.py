from PyQt6.QtWidgets import QVBoxLayout, QTabWidget
from PyQt6.QtCore import Qt

from core.windows.tf_draggable_window import TFDraggableWindow
from ui.components.tf_animated_button import TFAnimatedButton
from utils.registry.tf_tool_matadata import TFToolMetadata
# from implements.components.card1 import Card1
# from implements.components.card2 import Card2
# from implements.components.card3 import Card3


class TFPcCardV2(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="调查员角色卡v2",
        window_title="调查员角色卡v2",
        window_size=(400, 640),
        description="PC card",
        max_instances=6
    )

    def __init__(self, parent=None):
        super().__init__(parent)

    def initialize_window(self):
        main_layout = QVBoxLayout(self.content_container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        navigation_bar = QTabWidget(self)
        # card1 = Card1(self)
        # card2 = Card2(self)
        # card3 = Card3(self)

        # navigation_bar.addTab(card1, 'Card1')
        # navigation_bar.addTab(card2, 'Card2')
        # navigation_bar.addTab(card3, 'Card3')

        main_layout.addWidget(navigation_bar)

    def init_custom_menu_items(self, layout):
        self._load_character_button = TFAnimatedButton(
            icon_name="load",
            tooltip="加载角色",
            size=20 ,
            parent=self
        )
        self._load_character_button.clicked_signal.connect(self._load_character)

        self._enable_edit_button = TFAnimatedButton(
            icon_name="edit",
            tooltip="加载角色",
            size=20 ,
            parent=self
        )
        self._enable_edit_button.clicked_signal.connect(self._enable_edit)

        layout.addWidget(self._load_character_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._enable_edit_button, alignment=Qt.AlignmentFlag.AlignVCenter)

    def _load_character(self):
        print(1)

    def _enable_edit(self):
        print(2)
