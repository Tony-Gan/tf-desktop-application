from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont, QColor, QPainter
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty

class TFBaseButton(QPushButton):
    """
    A customized base button class that provides consistent styling and behavior
    for buttons across the application.
    
    This class serves as the foundation for all application buttons, providing standard
    styling, sizing, font settings and interaction behaviors. It extends QPushButton
    with additional functionality like strong focus policy and simplified initialization.

    The button automatically applies the application's standard styling and can be
    further customized through stylesheet object names.

    Args:
        text (str): Text to display on the button
        parent (QWidget, optional): Parent widget. Defaults to None.
        width (int, optional): Fixed width in pixels. Defaults to 100.
        height (int, optional): Fixed height in pixels. If None, uses default height.
        font_family (str, optional): Font family name. Defaults to "Inconsolata SemiCondensed".
        font_size (int, optional): Font size in points. Defaults to 10.
        enabled (bool, optional): Initial enabled state. Defaults to True.
        checkable (bool, optional): Whether button can be toggled. Defaults to False.
        object_name (str, optional): Qt object name for styling. Defaults to None.
        tooltip (str, optional): Hover tooltip text. Defaults to None.
        on_clicked (callable, optional): Click event handler. Defaults to None.

    Attributes:
        clicked (Signal): Emitted when button is clicked.

    Note:
        All buttons in the application should inherit from this class to maintain
        consistent appearance and behavior. The class automatically sets strong
        focus policy for proper keyboard navigation.
    """
    def __init__(
        self,
        text: str,
        parent=None,
        width: int = 100,
        height: int = None,
        font_family: str = "Merriweather Light",
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

        self.setObjectName("TFBaseButton")
        
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

        if not enabled:
            self._bg_color = QColor("#4D4D4D")
            self._text_color = QColor("#808080")
        else:
            self._bg_color = QColor("#242831")
            self._text_color = QColor("#FFFFFF")
        
        self._bg_animation = QPropertyAnimation(self, b"backgroundColor", self)
        self._bg_animation.setDuration(200)
        
        self._text_animation = QPropertyAnimation(self, b"textColor", self)
        self._text_animation.setDuration(200)

    @pyqtProperty(QColor)
    def backgroundColor(self):
        return self._bg_color

    @backgroundColor.setter
    def backgroundColor(self, color):
        self._bg_color = color
        self.update()

    @pyqtProperty(QColor)
    def textColor(self):
        return self._text_color

    @textColor.setter
    def textColor(self, color):
        self._text_color = color
        self.update()

    def enterEvent(self, event):
        if not self.isEnabled():
            return super().enterEvent(event)
            
        self._bg_animation.stop()
        self._bg_animation.setStartValue(QColor("#242831"))
        self._bg_animation.setEndValue(QColor("#858585"))
        self._bg_animation.start()
        
        # 文字颜色动画
        self._text_animation.stop()
        self._text_animation.setStartValue(QColor("#FFFFFF"))
        self._text_animation.setEndValue(QColor("#FFFFFF"))
        self._text_animation.start()
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.isEnabled():
            return super().leaveEvent(event)
            
        self._bg_animation.stop()
        self._bg_animation.setStartValue(QColor("#858585"))
        self._bg_animation.setEndValue(QColor("#242831"))
        self._bg_animation.start()
        
        self._text_animation.stop()
        self._text_animation.setStartValue(QColor("#FFFFFF"))
        self._text_animation.setEndValue(QColor("#FFFFFF"))
        self._text_animation.start()
        
        super().leaveEvent(event)

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        if not enabled:
            self._bg_color = QColor("#4D4D4D")
            self._text_color = QColor("#808080")
        else:
            self._bg_color = QColor("#242831")
            self._text_color = QColor("#FFFFFF")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(self._bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)
        
        painter.setPen(self._text_color)
        painter.setFont(self.font())
        text_rect = self.rect()
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text())

    def disable_animations(self):
        self._bg_color = QColor("#4D4D4D")
        self._text_color = QColor("#808080")
        self.update()

class TFNextButton(TFBaseButton):
    """
    Standard "Next" button with predefined styling and behavior.
    
    A button typically used for navigating to the next step in a workflow or wizard.
    Uses default text "Next" and standard dimensions.

    Args:
        parent (QWidget, optional): Parent widget. Defaults to None.
        width (int, optional): Button width in pixels. Defaults to 100.
        height (int, optional): Button height in pixels. Defaults to 30.
        font_family (str, optional): Font family name. Defaults to "Inconsolata SemiCondensed".
        font_size (int, optional): Font size in points. Defaults to 10.
        on_clicked (callable, optional): Click event handler. Defaults to None.
        tooltip (str, optional): Custom tooltip text. Defaults to "Next step".
    """
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Merriweather Light",
        font_size: int = 10,
        enabled:bool = False,
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
            enabled=enabled,
            object_name="next_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFNextButton")

class TFPreviousButton(TFBaseButton):
    """
    Standard "Previous" button with predefined styling and behavior.
    
    A button typically used for navigating to the previous step in a workflow or wizard.
    Uses default text "Previous" and standard dimensions.

    Args:
        parent (QWidget, optional): Parent widget. Defaults to None.
        width (int, optional): Button width in pixels. Defaults to 100.
        height (int, optional): Button height in pixels. Defaults to 30.
        font_family (str, optional): Font family name. Defaults to "Inconsolata SemiCondensed".
        font_size (int, optional): Font size in points. Defaults to 10.
        on_clicked (callable, optional): Click event handler. Defaults to None.
        tooltip (str, optional): Custom tooltip text. Defaults to "Previous step".
    """
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Merriweather Light",
        font_size: int = 10,
        enabled:bool = True,
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
            enabled=enabled,
            object_name="previous_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFPreviousButton")

class TFBackButton(TFBaseButton):
    """
    Standard "Back" button with predefined styling and behavior.
    
    A button typically used for returning to a previous view or canceling a workflow.
    Uses default text "Back" and standard dimensions.

    Args:
        parent (QWidget, optional): Parent widget. Defaults to None.
        width (int, optional): Button width in pixels. Defaults to 100.
        height (int, optional): Button height in pixels. Defaults to 30.
        font_family (str, optional): Font family name. Defaults to "Inconsolata SemiCondensed".
        font_size (int, optional): Font size in points. Defaults to 10.
        on_clicked (callable, optional): Click event handler. Defaults to None.
        tooltip (str, optional): Custom tooltip text. Defaults to "Go back".
    """
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Merriweather Light",
        font_size: int = 10,
        enabled:bool = False,
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
            enabled=enabled,
            object_name="back_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFBackButton")

class TFConfirmButton(TFBaseButton):
    """
    Standard "Confirm" button with predefined styling and behavior.
    
    A button typically used for confirming actions or accepting changes.
    Uses default text "Confirm" and standard dimensions.

    Args:
        parent (QWidget, optional): Parent widget. Defaults to None.
        width (int, optional): Button width in pixels. Defaults to 100.
        height (int, optional): Button height in pixels. Defaults to 30.
        font_family (str, optional): Font family name. Defaults to "Inconsolata SemiCondensed".
        font_size (int, optional): Font size in points. Defaults to 10.
        on_clicked (callable, optional): Click event handler. Defaults to None.
        tooltip (str, optional): Custom tooltip text. Defaults to "Confirm action".
    """
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Merriweather Light",
        font_size: int = 10,
        enabled:bool = False,
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
            enabled=enabled,
            object_name="confirm_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFConfirmButton")

class TFResetButton(TFBaseButton):
    """
    Standard "Reset" button with predefined styling and behavior.
    
    A button typically used for resetting form fields or reverting changes to default values.
    Uses default text "Reset" and standard dimensions.

    Args:
        parent (QWidget, optional): Parent widget. Defaults to None.
        width (int, optional): Button width in pixels. Defaults to 100.
        height (int, optional): Button height in pixels. Defaults to 30.
        font_family (str, optional): Font family name. Defaults to "Inconsolata SemiCondensed".
        font_size (int, optional): Font size in points. Defaults to 10.
        on_clicked (callable, optional): Click event handler. Defaults to None.
        tooltip (str, optional): Custom tooltip text. Defaults to "Reset to default".
    """
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Merriweather Light",
        font_size: int = 10,
        enabled:bool = True,
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
            enabled=enabled,
            object_name="reset_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFResetButton")

class TFCancelButton(TFBaseButton):
    """
    Standard "Cancel" button with predefined styling and behavior.
    
    A button typically used for canceling operations or closing dialogs without saving.
    Uses default text "Cancel" and standard dimensions.

    Args:
        parent (QWidget, optional): Parent widget. Defaults to None.
        width (int, optional): Button width in pixels. Defaults to 100.
        height (int, optional): Button height in pixels. Defaults to 30.
        font_family (str, optional): Font family name. Defaults to "Inconsolata SemiCondensed".
        font_size (int, optional): Font size in points. Defaults to 10.
        on_clicked (callable, optional): Click event handler. Defaults to None.
        tooltip (str, optional): Custom tooltip text. Defaults to "Cancel action".
    """
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Merriweather Light",
        font_size: int = 10,
        enabled:bool = False,
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
            enabled=enabled,
            object_name="cancel_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFCancelButton")

class TFSubmitButton(TFBaseButton):
    """
    Standard "Submit" button with predefined styling and behavior.
    
    A button typically used for submitting forms or finalizing data entry.
    Uses default text "Submit" and standard dimensions.

    Args:
        parent (QWidget, optional): Parent widget. Defaults to None.
        width (int, optional): Button width in pixels. Defaults to 100.
        height (int, optional): Button height in pixels. Defaults to 30.
        font_family (str, optional): Font family name. Defaults to "Inconsolata SemiCondensed".
        font_size (int, optional): Font size in points. Defaults to 10.
        on_clicked (callable, optional): Click event handler. Defaults to None.
        tooltip (str, optional): Custom tooltip text. Defaults to "Submit form".
    """
    def __init__(
        self, 
        parent=None, 
        width: int = 100,
        height: int = 30,
        font_family: str = "Merriweather Light",
        font_size: int = 10,
        enabled:bool = False,
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
            enabled=enabled,
            object_name="submit_button",
            tooltip=tooltip,
            on_clicked=on_clicked
        )

        self.setObjectName("TFSubmitButton")

