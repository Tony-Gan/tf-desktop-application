from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional

class TFCheckWithLabel(QWidget):
    """
    A customizable checkbox widget with an associated label that supports click interactions.

    This widget combines a checkbox and a label with configurable appearance and behavior.
    The label is clickable and toggles the checkbox state. The widget supports value change
    notifications through signals.

    Signals:
        value_changed(bool):
            Emitted when the checkbox state changes.
            Contains the new state as boolean.

    Args:
        label_text (str, optional): Text for the label. Defaults to "".
        checked (bool, optional): Initial state of the checkbox. Defaults to False.
        height (int, optional): Height of the entire widget in pixels. Defaults to 24.
        spacing (int, optional): Spacing between checkbox and label in pixels. Defaults to 6.
        custom_font (QFont, optional): Custom font for the label. If None, uses default label font.
        label_alignment (Qt.AlignmentFlag, optional): Text alignment for the label.
            Defaults to Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft.
        object_name (str, optional): Object name for styling purposes. Defaults to None.
        parent (QWidget, optional): Parent widget. Defaults to None.

    Attributes:
        check (QCheckBox): The checkbox widget.
        label (QLabel): The label widget.
        label_font (QFont): The default font used for the label.

    Example:
        >>> # Create a basic checkbox with label
        >>> checkbox = TFCheckWithLabel(
        ...     label_text="Enable feature",
        ...     checked=True,
        ...     height=30,
        ...     spacing=8
        ... )
        >>>
        >>> # Create a checkbox with custom font and styling
        >>> custom_font = QFont("Arial", 12, QFont.Weight.Bold)
        >>> styled_checkbox = TFCheckWithLabel(
        ...     label_text="Advanced options",
        ...     custom_font=custom_font,
        ...     object_name="advanced-checkbox"
        ... )
        >>>
        >>> # Connect to value changed signal
        >>> def on_state_changed(state):
        ...     print(f"Checkbox state changed to: {state}")
        >>>
        >>> checkbox.value_changed.connect(on_state_changed)
    """
    value_changed = pyqtSignal(bool)
    
    @property
    def label_font(self):
        """
        Default font for the label.

        Returns:
            QFont: A normal weight Inconsolata font, size 10.
        """
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
        """
        Get the current state of the checkbox.

        Returns:
            bool: True if checked, False otherwise.
        """
        return self.check.isChecked()

    def set_value(self, checked: bool) -> None:
        """
        Set the state of the checkbox.

        Args:
            checked (bool): New state for the checkbox.
        """
        self.check.setChecked(checked)

    def set_label(self, text: str) -> None:
        """
        Set the text of the label.

        Args:
            text (str): New label text.
        """
        self.label.setText(text)

    def set_font(self, font: QFont) -> None:
        """
        Set the font for the label.

        Args:
            font (QFont): New font for the label.
        """
        self.label.setFont(font)
