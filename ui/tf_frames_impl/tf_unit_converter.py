from PyQt6.QtWidgets import QComboBox, QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from ui.tf_draggable_window import TFDraggableWindow
from ui.tf_widgets.tf_buttons import TFConfirmButton, TFResetButton
from ui.tf_widgets.tf_number_receiver import TFNumberReceiver

class UnitTypeSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("unit_type_selector")
        font = QFont("Nunito", 10)
        font.setStyleName("Condensed")
        self.setFont(font)

class UnitSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("unit_selector")
        font = QFont("Nunito", 10)
        font.setStyleName("Condensed")
        self.setFont(font)
        self.setEnabled(False)

class TFUnitConverter(TFDraggableWindow):
    def __init__(self, parent=None):
        self.conversion_factors = {
            "Length": {
                "Meter": 1.0,
                "Kilometer": 1000.0,
                "Centimeter": 0.01,
                "Millimeter": 0.001,
                "Mile": 1609.34,
                "Yard": 0.9144,
                "Foot": 0.3048,
                "Inch": 0.0254
            },
            "Weight": {
                "Kilogram": 1.0,
                "Gram": 0.001,
                "Milligram": 0.000001,
                "Metric Ton": 1000.0,
                "Pound": 0.453592,
                "Ounce": 0.0283495,
            },
            "Area": {
                "Square Meter": 1.0,
                "Square Kilometer": 1000000.0,
                "Square Centimeter": 0.0001,
                "Hectare": 10000.0,
                "Square Mile": 2589988.11,
                "Square Yard": 0.836127,
                "Square Foot": 0.092903,
                "Acre": 4046.86
            },
            "Volume": {
                "Cubic Meter": 1.0,
                "Liter": 0.001,
                "Milliliter": 0.000001,
                "Cubic Foot": 0.0283168,
                "Cubic Inch": 0.0000163871,
                "Gallon (US)": 0.00378541,
                "Quart (US)": 0.000946353,
                "Pint (US)": 0.000473176
            },
            "Speed": {
                "Meters per Second": 1.0,
                "Kilometers per Hour": 0.277778,
                "Miles per Hour": 0.44704,
                "Knot": 0.514444,
                "Foot per Second": 0.3048
            },
            "Temperature": {
                "Celsius": "C",
                "Fahrenheit": "F",
                "Kelvin": "K"
            }
        }
        super().__init__(parent, (300, 500), "Unit Converter", 1)

    def initialize_window(self):
        self.setup_ui()

    def setup_ui(self):
        self.container = QWidget(self)
        self.container.setGeometry(0, 30, self.size[0], self.size[1] - 30)
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        type_container = QWidget()
        type_layout = QVBoxLayout(type_container)
        type_layout.setContentsMargins(0, 5, 0, 5)

        type_label = QLabel("Select Unit Type")
        type_label.setFont(QFont("Open Sans", 10))
        type_layout.addWidget(type_label)

        self.type_selector = UnitTypeSelector()
        self.type_selector.addItems(list(self.conversion_factors.keys()))
        self.type_selector.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_selector)

        main_layout.addWidget(type_container)

        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(10)

        self.confirm_button = TFConfirmButton()
        self.confirm_button.clicked.connect(self.confirm_selection)
        button_layout.addWidget(self.confirm_button)

        self.reset_button = TFResetButton()
        self.reset_button.clicked.connect(self.reset_converter)
        button_layout.addWidget(self.reset_button)

        main_layout.addWidget(button_container)

        conversion_container = QWidget()
        conversion_layout = QVBoxLayout(conversion_container)
        conversion_layout.setSpacing(15)

        from_frame = QFrame()
        from_frame.setObjectName("conversion_item")
        from_layout = QVBoxLayout(from_frame)
        
        from_label = QLabel("From:")
        from_label.setFont(QFont("Open Sans", 10))
        from_layout.addWidget(from_label)
        
        self.from_unit = UnitSelector()
        from_layout.addWidget(self.from_unit)
        
        self.from_input = TFNumberReceiver("0", Qt.AlignmentFlag.AlignRight)
        self.from_input.setObjectName("conversion_amount")
        self.from_input.setEnabled(False)
        self.from_input.textChanged.connect(lambda: self.update_conversion("from"))
        from_layout.addWidget(self.from_input)
        
        conversion_layout.addWidget(from_frame)

        to_frame = QFrame()
        to_frame.setObjectName("conversion_item")
        to_layout = QVBoxLayout(to_frame)
        
        to_label = QLabel("To:")
        to_label.setFont(QFont("Open Sans", 10))
        to_layout.addWidget(to_label)
        
        self.to_unit = UnitSelector()
        to_layout.addWidget(self.to_unit)
        
        self.to_input = TFNumberReceiver("0", Qt.AlignmentFlag.AlignRight)
        self.to_input.setObjectName("conversion_amount")
        self.to_input.setEnabled(False)
        self.to_input.textChanged.connect(lambda: self.update_conversion("to"))
        to_layout.addWidget(self.to_input)
        
        conversion_layout.addWidget(to_frame)

        main_layout.addWidget(conversion_container)
        main_layout.addStretch()

    def on_type_changed(self):
        self.from_unit.setEnabled(False)
        self.to_unit.setEnabled(False)
        self.from_input.setEnabled(False)
        self.to_input.setEnabled(False)
        self.from_input.setText("0")
        self.to_input.setText("0")

    def confirm_selection(self):
        unit_type = self.type_selector.currentText()
        
        self.from_unit.clear()
        self.to_unit.clear()
        self.from_unit.addItems(self.conversion_factors[unit_type].keys())
        self.to_unit.addItems(self.conversion_factors[unit_type].keys())
        
        self.from_unit.setEnabled(True)
        self.to_unit.setEnabled(True)
        self.from_input.setEnabled(True)
        self.to_input.setEnabled(True)
        
        self.type_selector.setEnabled(False)
        self.confirm_button.setEnabled(False)

    def reset_converter(self):
        self.type_selector.setEnabled(True)
        self.confirm_button.setEnabled(True)
        
        self.from_unit.clear()
        self.to_unit.clear()
        self.from_unit.setEnabled(False)
        self.to_unit.setEnabled(False)
        
        self.from_input.setText("0")
        self.to_input.setText("0")
        self.from_input.setEnabled(False)
        self.to_input.setEnabled(False)

    def update_conversion(self, source):
        try:
            unit_type = self.type_selector.currentText()
            from_unit = self.from_unit.currentText()
            to_unit = self.to_unit.currentText()

            if unit_type == "Temperature":
                if source == "from":
                    value = float(self.from_input.text())
                    result = self.convert_temperature(value, from_unit, to_unit)
                    self.to_input.blockSignals(True)
                    self.to_input.setText(f"{result:.2f}")
                    self.to_input.blockSignals(False)
                else:
                    value = float(self.to_input.text())
                    result = self.convert_temperature(value, to_unit, from_unit)
                    self.from_input.blockSignals(True)
                    self.from_input.setText(f"{result:.2f}")
                    self.from_input.blockSignals(False)
            else:
                if source == "from":
                    value = float(self.from_input.text())
                    from_factor = self.conversion_factors[unit_type][from_unit]
                    to_factor = self.conversion_factors[unit_type][to_unit]
                    result = value * (from_factor / to_factor)
                    self.to_input.blockSignals(True)
                    self.to_input.setText(f"{result:.6g}")
                    self.to_input.blockSignals(False)
                else:
                    value = float(self.to_input.text())
                    from_factor = self.conversion_factors[unit_type][from_unit]
                    to_factor = self.conversion_factors[unit_type][to_unit]
                    result = value * (to_factor / from_factor)
                    self.from_input.blockSignals(True)
                    self.from_input.setText(f"{result:.6g}")
                    self.from_input.blockSignals(False)
        except ValueError:
            if self.message_bar:
                self.message_bar.show_message('Invalid input', 3000, 'yellow')

    def convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        if from_unit == "Fahrenheit":
            celsius = (value - 32) * 5/9
        elif from_unit == "Kelvin":
            celsius = value - 273.15
        else:
            celsius = value

        if to_unit == "Fahrenheit":
            return (celsius * 9/5) + 32
        elif to_unit == "Kelvin":
            return celsius + 273.15
        else:
            return celsius
        