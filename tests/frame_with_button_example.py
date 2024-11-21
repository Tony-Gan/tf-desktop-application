import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.components.tf_base_frame import TFBaseFrame

class ExampleFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def _setup_content(self) -> None:
        self.input_entry = self.create_value_entry(
            "input_value",
            "Value:",
            value_text="Initial text"
        )
        self.layout().addWidget(self.input_entry)

        self.check = self.create_check_box(
            "check",
            "Enable feature",
            checked=True
        )
        self.layout().addWidget(self.check)

        self.combo = self.create_combo_box(
            "combo",
            ["Option 1", "Option 2", "Option 3"]
        )
        self.layout().addWidget(self.combo)

        self.button = self.create_button(
            "action_button",
            "Toggle State",
            on_clicked=self._on_button_clicked
        )
        self.layout().addWidget(self.button)

    def _on_button_clicked(self):
        current_text = self.input_entry.get_value()
        self.input_entry.set_value(current_text + " (Modified)")
        
        self.check.setChecked(not self.check.isChecked())
        
        current_index = self.combo.currentIndex()
        next_index = (current_index + 1) % self.combo.count()
        self.combo.setCurrentIndex(next_index)

def main():
    app = QApplication(sys.argv)
    
    frame = ExampleFrame()
    frame.setWindowFlags(Qt.WindowType.Window)
    frame.resize(300, 200)
    frame.move(300, 300)
    frame.setWindowTitle('Example Frame')
    frame.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()