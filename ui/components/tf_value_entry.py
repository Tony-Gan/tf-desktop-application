from typing import Optional, Callable, Union

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QMouseEvent

from ui.components.tf_number_receiver import TFNumberReceiver

class TFValueEntry(QWidget):
    """
    A customizable labeled input field widget that supports various input types and styles.
    
    This widget combines a label and an input field (either a standard text field or a
    number-only field) with configurable appearance and behavior. It supports special
    edit triggers and value change notifications.

    Signals:
        value_changed(str): 
            Emitted when the input value changes.
            Contains the new value as string.

    Args:
        label_text (str, optional): Text for the label. Defaults to "".
        value_text (str, optional): Initial value for the input field. Defaults to "".
        label_size (int, optional): Width of the label in pixels. Defaults to 80.
        value_size (int, optional): Width of the input field in pixels. Defaults to 36.
        height (int, optional): Height of the entire widget in pixels. Defaults to 24.
        custom_label_font (QFont, optional): Custom font for the label. If None, uses default label font.
        custom_edit_font (QFont, optional): Custom font for the input field. If None, uses default edit font.
        alignment (Qt.AlignmentFlag, optional): Text alignment for the input field. 
            Defaults to Qt.AlignmentFlag.AlignCenter.
        label_alignment (Qt.AlignmentFlag, optional): Text alignment for the label.
            Defaults to Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft.
        object_name (str, optional): Object name for styling purposes. Defaults to None.
        number_only (bool, optional): Whether to restrict input to numbers only. Defaults to False.
        allow_decimal (bool, optional): Whether to allow decimal numbers when number_only is True. 
            Defaults to True.
        allow_negative (bool, optional): Whether to allow negative numbers when number_only is True.
            Defaults to False.
        special_edit (callable, optional): Callback function for special edit behavior when
            clicking the input field. Defaults to None.
        parent (QWidget, optional): Parent widget. Defaults to None.

    Attributes:
        label (QLabel): The label widget.
        value_field (Union[QLineEdit, TFNumberReceiver]): The input field widget.
        special_edit (callable): Custom edit callback function.
    
    Example:
        >>> # Create a basic text entry
        >>> entry = TFValueEntry(
        ...     label_text="Name:",
        ...     value_text="John Doe",
        ...     label_size=100,
        ...     value_size=200
        ... )
        >>> 
        >>> # Create a number-only entry with custom edit behavior
        >>> def custom_edit():
        ...     dialog = CustomNumberDialog()
        ...     if dialog.exec() == QDialog.DialogCode.Accepted:
        ...         return dialog.get_value()
        ...     return None
        >>> 
        >>> number_entry = TFValueEntry(
        ...     label_text="Amount:",
        ...     number_only=True,
        ...     allow_decimal=True,
        ...     special_edit=custom_edit
        ... )
    """
    value_changed = pyqtSignal(str)
    
    @property
    def label_font(self):
        """
        Default font for the label.

        Returns:
            QFont: A semi-bold Inconsolata font, size 10.
        """
        font = QFont("Inconsolata", 10)
        font.setWeight(QFont.Weight.DemiBold)
        return font

    @property
    def edit_font(self):
        """
        Default font for the input field.

        Returns:
            QFont: A normal weight Inconsolata font, size 10.
        """
        font = QFont("Inconsolata", 10)
        font.setWeight(QFont.Weight.Normal)
        return font

    def __init__(self, label_text: str = "", value_text: str = "", label_size: int = 80, value_size: int = 36, height: int = 24,
                custom_label_font: Optional[QFont] = None, custom_edit_font: Optional[QFont] = None, 
                alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter,
                label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                object_name: Optional[str] = None, 
                number_only: bool = False,
                allow_decimal: bool = True,
                allow_negative: bool = False,
                special_edit: Optional[Callable[[], Optional[Union[str, int, float]]]] = None,
                parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.special_edit = special_edit
        self._setup_ui(label_text, value_text, label_size, value_size, height,
                     custom_label_font, custom_edit_font, alignment, label_alignment,
                     object_name, number_only, allow_decimal, allow_negative)

    def _setup_ui(self, label_text: str, value_text: str, label_size: int, value_size: int, height: int,
                custom_label_font: Optional[QFont], custom_edit_font: Optional[QFont], 
                alignment: Qt.AlignmentFlag, label_alignment: Qt.AlignmentFlag,
                object_name: Optional[str], number_only: bool, allow_decimal: bool, allow_negative: bool) -> None:
        self.setFixedHeight(height)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 0, 2, 0)
        self.layout.setSpacing(2)

        self.label = QLabel(label_text)
        self.label.setFont(custom_label_font if custom_label_font else self.label_font)
        self.label.setFixedWidth(label_size)
        self.label.setAlignment(label_alignment)

        if number_only:
            self.value_field = TFNumberReceiver(
                text=str(value_text),
                alignment=alignment,
                font=custom_edit_font if custom_edit_font else self.edit_font,
                allow_decimal=allow_decimal,
                allow_negative=allow_negative,
                parent=self
            )
        else:
            self.value_field = QLineEdit()
            self.value_field.setFont(custom_edit_font if custom_edit_font else self.edit_font)
            self.value_field.setAlignment(alignment)
            self.value_field.setText(str(value_text))

        if object_name:
            self.value_field.setObjectName(object_name)
        self.value_field.setFixedWidth(value_size)
        self.value_field.setEnabled(False)
        self.value_field.setStyleSheet("QLineEdit { padding: 1px; }")
        
        self.value_field.textChanged.connect(self._on_value_changed)
        if self.special_edit:
            self.value_field.mousePressEvent = self._handle_special_edit

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value_field)
        self.layout.addStretch()

    def _handle_special_edit(self, event: QMouseEvent) -> None:
        if self.value_field.isEnabled() and self.special_edit:
            result = self.special_edit()
            if result is not None:
                self.value_field.setText(str(result))
        elif hasattr(self.value_field, 'mousePressEvent'):
            super(type(self.value_field), self.value_field).mousePressEvent(event)

    def _on_value_changed(self, text: str) -> None:
        self.value_changed.emit(text)

    def get_value(self) -> str:
        """
        Get the current text value of the input field.

        Returns:
            str: Current text in the input field.
        """
        return self.value_field.text()

    def set_value(self, value: Union[str, int, float]) -> None:
        """
        Set the text value of the input field.

        Args:
            value: Value to set (will be converted to string).
        """
        self.value_field.setText(str(value))

    def set_label(self, text: str) -> None:
        """
        Set the text of the label.

        Args:
            text (str): New label text.
        """
        self.label.setText(text)

    def set_label_font(self, font: QFont) -> None:
        """
        Set the font for the label.

        Args:
            font (QFont): New font for the label.
        """
        self.label.setFont(font)

    def set_edit_font(self, font: QFont) -> None:
        """
        Set the font for the input field.

        Args:
            font (QFont): New font for the input field.
        """
        self.value_field.setFont(font)

    def set_special_edit(self, callback: Optional[Callable[[], Optional[Union[str, int, float]]]]) -> None:
        """
        Set or update the special edit callback.

        The special edit callback is triggered when the user clicks on the input field.
        This is useful for implementing custom edit dialogs or behaviors.

        Args:
            callback (callable): Function to call when input field is clicked.
                Should return the new value to set, or None to keep current value.
        """
        self.special_edit = callback
        if callback:
            self.value_field.mousePressEvent = self._handle_special_edit
        else:
            self.value_field.mousePressEvent = super(type(self.value_field), self.value_field).mousePressEvent
