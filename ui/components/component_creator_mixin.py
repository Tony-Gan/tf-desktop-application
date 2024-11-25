from typing import Callable, List, Dict, Optional, Any

from PyQt6.QtWidgets import QLabel, QLineEdit, QComboBox, QCheckBox, QCompleter
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ui.components.tf_base_button import TFBaseButton
from ui.components.tf_check_with_label import TFCheckWithLabel
from ui.components.tf_date_entry import TFDateEntry
from ui.components.tf_option_entry import TFOptionEntry
from ui.components.tf_value_entry import TFValueEntry
from ui.components.tf_font import TEXT_FONT, LABEL_FONT, Merriweather

DEBOUNCE_INTERVAL = 500


class ComponentCreatorMixin:

    def __init__(self):
        self._components: Dict[str, Any] = {}
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_values_changed)

    def _register_component(self, name: str, component: Any) -> None:
        self._components[name] = component
        self._connect_component_signals(component)

    def _connect_component_signals(self, component: Any) -> None:
        signal_mappings = {
            'textChanged': self._on_values_changed,
            'currentTextChanged': self._on_values_changed,
            'stateChanged': self._on_values_changed,
            'value_changed': self._on_values_changed,
            'values_changed': self._on_values_changed
        }
        
        for signal_name, handler in signal_mappings.items():
            if hasattr(component, signal_name):
                getattr(component, signal_name).connect(handler)

    def update_component_value(self, name: str, value: Any) -> None:
        if name not in self._components:
            return
            
        component = self._components[name]
        self._set_component_value(component, value)

    def update_components_from_values(self, values: dict) -> None:
        for name, value in values.items():
            self.update_component_value(name, value)

    def _set_component_value(self, component: Any, value: Any) -> None:
        method_mappings = {
            'setText': str,
            'setCurrentText': str,
            'setChecked': bool,
            'set_value': lambda x: x,
            'set_values': lambda x: x
        }
        
        for method_name, converter in method_mappings.items():
            if hasattr(component, method_name):
                try:
                    getattr(component, method_name)(converter(value))
                    break
                except (ValueError, TypeError):
                    continue

    def _on_values_changed(self) -> None:
        self._debounce_timer.start(DEBOUNCE_INTERVAL)

    def _emit_values_changed(self) -> None:
        values = self.get_values()
        print(values)
        if hasattr(self, 'values_changed'):
            self.values_changed.emit(values)

    def get_component_value(self, name: str) -> Any:
        if name not in self._components:
            return None
            
        component = self._components[name]
        return self._get_component_value(component)

    def _get_component_value(self, component: Any) -> Any:
        if hasattr(component, 'text'):
            if isinstance(component, QCheckBox):
                return component.isChecked()
            return component.text()
        elif hasattr(component, 'currentText'):
            return component.currentText()
        elif hasattr(component, 'isChecked'):
            return component.isChecked()
        elif hasattr(component, 'get_values'):
            return component.get_values()
        elif hasattr(component, 'get_value'):
            return component.get_value()
        return None
    
    def get_values(self) -> Dict[str, Any]:
        return {
            name: self.get_component_value(name)
            for name in self._components
        }

    def create_value_entry(
            self,
            name: str,
            label_text: str,
            value_text: str = "",
            label_size: int = 80,
            value_size: int = 36,
            label_font: QFont = LABEL_FONT,
            value_font: QFont = TEXT_FONT,
            height: int = 24,
            number_only: bool = False,
            allow_decimal: bool = True,
            allow_negative: bool = False,
            expanding: bool = False,
            expanding_text_width: int = 300,
            expanding_text_height: int = 100,
            show_tooltip: bool = False,
            tooltip_text: str = ""
    ) -> TFValueEntry:
        entry = TFValueEntry(
            label_text=label_text,
            value_text=value_text,
            label_size=label_size,
            value_size=value_size,
            label_font=label_font,
            value_font=value_font,
            height=height,
            number_only=number_only,
            allow_decimal=allow_decimal,
            allow_negative=allow_negative,
            expanding=expanding,
            expanding_text_width=expanding_text_width,
            expanding_text_height=expanding_text_height,
            show_tooltip=show_tooltip,
            tooltip_text=tooltip_text,
            parent=self
        )
        self._register_component(name, entry)
        return entry

    def create_option_entry(
            self,
            name: str,
            label_text: str,
            options: List[str],
            current_value: str = "",
            label_size: int = 80,
            value_size: int = 36,
            label_font: QFont = LABEL_FONT,
            value_font: QFont = TEXT_FONT,
            height: int = 24,
            extra_value_width: Optional[int] = None,
            enable_filter: bool = False,
            show_tooltip: bool = False,
            tooltip_text: str = ""
    ) -> TFOptionEntry:
        entry = TFOptionEntry(
            label_text=label_text,
            options=options,
            current_value=current_value,
            label_size=label_size,
            value_size=value_size,
            label_font=label_font,
            value_font=value_font,
            height=height,
            extra_value_width=extra_value_width,
            enable_filter=enable_filter,
            show_tooltip=show_tooltip,
            tooltip_text=tooltip_text,
            parent=self
        )
        self._register_component(name, entry)
        return entry

    def create_date_entry(
            self,
            name: str,
            label_text: str,
            label_size: Optional[int] = None,
            value_size: Optional[int] = None,
            height: int = 24
    ) -> TFDateEntry:
        entry = TFDateEntry(
            label_text=label_text,
            label_size=label_size,
            value_size=value_size,
            height=height,
            parent=self
        )
        self._register_component(name, entry)
        return entry

    def create_check_with_label(
            self,
            name: str,
            label_text: str,
            label_font: QFont,
            checked: bool = False,
            height: int = 24,
            spacing: int = 6,
            show_tooltip: bool = False,
            tooltip_text: str = ""
    ) -> TFCheckWithLabel:
        entry = TFCheckWithLabel(
            label_text=label_text,
            label_font=label_font,
            checked=checked,
            height=height,
            spacing=spacing,
            show_tooltip=show_tooltip,
            tooltip_text=tooltip_text,
            parent=self
        )
        self._register_component(name, entry)
        return entry

    def create_label(
            self,
            text: str,
            fixed_width: Optional[int] = None,
            alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
            height: int = 24,
            serif: bool = False
    ) -> QLabel:
        label = QLabel(text, parent=self)
        label.setFont(Merriweather if serif else TEXT_FONT)
        if fixed_width:
            label.setFixedWidth(fixed_width)
        label.setAlignment(alignment)
        label.setFixedHeight(height)
        return label

    def create_line_edit(
            self,
            name: str,
            text: str = "",
            width: Optional[int] = None,
            height: int = 24,
            alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft
    ) -> QLineEdit:
        edit = QLineEdit(self)
        edit.setText(text)
        edit.setFont(TEXT_FONT)
        if width:
            edit.setFixedWidth(width)
        edit.setFixedHeight(height)
        edit.setAlignment(alignment)
        self._register_component(name, edit)
        return edit

    def create_combo_box(
            self,
            name: str,
            items: list[str],
            current_text: str = "",
            width: Optional[int] = None,
            height: int = 24,
            editable: bool = False,
            enable_completer: bool = False
    ) -> QComboBox:
        combo = QComboBox(self)
        combo.addItems(items)
        combo.setFont(TEXT_FONT)
        if width:
            combo.setFixedWidth(width)
        combo.setFixedHeight(height)
        combo.setEditable(editable)

        if current_text and current_text in items:
            combo.setCurrentText(current_text)

        if enable_completer and editable:
            completer = QCompleter(items)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            combo.setCompleter(completer)

        self._register_component(name, combo)
        return combo

    def create_check_box(
            self,
            name: str,
            text: str = "",
            checked: bool = False,
            width: Optional[int] = None,
            height: int = 24
    ) -> QCheckBox:
        check = QCheckBox(text, self)
        check.setFont(TEXT_FONT)
        check.setChecked(checked)
        if width:
            check.setFixedWidth(width)
        check.setFixedHeight(height)
        self._register_component(name, check)
        return check

    def create_button(
            self,
            name: str,
            text: str,
            width: int = 100,
            height: Optional[int] = None,
            font_family: str = "Inconsolata SemiCondensed",
            font_size: int = 10,
            enabled: bool = True,
            checkable: bool = False,
            object_name: Optional[str] = None,
            tooltip: Optional[str] = None,
            on_clicked: Optional[Callable] = None
    ) -> TFBaseButton:
        button = TFBaseButton(
            text=text,
            parent=self,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
            enabled=enabled,
            checkable=checkable,
            object_name=object_name,
            tooltip=tooltip,
            on_clicked=on_clicked
        )
        self._register_component(name, button)
        return button
