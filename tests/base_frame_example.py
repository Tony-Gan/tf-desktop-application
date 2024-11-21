import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, 
    QWidget, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
import json
from ui.components.tf_base_frame import TFBaseFrame

class ChildFrame(TFBaseFrame):
    def _setup_content(self) -> None:
        self.setFixedHeight(30)
        
        entry = self.create_value_entry(
            "child_amount", 
            "Amount:", 
            "0.00",
            number_only=True,
            allow_decimal=True,
            label_size=60,
            value_size=80
        )
        self.layout().addWidget(entry)
        
        check = self.create_check_with_label(
            "child_active",
            "Active Status",
            checked=True
        )
        self.layout().addWidget(check)

class MainFrame(TFBaseFrame):
    def _setup_content(self) -> None:
        name_entry = self.create_value_entry(
            "name_entry",
            "Name:",
            "John Doe",
            label_size=100,
            value_size=200
        )
        self.layout().addWidget(name_entry)
        
        amount_entry = self.create_value_entry(
            "amount_entry",
            "Amount:",
            "100.50",
            number_only=True,
            allow_decimal=True,
            label_size=100,
            value_size=100
        )
        self.layout().addWidget(amount_entry)

        category_entry = self.create_option_entry(
            "category",
            "Category:",
            ["Food", "Transport", "Entertainment", "Other"],
            "Food",
            label_size=100,
            value_size=150,
            enable_filter=True
        )
        self.layout().addWidget(category_entry)

        date_entry = self.create_date_entry(
            "date",
            "Date:",
            label_size=100,
            value_size=150
        )
        self.layout().addWidget(date_entry)

        notes_entry = self.create_value_entry(
            "notes",
            "Notes:",
            "Enter detailed notes here...",
            label_size=100,
            expanding=True,
            expanding_text_width=400,
            expanding_text_height=100
        )
        self.layout().addWidget(notes_entry)

        h_layout = QHBoxLayout()
        
        reference_edit = self.create_line_edit(
            "reference",
            "REF-001",
            width=150
        )
        h_layout.addWidget(reference_edit)

        priority_combo = self.create_combo_box(
            "priority",
            ["Low", "Medium", "High"],
            "Medium",
            width=100,
            editable=True,
            enable_completer=True
        )
        h_layout.addWidget(priority_combo)

        urgent_check = self.create_check_box(
            "urgent",
            "Urgent",
            checked=False,
            width=80
        )
        h_layout.addWidget(urgent_check)
        
        h_layout.addStretch()
        
        h_widget = QWidget()
        h_widget.setLayout(h_layout)
        self.layout().addWidget(h_widget)

        child_frame = ChildFrame(QHBoxLayout)
        self.add_child("child_section", child_frame)

        self._value_display = self.create_label(
            "Values will appear here...",
            height=200, 
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        self._value_display.setWordWrap(True) 
        self._value_display.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.layout().addWidget(self._value_display)

        self._tooltip = self.create_tooltip("Test tooltip")
        self.layout().addWidget(self._tooltip)

        self.layout().addStretch()
        
        self.values_changed.connect(self._update_value_display)

    def _update_value_display(self, values: dict) -> None:
        formatted_text = json.dumps(values, indent=2)
        self._value_display.setText(formatted_text)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TFBaseFrame Demo")
        self.setMinimumSize(600, 800)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)
        
        main_frame = MainFrame()
        scroll.setWidget(main_frame)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
