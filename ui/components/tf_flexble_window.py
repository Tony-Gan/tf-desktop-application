from PyQt6.QtWidgets import QLayout
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal, pyqtProperty, QDataStream, QSize, QIODevice

from ui.components.tf_base_frame import TFBaseFrame

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=10):
        super().__init__(parent)
        self.itemList = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        try:
            return self.itemList[index]
        except IndexError:
            return None

    def takeAt(self, index):
        try:
            return self.itemList.pop(index)
        except IndexError:
            return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + wid.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + wid.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), wid.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, wid.sizeHint().height())

        return y + lineHeight - rect.y()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

class TFFlexibleWindow(TFBaseFrame):
    label_dropped = pyqtSignal(object)

    def __init__(self, width=400, height=300, parent=None):
        super().__init__(layout_type=FlowLayout, parent=parent)
        self.setFixedSize(width, height)
        self.setAcceptDrops(True)
        self.labels = []

    def add_draggable_label(self, label):
        if not self.has_space_for_label(label):
            # 这里可以调用您已有的提示方法，暂时用占位符
            print("没有足够的空间添加新的标签")
            return False

        self.labels.append(label)
        label.set_parent_window(self)
        self.layout().addWidget(label)
        return True

    def has_space_for_label(self, label):
        # 简单判断是否有空间，可以根据需要调整逻辑
        return True  # 暂时返回 True，实际需要计算是否有空间

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-draggable-label'):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-draggable-label'):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-draggable-label'):
            data = event.mimeData().data('application/x-draggable-label')
            stream = QDataStream(data, QIODevice.OpenModeFlag.ReadOnly)
            label_text = stream.readQString()

            source_label = event.source()
            source_window = source_label.parent_window

            if source_window is not self:
                if not self.add_draggable_label(source_label):
                    # 目标窗口没有空间，拖动失败
                    print("目标窗口没有空间，拖动失败")
                    return
                else:
                    source_window.remove_draggable_label(source_label)

            pos = event.position().toPoint()
            self.reorder_labels(source_label, pos)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def remove_draggable_label(self, label):
        if label in self.labels:
            self.labels.remove(label)
            self.layout().removeWidget(label)
            label.setParent(None)

    def reorder_labels(self, moving_label, pos):
        index = 0
        for i in range(len(self.labels)):
            widget = self.labels[i]
            if widget == moving_label:
                continue
            if widget.geometry().contains(pos):
                index = i
                break
        else:
            index = len(self.labels)

        self.labels.remove(moving_label)
        self.labels.insert(index, moving_label)

        for label in self.labels:
            self.layout().removeWidget(label)
        for label in self.labels:
            self.layout().addWidget(label)