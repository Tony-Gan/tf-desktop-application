from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, Qt
from PyQt6.QtGui import QPainter, QPixmap, QCursor

from utils.helper import resource_path


class TFAnimatedButton(QPushButton):
    clicked_signal = pyqtSignal(str)

    def __init__(self, icon_name, tooltip="", size=24, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.setFixedSize(size, size)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        if tooltip:
            self.setToolTip(tooltip)

        self.normal_icon = QPixmap(resource_path(f"resources/images/icons/{icon_name}.png")).scaled(
            size*2, size*2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.hover_icon = QPixmap(resource_path(f"resources/images/icons/{icon_name}_hover.png")).scaled(
            size*2, size*2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        
        self.setIconSize(self.size())
        self.setStyleSheet("border: none; background: transparent;")
        
        self._icon_opacity = 1.0
        
        self.hover_animation = QPropertyAnimation(self, b"iconOpacity")
        self.hover_animation.setDuration(300)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.clicked.connect(lambda: self.clicked_signal.emit(self.icon_name))
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        target_rect = self.rect()
        source_rect = self.normal_icon.rect()
        target_rect.adjust(
            (target_rect.width() - source_rect.width() // 2) // 2,
            (target_rect.height() - source_rect.height() // 2) // 2,
            -(target_rect.width() - source_rect.width() // 2) // 2,
            -(target_rect.height() - source_rect.height() // 2) // 2
        )
        
        painter.setOpacity(self._icon_opacity)
        painter.drawPixmap(target_rect, self.normal_icon)
        painter.setOpacity(1 - self._icon_opacity)
        painter.drawPixmap(target_rect, self.hover_icon)
        
    def enterEvent(self, event):
        self.hover_animation.setStartValue(1.0)
        self.hover_animation.setEndValue(0.0)
        self.hover_animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.hover_animation.setStartValue(0.0)
        self.hover_animation.setEndValue(1.0)
        self.hover_animation.start()
        super().leaveEvent(event)
    
    @pyqtProperty(float)
    def iconOpacity(self):
        return self._icon_opacity
        
    @iconOpacity.setter
    def iconOpacity(self, value):
        self._icon_opacity = value
        self.update()
