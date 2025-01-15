from PyQt6.QtWidgets import QMainWindow, QScrollArea, QSizePolicy, QHBoxLayout, QFrame, QSpacerItem, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont

from ui.components.tf_action_label import TFActionLabel
from ui.components.tf_animated_button import TFAnimatedButton
from ui.components.tf_base_dialog import TFBaseDialog
from ui.components.tf_base_frame import TFBaseFrame
from ui.components.tf_font import NotoSerifNormal
from ui.tf_application import TFApplication
from ui.views.tf_window_container import TFWindowContainer
from utils.helper import resource_path
from utils.registry.tf_tool_registry import TFToolRegistry

WIDTH = 100


class TFMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)

        self.app = TFApplication.instance()
        self.setWindowTitle('摸会儿鱼')
        self.setWindowIcon(QIcon(resource_path("resources/images/icons/app.png")))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setObjectName("mainWindow")
        self.setStyleSheet("""
            QMainWindow#mainWindow {
                background: transparent;
                border: none;
            }
            QWidget#centralWidget {
                background-color: #181C26;
                border-radius: 12px;
            }
        """)

        self.setGeometry(100, 100, 1600, 900)

        self.dragging = False
        self.resizing = False
        self.drag_position = QPoint()
        self.resize_edge = None
        self.resize_border = 5

        self._setup_ui()

        self.central_widget.setMouseTracking(True)
        for child in self.central_widget.findChildren(QWidget):
            child.setMouseTracking(True)
        
    def _setup_ui(self):
        self.central_widget = QFrame(self)
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        
        titlebar = QFrame()
        titlebar.setFixedHeight(30)
        titlebar.setStyleSheet("background-color: transparent;")
        titlebar_layout = QHBoxLayout(titlebar)
        titlebar_layout.setContentsMargins(0, 0, 0, 0)

        class HoverContainer(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setMouseTracking(True)
                self.buttons = []
                
            def enterEvent(self, event):
                for btn in self.buttons:
                    btn.setIconSize(QSize(10, 10))
                super().enterEvent(event)
                
            def leaveEvent(self, event):
                for btn in self.buttons:
                    btn.setIconSize(QSize(0, 0))
                super().leaveEvent(event)
        
        button_container = HoverContainer()
        button_container.setFixedWidth(100)
        button_container.setObjectName("windowControlContainer")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)
        
        button_size = 14
        button_configs = [
            {
                "color": "#FF605C",
                "tooltip": "Close",
                "callback": self.close,
                "icon": "close_button",
                "object_name": "windowCloseButton"
            },
            {
                "color": "#FFBD44",
                "tooltip": "Minimize",
                "callback": self.showMinimized,
                "icon": "minimize_button",
                "object_name": "windowMinButton"
            },
            {
                "color": "#00CA4E",
                "tooltip": "Maximize",
                "callback": self.toggle_maximize,
                "icon": "maximize_button",
                "object_name": "windowMaxButton"
            }
        ]

        for config in button_configs:
            button = QPushButton()
            button.setObjectName(config["object_name"])
            button.setFixedSize(button_size, button_size)
            button.setToolTip(config["tooltip"])
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            
            icon = QIcon(resource_path(f"resources/images/icons/{config['icon']}.png"))
            button.setIcon(icon)
            button.setIconSize(QSize(0, 0))
            
            button.setStyleSheet(f"""
                QPushButton#{config["object_name"]} {{
                    background-color: {config["color"]};
                    border-radius: {button_size//2}px;
                    border: none;
                }}
            """)
            
            button.clicked.connect(config["callback"])
            button_layout.addWidget(button)
            button_container.buttons.append(button)
        
        titlebar_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        titlebar_layout.addWidget(button_container)
        titlebar_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        main_layout.addWidget(titlebar)
        
        content_container = QFrame()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setMinimumSize(200, 200)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.window_container = TFWindowContainer(self)
        self.scroll_area.setWidget(self.window_container)
        
        self.menu_frame = MenuFrame(parent=self)
        self.menu_frame.setFixedWidth(100)
        self.menu_frame.register_tools()
        
        content_layout.addWidget(self.menu_frame)
        content_layout.addWidget(self.scroll_area)
        
        main_layout.addWidget(content_container)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            if self._is_on_edge(pos):
                self.resizing = True
                self.resize_edge = self._get_resize_edge(pos)
            else:
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        if self.resizing and event.buttons() & Qt.MouseButton.LeftButton:
            global_pos = event.globalPosition().toPoint()
            if self.resize_edge:
                self._handle_resize(global_pos)
        elif self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
        else:
            if self._is_on_edge(pos):
                edge = self._get_resize_edge(pos)
                self._update_cursor(edge)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        event.accept()

    def _is_on_edge(self, pos):
        x, y = pos.x(), pos.y()
        width, height = self.width(), self.height()
        return (x < self.resize_border or 
                x > width - self.resize_border or 
                y < self.resize_border or 
                y > height - self.resize_border)

    def _get_resize_edge(self, pos):
        x, y = pos.x(), pos.y()
        width, height = self.width(), self.height()
        
        if x < self.resize_border:
            if y < self.resize_border:
                return 'top-left'
            elif y > height - self.resize_border:
                return 'bottom-left'
            return 'left'
        elif x > width - self.resize_border:
            if y < self.resize_border:
                return 'top-right'
            elif y > height - self.resize_border:
                return 'bottom-right'
            return 'right'
        elif y < self.resize_border:
            return 'top'
        elif y > height - self.resize_border:
            return 'bottom'
        return None

    def _update_cursor(self, edge):
        if edge in ['left', 'right']:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edge in ['top', 'bottom']:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif edge in ['top-left', 'bottom-right']:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge in ['top-right', 'bottom-left']:
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)

    def _handle_resize(self, global_pos):
        new_rect = self.geometry()
        pos = self.mapToGlobal(QPoint(0, 0))
        
        if self.resize_edge in ['left', 'top-left', 'bottom-left']:
            _ = pos.x() - global_pos.x()
            new_rect.setLeft(global_pos.x())
            if new_rect.width() < self.minimumWidth():
                new_rect.setLeft(pos.x() + self.width() - self.minimumWidth())
                
        if self.resize_edge in ['right', 'top-right', 'bottom-right']:
            new_rect.setRight(global_pos.x())
            
        if self.resize_edge in ['top', 'top-left', 'top-right']:
            _ = pos.y() - global_pos.y()
            new_rect.setTop(global_pos.y())
            if new_rect.height() < self.minimumHeight():
                new_rect.setTop(pos.y() + self.height() - self.minimumHeight())
                
        if self.resize_edge in ['bottom', 'bottom-left', 'bottom-right']:
            new_rect.setBottom(global_pos.y())
            
        self.setGeometry(new_rect)


class MenuFrame(TFBaseFrame):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.setMinimumWidth(WIDTH)
        self.tools = {}

    def _setup_content(self):
        self.main_layout.setSpacing(60)
        self.main_layout.setContentsMargins(0, 30, 0, 30)

        icon_container = QWidget()
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label = QLabel()
        icon = QPixmap("resources/images/icons/app.ico").scaled(
            32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        icon_label.setPixmap(icon)
        icon_label.setFixedSize(32, 32)
        icon_layout.addWidget(icon_label)
        self.main_layout.addWidget(icon_container)
        
        self.tools_group = ExpandableIconGroup('tools', [], parent=self)
        self.main_layout.addWidget(self.tools_group, 0, Qt.AlignmentFlag.AlignHCenter)
        
        self.tools_group.main_button.clicked.connect(self.toggle_tools)
        
        about_btn = TFAnimatedButton('about')
        about_btn.clicked_signal.connect(self._show_about)
        self.main_layout.addWidget(about_btn, 0, Qt.AlignmentFlag.AlignHCenter)

        settings_btn = TFAnimatedButton('settings')
        self.main_layout.addWidget(settings_btn, 0, Qt.AlignmentFlag.AlignHCenter)
        
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        layers_btn = TFAnimatedButton('layers')
        self.main_layout.addWidget(layers_btn, 0, Qt.AlignmentFlag.AlignHCenter)
        
        exit_btn = TFAnimatedButton('exit')
        exit_btn.clicked_signal.connect(TFApplication.instance().quit)
        self.main_layout.addWidget(exit_btn, 0, Qt.AlignmentFlag.AlignHCenter)

    def register_tools(self):
        registered_tools = TFToolRegistry.get_tools()
        
        tool_actions = []
        for tool_class in registered_tools.values():
            metadata = tool_class.metadata
            self.tools[metadata.name] = tool_class
            tool_actions.append(metadata.name)
            
        tool_actions.sort()
        
        self.tools_group.update_actions(tool_actions)
        self.tools_group.action_triggered.connect(self.handle_tool_action)

    def handle_tool_action(self, action_text):
        if action_text in self.tools:
            tool_class = self.tools[action_text]
            self.parent.window_container.add_window(window_class=tool_class)
            self.tools_group.collapse()

    def _decrement_instance_count(self, tool_name):
        if tool_name in self.tool_instances:
            self.tool_instances[tool_name] = max(0, self.tool_instances[tool_name] - 1)

    def toggle_tools(self):
        if self.tools_group.expanded:
            self.tools_group.collapse()
        else:
            self.tools_group.expand()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if not self.tools_group.geometry().contains(event.pos()):
            self.tools_group.collapse()

    def _show_about(self):
        AboutDialog.get_input(self)


class ExpandableIconGroup(QWidget):
    action_triggered = pyqtSignal(str)

    def __init__(self, main_icon, actions, parent=None):
        super().__init__(parent)
        self.setFixedWidth(WIDTH)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        main_button_container = QWidget()
        main_button_layout = QHBoxLayout(main_button_container)
        main_button_layout.setContentsMargins(0, 0, 0, 0)
        main_button_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.main_button = TFAnimatedButton(main_icon)
        main_button_layout.addWidget(self.main_button)
        self.layout.addWidget(main_button_container)
        
        self.sub_container = QWidget()
        self.sub_layout = QVBoxLayout(self.sub_container)
        self.sub_layout.setSpacing(15)
        self.sub_layout.setContentsMargins(0, 0, 0, 0)
        self.sub_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.layout.addWidget(self.sub_container)
        
        self.action_labels = []
        self.update_actions(actions)
        
        self.animation = QPropertyAnimation(self.sub_container, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.expanded = False

    def update_actions(self, actions):
        for label in self.action_labels:
            self.sub_layout.removeWidget(label)
            label.deleteLater()
        self.action_labels.clear()
        
        for action_text in actions:
            label = TFActionLabel(action_text)
            label.setFont(NotoSerifNormal)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.clicked.connect(lambda t=action_text: self.handle_action(t))
            self.action_labels.append(label)
            self.sub_layout.addWidget(label)
            label.setVisible(False)
        
        self.sub_container.setMaximumHeight(0)

    def expand(self):
        for label in self.action_labels:
            label.setVisible(True)
            
        total_height = (self.sub_layout.spacing() * (len(self.action_labels) - 1) + 
                       sum(label.sizeHint().height() for label in self.action_labels) +
                       self.sub_layout.contentsMargins().top() +
                       self.sub_layout.contentsMargins().bottom())
        
        self.animation.setStartValue(0)
        self.animation.setEndValue(total_height)
        self.animation.start()
        self.expanded = True

    def collapse(self):
        current_height = self.sub_container.height()
        self.animation.setStartValue(current_height)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.hide_labels)
        self.animation.start()
        self.expanded = False
    
    def hide_labels(self):
        for label in self.action_labels:
            label.setVisible(False)
        self.animation.finished.disconnect(self.hide_labels)
        
    def handle_action(self, action_text):
        self.action_triggered.emit(action_text)


class AboutDialog(TFBaseDialog):
    FIRST_TEST_NAMES = ["秋刀鱼", "我不是惜林", "零九七", "BTap1920"]
    def __init__(self, parent=None):
        super().__init__(
            title="关于摸摸鱼",
            layout_type=QVBoxLayout,
            parent=parent,
            button_config=[{"text": "确定", "callback": self.accept}]
        )
        self.resize(800, 600)

    def _setup_content(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = TFBaseFrame(QVBoxLayout, parent=scroll)
        content_widget.main_layout.setSpacing(10)
        content_widget.main_layout.setContentsMargins(20, 20, 20, 20)
        scroll.setWidget(content_widget)

        label_font = QFont("Noto Serif SC")
        label_font.setPointSize(12)

        label = content_widget.create_label(
            '项目启动 - 2024/10/31', 
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
            height=24
        )
        label.setFont(label_font)
        content_widget.main_layout.addWidget(label)

        content_widget.main_layout.addSpacing(50)

        label = content_widget.create_label(
            '项目确定为COC工具 - 2024/11/09', 
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
            height=24
        )
        label.setFont(label_font)
        content_widget.main_layout.addWidget(label)

        content_widget.main_layout.addSpacing(50)

        label = content_widget.create_label(
            '调查员角色卡完成 - 2024/11/10', 
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
            height=24
        )
        label.setFont(label_font)
        content_widget.main_layout.addWidget(label)

        content_widget.main_layout.addSpacing(50)

        label = content_widget.create_label(
            '角色构筑器完成 - 2024/11/20', 
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
            height=24
        )
        label.setFont(label_font)
        content_widget.main_layout.addWidget(label)

        content_widget.main_layout.addSpacing(50)

        label = content_widget.create_label(
            '第一次用户测试（调查员角色卡 / 角色构筑器） - 2024/11/20-2024/11/21', 
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
            height=24
        )
        label.setFont(label_font)
        content_widget.main_layout.addWidget(label)

        for n in self.FIRST_TEST_NAMES:
            n_label = content_widget.create_label(
                n, 
                height=24,
                alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter
            )
            n_label.setFont(NotoSerifNormal)
            content_widget.main_layout.addWidget(n_label)
            
        content_widget.main_layout.addSpacing(50)

        label = content_widget.create_label(
            'V2代码重构完成 - 2024/11/24', 
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
            height=24
        )
        label.setFont(label_font)
        content_widget.main_layout.addWidget(label)

        content_widget.main_layout.addSpacing(50)

        label = content_widget.create_label(
            '添加中文支持 - 2024/12/01', 
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
            height=24
        )
        label.setFont(label_font)
        content_widget.main_layout.addWidget(label)

        content_widget.main_layout.addSpacing(50)

        label = content_widget.create_label(
            '角色构筑器V2完成 - 2024/12/03', 
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
            height=24
        )
        label.setFont(label_font)
        content_widget.main_layout.addWidget(label)

        content_widget.main_layout.addSpacing(50)

        label = content_widget.create_label(
            'UI整体优化完成（放假回来了） - 2025/01/15', 
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
            height=24
        )
        label.setFont(label_font)
        content_widget.main_layout.addWidget(label)

        self.main_layout.addWidget(scroll)
