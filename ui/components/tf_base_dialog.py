from typing import List, Dict, Any, Optional, Tuple
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLayout

from ui.components.tf_base_button import TFBaseButton 
from ui.components.tf_base_frame import TFBaseFrame
from ui.components.if_component_creator import IComponentCreator
from ui.tf_application import TFApplication

class TFBaseDialog(QDialog, IComponentCreator):

    def __init__(self, title: str, layout_type: type[QLayout] = QVBoxLayout, parent=None, button_config: Optional[List[Dict]] = None):
        QDialog.__init__(self, parent)
        IComponentCreator.__init__(self)
        
        self.setWindowTitle(title)
        
        self._result = None
        self._children = {}
        self.button_config = button_config or self.default_button_config()
        
        self._setup_ui(layout_type)
        self._setup_content()
        self._setup_buttons()

    def _setup_ui(self, layout_type) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(20)

        self.content_frame = TFBaseFrame(layout_type, self)
        self.button_frame = TFBaseFrame(QHBoxLayout, parent=self)

        self.main_layout = self.content_frame.layout()

        self.layout.addWidget(self.content_frame)
        self.layout.addWidget(self.button_frame)

    def _setup_buttons(self) -> None:
        for config in self.button_config:
            btn = TFBaseButton(config["text"])
            
            if "callback" in config and callable(config["callback"]):
                btn.clicked.connect(config["callback"])
                
            if config.get("role") == "reject":
                btn.clicked.connect(self.reject)
                
            self.button_frame.main_layout.addWidget(btn)

    def default_button_config(self) -> List[Dict]:
        return [
            {"text": "OK", "callback": self._on_ok_clicked},
            {"text": "Cancel", "callback": self.reject, "role": "reject"}
        ]

    def _setup_content(self) -> None:
        pass

    def validate(self) -> List[Tuple[Any, str]]:
        return []

    def get_validated_data(self) -> Any:
        return self.get_values()

    def _on_ok_clicked(self) -> None:
        invalid_items = self.validate()
        if invalid_items:
            error_messages = []
            for _, error_msg in invalid_items:
                error_messages.append(error_msg)
            
            TFApplication.instance().show_message("\n".join(error_messages), "yellow")
            return

        try:
            self._result = self.get_validated_data()
            self.accept()
        except Exception as e:
            TFApplication.instance().show_message(str(e), "red")

    def get_result(self) -> Any:
        return self._result
    
    def add_child(self, name: str, child: TFBaseFrame) -> None:
        self._register_component(name, child)
        self._children[name] = child
        self.content_frame.main_layout.addWidget(child)

    @classmethod
    def get_input(cls, parent=None, **kwargs) -> Tuple[bool, Any]:
        dialog = cls(parent=parent, **kwargs)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return True, dialog.get_result()
        return False, None
