from typing import List, Dict, Optional, Any
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLayout
from PyQt6.QtCore import pyqtSignal

from ui.components.tf_check_with_label import TFCheckWithLabel
from ui.components.tf_date_entry import TFDateEntry
from ui.components.tf_option_entry import TFOptionEntry
from ui.components.tf_value_entry import TFValueEntry


class TFBaseFrame(QFrame):
    values_changed = pyqtSignal(dict)

    def __init__(
            self,
            layout_type: type[QLayout] = QVBoxLayout,  # 默认垂直布局
            margins: tuple[int, int, int, int] = (10, 10, 10, 10),
            spacing: int = 10,
            parent=None
    ):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._entries: Dict[str, Any] = {}  # 存储所有entry的引用
        self._setup_ui(layout_type, margins, spacing)
        self._setup_content()

    def _setup_ui(
            self,
            layout_type: type[QLayout],
            margins: tuple[int, int, int, int],
            spacing: int
    ) -> None:
        self.main_layout = layout_type(self)
        self.main_layout.setContentsMargins(*margins)
        self.main_layout.setSpacing(spacing)

        self.content_frame = QFrame()
        self.content_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.main_layout.addWidget(self.content_frame)

    def _setup_content(self) -> None:
        pass

    def _register_entry(self, name: str, entry: Any) -> None:
        self._entries[name] = entry
        if hasattr(entry, 'value_changed'):
            entry.value_changed.connect(lambda *_: self._on_values_changed())

    def _on_values_changed(self) -> None:
        current_values = self.get_values()
        self.values_changed.emit(current_values)
        self.on_values_changed(current_values)

    def on_values_changed(self, values: Dict[str, Any]) -> None:
        pass

    def get_values(self) -> Dict[str, Any]:
        return {
            name: entry.get_value()
            for name, entry in self._entries.items()
        }

    def create_value_entry(
            self,
            name: str,
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
        entry = TFValueEntry(
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
        self._register_entry(name, entry)
        return entry

    def create_option_entry(
            self,
            name: str,
            label_text: str,
            options: List[str],
            current_value: str = "",
            label_size: int = 80,
            value_size: int = 36,
            height: int = 24,
            extra_value_width: Optional[int] = None,
            enable_filter: bool = False
    ) -> TFOptionEntry:
        entry = TFOptionEntry(
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
        self._register_entry(name, entry)
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
        self._register_entry(name, entry)
        return entry

    def create_check_with_label(
            self,
            name: str,
            label_text: str,
            checked: bool = False,
            height: int = 24,
            spacing: int = 6
    ) -> TFCheckWithLabel:
        entry = TFCheckWithLabel(
            label_text=label_text,
            checked=checked,
            height=height,
            spacing=spacing,
            parent=self
        )
        self._register_entry(name, entry)
        return entry
