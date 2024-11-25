from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QLayout, QWidget
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor

from ui.components.if_component_creator import IComponentCreator

LEVEL_COLORS = {
    0: QColor("#181C26"),
    1: QColor("#E8E8E8")
}

class TFGroupBox(QGroupBox, IComponentCreator):
    values_changed = pyqtSignal(dict)

    def __init__(self, title, layout_type=QVBoxLayout, level: int = 0, radius: int = 5, parent=None):
        QGroupBox.__init__(self, title, parent)
        IComponentCreator.__init__(self)

        if not issubclass(layout_type, QLayout):
            raise TypeError(f"Invalid layout_type: {layout_type}. Expected a subclass of QLayout.")
        
        self.parent = parent
        self.level = level
        self.radius = radius

        self.layout = layout_type(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)

        self._setup_content()

    def _set_background_color(self) -> None:
        color = LEVEL_COLORS.get(self.level, LEVEL_COLORS[0])
        self.setStyleSheet(f"background-color: {color.name()}; border-radius: {self.radius}px")

    def _setup_ui(self, layout_type: type[QLayout]) -> None:
        self.main_layout = layout_type(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.main_layout)

    def _setup_content(self):
        pass

    def add_child(self, name: str, child: QWidget) -> None:
        self._register_component(name, child)
        self.layout.addWidget(child)
