from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt 
from PyQt6.QtGui import QFont

from ui.components.tf_message_box import TFMessageBox
from ui.components.tf_separator import TFSeparator

class TFComputingDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        
        self._result = None
        
        self.setup_ui()
        
    def setup_ui(self):
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
        self.ok_button.setFont(QFont("Inconsolata", 10))
        self.ok_button.clicked.connect(self._on_ok_clicked)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFont(QFont("Inconsolata", 10))
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        self.main_layout.addLayout(button_layout)

    def setup_content(self) -> None:
        raise NotImplementedError("Subclasses must implement setup_content()")

    def compute_result(self) -> tuple[bool, str]:
        raise NotImplementedError("Subclasses must implement compute_result()")

    def _on_ok_clicked(self):
        success, result = self.compute_result()
        if success:
            self._result = result
            self.accept()
        else:
            TFMessageBox.warning(self, "Invalid Input", result)

    def get_result(self) -> str:
        return self._result

    @classmethod
    def get_computed_value(cls, parent, title: str) -> tuple[bool, str]:
        dialog = cls(title, parent)
        dialog.setup_content()
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return True, dialog.get_result()
        return False, ""
