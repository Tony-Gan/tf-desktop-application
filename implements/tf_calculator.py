from PyQt6.QtWidgets import QLineEdit, QPushButton, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.windows.tf_draggable_window import TFDraggableWindow
from utils.registry.tf_tool_matadata import TFToolMetadata

class TFCalculator(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="calculator",
        menu_path="Tools/Calculators",
        window_title="Calculator",
        menu_title="Add Calculator",
        window_size=(300, 500),
        description="Basic calculator for simple calculations",
        max_instances=1
    )

    def __init__(self, parent=None):
        self.current_value = 0
        self.pending_operation = None
        self.new_number = True
        self.last_operator = None
        super().__init__(parent)

    def initialize_window(self):
        layout = QGridLayout(self.content_container)
        layout.setSpacing(10)
        
        self.display = QLineEdit(self.content_container)
        self.display.setObjectName("calculator_display")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setMaxLength(15)
        display_font = QFont("Montserrat", 24, QFont.Weight.Bold)
        self.display.setFont(display_font)
        self.display.setFixedHeight(80)
        self.display.setText("0")
        layout.addWidget(self.display, 0, 0, 1, 4)
        
        self.history = QLineEdit(self.content_container)
        self.history.setObjectName("calculator_history")
        self.history.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.history.setReadOnly(True)
        history_font = QFont("Montserrat", 16)
        history_font.setItalic(True)
        self.history.setFont(history_font)
        self.history.setFixedHeight(40)
        layout.addWidget(self.history, 1, 0, 1, 4)
        
        buttons = [
            ('C', 'special'), ('', 'operator'), ('', 'operator'), ('/', 'operator'),
            ('7', 'number'), ('8', 'number'), ('9', 'number'), ('*', 'operator'),
            ('4', 'number'), ('5', 'number'), ('6', 'number'), ('-', 'operator'),
            ('1', 'number'), ('2', 'number'), ('3', 'number'), ('+', 'operator'),
            ('±', 'number'), ('0', 'number'), ('.', 'number'), ('=', 'equal')
        ]
        
        button_font = QFont("Montserrat", 16)
        positions = [(i + 2, j) for i in range(5) for j in range(4)]
        
        for position, (button_text, button_type) in zip(positions, buttons):
            if button_text:
                button = QPushButton(button_text)
                button.setObjectName(f"calculator_{button_type}")
                button.setFont(button_font)
                button.setFixedSize(65, 65)
                
                if button_text == '=':
                    button.clicked.connect(self.calculate)
                elif button_text == 'C':
                    button.clicked.connect(self.clear)
                elif button_text == '±':
                    button.clicked.connect(self.toggle_sign)
                else:
                    button.clicked.connect(lambda _, text=button_text: self.button_clicked(text))
                    
                layout.addWidget(button, *position)
        
    def button_clicked(self, text):
        if text in '0123456789.':
            if self.new_number:
                self.display.setText(text)
                self.new_number = False
            else:
                current = self.display.text()
                if text != '.' or '.' not in current:
                    self.display.setText(current + text)
        elif text in '/*-+':
            self.handle_operator(text)
    
    def handle_operator(self, operator):
        if not self.new_number:
            self.calculate()
        
        current_text = self.display.text()
        try:
            self.current_value = float(current_text)
        except ValueError:
            return
            
        self.pending_operation = operator
        self.new_number = True
        self.last_operator = operator
        self.history.setText(f"{current_text} {operator}")
    
    def calculate(self):
        if self.pending_operation is None and self.last_operator is None:
            return
            
        try:
            current_text = self.display.text()
            current_number = float(current_text)
            
            if self.pending_operation == '+':
                result = self.current_value + current_number
            elif self.pending_operation == '-':
                result = self.current_value - current_number
            elif self.pending_operation == '*':
                result = self.current_value * current_number
            elif self.pending_operation == '/':
                if current_number == 0:
                    self.display.setText('Error')
                    return
                result = self.current_value / current_number
            else:
                result = current_number
                
            result_str = f"{result:.10f}".rstrip('0').rstrip('.')
            self.display.setText(result_str)

            if self.pending_operation:
                self.history.setText(f"{self.current_value} {self.pending_operation} {current_number} =")
            
            self.current_value = result
            self.new_number = True
            self.pending_operation = None
            
        except:
            self.display.setText('Error')
            self.clear()
            
    def clear(self):
        self.display.setText('0')
        self.history.setText('')
        self.current_value = 0
        self.pending_operation = None
        self.new_number = True
        self.last_operator = None
        
    def toggle_sign(self):
        current = self.display.text()
        try:
            value = float(current)
            self.display.setText(str(-value))
        except:
            pass