from ui.tf_draggable_window import TFDraggableWindow
from PyQt6.QtWidgets import QLineEdit, QPushButton, QGridLayout, QWidget, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import math
import re

class TFScientificCalculator(TFDraggableWindow):
    def __init__(self, parent=None, message_bar=None):
        super().__init__(parent, (450, 500), "Scientific Calculator", 1, message_bar)
        
        self.container = QWidget(self)
        self.container.setGeometry(10, 30, 430, 460)
        
        layout = QGridLayout(self.container)
        layout.setSpacing(5)
        
        self.display = QLineEdit(self.container)
        self.display.setObjectName("scientific_display")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        display_font = QFont("Montserrat", 24, QFont.Weight.Bold)
        self.display.setFont(display_font)
        self.display.setFixedHeight(60)
        layout.addWidget(self.display, 0, 0, 1, 5)
        
        self.history_display = QTextEdit(self.container)
        self.history_display.setObjectName("scientific_record")
        self.history_display.setReadOnly(True)
        history_font = QFont("Montserrat", 12)
        self.history_display.setFont(history_font)
        layout.addWidget(self.history_display, 1, 0, 2, 5)
        
        buttons = [
            ('C', 'special'), ('(', 'operator'), (')', 'operator'), ('sin', 'function'), ('⌫', 'special'),
            ('rad', 'function'), ('cos', 'function'), ('tan', 'function'), ('ln', 'function'), ('÷', 'operator'),
            ('7', 'number'), ('8', 'number'), ('9', 'number'), ('log', 'function'), ('*', 'operator'),
            ('4', 'number'), ('5', 'number'), ('6', 'number'), ('√', 'function'), ('-', 'operator'),
            ('1', 'number'), ('2', 'number'), ('3', 'number'), ('π', 'function'), ('+', 'operator'),
            ('0', 'number'), ('.', 'number'), ('e', 'function'), ('^', 'operator'), ('=', 'equal'),
        ]
        
        button_font = QFont("Montserrat", 16)
        positions = [(i + 3, j) for i in range(6) for j in range(5)]
        
        for position, (text, btn_type) in zip(positions, buttons):
            button = QPushButton(text)
            button.setObjectName(f"scientific_{btn_type}")
            button.setFont(button_font)
            button.setFixedSize(80, 65)
            
            if text == '=':
                button.clicked.connect(self.calculate)
            elif text == 'C':
                button.clicked.connect(self.clear)
            elif text == '⌫':
                button.clicked.connect(self.backspace)
            else:
                button.clicked.connect(lambda checked, t=text: self.button_clicked(t))
                
            layout.addWidget(button, *position)
        
        self.angle_mode = 'deg'
        self.math_error = False
        
    def button_clicked(self, text):
        if self.math_error:
            self.display.clear()
            self.math_error = False

        if text == 'rad':
            self.angle_mode = 'rad'
            self.history_display.append("Switched to radian mode")
            return
            
        if text == 'π':
            text = str(math.pi)
        elif text == 'e':
            text = str(math.e)
            
        cursor_pos = self.display.cursorPosition()
        current = self.display.text()
        
        if text in ['sin', 'cos', 'tan', 'ln', 'log', '√']:
            text = text + '('
            
        if text == '^':
            text = '**'
            
        new_text = current[:cursor_pos] + text + current[cursor_pos:]
        self.display.setText(new_text)
        self.display.setCursorPosition(cursor_pos + len(text))
        
    def calculate(self):
        try:
            expression = self.display.text()
            original_expression = expression
            
            trig_functions = ['sin', 'cos', 'tan']
            pattern = r"(sin|cos|tan)\((.*?)\)"
            
            def replace_trig(match):
                func, arg = match.groups()
                try:
                    arg_val = eval(arg)
                    if self.angle_mode == 'deg':
                        arg_val = math.radians(arg_val)
                    return str(getattr(math, func)(arg_val))
                except:
                    raise ValueError(f"Invalid argument for {func}: {arg}")
            
            expression = re.sub(pattern, replace_trig, expression)

            expression = expression.replace('ln(', 'math.log(')
            expression = expression.replace('log(', 'math.log10(')
            expression = expression.replace('√(', 'math.sqrt(')
            
            result = eval(expression)

            if isinstance(result, float):
                if abs(result) < 1e-10:
                    formatted_result = '0'
                elif result.is_integer():
                    formatted_result = str(int(result))
                else:
                    formatted_result = f"{result:.10g}"
            else:
                formatted_result = str(result)
                
            self.history_display.append(f"{original_expression} = {formatted_result}")
            
            self.display.setText(formatted_result)
            
        except Exception as e:
            self.math_error = True
            self.display.setText("Math Error")
            
    def clear(self):
        self.display.clear()
        self.math_error = False
        
    def backspace(self):
        if self.math_error:
            self.display.clear()
            self.math_error = False
            return
        
        current = self.display.text()
        cursor_pos = self.display.cursorPosition()
        if cursor_pos > 0:
            new_text = current[:cursor_pos-1] + current[cursor_pos:]
            self.display.setText(new_text)
            self.display.setCursorPosition(cursor_pos-1)
