from PyQt6.QtWidgets import QComboBox, QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from core.windows.tf_draggable_window import TFDraggableWindow
from ui.components.tf_buttons import TFConfirmButton, TFResetButton
from ui.components.tf_number_receiver import TFNumberReceiver
from utils.registry.tf_tool_matadata import TFToolMetadata

CONVERSION_FACTORS = {
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
    metadata = TFToolMetadata(
        name="unit_converter",
        menu_path="Tools",
        menu_title="Unit Converter",
        window_title="Unit Converter",
        window_size=(300, 500),
        description="Convert between different units of measurement",
        max_instances=1
    )

    def __init__(self, parent=None):
        self.conversion_factors = CONVERSION_FACTORS
        super().__init__(parent)

    def initialize_window(self):
        main_layout = QVBoxLayout(self.content_container)
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

        from_frame = self._create_conversion_frame("From:", self.from_unit_changed)
        self.from_unit = from_frame.findChild(UnitSelector)
        self.from_input = from_frame.findChild(TFNumberReceiver)
        conversion_layout.addWidget(from_frame)

        to_frame = self._create_conversion_frame("To:", self.to_unit_changed)
        self.to_unit = to_frame.findChild(UnitSelector)
        self.to_input = to_frame.findChild(TFNumberReceiver)
        conversion_layout.addWidget(to_frame)

        main_layout.addWidget(conversion_container)
        main_layout.addStretch()

    def _create_conversion_frame(self, label_text: str, input_callback) -> QFrame:
        frame = QFrame()
        frame.setObjectName("conversion_item")
        layout = QVBoxLayout(frame)

        label = QLabel(label_text)
        label.setFont(QFont("Open Sans", 10))
        layout.addWidget(label)

        unit_selector = UnitSelector()
        layout.addWidget(unit_selector)

        number_input = TFNumberReceiver("0", Qt.AlignmentFlag.AlignRight)
        number_input.setObjectName("conversion_amount")
        number_input.setEnabled(False)
        number_input.textChanged.connect(input_callback)
        layout.addWidget(number_input)

        return frame

    def from_unit_changed(self):
        self.update_conversion("from")

    def to_unit_changed(self):
        self.update_conversion("to")

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
            self.app.show_message('Invalid input', 3000, 'yellow')

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
        