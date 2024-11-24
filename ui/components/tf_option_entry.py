from typing import Optional, List
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QFrame, QLineEdit, QCompleter, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QEvent
from ui.components.tf_font import LABEL_FONT, TEXT_FONT, Merriweather
from ui.tf_application import TFApplication

class TFOptionEntry(QFrame):
    value_changed = pyqtSignal(str)

    def __init__(
            self,
            label_text: str = "",
            options: List[str] = None,
            current_value: str = "",
            label_size: int = 80,
            value_size: int = 36,
            height: int = 24,
            extra_value_width: Optional[int] = None,
            enable_filter: bool = False,
            parent: Optional[QFrame] = None
    ) -> None:
        super().__init__(parent)

        self.extra_value_width = extra_value_width
        self.options = options or []
        self._setup_ui(
            label_text, current_value,
            label_size, value_size, height, enable_filter
        )
        self.dropdown = TFDropDownFrame(self.options, self)
        self.dropdown.option_selected.connect(self.on_option_selected)
        self.dropdown.hide()

        TFApplication.instance().installEventFilter(self)

    def _setup_ui(
            self,
            label_text: str,
            current_value: str,
            label_size: int,
            value_size: int,
            height: int,
            enable_filter: bool
    ) -> None:
        self.setFixedHeight(height)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label = QLabel(label_text)
        self.label.setFont(LABEL_FONT)
        self.label.setFixedWidth(label_size)
        self.label.setFixedHeight(height)

        self.value_field = QLineEdit()
        self.value_field.setFont(TEXT_FONT)
        self.value_field.setText(current_value)
        self.value_field.setFixedHeight(height)
        self.value_field.setFixedWidth(value_size)
        self.value_field.setReadOnly(True)
        self.value_field.mousePressEvent = self.show_dropdown

        if enable_filter:
            self._setup_filter()

        layout.addWidget(self.label)
        layout.addSpacing(2)
        layout.addWidget(self.value_field)
        layout.addStretch()

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            if self.dropdown.isVisible():
                global_pos = event.globalPosition().toPoint()
                if not self.dropdown.geometry().contains(self.dropdown.mapFromGlobal(global_pos)):
                    self.dropdown.hide()
        return super().eventFilter(obj, event)

    def show_dropdown(self, event) -> None:
        if self.dropdown.isVisible():
            self.dropdown.hide()
            return

        if self.options:
            self.dropdown.update_options(self.options)
            
            if self.extra_value_width:
                self.dropdown.setFixedWidth(self.value_field.width() + self.extra_value_width)
            else:
                self.dropdown.setFixedWidth(self.value_field.width())
                
            self.dropdown.updateGeometry()
            target_height = self.dropdown.sizeHint().height()
            
            self.dropdown.setFixedHeight(0)
            pos = self.value_field.mapToGlobal(self.value_field.rect().bottomLeft())
            self.dropdown.move(pos)
            self.dropdown.setVisible(True)
            
            self.height_animation = QPropertyAnimation(self.dropdown, b"maximumHeight", self)
            self.height_animation.setDuration(150)
            self.height_animation.setStartValue(0)
            self.height_animation.setEndValue(target_height)
            self.height_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            self.min_height_animation = QPropertyAnimation(self.dropdown, b"minimumHeight", self)
            self.min_height_animation.setDuration(150)
            self.min_height_animation.setStartValue(0)
            self.min_height_animation.setEndValue(target_height)
            self.min_height_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            self.min_height_animation.start()
            self.height_animation.start()
            
            self.dropdown.raise_()

    def on_option_selected(self, value: str) -> None:
        self.value_field.setText(value)
        self.value_changed.emit(value)
        self.dropdown.hide()

    def _setup_filter(self) -> None:
        completer = QCompleter(self.options, self.value_field)
        completer.setCompletionRole(Qt.ItemDataRole.DisplayRole)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.value_field.setCompleter(completer)

    def update_options(self, options: List[str]) -> None:
        self.options = options
        self.dropdown.update_options(options)

    def get_value(self) -> str:
        return self.value_field.text()
    

class OptionItem(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.text = text
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        label = QLabel(self.text)
        label.setFont(TEXT_FONT)
        layout.addWidget(label)
        
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.text)


class TFDropDownFrame(QFrame):
    option_selected = pyqtSignal(str)

    def __init__(self, options: List[str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        for option in options:
            self.add_option(option)

    def add_option(self, text: str):
        item = OptionItem(text, self)
        item.clicked.connect(self.option_selected)
        self.layout.addWidget(item)

    def update_options(self, options: List[str]) -> None:
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        for option in options:
            self.add_option(option)
