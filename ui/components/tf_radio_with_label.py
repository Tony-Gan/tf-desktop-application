from typing import Optional

from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QFrame, QRadioButton
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QPropertyAnimation, pyqtProperty
)
from PyQt6.QtGui import QFont, QColor

from ui.components.if_state_controll import IStateController
from ui.components.tf_font import TEXT_FONT
from ui.components.tf_tooltip import TFTooltip


class TFRadioWithLabel(QFrame, IStateController):
    """
    为鼠标悬停添加渐入渐出动画：
      - 正常状态：透明
      - 悬停状态：rgba(200,200,200,0.2)
    """

    value_changed = pyqtSignal(bool)

    def __init__(
            self,
            label_text: str = "",
            label_font: QFont = TEXT_FONT,
            checked: bool = False,
            height: int = 24,
            spacing: int = 6,
            label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            show_tooltip: bool = False,
            tooltip_text: str = "",
            parent: Optional[QFrame] = None
    ) -> None:
        super().__init__(parent)
        
        IStateController.__init__(self)

        # 设置对象名（如果想在其他地方用样式表，也可以）
        self.setObjectName("tfRadioWithLabel")

        # 固定高度、无边框
        self.setFixedHeight(height)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # 默认背景色：全透明
        self._bg_color = QColor(0, 0, 0, 0)

        # 创建属性动画，用于在 enter/leave 时渐变背景
        self._animation = QPropertyAnimation(self, b"bgColor")
        self._animation.setDuration(200)  # 动画时长：毫秒
        # 你也可以设置缓动曲线
        # self._animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.show_tooltip = show_tooltip

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(spacing)

        self.radio = QRadioButton()
        self.radio.setChecked(checked)
        self.radio.toggled.connect(self._on_toggled)
        layout.addWidget(self.radio)

        self.label = QLabel(label_text)
        self.label.setFont(label_font)
        self.label.setAlignment(label_alignment)
        layout.addWidget(self.label)

        if show_tooltip and tooltip_text:
            icon_size = height - 4
            self.tooltip_icon = TFTooltip(icon_size, tooltip_text)
            layout.addWidget(self.tooltip_icon)
            layout.addSpacing(2)

        layout.addStretch()

    @pyqtProperty(QColor)
    def bgColor(self) -> QColor:
        return self._bg_color

    @bgColor.setter
    def bgColor(self, color: QColor) -> None:
        self._bg_color = color
        self.setStyleSheet(f"""
            #{self.objectName()} {{
                border-radius: 4px;
                background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()});
            }}
        """)

    def enterEvent(self, event):
        self._animation.stop()
        self._animation.setStartValue(self.bgColor)
        self._animation.setEndValue(QColor(200, 200, 200, 51))
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animation.stop()
        self._animation.setStartValue(self.bgColor)
        self._animation.setEndValue(QColor(0, 0, 0, 0))
        self._animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.radio.setChecked(True)
            self.value_changed.emit(self.radio.isChecked())
        super().mousePressEvent(event)

    def _on_toggled(self, checked: bool) -> None:
        self.value_changed.emit(checked)

    def get_value(self) -> bool:
        return self.radio.isChecked()
    
    def set_checked(self, checked: bool) -> None:
        self.radio.setChecked(checked)
        
    def get_text(self) -> str:
        return self.label.text()
    
    def is_checked(self) -> bool:
        return self.radio.isChecked()

    def update_tooltip(self, text: str) -> None:
        if self.show_tooltip:
            self.tooltip_icon.update_tooltip(text)
