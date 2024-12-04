from PyQt6.QtWidgets import QVBoxLayout, QFrame, QLayout
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor

from ui.components.if_component_creator import IComponentCreator

LEVEL_COLORS = {
    0: QColor("#181C26"),
    1: QColor("#242831")
}


class TFBaseFrame(QFrame, IComponentCreator):
    values_changed = pyqtSignal(dict)
    parent_values_updated = pyqtSignal(dict)

    def __init__(self, layout_type: type[QLayout] = QVBoxLayout, level: int = 0, radius: int = 5,parent=None):
        QFrame.__init__(self, parent)
        IComponentCreator.__init__(self)

        if not issubclass(layout_type, QLayout):
            raise TypeError(f"Invalid layout_type: {layout_type}. Expected a subclass of QLayout.")

        self.parent = parent
        self.level = level
        self.radius = radius
        self._children = {}
        
        self.setProperty("frameLevel", level)
        self.setProperty("frameRadius", radius)

        self.setFrameShape(QFrame.Shape.NoFrame)
        self._setup_ui(layout_type)
        self._setup_content()

    def _setup_ui(self, layout_type: type[QLayout]) -> None:
        self.main_layout = layout_type(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(10)
        self.setLayout(self.main_layout)

    def _setup_content(self) -> None:
        pass

    def add_child(self, name: str, child: "TFBaseFrame") -> None:
        self._register_component(name, child)
        self._children[name] = child
        self.layout().addWidget(child)
        
        child.values_changed.connect(lambda values: self._handle_child_values_changed(name, values))
        
        self.parent_values_updated.connect(child.handle_parent_update)

    def _handle_child_values_changed(self, child_name: str, child_values: dict) -> None:
        all_values = self.get_values()
        self.values_changed.emit(all_values)

    def handle_parent_update(self, parent_values: dict) -> None:
        self.update_components_from_values(parent_values)
        self.parent_values_updated.emit(parent_values)
