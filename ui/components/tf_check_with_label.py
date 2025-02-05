from typing import Optional

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QFrame, QCheckBox, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QPainter, QColor

from ui.components.if_state_controll import IStateController
from ui.components.tf_font import TEXT_FONT
from ui.components.tf_tooltip import TFTooltip


class HoverOverlay(QWidget):
    def __init__(self, parent=None, corner_radius: int = 4):
        super().__init__(parent)
        self._opacity = 0.0
        self._corner_radius = corner_radius
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        self.setAutoFillBackground(False)

    def getOpacity(self) -> float:
        return self._opacity

    def setOpacity(self, value: float) -> None:
        self._opacity = value
        self.update()

    opacity = pyqtProperty(float, fget=getOpacity, fset=setOpacity)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        alpha = int(self._opacity * 255)
        painter.setBrush(QColor(255, 255, 255, alpha))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), self._corner_radius, self._corner_radius)
        painter.end()


class AnimatedCheckBox(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

        self._overlay = HoverOverlay(self, corner_radius=4)
        self._overlay.setGeometry(self.rect())

        self._animation = QPropertyAnimation(self._overlay, b"opacity", self)
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._overlay.setGeometry(self.rect())

    def enterEvent(self, event):
        if not self.isEnabled():
            return super().enterEvent(event)
        self._animation.stop()
        self._animation.setStartValue(self._overlay.opacity)
        self._animation.setEndValue(0.15)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animation.stop()
        self._animation.setStartValue(self._overlay.opacity)
        self._animation.setEndValue(0.0)
        self._animation.start()
        super().leaveEvent(event)

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        if not enabled:
            self._animation.stop()
            self._overlay.setOpacity(0.0)


class TFCheckWithLabel(QFrame, IStateController):
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
        QFrame.__init__(self, parent)
        IStateController.__init__(self)

        self.show_tooltip = show_tooltip

        self.label_text = label_text
        self.label_font = label_font
        self.label_alignment = label_alignment

        self.height = height
        self.spacing = spacing

        self.checked = checked

        self.show_tooltip = show_tooltip
        self.tooltip_text = tooltip_text

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(self.height)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(self.spacing)

        self.check = AnimatedCheckBox()
        self.check.setChecked(self.checked)
        self.check.stateChanged.connect(lambda state: self.value_changed.emit(bool(state)))

        self.label = QLabel(self.label_text)
        self.label.setFont(self.label_font)
        self.label.setAlignment(self.label_alignment)
        self.label.mousePressEvent = self._on_label_clicked

        layout.addWidget(self.check)
        layout.addWidget(self.label)

        if self.show_tooltip and self.tooltip_text:
            icon_size = self.height - 4
            self.tooltip_icon = TFTooltip(icon_size, self.tooltip_text)
            layout.addWidget(self.tooltip_icon)
            layout.addSpacing(2)

        layout.addStretch()

    def _on_label_clicked(self, event) -> None:
        self.check.setChecked(not self.check.isChecked())

    def get_value(self) -> bool:
        return self.check.isChecked()

    def set_checked(self, checked) -> None:
        self.check.setChecked(checked)

    def update_tooltip(self, text: str) -> None:
        if self.show_tooltip:
            self.tooltip_icon.update_tooltip(text)

    def set_enabled(self, enable, check_only=True):
        self.check.setEnabled(enable)
        if not check_only:
            self.label.setEnabled(enable)
