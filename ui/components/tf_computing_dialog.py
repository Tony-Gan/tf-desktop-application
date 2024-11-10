from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QFrame, QLabel, QLineEdit, QCheckBox, QScrollArea, QWidget)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QFont, QRegularExpressionValidator

from ui.components.tf_message_box import TFMessageBox
from ui.components.tf_separator import TFSeparator
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_number_receiver import TFNumberReceiver
from utils.validator.tf_validator import TFValidator

class TFComputingDialog(QDialog):
    """
    A base dialog class for input validation and computation tasks.

    This class provides a standardized framework for creating dialogs that collect,
    validate, and process user input. It includes standard UI components and a
    validation system for ensuring data correctness before processing.

    Args:
        title (str): Title of the dialog window.
        parent (QWidget, optional): Parent widget. Defaults to None.

    Attributes:
        validator (TFValidator): Validator instance for input validation.
        _result: Processed result after successful validation.

    Example:
        >>> class MyComputingDialog(TFComputingDialog):
        ...     def setup_validation_rules(self):
        ...         self.validator.add_rule('field1', 
        ...             TFValidationRule(type_=int, required=True))
        ...
        ...     def get_field_values(self):
        ...         return {'field1': self.field1_input.text()}
        ...
        ...     def process_validated_data(self, data):
        ...         return data['field1'] * 2

    Notes:
        Subclasses must implement:
        - setup_validation_rules(): Define validation rules for input fields
        - get_field_values(): Collect current values from UI fields
        - process_validated_data(): Process validated data to produce result
        - setup_content(): Set up dialog-specific UI components
    """
    DEFAULT_FONT_FAMILY = "Inconsolata"
    DEFAULT_FONT_SIZE = 10
    TITLE_FONT_SIZE = 11
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        self._result = None
        self.validator = TFValidator()
        self.setup_ui()
        
    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        self.content_frame = QFrame()
        self.content_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.content_frame.setObjectName("content_frame")
        self.main_layout.addWidget(self.content_frame)
        
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
        """
        Create a font with standard dialog settings.

        Args:
            size (int, optional): Font size in points. Defaults to DEFAULT_FONT_SIZE.
            bold (bool, optional): Whether to make font bold. Defaults to False.

        Returns:
            QFont: Configured font instance.
        """
        size = size or self.DEFAULT_FONT_SIZE
        font = QFont(self.DEFAULT_FONT_FAMILY, size)
        if bold:
            font.setWeight(QFont.Weight.Bold)
        return font

    def create_label(self, text: str, bold=False, fixed_width=None) -> QLabel:
        """
        Create a standardized label with consistent styling.

        Args:
            text (str): Label text.
            bold (bool, optional): Whether to use bold font. Defaults to False.
            fixed_width (int, optional): Fixed width in pixels. Defaults to None.

        Returns:
            QLabel: Configured label instance.
        """
        label = QLabel(text)
        label.setFont(self.create_font(bold=bold))
        if fixed_width is not None:
            label.setFixedWidth(fixed_width)
        return label

    def create_value_entry(self, label_text: str, number_only=False, allow_decimal=False, label_size=120, value_size=200) -> TFValueEntry:
        """
        Create a standardized value entry field with label.

        Args:
            label_text (str): Label text for the entry field.
            number_only (bool): Whether to restrict input to numbers only.
            allow_decimal (bool): Whether to allow decimal numbers.
            label_size (int): Width of the label in pixels.
            value_size (int): Width of the value field in pixels.

        Returns:
            TFValueEntry: Configured value entry instance.
        """
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

    def create_number_receiver(self, allow_decimal=False, allow_negative=False) -> TFNumberReceiver:
        """
        Create a standardized number input field with validation.

        Creates a specialized input field that only accepts numeric values with
        configurable decimal and negative number support.

        Args:
            allow_decimal (bool, optional): Whether to allow decimal numbers. Defaults to False.
            allow_negative (bool, optional): Whether to allow negative numbers. Defaults to False.

        Returns:
            TFNumberReceiver: Configured number input field instance.
        """
        return TFNumberReceiver(
            text="",
            alignment=Qt.AlignmentFlag.AlignLeft,
            font=self.create_font(),
            allow_decimal=allow_decimal,
            allow_negative=allow_negative
        )

    def create_text_input(self, validator_pattern=None) -> QLineEdit:
        """
        Create a standardized text input field with optional validation.
        
        Creates a text input field with consistent styling and optional
        regular expression validation.

        Args:
            validator_pattern (str, optional): Regular expression pattern for input validation.
                If provided, only input matching this pattern will be accepted.

        Returns:
            QLineEdit: Configured text input field instance.
        """
        text_input = QLineEdit()
        text_input.setFont(self.create_font())
        if validator_pattern:
            text_input.setValidator(
                QRegularExpressionValidator(QRegularExpression(validator_pattern))
            )
        return text_input

    def create_checkbox(self, text: str) -> QCheckBox:
        """
        Create a standardized checkbox with consistent styling.
        
        Creates a checkbox with the specified text and standard font settings.

        Args:
            text (str): Label text to display next to the checkbox.

        Returns:
            QCheckBox: Configured checkbox instance.
        """
        checkbox = QCheckBox(text)
        checkbox.setFont(self.create_font())
        return checkbox

    def create_scroll_area(self) -> tuple[QScrollArea, QWidget, QVBoxLayout]:
        """
        Create a standardized scroll area with container widget and layout.
        
        Creates a scroll area setup with standard settings and a contained widget
        with vertical layout. Useful for dialogs with potentially overflowing content.

        Returns:
            tuple[QScrollArea, QWidget, QVBoxLayout]: A tuple containing:
                - QScrollArea: The configured scroll area
                - QWidget: The container widget inside the scroll area
                - QVBoxLayout: The vertical layout of the container widget

        Notes:
            - The scroll area is configured to only show vertical scrollbar when needed
            - The container widget uses a vertical layout with 10px spacing
            - The scroll area has no frame for a cleaner appearance
        """
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
        """
        Set fixed size for the dialog window.
        
        Prevents the dialog from being resized by the user by setting both width
        and height as fixed dimensions.

        Args:
            width (int): Fixed width in pixels for the dialog.
            height (int): Fixed height in pixels for the dialog.
        """
        self.setFixedSize(width, height)

    def setup_validation_rules(self) -> None:
        """
        Define validation rules for dialog input fields.
        
        This method should be implemented by subclasses to set up field validation
        rules using the dialog's validator instance. Each input field that requires
        validation should have its rules defined here.

        Example:
            >>> def setup_validation_rules(self):
            ...     self.validator.add_rule('age', 
            ...         TFValidationRule(type_=int, min_val=0, max_val=120))
            ...     self.validator.add_rule('name',
            ...         TFValidationRule(required=True, min_val=2))

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
        """
        raise NotImplementedError("Subclasses must implement setup_validation_rules()")

    def get_field_values(self) -> dict:
        """
        Collect current values from all input fields.
        
        This method should be implemented by subclasses to gather values from
        all input fields in the dialog. The returned dictionary should use field
        names that match the validation rules defined in setup_validation_rules().

        Returns:
            dict: Dictionary mapping field names to their current values.

        Example:
            >>> def get_field_values(self):
            ...     return {
            ...         'name': self.name_input.text(),
            ...         'age': self.age_input.value(),
            ...         'active': self.active_checkbox.isChecked()
            ...     }

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
        """
        raise NotImplementedError("Subclasses must implement get_field_values()")

    def process_validated_data(self, data: dict) -> any:
        """
        Process the validated input data to produce a result.
        
        This method should be implemented by subclasses to perform the actual
        computation or processing on the validated input data. It is only called
        if all validation rules pass.

        Args:
            data (dict): Dictionary of field names and their validated values.
                This is the same dictionary returned by get_field_values() after
                successful validation.

        Returns:
            any: The processed result in any form required by the specific dialog.
                This value will be stored as the dialog's result.

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
            Exception: Any exception raised during processing will be caught and
                displayed to the user.

        Example:
            >>> def process_validated_data(self, data):
            ...     return {
            ...         'full_name': f"{data['first_name']} {data['last_name']}",
            ...         'age_in_months': data['age'] * 12
            ...     }
        """
        raise NotImplementedError("Subclasses must implement process_validated_data()")

    def setup_content(self) -> None:
        """
        Set up the dialog-specific UI components and layout.
        
        This method should be implemented by subclasses to create and arrange all
        UI components specific to the dialog. All widgets should be added to the
        dialog's content_frame.

        Example:
            >>> def setup_content(self):
            ...     layout = QVBoxLayout(self.content_frame)
            ...     self.name_input = self.create_value_entry("Name:")
            ...     self.age_input = self.create_number_receiver()
            ...     layout.addWidget(self.name_input)
            ...     layout.addWidget(self.age_input)

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
        """
        raise NotImplementedError("Subclasses must implement setup_content()")

    def compute_result(self) -> tuple[bool, any]:
        """
        Validate input and compute result.

        Collects field values, validates them against rules, and processes
        the validated data to produce a result.

        Returns:
            tuple[bool, any]: (success, result) where result is either the computed
                value or error message string if validation failed.
        """
        data = self.get_field_values()
        errors = []
        
        for field, value in data.items():
            is_valid, message = self.validator.validate_field(field, value)
            if not is_valid:
                errors.append(message)
                
        if errors:
            return False, "\n".join(errors)
            
        try:
            result = self.process_validated_data(data)
            return True, result
        except Exception as e:
            return False, str(e)

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
        """
        Static method to create dialog and get result.

        Creates and shows dialog modally, returning the result if accepted.

        Args:
            parent: Parent widget for the dialog.
            **kwargs: Additional arguments passed to dialog constructor.

        Returns:
            tuple[bool, any]: (success, result) where success indicates if dialog
                was accepted and result contains the computed value if successful.
        """
        dialog = cls(parent, **kwargs)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return True, dialog.get_result()
        return False, None
