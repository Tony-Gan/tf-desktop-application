from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap, QFontMetrics
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty, QRect


class TFBaseButton(QPushButton):
    LEVEL_COLORS = {
        0: {
            'idle_bg': QColor("#242831"),
            'hover_bg': QColor("#858585"),
            'disabled_bg': QColor("#4D4D4D"),
            'idle_text': QColor("#FFFFFF"),
            'hover_text': QColor("#FFFFFF"),
            'disabled_text': QColor("#808080")
        },
        1: {
            'idle_bg': QColor("#2C3340"),
            'hover_bg': QColor("#959595"), 
            'disabled_bg': QColor("#575757"),
            'idle_text': QColor("#FFFFFF"),
            'hover_text': QColor("#FFFFFF"),
            'disabled_text': QColor("#808080")
        }
    }
    def __init__(
        self,
        text: str,
        parent=None,
        width: int = 100,
        height: int = None,
        font_family: str = "Noto Serif SC Light",
        font_size: int = 10,
        enabled: bool = True,
        checkable: bool = False,
        object_name: str = None,
        tooltip: str = None,
        border_radius: int = 15,
        level: int = 1,
        on_clicked=None,
        icon_path: str = None
    ):
        super().__init__(text, parent)

        self.level = level
        self.setObjectName("TFBaseButton")
        self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
            
        font = QFont(font_family)
        font.setPointSize(font_size)
        self.setFont(font)
        
        self.setEnabled(enabled)
        self.setCheckable(checkable)

        self.radius = border_radius
        
        if object_name:
            self.setObjectName(object_name)
            
        if tooltip:
            self.setToolTip(tooltip)
            
        if on_clicked:
            self.clicked.connect(on_clicked)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        colors = self.LEVEL_COLORS.get(level, self.LEVEL_COLORS[0])
        if not enabled:
            self._bg_color = colors['disabled_bg']
            self._text_color = colors['disabled_text']
        else:
            self._bg_color = colors['idle_bg']
            self._text_color = colors['idle_text']
        
        self._bg_animation = QPropertyAnimation(self, b"backgroundColor", self)
        self._bg_animation.setDuration(200)
        
        self._text_animation = QPropertyAnimation(self, b"textColor", self)
        self._text_animation.setDuration(200)

        if icon_path:
            self.icon = QPixmap(icon_path)
        else:
            self.icon = None

    @pyqtProperty(QColor)
    def backgroundColor(self):
        return self._bg_color

    @backgroundColor.setter
    def backgroundColor(self, color):
        self._bg_color = color
        self.update()

    @pyqtProperty(QColor)
    def textColor(self):
        return self._text_color

    @textColor.setter
    def textColor(self, color):
        self._text_color = color
        self.update()

    def enterEvent(self, event):
        if not self.isEnabled():
            return super().enterEvent(event)
            
        colors = self.LEVEL_COLORS.get(self.level, self.LEVEL_COLORS[0])
        
        self._bg_animation.stop()
        self._bg_animation.setStartValue(colors['idle_bg'])
        self._bg_animation.setEndValue(colors['hover_bg'])
        self._bg_animation.start()
        
        self._text_animation.stop()
        self._text_animation.setStartValue(colors['idle_text'])
        self._text_animation.setEndValue(colors['hover_text'])
        self._text_animation.start()
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.isEnabled():
            return super().leaveEvent(event)
            
        colors = self.LEVEL_COLORS.get(self.level, self.LEVEL_COLORS[0])
        
        self._bg_animation.stop()
        self._bg_animation.setStartValue(colors['hover_bg'])
        self._bg_animation.setEndValue(colors['idle_bg'])
        self._bg_animation.start()
        
        self._text_animation.stop()
        self._text_animation.setStartValue(colors['hover_text'])
        self._text_animation.setEndValue(colors['idle_text'])
        self._text_animation.start()
        
        super().leaveEvent(event)

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        colors = self.LEVEL_COLORS.get(self.level, self.LEVEL_COLORS[0])
        if not enabled:
            self._bg_color = colors['disabled_bg']
            self._text_color = colors['disabled_text']
        else:
            self._bg_color = colors['idle_bg']
            self._text_color = colors['idle_text']
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(self._bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)

        painter.setPen(self._text_color)
        painter.setFont(self.font())

        rect = self.rect()
        margin = 5

        if self.icon and not self.text():
            icon_size = min(rect.width(), rect.height()) - 2 * margin
            icon_rect = QRect(
                int((rect.width() - icon_size) / 2),
                int((rect.height() - icon_size) / 2),
                icon_size,
                icon_size
            )
            painter.drawPixmap(
                icon_rect,
                self.icon.scaled(
                    icon_rect.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
            return

        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.horizontalAdvance(self.text())
        text_height = font_metrics.height()

        icon_width = 0
        icon_height = 0

        if self.icon:
            icon_size = self.icon.size()
            icon_height = min(rect.height() - 2 * margin, icon_size.height())
            icon_width = int(icon_size.width() * (icon_height / icon_size.height()))

        total_width = text_width + icon_width
        if self.icon:
            total_width += margin

        start_x = (rect.width() - total_width) / 2
        text_y = (rect.height() + text_height) / 2 - font_metrics.descent()

        if self.icon:
            icon_rect = QRect(
                int(start_x),
                int((rect.height() - icon_height) / 2),
                icon_width,
                icon_height
            )
            painter.drawPixmap(
                icon_rect,
                self.icon.scaled(
                    icon_rect.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
            text_x = icon_rect.right() + margin
        else:
            text_x = start_x

        painter.drawText(
            QRect(int(text_x), 0, int(text_width), rect.height()),
            Qt.AlignmentFlag.AlignVCenter,
            self.text()
        )

    def disable_animations(self):
        self._bg_color = QColor("#4D4D4D")
        self._text_color = QColor("#808080")
        self.update()

class TFNextButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Noto Serif SC Light",
        font_size: int = 10,
        enabled:bool = False,
        on_clicked=None, 
        tooltip="Next step"
    ):
        super().__init__(
            "下一步",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            enabled=enabled,
            object_name="next_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFNextButton")

class TFPreviousButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Noto Serif SC Light",
        font_size: int = 10,
        enabled:bool = True,
        on_clicked=None, 
        tooltip="Previous step"
    ):
        super().__init__(
            "上一步",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            enabled=enabled,
            object_name="previous_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFPreviousButton")

class TFBackButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Noto Serif SC Light",
        font_size: int = 10,
        enabled:bool = False,
        on_clicked=None, 
        tooltip="Go back"
    ):
        super().__init__(
            "返回",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            enabled=enabled,
            object_name="back_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFBackButton")

class TFConfirmButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Noto Serif SC Light",
        font_size: int = 10,
        enabled:bool = False,
        on_clicked=None, 
        tooltip="Confirm action"
    ):
        super().__init__(
            "确认",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            enabled=enabled,
            object_name="confirm_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFConfirmButton")

class TFResetButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Noto Serif SC Light",
        font_size: int = 10,
        enabled:bool = True,
        on_clicked=None, 
        tooltip="Reset to default"
    ):
        super().__init__(
            "重置",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            enabled=enabled,
            object_name="reset_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFResetButton")

class TFCancelButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Noto Serif SC Light",
        font_size: int = 10,
        enabled:bool = False,
        on_clicked=None, 
        tooltip="Cancel action"
    ):
        super().__init__(
            "取消",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            enabled=enabled,
            object_name="cancel_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFCancelButton")

class TFSubmitButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Noto Serif SC Light",
        font_size: int = 10,
        enabled:bool = False,
        on_clicked=None, 
        tooltip="Submit form"
    ):
        super().__init__(
            "提交",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            enabled=enabled,
            object_name="submit_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFSubmitButton")

