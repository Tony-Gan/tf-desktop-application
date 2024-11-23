from PyQt6.QtWidgets import QVBoxLayout, QFrame, QLayout
from PyQt6.QtCore import pyqtSignal

from ui.components.component_creator_mixin import ComponentCreatorMixin

DEBOUNCE_INTERVAL = 500


class TFBaseFrame(QFrame, ComponentCreatorMixin):
    values_changed = pyqtSignal(dict)

    def __init__(self, layout_type: type[QLayout] = QVBoxLayout, parent=None):
        QFrame.__init__(self, parent)
        ComponentCreatorMixin.__init__(self)

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
