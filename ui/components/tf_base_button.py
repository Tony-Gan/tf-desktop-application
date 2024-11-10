from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class TFBaseButton(QPushButton):
    """
    A customized base button class that provides consistent styling and behavior
    for buttons across the application.
    """
    def __init__(
        self,
        text: str,
        parent=None,
        width: int = 100,
        height: int = None,
        font_family: str = "Inconsolata SemiCondensed",
        font_size: int = 10,
        enabled: bool = True,
        checkable: bool = False,
        object_name: str = None,
        tooltip: str = None,
        on_clicked=None
    ):
        """
        Initialize a TFBaseButton.

        Args:
            text (str): Button text
            parent: Parent widget
            width (int): Fixed width of the button
            height (int): Fixed height of the button (optional)
            font_family (str): Font family to use
            font_size (int): Font size
            enabled (bool): Whether the button is enabled initially
            checkable (bool): Whether the button is checkable
            object_name (str): Object name for the button
            tooltip (str): Tooltip text for the button
            on_clicked: Callback function for click events
        """
        super().__init__(text, parent)
        
        # Set fixed size
        self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
            
        # Set font
        font = QFont(font_family)
        font.setPointSize(font_size)
        self.setFont(font)
        
        # Set properties
        self.setEnabled(enabled)
        self.setCheckable(checkable)
        
        if object_name:
            self.setObjectName(object_name)
            
        if tooltip:
            self.setToolTip(tooltip)
            
        if on_clicked:
            self.clicked.connect(on_clicked)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

class TFNextButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Inconsolata SemiCondensed",
        font_size: int = 10,
        on_clicked=None, 
        tooltip="Next step"
    ):
        super().__init__(
            "Next",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            object_name="next_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

class TFPreviousButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Inconsolata SemiCondensed",
        font_size: int = 10,
        on_clicked=None, 
        tooltip="Previous step"
    ):
        super().__init__(
            "Previous",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            object_name="previous_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

class TFBackButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Inconsolata SemiCondensed",
        font_size: int = 10,
        on_clicked=None, 
        tooltip="Go back"
    ):
        super().__init__(
            "Back",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            object_name="back_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

class TFConfirmButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Inconsolata SemiCondensed",
        font_size: int = 10,
        on_clicked=None, 
        tooltip="Confirm action"
    ):
        super().__init__(
            "Confirm",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            object_name="confirm_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

class TFResetButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Inconsolata SemiCondensed",
        font_size: int = 10,
        on_clicked=None, 
        tooltip="Reset to default"
    ):
        super().__init__(
            "Reset",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            object_name="reset_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

class TFCancelButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Inconsolata SemiCondensed",
        font_size: int = 10,
        on_clicked=None, 
        tooltip="Cancel action"
    ):
        super().__init__(
            "Cancel",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            object_name="cancel_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

class TFSubmitButton(TFBaseButton):
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Inconsolata SemiCondensed",
        font_size: int = 10,
        on_clicked=None, 
        tooltip="Submit form"
    ):
        super().__init__(
            "Submit",
            parent=parent,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            object_name="submit_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

