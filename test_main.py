from PyQt6.QtWidgets import QApplication
from ui.components.tf_base_frame import TFBaseFrame
from ui.components.tf_draggable_label import TFDraggableLabel
from ui.components.tf_flexble_window import TFFlexibleWindow

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    main_window = TFBaseFrame()
    main_window.setWindowTitle("TFFlexibleWindow 测试")
    main_window.setFixedSize(800, 400)

    # 创建两个 TFFlexibleWindow
    flexible_window1 = TFFlexibleWindow(width=380, height=360)
    flexible_window2 = TFFlexibleWindow(width=380, height=360)

    # 创建一些可拖动的标签
    label_texts = ["标签1", "标签2", "标签3", "标签4", "标签5", "标签6"]
    labels = [TFDraggableLabel(text) for text in label_texts]

    # 将前3个标签添加到第一个窗口
    for label in labels[:3]:
        flexible_window1.add_draggable_label(label)

    # 将后3个标签添加到第二个窗口
    for label in labels[3:]:
        flexible_window2.add_draggable_label(label)

    # 将 TFFlexibleWindow 添加到 main_window 的 main_layout
    main_window.main_layout.addWidget(flexible_window1)
    main_window.main_layout.addWidget(flexible_window2)

    main_window.show()

    sys.exit(app.exec())
