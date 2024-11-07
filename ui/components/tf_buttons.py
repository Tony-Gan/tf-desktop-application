from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont

from settings.general import GENERAL_BUTTON_HEIGHT

class TFPushButton(QPushButton):
    """
    A custom push button with standardized styling for the TF application.

    This base button class provides consistent font, height, and styling across
    the application. It serves as the foundation for specialized button types.

    Args:
        text (str): Button text label.
        parent (QWidget, optional): Parent widget. Defaults to None.
        callback (callable, optional): Function to call when clicked. Defaults to None.
        object_name (str, optional): Qt object name for styling. Defaults to None.

    Example:
        >>> # Creating a basic button with callback
        >>> def on_click():
        ...     print("Button clicked!")
        >>> button = TFPushButton(
        ...     text="Click Me",
        ...     parent=widget,
        ...     callback=on_click,
        ...     object_name="custom_button"
        ... )
    """
    def __init__(self, text, parent=None, callback=None, object_name=None):
        super().__init__(text, parent)
        
        self.setFont(QFont("Montserrat", 10))
        self.setFixedHeight(GENERAL_BUTTON_HEIGHT)
        
        if object_name:
            self.setObjectName(object_name)
            
        if callback:
            self.clicked.connect(callback)

class TFConfirmButton(TFPushButton):
    """
    A standardized confirmation button.

    Pre-configured button with "Confirm" text and standard styling for
    confirmation actions.

    Args:
        parent (QWidget, optional): Parent widget. Defaults to None.
        callback (callable, optional): Function to call when clicked. Defaults to None.

    Example:
        >>> confirm_btn = TFConfirmButton(
        ...     parent=dialog,
        ...     callback=lambda: dialog.accept()
        ... )
    """
    def __init__(self, parent=None, callback=None):
        super().__init__(
            text="Confirm",
            parent=parent,
            callback=callback,
            object_name="confirm_button"
        )

class TFResetButton(TFPushButton):
    """
    A standardized reset button.

    Pre-configured button with "Reset" text and standard styling for
    reset actions.

    Args:
        parent (QWidget, optional): Parent widget. Defaults to None.
        callback (callable, optional): Function to call when clicked. Defaults to None.

    Example:
        >>> reset_btn = TFResetButton(
        ...     parent=form,
        ...     callback=lambda: form.reset_fields()
        ... )
    """
    def __init__(self, parent=None, callback=None):
        super().__init__(
            text="Reset",
            parent=parent,
            callback=callback,
            object_name="reset_button"
        )
