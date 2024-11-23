from PyQt6.QtWidgets import QVBoxLayout, QFrame, QLayout
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor

from ui.components.component_creator_mixin import ComponentCreatorMixin

LEVEL_COLORS = {
    0: QColor("#181C26"),
    1: QColor("#242831")
}


class TFBaseFrame(QFrame, ComponentCreatorMixin):
    values_changed = pyqtSignal(dict)

    def __init__(self, layout_type: type[QLayout] = QVBoxLayout, level: int = 0, radius: int = 5,parent=None):
        QFrame.__init__(self, parent)
        ComponentCreatorMixin.__init__(self)

        if not issubclass(layout_type, QLayout):
            raise TypeError(f"Invalid layout_type: {layout_type}. Expected a subclass of QLayout.")

        self.parent = parent
        self.level = level
        self.radius = radius
        
        self.setProperty("frameLevel", level)
        self.setProperty("frameRadius", radius)

        self.setFrameShape(QFrame.Shape.NoFrame)
        self._setup_ui(layout_type)
        self._setup_content()

    def _setup_ui(self, layout_type: type[QLayout]) -> None:
        self.main_layout = layout_type(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.main_layout)

    def _setup_content(self) -> None:
        pass

    def add_child(self, name: str, child: "TFBaseFrame") -> None:
        self._register_component(name, child)
        self.layout().addWidget(child)
        
