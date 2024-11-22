from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QLayout, QWidget
from PyQt6.QtCore import pyqtSignal

from ui.components.component_creator_mixin import ComponentCreatorMixin


class TFGroupBox(QGroupBox, ComponentCreatorMixin):
    values_changed = pyqtSignal(dict)

    def __init__(self, title, layout_type=QVBoxLayout, object_name='section_frame', parent=None):
        QGroupBox.__init__(self, title, parent)
        ComponentCreatorMixin.__init__(self)

        if not issubclass(layout_type, QLayout):
            raise TypeError(f"Invalid layout_type: {layout_type}. Expected a subclass of QLayout.")

        self.setObjectName(object_name)
        self.layout = layout_type(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)

        self._setup_content()

    def _setup_content(self):
        pass

    def add_child(self, name: str, child: QWidget) -> None:
        self._register_component(name, child)
        self.layout.addWidget(child)
