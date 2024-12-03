from PyQt6.QtWidgets import QTabWidget, QTabBar, QStylePainter
from PyQt6.QtGui import QPainterPath, QColor
from PyQt6.QtCore import Qt, QSize, QObject, QPropertyAnimation, pyqtProperty

from ui.components.tf_font import NotoSerifNormal

class TFTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDrawBase(False)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        self.hover_index = -1
        self.setMouseTracking(True)

        self.tab_animations = {}
        for index in range(self.count()):
            anim = TabHoverAnimation(index, self)
            self.tab_animations[index] = anim

    def tabSizeHint(self, index: int) -> QSize:
        size = super().tabSizeHint(index)
        size.setWidth(size.width())
        size.setHeight(size.height() + 4)
        return size
    
    def tabInserted(self, index):
        super().tabInserted(index)
        anim = TabHoverAnimation(index, self)
        self.tab_animations[index] = anim

    def tabRemoved(self, index):
        super().tabRemoved(index)
        if index in self.tab_animations:
            del self.tab_animations[index]
    
    def mouseMoveEvent(self, event):
        hovered_index = -1
        for index in range(self.count()):
            if self.tabRect(index).contains(event.pos()):
                hovered_index = index
                break

        if self.hover_index != hovered_index:
            old_hover_index = self.hover_index
            self.hover_index = hovered_index

            if old_hover_index != -1:
                self.startFadeOut(old_hover_index)
            if self.hover_index != -1:
                self.startFadeIn(self.hover_index)

    def leaveEvent(self, event):
        if self.hover_index != -1:
            self.startFadeOut(self.hover_index)
            self.hover_index = -1

    def startFadeIn(self, index):
        anim = self.tab_animations[index]
        if anim.animation is not None:
            anim.animation.stop()
        animation = QPropertyAnimation(anim, b'opacity', self)
        animation.setDuration(250)
        animation.setStartValue(anim.opacity)
        animation.setEndValue(1.0)
        animation.finished.connect(lambda: self.onAnimationFinished(index))
        animation.start()
        anim.animation = animation

    def startFadeOut(self, index):
        anim = self.tab_animations[index]
        if anim.animation is not None:
            anim.animation.stop()
        animation = QPropertyAnimation(anim, b'opacity', self)
        animation.setDuration(250)
        animation.setStartValue(anim.opacity)
        animation.setEndValue(0.0)
        animation.finished.connect(lambda: self.onAnimationFinished(index))
        animation.start()
        anim.animation = animation

    def onAnimationFinished(self, index):
        anim = self.tab_animations[index]
        anim.animation = None

    def paintEvent(self, event):
        painter = QStylePainter(self)
        overlap = -15

        selected_index = self.currentIndex()

        for index in range(self.count()):
            rect = self.tabRect(index)
            if index > 0:
                rect.adjust(overlap, 0, 0, 0)

            path = QPainterPath()
            path.moveTo(rect.left(), rect.bottom())
            path.lineTo(rect.left(), rect.top() + 5)
            path.arcTo(rect.left(), rect.top(), 10, 10, 180, -90)
            path.lineTo(rect.right() - 5, rect.top())
            path.arcTo(rect.right() - 10, rect.top(), 10, 10, 90, -90)
            path.lineTo(rect.right(), rect.bottom())
            path.closeSubpath()

            if index == selected_index:
                painter.setBrush(QColor("#2E3440"))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawPath(path)
            else:
                painter.setBrush(QColor("#4E5666"))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawPath(path)

                opacity = self.tab_animations[index].opacity
                if opacity > 0:
                    painter.save()
                    painter.setOpacity(opacity)
                    painter.setBrush(QColor("#5A6437"))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawPath(path)
                    painter.restore()

            text_rect = rect.adjusted(10, 5, -10, -5)
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.tabText(index))

class TFTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(TFTabBar())
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
        """)

        self.setFont(NotoSerifNormal)


class TabHoverAnimation(QObject):
    def __init__(self, index, parent):
        super().__init__(parent)
        self.index = index
        self._opacity = 0
        self.animation = None

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.parent().update()
