from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional

class TFCheckWithLabel(QWidget):
    value_changed = pyqtSignal(bool)
    
    @property
    def label_font(self):
        font = QFont("Inconsolata", 10)
        font.setWeight(QFont.Weight.Normal)
        return font
        
    def __init__(self, label_text: str = "", checked: bool = False, 
                 height: int = 24, spacing: int = 6,
                 custom_font: Optional[QFont] = None,
                 label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                 object_name: Optional[str] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui(label_text, checked, height, spacing,
                      custom_font, label_alignment, object_name)

    def _setup_ui(self, label_text: str, checked: bool, height: int, spacing: int,
                 custom_font: Optional[QFont], label_alignment: Qt.AlignmentFlag,
                 object_name: Optional[str]) -> None:
        self.setFixedHeight(height)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 0, 2, 0)
        self.layout.setSpacing(spacing)

        self.check = QCheckBox()
        if object_name:
            self.check.setObjectName(object_name)
            
        self.label = QLabel(label_text)
        self.label.setFont(custom_font if custom_font else self.label_font)
        self.label.setAlignment(label_alignment)
        
        self.layout.addWidget(self.check)
        self.layout.addWidget(self.label)
        self.layout.addStretch()
        
        self.check.setChecked(checked)
        self.check.stateChanged.connect(self._on_value_changed)
        
        self.label.mousePressEvent = self._on_label_clicked

    def _on_value_changed(self, state: int) -> None:
        self.value_changed.emit(bool(state))

    def _on_label_clicked(self, event) -> None:
        self.check.setChecked(not self.check.isChecked())

    def get_value(self) -> bool:
        return self.check.isChecked()

    def set_value(self, checked: bool) -> None:
        self.check.setChecked(checked)

    def set_label(self, text: str) -> None:
        self.label.setText(text)

    def set_font(self, font: QFont) -> None:
        self.label.setFont(font)
