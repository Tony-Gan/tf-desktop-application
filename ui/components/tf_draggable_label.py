from PyQt6.QtCore import Qt, QByteArray, QMimeData, QDataStream, QIODevice
from PyQt6.QtGui import QDrag

from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_font import NotoSerifNormal
from ui.tf_application import TFApplication


class TFDraggableLabel(TFBaseButton):
    def __init__(self, text, callback=None, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(24)
        self.setFont(NotoSerifNormal)
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
        self.callback = callback
        self.setAcceptDrops(False)
        self.parent_window = None

    def set_parent_window(self, window):
        self.parent_window = window

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < TFApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()

        data = QByteArray()
        stream = QDataStream(data, QIODevice.OpenModeFlag.WriteOnly)
        stream.writeQString(self.text())
        mime_data.setData('application/x-draggable-label', data)

        drag.setMimeData(mime_data)
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint() - self.rect().topLeft())

        drop_action = drag.exec(Qt.DropAction.MoveAction)
        if drop_action == Qt.DropAction.MoveAction:
            if self.parent_window:
                self.parent_window.remove_draggable_label(self)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.setStyleSheet("background-color: #858585;")

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.setStyleSheet("")

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.callback:
            self.callback()
