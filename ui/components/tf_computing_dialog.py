from typing import List, Dict, Any, Optional, Tuple
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt

from ui.components.tf_check_with_label import TFCheckWithLabel
from ui.components.tf_date_entry import TFDateEntry
from ui.components.tf_option_entry import TFOptionEntry
from ui.components.tf_value_entry import TFValueEntry
from utils.validator.tf_validator import TFValidator
from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_message_box import TFMessageBox


class TFComputingDialog(QDialog):

    def __init__(self, title: str, parent=None, button_config: Optional[List[Dict]] = None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self._result = None
        self.validator = TFValidator()
        self.button_config = button_config or self.default_button_config()

        self._setup_ui()
        self._setup_validation_rules()
        self._setup_content()

    def _setup_ui(self) -> None:
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        self.content_frame = QFrame()
        self.content_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.content_frame.setObjectName("content_frame")
        self.main_layout.addWidget(self.content_frame)

        self._setup_buttons()

    def _setup_buttons(self) -> None:
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        for config in self.button_config:
            btn = TFBaseButton(config["text"])

            if "callback" in config and callable(config["callback"]):
                btn.clicked.connect(config["callback"])

            if config.get("role") == "accept":
                btn.clicked.connect(self.accept)
            elif config.get("role") == "reject":
                btn.clicked.connect(self.reject)

            button_layout.addWidget(btn)

        self.main_layout.addLayout(button_layout)

    def default_button_config(self) -> List[Dict]:
        return [
            {"text": "OK", "callback": self._on_ok_clicked, "role": "accept"},
            {"text": "Cancel", "callback": self.reject, "role": "reject"}
        ]

    def _setup_validation_rules(self) -> None:
        pass

    def _setup_content(self) -> None:
        pass

    def get_field_values(self) -> Dict[str, Any]:
        return {}

    def process_validated_data(self, data: Dict[str, Any]) -> Any:
        return data

    def _validate_fields(self) -> Tuple[bool, Optional[str]]:
        values = self.get_field_values()
        errors = self.validator.validate_fields(values)

        if errors:
            return False, "\n".join(errors.values())
        return True, None

    def _on_ok_clicked(self) -> None:
        is_valid, error_message = self._validate_fields()
        if not is_valid:
            TFMessageBox.warning(self, "Invalid Input", error_message)
            return

        try:
            self._result = self.process_validated_data(self.get_field_values())
            self.accept()
        except Exception as e:
            TFMessageBox.error(self, "Error", str(e))

    def get_result(self) -> Any:
        return self._result

    def create_value_entry(
            self,
            label_text: str,
            value_text: str = "",
            label_size: int = 80,
            value_size: int = 36,
            height: int = 24,
            number_only: bool = False,
            allow_decimal: bool = True,
            allow_negative: bool = False,
            expanding: bool = False,
            expanding_text_width: int = 300,
            expanding_text_height: int = 100
    ) -> TFValueEntry:
        return TFValueEntry(
            label_text=label_text,
            value_text=value_text,
            label_size=label_size,
            value_size=value_size,
            height=height,
            number_only=number_only,
            allow_decimal=allow_decimal,
            allow_negative=allow_negative,
            expanding=expanding,
            expanding_text_width=expanding_text_width,
            expanding_text_height=expanding_text_height,
            parent=self
        )

    def create_option_entry(
            self,
            label_text: str,
            options: List[str],
            current_value: str = "",
            label_size: int = 80,
            value_size: int = 36,
            height: int = 24,
            extra_value_width: Optional[int] = None,
            enable_filter: bool = False
    ) -> TFOptionEntry:
        return TFOptionEntry(
            label_text=label_text,
            options=options,
            current_value=current_value,
            label_size=label_size,
            value_size=value_size,
            height=height,
            extra_value_width=extra_value_width,
            enable_filter=enable_filter,
            parent=self
        )

    def create_date_entry(
            self,
            label_text: str,
            label_size: Optional[int] = None,
            value_size: Optional[int] = None,
            height: int = 24
    ) -> TFDateEntry:
        return TFDateEntry(
            label_text=label_text,
            label_size=label_size,
            value_size=value_size,
            height=height,
            parent=self
        )

    def create_check_with_label(
            self,
            label_text: str,
            checked: bool = False,
            height: int = 24,
            spacing: int = 6
    ) -> TFCheckWithLabel:
        return TFCheckWithLabel(
            label_text=label_text,
            checked=checked,
            height=height,
            spacing=spacing,
            parent=self
        )

    @classmethod
    def get_input(cls, parent=None, **kwargs) -> Tuple[bool, Any]:
        dialog = cls(parent=parent, **kwargs)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return True, dialog.get_result()
        return False, None
