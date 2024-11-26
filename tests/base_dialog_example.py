import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt

from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_base_dialog import TFComputingDialog
from utils.validator.tf_validation_rules import TFBasicRule, TFCustomRule, TFAndRule

class UserInputDialog(TFComputingDialog):
    def __init__(self, parent=None):
        super().__init__("User Information", parent)
        self.setMinimumWidth(400)

    def _setup_validation_rules(self) -> None:
        self.validator.add_rules({
            'name': TFBasicRule(
                required=True,
                error_messages={'required': 'Name is required'}
            ),
            'age': TFAndRule([
                TFBasicRule(
                    type_=int,
                    required=True,
                    error_messages={
                        'required': 'Age is required',
                        'type': 'Age must be a number'
                    }
                ),
                TFCustomRule(
                    lambda x: 0 <= int(x) <= 150,
                    'Age must be between 0 and 150'
                )
            ]),
            'email': TFCustomRule(
                lambda x: '@' in str(x),
                'Invalid email format'
            )
        })

    def _setup_content(self) -> None:
        self.name_entry = self.create_value_entry(
            "Name:",
            label_size=80,
            value_size=250
        )
        self.content_frame.layout().addWidget(self.name_entry)

        self.age_entry = self.create_value_entry(
            "Age:",
            label_size=80,
            value_size=100,
            number_only=True,
            allow_decimal=False,
            allow_negative=False
        )
        self.content_frame.layout().addWidget(self.age_entry)

        self.email_entry = self.create_value_entry(
            "Email:",
            label_size=80,
            value_size=250
        )
        self.content_frame.layout().addWidget(self.email_entry)

        self.newsletter_check = self.create_check_with_label(
            "Subscribe to newsletter",
            checked=True
        )
        self.content_frame.layout().addWidget(self.newsletter_check)

    def get_field_values(self) -> dict:
        return {
            'name': self.name_entry.get_value(),
            'age': self.age_entry.get_value(),
            'email': self.email_entry.get_value()
        }

    def process_validated_data(self, data: dict) -> dict:
        data['newsletter'] = self.newsletter_check.get_value()
        return data

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dialog Demo")
        self.setMinimumSize(500, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        open_dialog_btn = TFBaseButton("Open User Input Dialog")
        open_dialog_btn.clicked.connect(self.show_dialog)
        layout.addWidget(open_dialog_btn)

        self.result_label = QLabel("No data yet")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

    def show_dialog(self):
        success, result = UserInputDialog.get_input(self)
        if success and result:
            result_text = "Dialog Result:\n"
            for key, value in result.items():
                result_text += f"{key}: {value}\n"
            self.result_label.setText(result_text)
        else:
            self.result_label.setText("Operation cancelled or no data provided")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
