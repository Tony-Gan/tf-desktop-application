import pytz
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from PyQt6.QtWidgets import QCompleter, QLineEdit, QListView, QVBoxLayout, QWidget, QComboBox, QHBoxLayout, QLabel, QFrame, QStyledItemDelegate
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon, QStandardItemModel, QStandardItem

from ui.tf_draggable_window import TFDraggableWindow
from ui.tf_widgets.tf_number_receiver import TFNumberReceiver
from ui.tf_widgets.tf_buttons import TFPushButton, TFConfirmButton, TFResetButton
from tools.tf_api_loader import TFAPILoader

try:
    from settings.secret import API_KEY
except ImportError:
    API_KEY = None

class CleanTextBox(QComboBox):
    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.currentText() == "Select Currency":
            self.lineEdit().clear()

class TFCurrencyConverter(TFDraggableWindow):

    def __init__(self, parent=None):
        self.selected_currencies: List[str] = []
        self.rates: Dict[str, float] = {}
        self.last_update: Optional[str] = None
        self.currency_names: Dict[str, str] = {
            "USD": "United States Dollar - USD",
            "AED": "United Arab Emirates Dirham - AED",
            "AFN": "Afghan Afghani - AFN",
            "ALL": "Albanian Lek - ALL",
            "AMD": "Armenian Dram - AMD",
            "ANG": "Netherlands Antillean Guilder - ANG",
            "AOA": "Angolan Kwanza - AOA",
            "ARS": "Argentine Peso - ARS",
            "AUD": "Australian Dollar - AUD",
            "AWG": "Aruban Florin - AWG",
            "AZN": "Azerbaijani Manat - AZN",
            "BAM": "Bosnia-Herzegovina Convertible Mark - BAM",
            "BBD": "Barbadian Dollar - BBD",
            "BDT": "Bangladeshi Taka - BDT",
            "BGN": "Bulgarian Lev - BGN",
            "BHD": "Bahraini Dinar - BHD",
            "BIF": "Burundian Franc - BIF",
            "BMD": "Bermudian Dollar - BMD",
            "BND": "Brunei Dollar - BND",
            "BOB": "Bolivian Boliviano - BOB",
            "BRL": "Brazilian Real - BRL",
            "BSD": "Bahamian Dollar - BSD",
            "BTN": "Bhutanese Ngultrum - BTN",
            "BWP": "Botswana Pula - BWP",
            "BYN": "Belarusian Ruble - BYN",
            "BZD": "Belize Dollar - BZD",
            "CAD": "Canadian Dollar - CAD",
            "CDF": "Congolese Franc - CDF",
            "CHF": "Swiss Franc - CHF",
            "CLP": "Chilean Peso - CLP",
            "CNY": "Chinese Yuan - CNY",
            "COP": "Colombian Peso - COP",
            "CRC": "Costa Rican Colón - CRC",
            "CUP": "Cuban Peso - CUP",
            "CVE": "Cape Verdean Escudo - CVE",
            "CZK": "Czech Koruna - CZK",
            "DJF": "Djiboutian Franc - DJF",
            "DKK": "Danish Krone - DKK",
            "DOP": "Dominican Peso - DOP",
            "DZD": "Algerian Dinar - DZD",
            "EGP": "Egyptian Pound - EGP",
            "ERN": "Eritrean Nakfa - ERN",
            "ETB": "Ethiopian Birr - ETB",
            "EUR": "Euro - EUR",
            "FJD": "Fijian Dollar - FJD",
            "FKP": "Falkland Islands Pound - FKP",
            "FOK": "Faroese Króna - FOK",
            "GBP": "British Pound Sterling - GBP",
            "GEL": "Georgian Lari - GEL",
            "GGP": "Guernsey Pound - GGP",
            "GHS": "Ghanaian Cedi - GHS",
            "GIP": "Gibraltar Pound - GIP",
            "GMD": "Gambian Dalasi - GMD",
            "GNF": "Guinean Franc - GNF",
            "GTQ": "Guatemalan Quetzal - GTQ",
            "GYD": "Guyanese Dollar - GYD",
            "HKD": "Hong Kong Dollar - HKD",
            "HNL": "Honduran Lempira - HNL",
            "HRK": "Croatian Kuna - HRK",
            "HTG": "Haitian Gourde - HTG",
            "HUF": "Hungarian Forint - HUF",
            "IDR": "Indonesian Rupiah - IDR",
            "ILS": "Israeli New Shekel - ILS",
            "IMP": "Isle of Man Pound - IMP",
            "INR": "Indian Rupee - INR",
            "IQD": "Iraqi Dinar - IQD",
            "IRR": "Iranian Rial - IRR",
            "ISK": "Icelandic Króna - ISK",
            "JEP": "Jersey Pound - JEP",
            "JMD": "Jamaican Dollar - JMD",
            "JOD": "Jordanian Dinar - JOD",
            "JPY": "Japanese Yen - JPY",
            "KES": "Kenyan Shilling - KES",
            "KGS": "Kyrgyzstani Som - KGS",
            "KHR": "Cambodian Riel - KHR",
            "KID": "Kiribati Dollar - KID",
            "KMF": "Comorian Franc - KMF",
            "KRW": "South Korean Won - KRW",
            "KWD": "Kuwaiti Dinar - KWD",
            "KYD": "Cayman Islands Dollar - KYD",
            "KZT": "Kazakhstani Tenge - KZT",
            "LAK": "Lao Kip - LAK",
            "LBP": "Lebanese Pound - LBP",
            "LKR": "Sri Lankan Rupee - LKR",
            "LRD": "Liberian Dollar - LRD",
            "LSL": "Lesotho Loti - LSL",
            "LYD": "Libyan Dinar - LYD",
            "MAD": "Moroccan Dirham - MAD",
            "MDL": "Moldovan Leu - MDL",
            "MGA": "Malagasy Ariary - MGA",
            "MKD": "Macedonian Denar - MKD",
            "MMK": "Myanmar Kyat - MMK",
            "MNT": "Mongolian Tögrög - MNT",
            "MOP": "Macanese Pataca - MOP",
            "MRU": "Mauritanian Ouguiya - MRU",
            "MUR": "Mauritian Rupee - MUR",
            "MVR": "Maldivian Rufiyaa - MVR",
            "MWK": "Malawian Kwacha - MWK",
            "MXN": "Mexican Peso - MXN",
            "MYR": "Malaysian Ringgit - MYR",
            "MZN": "Mozambican Metical - MZN",
            "NAD": "Namibian Dollar - NAD",
            "NGN": "Nigerian Naira - NGN",
            "NIO": "Nicaraguan Córdoba - NIO",
            "NOK": "Norwegian Krone - NOK",
            "NPR": "Nepalese Rupee - NPR",
            "NZD": "New Zealand Dollar - NZD",
            "OMR": "Omani Rial - OMR",
            "PAB": "Panamanian Balboa - PAB",
            "PEN": "Peruvian Sol - PEN",
            "PGK": "Papua New Guinean Kina - PGK",
            "PHP": "Philippine Peso - PHP",
            "PKR": "Pakistani Rupee - PKR",
            "PLN": "Polish Złoty - PLN",
            "PYG": "Paraguayan Guaraní - PYG",
            "QAR": "Qatari Riyal - QAR",
            "RON": "Romanian Leu - RON",
            "RSD": "Serbian Dinar - RSD",
            "RUB": "Russian Ruble - RUB",
            "RWF": "Rwandan Franc - RWF",
            "SAR": "Saudi Riyal - SAR",
            "SBD": "Solomon Islands Dollar - SBD",
            "SCR": "Seychellois Rupee - SCR",
            "SDG": "Sudanese Pound - SDG",
            "SEK": "Swedish Krona - SEK",
            "SGD": "Singapore Dollar - SGD",
            "SHP": "Saint Helena Pound - SHP",
            "SLE": "Sierra Leonean Leone - SLE",
            "SLL": "Sierra Leonean Leone - SLL",
            "SOS": "Somali Shilling - SOS",
            "SRD": "Surinamese Dollar - SRD",
            "SSP": "South Sudanese Pound - SSP",
            "STN": "São Tomé and Príncipe Dobra - STN",
            "SYP": "Syrian Pound - SYP",
            "SZL": "Eswatini Lilangeni - SZL",
            "THB": "Thai Baht - THB",
            "TJS": "Tajikistani Somoni - TJS",
            "TMT": "Turkmenistani Manat - TMT",
            "TND": "Tunisian Dinar - TND",
            "TOP": "Tongan Paʻanga - TOP",
            "TRY": "Turkish Lira - TRY",
            "TTD": "Trinidad and Tobago Dollar - TTD",
            "TVD": "Tuvaluan Dollar - TVD",
            "TWD": "New Taiwan Dollar - TWD",
            "TZS": "Tanzanian Shilling - TZS",
            "UAH": "Ukrainian Hryvnia - UAH",
            "UGX": "Ugandan Shilling - UGX",
            "UYU": "Uruguayan Peso - UYU",
            "UZS": "Uzbekistani Soʻm - UZS",
            "VES": "Venezuelan Bolívar - VES",
            "VND": "Vietnamese Đồng - VND",
            "VUV": "Vanuatu Vatu - VUV",
            "WST": "Samoan Tālā - WST",
            "XAF": "Central African CFA Franc - XAF",
            "XCD": "East Caribbean Dollar - XCD",
            "XDR": "Special Drawing Rights - XDR",
            "XOF": "West African CFA Franc - XOF",
            "XPF": "CFP Franc - XPF",
            "YER": "Yemeni Rial - YER",
            "ZAR": "South African Rand - ZAR",
            "ZMW": "Zambian Kwacha - ZMW",
            "ZWL": "Zimbabwean Dollar - ZWL"
        }
        self.currency_icons: Dict[str, QIcon] = {}

        self.selectors = []
        self.currency_frames: List[QFrame] = []
        self.currency_inputs: List[QLineEdit] = []

        super().__init__(parent, (300, 500), "Currency Converter", 1)

    def initialize_window(self):
        self.setup_ui()
        
    def setup_ui(self):
        self.container = QWidget(self)
        self.container.setGeometry(0, 30, self.size[0], self.size[1] - 30)

        main_layout = QVBoxLayout(self.container)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        selector_container = QWidget()
        selector_layout = QVBoxLayout(selector_container)
        selector_layout.setSpacing(12)
        selector_layout.setContentsMargins(0, 5, 0, 5)

        self.selectors = []
        for i in range(3):
            selector = CleanTextBox()
            selector.setObjectName("currency_selector")
            font = QFont("Nunito", 10)
            selector.setFont(font)
            self.setup_selector(selector)
            selector_layout.addWidget(selector)
            self.selectors.append(selector)
            selector.currentTextChanged.connect(self.on_selection_changed)

            if i > 0:
                selector.setEnabled(False)

        main_layout.addWidget(selector_container)

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)

        self.confirm_button = TFConfirmButton(self, self.confirm_selection)
        button_layout.addWidget(self.confirm_button)

        self.reset_button = TFResetButton(self, self.reset_converter)
        button_layout.addWidget(self.reset_button)

        self.zero_button = TFPushButton("Zero", self, self.zero_amounts, "zero_button")
        button_layout.addWidget(self.zero_button)

        main_layout.addWidget(button_container)

        currency_container = QWidget()
        currency_layout = QVBoxLayout(currency_container)
        currency_layout.setSpacing(5)
        currency_layout.setContentsMargins(0, 0, 0, 0)

        self.currency_frames: List[QFrame] = []
        self.currency_inputs: List[QLineEdit] = []

        for i in range(3):
            frame = QFrame()
            frame.setObjectName("currency_item")
            frame_layout = QHBoxLayout(frame)
            frame_layout.setContentsMargins(10, 5, 10, 5)

            icon_label = QLabel()
            icon_label.setFixedSize(30, 30)
            icon_label.setStyleSheet("background-color: #ddd; border-radius: 15px;")
            frame_layout.addWidget(icon_label)

            currency_label = QLabel("Select Currency")
            currency_label.setFont(QFont("Nunito", 10))
            frame_layout.addWidget(currency_label)

            amount_input = TFNumberReceiver("0", Qt.AlignmentFlag.AlignRight)
            amount_input.setObjectName("currency_amount")
            amount_input.setEnabled(False)
            amount_input.textChanged.connect(self.update_amounts)
            frame_layout.addWidget(amount_input)

            self.currency_frames.append(frame)
            self.currency_inputs.append(amount_input)
            currency_layout.addWidget(frame)

            self.set_currency_icon(icon_label, "default")

        main_layout.addWidget(currency_container)

        self.time_label = QLabel("Update time: Not yet fetched")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Open Sans", 9))
        main_layout.addWidget(self.time_label)

        main_layout.addStretch()
        
    def setup_selector(self, selector: QComboBox):
        selector.clear()
        default_icon_path = "static/images/countries/default.png"
        default_icon = QIcon(QPixmap(default_icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        selector.setEditable(True)
        selector.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        model = QStandardItemModel()
        item = QStandardItem("Select Currency")
        item.setIcon(default_icon)
        model.appendRow(item)

        for code, name in self.currency_names.items():
            if code.lower() in self.currency_icons:
                icon = self.currency_icons[code.lower()]
            else:
                icon_path = f"static/images/countries/{code.lower()}.png"
                if os.path.exists(icon_path):
                    icon = QIcon(QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    icon = default_icon
                self.currency_icons[code.lower()] = icon

            item = QStandardItem(name)
            item.setIcon(icon)
            item.setData(code, Qt.ItemDataRole.UserRole)
            model.appendRow(item)

        selector.setModel(model)
        selector.setModelColumn(0)

        completer = QCompleter(model, selector)
        completer.setCompletionRole(Qt.ItemDataRole.DisplayRole)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        popup = QListView()
        popup.setIconSize(QSize(24, 24))
        popup.setUniformItemSizes(True)
        completer.setPopup(popup)
        selector.setCompleter(completer)

        delegate = QStyledItemDelegate(selector)
        selector.setItemDelegate(delegate)

    def on_selection_changed(self, text):
        sender = self.sender()
        if text == "Select Currency" or text == "":
            sender_index = self.selectors.index(sender)
            for i in range(sender_index + 1, len(self.selectors)):
                self.selectors[i].setCurrentIndex(0)
                self.selectors[i].setEnabled(False)
            return

        sender_index = self.selectors.index(sender)
        if sender_index + 1 < len(self.selectors):
            self.selectors[sender_index + 1].setEnabled(True)
            
    def confirm_selection(self):
        selected = []
        for selector in self.selectors:
            if selector.currentText() != "Select Currency":
                currency = selector.currentText().split(' - ')[-1]
                if currency not in selected:
                    selected.append(currency)

        if len(selected) < 2:
            self.app.show_message('You need to select at least two currencies.', 3000, 'yellow')
            return

        self.selected_currencies = selected

        self.load_exchange_rates()

    def load_exchange_rates(self):
        if not self.should_update_data():
            self.load_saved_data()
            return

        if not API_KEY:
            self.app.show_message("API key is missing", 3000, 'red')
            return
        
        self.loader_thread = TFAPILoader(f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD")
        self.loader_thread.data_loaded.connect(self.on_data_loaded)
        self.loader_thread.error_occured.connect(self.on_error_occurred)
        self.loader_thread.start()

    def on_data_loaded(self, data):
        self.rates = data['conversion_rates']
        self.last_update = data['time_last_update_utc']

        self.save_exchange_data(data)

        self.update_ui_with_rates()

    def on_error_occurred(self, error_message):
        self.app.show_message(error_message, 3000, 'red')

    def should_update_data(self):
        path = os.path.abspath("data/currency_record.json")
        if not os.path.exists(path):
            return True

        try:
            with open(path, "r") as f:
                saved_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return True

        saved_time_str = saved_data.get("current_time")
        if not saved_time_str:
            return True

        try:
            saved_time = datetime.fromisoformat(saved_time_str)
        except ValueError:
            return True

        current_time = datetime.now()

        return current_time - saved_time > timedelta(hours=24)
    
    def load_saved_data(self):
        path = os.path.abspath("data/currency_record.json")
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.app.show_message("Error loading saved data", 3000, 'red')
            return

        self.rates = data['conversion_rates']
        self.last_update = data['time_last_update_utc']
        self.update_ui_with_rates()

    def save_exchange_data(self, data):
        path = os.path.abspath("data/currency_record.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)

        data["current_time"] = datetime.now().isoformat()

        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
        except IOError:
            self.app.show_message("Error saving data", 3000, 'red')


    def update_ui_with_rates(self):
        for i, frame in enumerate(self.currency_frames):
            if i < len(self.selected_currencies):
                code = self.selected_currencies[i]
                currency_label = frame.findChildren(QLabel)[1]
                currency_label.setText(code)

                icon_label = frame.findChildren(QLabel)[0]
                self.set_currency_icon(icon_label, code)

                amount_input = frame.findChild(QLineEdit)
                amount_input.setEnabled(True)
                amount_input.setText("0")
            else:
                icon_label = frame.findChildren(QLabel)[0]
                self.set_currency_icon(icon_label, "default")

                currency_label = frame.findChildren(QLabel)[1]
                currency_label.setText("Select Currency")

                amount_input = frame.findChild(QLineEdit)
                amount_input.setEnabled(False)
                amount_input.setText("0")

        if self.last_update:
            update_time = self.convert_to_local_time(self.last_update)
            self.time_label.setText(f"Update time: {update_time}")

        for selector in self.selectors:
            selector.setEnabled(False)
        self.confirm_button.setEnabled(False)
                        
    def update_amounts(self, text: str):
        sender = self.sender()

        if not text:
            text = "0"
            sender.blockSignals(True)
            sender.setText(text)
            sender.blockSignals(False)
            return

        try:
            sender_index = self.currency_inputs.index(sender)
            amount = float(text)

            digit_count = len(text.replace('.', '').replace('-', ''))
            if digit_count > 12:
                scientific_text = f"{amount:.2e}"
                sender.blockSignals(True)
                sender.setText(scientific_text)
                sender.blockSignals(False)
                sender.setReadOnly(True)
            else:
                sender.setReadOnly(False)

            source_currency = self.selected_currencies[sender_index]

            for i, currency_code in enumerate(self.selected_currencies):
                if i != sender_index:
                    target_input = self.currency_inputs[i]
                    rate = self.rates[currency_code] / self.rates[source_currency]
                    converted_amount = amount * rate

                    converted_text = f"{converted_amount:.2f}"
                    digit_count = len(converted_text.replace('.', '').replace('-', ''))
                    if digit_count > 12:
                        converted_text = f"{converted_amount:.2e}"
                        target_input.setReadOnly(True)
                    else:
                        target_input.setReadOnly(False)

                    target_input.blockSignals(True)
                    target_input.setText(converted_text)
                    target_input.blockSignals(False)
        except ValueError:
            self.app.show_message('Invalid input', 3000, 'yellow')

    def reset_converter(self):
        for i, selector in enumerate(self.selectors):
            selector.setCurrentIndex(0)
            selector.setEnabled(i == 0)

        self.confirm_button.setEnabled(True)

        for frame in self.currency_frames:
            icon_label = frame.findChildren(QLabel)[0]
            currency_label = frame.findChildren(QLabel)[1]

            self.set_currency_icon(icon_label, "default")
            currency_label.setText("Select Currency")

            amount_input = frame.findChild(QLineEdit)
            amount_input.setEnabled(False)
            amount_input.setText("0")

        self.selected_currencies = []

    def set_currency_icon(self, icon_label: QLabel, currency_code: str):
        default_icon_path = "static/images/countries/default.png"
        default_pixmap = QPixmap(default_icon_path).scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        if currency_code.lower() in self.currency_icons:
            pixmap = self.currency_icons[currency_code.lower()].pixmap(QSize(30, 30))
        else:
            icon_path = f"static/images/countries/{currency_code.lower()}.png"
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.currency_icons[currency_code.lower()] = QIcon(pixmap)
            else:
                pixmap = default_pixmap
        icon_label.setPixmap(pixmap)
        
    def convert_to_local_time(self, utc_time_str):
        utc_time = datetime.strptime(utc_time_str, "%a, %d %b %Y %H:%M:%S +0000")
        utc_time = pytz.utc.localize(utc_time)

        local_tz = datetime.now().astimezone().tzinfo

        local_time = utc_time.astimezone(local_tz)

        return local_time.strftime("%d %b %Y %H:%M:%S")
    
    def zero_amounts(self):
        for amount_input in self.currency_inputs:
            amount_input.blockSignals(True)
            amount_input.setText("0")
            amount_input.setReadOnly(False)
            amount_input.blockSignals(False)
