from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont

from settings.general import GENERAL_BUTTON_HEIGHT

class TFPushButton(QPushButton):
    def __init__(self, text, parent=None, callback=None, object_name=None):
        super().__init__(text, parent)
        
        self.setFont(QFont("Montserrat", 10))
        self.setFixedHeight(GENERAL_BUTTON_HEIGHT)
        
        if object_name:
            self.setObjectName(object_name)
            
        if callback:
            self.clicked.connect(callback)

class TFConfirmButton(TFPushButton):
    def __init__(self, parent=None, callback=None):
        super().__init__(
            text="Confirm",
            parent=parent,
            callback=callback,
            object_name="confirm_button"
        )

class TFResetButton(TFPushButton):
    def __init__(self, parent=None, callback=None):
        super().__init__(
            text="Reset",
            parent=parent,
            callback=callback,
            object_name="reset_button"
        )
