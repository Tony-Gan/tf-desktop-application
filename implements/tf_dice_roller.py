from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication

from core.windows.tf_draggable_window import TFDraggableWindow
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication


# 假设以下类在你的环境中已存在:
# TFDraggableWindow, TFBaseButton, TFBaseFrame, IComponentCreator
# 如有需要的类，请告知。
# 这里假定已经导入了上述类，并根据你的给定内容使用。

class TFDiceRoller(TFDraggableWindow):
    # 假设有metadata定义（与TFPcCardV2类似）
    # 你需要根据你的注册机制来定义metadata, 这里先写个示例:
    from utils.registry.tf_tool_matadata import TFToolMetadata
    metadata = TFToolMetadata(
        name="TFDiceRoller",
        window_title="投骰工具",
        window_size=(600, 400),
        description="Dice Roller Tool",
        max_instances=10
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent().set_focused_window(self)

    def initialize_window(self):
        # 使用 QStackedWidget 管理三个页面：
        # page0: 选择KP或PL模式
        # page1: KP模式UI
        # page2: PL模式UI
        self.stack = QStackedWidget(self.content_container)

        # 初始化三个页面
        self.page0 = self._create_mode_choice_page()
        self.page1 = self._create_kp_page()
        self.page2 = self._create_pl_page()

        self.stack.addWidget(self.page0)
        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)

        layout = QVBoxLayout(self.content_container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.stack)

        self.stack.setCurrentIndex(0)

    def _create_mode_choice_page(self):
        # 显示两个大按钮：KP模式 和 PL模式
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # 创建两个按钮使用TFBaseButton
        # 大按钮可以通过width, height等参数来设置比较大
        kp_button = TFBaseButton(
            text="KP模式", parent=page, width=200, height=80, font_size=16,
            on_clicked=self._enter_kp_mode
        )
        pl_button = TFBaseButton(
            text="PL模式", parent=page, width=200, height=80, font_size=16,
            on_clicked=self._enter_pl_mode
        )

        layout.addStretch()
        layout.addWidget(kp_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(pl_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        return page

    def _create_kp_page(self):
        # KP模式下的界面，左右结构
        page = QWidget(self)
        h_layout = QHBoxLayout(page)
        h_layout.setContentsMargins(5, 5, 5, 5)
        h_layout.setSpacing(10)

        # 左边是一个TFBaseFrame
        self.kp_left_frame = KPLeftFrame(self)
        # 右边是一个TFBaseFrame
        self.kp_right_frame = KPRightFrame(self)

        h_layout.addWidget(self.kp_left_frame)
        h_layout.addWidget(self.kp_right_frame, stretch=1)

        return page

    def _create_pl_page(self):
        # PL模式下的界面，左右结构
        page = QWidget(self)
        h_layout = QHBoxLayout(page)
        h_layout.setContentsMargins(5, 5, 5, 5)
        h_layout.setSpacing(10)

        self.pl_left_frame = PLLeftFrame(self)
        self.pl_right_frame = PLRightFrame(self)

        h_layout.addWidget(self.pl_left_frame)
        h_layout.addWidget(self.pl_right_frame, stretch=1)

        return page

    def _enter_kp_mode(self):
        self.stack.setCurrentIndex(1)

    def _enter_pl_mode(self):
        self.stack.setCurrentIndex(2)


class KPLeftFrame(TFBaseFrame):
    """
    KP模式左侧框架:
    上方：一个生成TOKEN的按钮(点击后复制"123456"到剪贴板)
    下方：一个label显示已连接的PL sid列表
    """

    def _setup_content(self):
        # 使用componentcreator的方法创建组件
        # create_button(name, text, ...) 来创建按钮
        self.token_button = self.create_button(
            name="generate_token_button",
            text="生成TOKEN(123456)",
            width=150,
            height=40,
            font_size=12,
            on_clicked=self._copy_token_to_clipboard
        )
        self.main_layout.addWidget(self.token_button)

        # 创建一个label显示当前连进来的PL sid
        self.connected_label = self.create_label(
            text="当前连进来的PL sid:",
            fixed_width=200,
            alignment=Qt.AlignmentFlag.AlignLeft,
            height=24,
            serif=True
        )
        self.main_layout.addWidget(self.connected_label)

        # 将来如果有需要，可以在此下方再加一个列表区或动态更新的文本框显示sid列表
        # 这里先简单提供一个label
        self.sids_display = self.create_label(
            text="无连接", fixed_width=200,
            alignment=Qt.AlignmentFlag.AlignLeft,
            height=24,
            serif=True
        )
        self.main_layout.addWidget(self.sids_display)
        self.main_layout.addStretch()

    def _copy_token_to_clipboard(self):
        TFApplication.clipboard().setText("123456")
        # 这里可弹出提示复制成功
        QMessageBox.information(self, "提示", "TOKEN已复制到剪贴板")

    def update_sids(self, sids_list):
        # 将sids_list（一个字符串列表）显示在label中
        if not sids_list:
            self.sids_display.setText("无连接")
        else:
            self.sids_display.setText(", ".join(sids_list))


class KPRightFrame(TFBaseFrame):
    """
    KP模式右侧框架:
    一个QTextEdit，用于实时输入（后面会与服务器交互）
    """

    def _setup_content(self):
        # 创建一个QTextEdit作为交互输入框
        self.interact_text = self.create_text_edit(
            name="kp_text_edit",
            width=300,
            height=300,
            placeholder_text="这里是KP的输入框内容，会通过服务器同步给PL...",
            word_wrap=True
        )
        self.main_layout.addWidget(self.interact_text)
        self.main_layout.addStretch()


class PLLeftFrame(TFBaseFrame):
    """
    PL模式左侧框架：
    一个输入token的TextEdit加一个确定按钮
    """

    def _setup_content(self):
        self.token_input = self.create_line_edit(
            name="pl_token_input",
            text="",
            width=120,
            height=24,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.main_layout.addWidget(self.token_input)

        self.confirm_button = self.create_button(
            name="pl_confirm_button",
            text="确定",
            width=60,
            height=24,
            font_size=10,
            on_clicked=self._on_confirm_token
        )
        self.main_layout.addWidget(self.confirm_button)
        self.main_layout.addStretch()

    def _on_confirm_token(self):
        # 获取输入的token并连接服务器，如果房间不存在则提示 "找不到房间"
        token = self.get_component_value("pl_token_input")
        # 这里先简单弹框演示，后续接入网络逻辑
        if token != "123456":
            QMessageBox.warning(self, "警告", "找不到房间")
        else:
            QMessageBox.information(self, "信息", "已加入房间")
            # 后续可在此初始化WebSocket连接并进入交互状态


class PLRightFrame(TFBaseFrame):
    """
    PL模式右侧框架：
    一个互动输入框（此处可以是只读的，用来显示KP输入的内容）
    """

    def _setup_content(self):
        self.interact_text = self.create_text_edit(
            name="pl_text_edit",
            width=300,
            height=300,
            placeholder_text="这里显示来自KP的消息",
            read_only=True,
            word_wrap=True
        )
        self.main_layout.addWidget(self.interact_text)
        self.main_layout.addStretch()
