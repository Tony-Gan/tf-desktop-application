from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFrame, QLabel, QLineEdit, QCheckBox, QScrollArea, QWidget)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QFont, QRegularExpressionValidator

from ui.components.tf_message_box import TFMessageBox
from ui.components.tf_separator import TFSeparator
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_number_receiver import TFNumberReceiver

class TFComputingDialog(QDialog):
    DEFAULT_FONT_FAMILY = "Inconsolata"
    DEFAULT_FONT_SIZE = 10
    TITLE_FONT_SIZE = 11
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        self._result = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the basic UI structure."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        self.content_frame = QFrame()
        self.content_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.content_frame.setObjectName("content_frame")
        self.main_layout.addWidget(self.content_frame)
        
        self.main_layout.addWidget(TFSeparator.horizontal())
        
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.setFont(self.create_font())
        self.ok_button.clicked.connect(self._on_ok_clicked)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFont(self.create_font())
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        self.main_layout.addLayout(button_layout)

    def create_font(self, size=None, bold=False) -> QFont:
        """Create a font with standard settings."""
        size = size or self.DEFAULT_FONT_SIZE
        font = QFont(self.DEFAULT_FONT_FAMILY, size)
        if bold:
            font.setWeight(QFont.Weight.Bold)
        return font

    def create_label(self, text: str, bold=False, fixed_width=None) -> QLabel:
        """Create a standardized label."""
        label = QLabel(text)
        label.setFont(self.create_font(bold=bold))
        if fixed_width is not None:
            label.setFixedWidth(fixed_width)
        return label

    def create_value_entry(self, label_text: str, number_only=False, 
                          allow_decimal=False, label_size=120, 
                          value_size=200) -> TFValueEntry:
        """Create a standardized value entry field."""
        entry = TFValueEntry(
            label_text=label_text,
            value_text="",
            label_size=label_size,
            value_size=value_size,
            custom_label_font=self.create_font(bold=True),
            custom_edit_font=self.create_font(),
            alignment=Qt.AlignmentFlag.AlignLeft,
            number_only=number_only,
            allow_decimal=allow_decimal
        )
        entry.value_field.setEnabled(True)
        return entry

    def create_number_receiver(self, allow_decimal=False, 
                             allow_negative=False) -> TFNumberReceiver:
        """Create a standardized number input field."""
        return TFNumberReceiver(
            text="",
            alignment=Qt.AlignmentFlag.AlignLeft,
            font=self.create_font(),
            allow_decimal=allow_decimal,
            allow_negative=allow_negative
        )

    def create_text_input(self, validator_pattern=None) -> QLineEdit:
        """Create a standardized text input field."""
        text_input = QLineEdit()
        text_input.setFont(self.create_font())
        if validator_pattern:
            text_input.setValidator(
                QRegularExpressionValidator(QRegularExpression(validator_pattern))
            )
        return text_input

    def create_checkbox(self, text: str) -> QCheckBox:
        """Create a standardized checkbox."""
        checkbox = QCheckBox(text)
        checkbox.setFont(self.create_font())
        return checkbox

    def create_scroll_area(self) -> tuple[QScrollArea, QWidget, QVBoxLayout]:
        """Create a standardized scroll area with container widget and layout."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(10)
        
        scroll_area.setWidget(container)
        return scroll_area, container, container_layout

    def set_dialog_size(self, width: int, height: int):
        """Set fixed size for the dialog."""
        self.setFixedSize(width, height)

    # Validation methods
    def validate_not_empty(self, value: str, field_name: str) -> tuple[bool, str]:
        """Validate that a value is not empty."""
        if not value.strip():
            return False, f"Please enter {field_name}."
        return True, value.strip()

    def validate_number_range(self, value: str, min_val: int, max_val: int, 
                            field_name: str) -> tuple[bool, int]:
        """Validate that a number is within the specified range."""
        try:
            num_value = int(value)
            if min_val <= num_value <= max_val:
                return True, num_value
            return False, f"{field_name} must be between {min_val} and {max_val}."
        except ValueError:
            return False, f"Please enter a valid number for {field_name}."

    def setup_content(self) -> None:
        """Setup the content specific to this dialog."""
        raise NotImplementedError("Subclasses must implement setup_content()")

    def compute_result(self) -> tuple[bool, any]:
        """Compute and validate the dialog result."""
        raise NotImplementedError("Subclasses must implement compute_result()")

    def _on_ok_clicked(self):
        """Handle OK button click."""
        success, result = self.compute_result()
        if success:
            self._result = result
            self.accept()
        else:
            TFMessageBox.warning(self, "Invalid Input", result)

    def get_result(self) -> any:
        """Get the dialog result."""
        return self._result

    @classmethod
    def get_input(cls, parent, **kwargs) -> tuple[bool, any]:
        """Generic class method for getting input."""
        dialog = cls(parent, **kwargs)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return True, dialog.get_result()
        return False, None