from PyQt6.QtWidgets import QTabWidget, QTabBar, QStylePainter
from PyQt6.QtGui import QPainterPath, QColor
from PyQt6.QtCore import Qt, QSize

class TFTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDrawBase(False)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        self.hover_index = -1
        self.setMouseTracking(True)

    def tabSizeHint(self, index: int) -> QSize:
        size = super().tabSizeHint(index)
        size.setWidth(size.width() + 20)
        size.setHeight(size.height() + 4)
        return size
    
    def mouseMoveEvent(self, event):
        for index in range(self.count()):
            if self.tabRect(index).contains(event.pos()):
                if self.hover_index != index:
                    self.hover_index = index
                    self.update()
                return
        self.hover_index = -1
        self.update()

    def leaveEvent(self, event):
        self.hover_index = -1
        self.update()

    def paintEvent(self, event):
        painter = QStylePainter(self)
        overlap = -10

        selected_index = self.currentIndex()

        for index in range(self.count()):
            if index == selected_index:
                continue

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

            if index == self.hover_index:
                painter.setBrush(QColor("#5A6473"))
            else:
                painter.setBrush(QColor("#4E5666"))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(path)

            text_rect = rect.adjusted(10, 5, -10, -5)
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.tabText(index))

        if selected_index >= 0:
            rect = self.tabRect(selected_index)
            if selected_index > 0:
                rect.adjust(overlap, 0, 0, 0)

            path = QPainterPath()
            path.moveTo(rect.left(), rect.bottom())
            path.lineTo(rect.left(), rect.top() + 5)
            path.arcTo(rect.left(), rect.top(), 10, 10, 180, -90)
            path.lineTo(rect.right() - 5, rect.top())
            path.arcTo(rect.right() - 10, rect.top(), 10, 10, 90, -90)
            path.lineTo(rect.right(), rect.bottom())
            path.closeSubpath()

            painter.setBrush(QColor("#2E3440"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(path)

            text_rect = rect.adjusted(10, 5, -10, -5)
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.tabText(selected_index))

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

        font = self.font()
        font.setFamily("CustomFont")
        font.setPointSize(12)
        self.setFont(font)
