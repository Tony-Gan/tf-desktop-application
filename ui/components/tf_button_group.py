from PyQt6.QtWidgets import QHBoxLayout, QLayout
from PyQt6.QtCore import pyqtSignal

from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_frame import TFBaseFrame


class TFButtonGroup(TFBaseFrame):
    values_changed = pyqtSignal(dict)

    def __init__(self,
                 allow_multiple: bool = False,
                 layout_type: type[QLayout] = QHBoxLayout,
                 level: int = 1,
                 parent=None):
        super().__init__(layout_type=layout_type, level=level, parent=parent)
        self.allow_multiple = allow_multiple
        self.buttons = {}

    def add_button(self,
                   name: str,
                   text: str,
                   width: int = 100,
                   height: int = None,
                   font_family: str = "Noto Serif SC Light",
                   font_size: int = 10,
                   tooltip: str = "",
                   border_radius: int = 15,
                   level: int = 1,
                   icon_path: str = None,
                   on_clicked=None) -> TFBaseButton:
        button = TFBaseButton(
            text=text,
            parent=self,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            tooltip=tooltip,
            border_radius=border_radius,
            level=level,
            icon_path=icon_path,
            on_clicked=on_clicked,
            checkable=True
        )
        self.buttons[name] = button
        self._register_component(name, button)
        button.toggled.connect(lambda checked, btn_name=name: self._on_button_toggled(btn_name, checked))
        self.main_layout.addWidget(button)
        return button

    def _on_button_toggled(self, button_name: str, checked: bool):
        if checked and not self.allow_multiple:
            for name, btn in self.buttons.items():
                if name != button_name and btn.isChecked():
                    btn.setChecked(False)
        self.values_changed.emit(self.get_values())

    def get_values(self) -> dict:
        return {name: btn.isChecked() for name, btn in self.buttons.items()}

    @property
    def states(self) -> dict:
        return self.get_values()
