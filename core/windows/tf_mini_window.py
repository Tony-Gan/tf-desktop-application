from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QMouseEvent

from ui.components.tf_animated_button import TFAnimatedButton
from ui.tf_application import TFApplication
from ui.components.tf_font import NotoSerifNormal

class TFMiniWindow(QFrame):
    moved = pyqtSignal()
    restored = pyqtSignal()
    closed = pyqtSignal()

    def __init__(self, parent, title: str):
        super().__init__(parent)
        self._dragging = False
        self._offset = QPoint()
        self.app = TFApplication.instance()

        self.setObjectName("TFMiniWindow")
        self.setFixedSize(160, 24)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        self._title_label = QLabel(title, self)
        self._title_label.setFont(NotoSerifNormal)
        self._title_label.setObjectName("miniTitleLabel")
        layout.addWidget(self._title_label)
        
        self._restore_button = TFAnimatedButton(
            icon_name="maximize",
            tooltip="复原",
            size=16,
            parent=self
        )
        self._restore_button.clicked_signal.connect(self._on_restore)
        
        self._close_button = TFAnimatedButton(
            icon_name="close",
            tooltip="关闭",
            size=16,
            parent=self
        )
        self._close_button.clicked_signal.connect(self._on_close)
        
        layout.addWidget(self._restore_button)
        layout.addWidget(self._close_button)
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._offset = event.position().toPoint()
            self.raise_()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragging:
            current_pos = event.position().toPoint()
            delta = current_pos - self._offset
            new_pos = self.pos() + delta
            
            new_pos.setX(max(0, new_pos.x()))
            new_pos.setY(max(0, new_pos.y()))
            
            self.move(new_pos)
            self.moved.emit()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def _on_restore(self):
        self.restored.emit()
        self.hide()
        self.deleteLater()
    
    def _on_close(self):
        self.closed.emit()
        self.hide()
        self.deleteLater()