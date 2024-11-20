from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QLayout


class TFGroupBox(QGroupBox):
    def __init__(self, title, layout_type=QVBoxLayout, object_name='section_frame', parent=None):
        super().__init__(title, parent)
        if not issubclass(layout_type, QLayout):
            raise TypeError(f"Invalid layout_type: {layout_type}. Expected a subclass of QLayout.")

        self.parent = parent
        self.setObjectName(object_name)

        self.layout = layout_type(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self._setup_content()

    def _setup_content(self):
        raise NotImplementedError("Subclasses must implement the _setup_content() method.")
