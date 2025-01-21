from PyQt6.QtWidgets import QVBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt

from core.windows.tf_draggable_window import TFDraggableWindow
from implements.components.kp_dice_frame import KPFrame
from implements.components.pl_dice_frame import PLFrame
from ui.components.tf_animated_button import TFAnimatedButton
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication
from utils.registry.tf_tool_matadata import TFToolMetadata

class TFDiceRoller(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="摸鱼骰子",
        window_title="骰子",
        window_size=(800, 600),
        description="Dice Roller Tool",
        max_instances=4
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent().set_focused_window(self)
        self.current_mode = 0

    def initialize_window(self):
        self.stack = QStackedWidget(self.content_container)

        self.page0 = self._create_mode_choice_page()
        self.page1 = KPFrame()
        self.page2 = PLFrame()

        self.stack.addWidget(self.page0)
        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)

        layout = QVBoxLayout(self.content_container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.stack)

        self.stack.setCurrentIndex(0)

    def init_custom_menu_items(self, layout):
        self._switch_mode_button = TFAnimatedButton(
            icon_name="switch",
            tooltip="切换模式(Ctrl+S)",
            size=20,
            parent=self
        )
        self._switch_mode_button.clicked_signal.connect(self._switch_mode)

        self._reset_button = TFAnimatedButton(
            icon_name="reset",
            tooltip="重置页面(Ctrl+R)",
            size=20,
            parent=self
        )
        self._reset_button.clicked_signal.connect(self._reset)

        layout.addWidget(self._switch_mode_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._reset_button, alignment=Qt.AlignmentFlag.AlignVCenter)

    def _switch_mode(self):
        if self.stack.currentIndex() == 0:
            TFApplication.instance().show_message('请先选择一种模式', 5000, 'yellow')
        elif self.stack.currentIndex() == 1:
            self.stack.setCurrentIndex(2)
            self.current_mode = 2
            TFApplication.instance().show_message('切换至PL模式', 5000, 'green')
        elif self.stack.currentIndex() == 2:
            self.stack.setCurrentIndex(1)
            self.current_mode = 1
            TFApplication.instance().show_message('切换至KP模式', 5000, 'green')

    def _reset(self):
        pass

    def _create_mode_choice_page(self):
        page = TFBaseFrame(parent=self)
        page.main_layout.setContentsMargins(50, 50, 50, 50)
        page.main_layout.setSpacing(50)

        kp_button = TFBaseButton(
            text="KP模式", 
            parent=page, 
            width=200, 
            height=60, 
            font_size=12,
            on_clicked=self._enter_kp_mode
        )
        pl_button = TFBaseButton(
            text="PL模式", 
            parent=page, 
            width=200, 
            height=60, 
            font_size=12,
            on_clicked=self._enter_pl_mode
        )

        page.main_layout.addStretch()
        page.main_layout.addWidget(kp_button, alignment=Qt.AlignmentFlag.AlignCenter)
        page.main_layout.addWidget(pl_button, alignment=Qt.AlignmentFlag.AlignCenter)
        page.main_layout.addStretch()

        return page

    def _enter_kp_mode(self):
        self.current_mode = 'KP'
        self.stack.setCurrentIndex(1)
        self.current_mode = 1

    def _enter_pl_mode(self):
        self.current_mode = 'PL'
        self.stack.setCurrentIndex(2)
        self.current_mode = 2

    def closeEvent(self, event):
        if self.page1 and hasattr(self.page1, 'ws_client') and self.page1.ws_client:
            if self.page1.ws_client.isRunning():
                self.page1.ws_client.stop()
                self.page1.ws_client.quit()
                self.page1.ws_client.wait()
                self.page1.ws_client = None

        if self.page2 and hasattr(self.page2, 'ws_client') and self.page2.ws_client:
            if self.page2.ws_client.isRunning():
                self.page2.ws_client.stop()
                self.page2.ws_client.quit()
                self.page2.ws_client.wait()
                self.page2.ws_client = None

        super().closeEvent(event)
