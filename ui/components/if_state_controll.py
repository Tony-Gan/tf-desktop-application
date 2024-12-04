from typing import ClassVar, Dict


class IStateController:

    STATE_STYLES: ClassVar[Dict[int, str]] = {
        0: "border: none;",
        1: "border: 1px solid #FF0000; border-radius: 2px;",
        2: "border: 1px solid #FFA500; border-radius: 2px;",
        3: "border: 1px solid #0000FF; border-radius: 2px;"
    }
    
    def __init__(self):
        self.state: int = 0
        self.setProperty("state", self._state)
        self._setup_style()

    def _setup_style(self) -> None:
        style_rules = []
        widget_name = self.__class__.__name__
        
        for state, style in self.STATE_STYLES.items():
            style_rules.append(f"{widget_name}[state='{state}'] {{ {style} }}")
        
        self.setStyleSheet("\n".join(style_rules))

    @classmethod
    def set_state_style(cls, state: int, style: str) -> None:
        cls.STATE_STYLES[state] = style

    def get_state(self) -> int:
        return self._state
    
    def set_state(self, state: int) -> None:
        if not isinstance(state, int):
            raise TypeError("State must be an integer")
        if state < 0:
            raise ValueError("State cannot be negative")
        
        self._state = state
        
        self.setProperty("state", state)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    @property
    def state(self) -> int:
        return self.get_state()
    
    @state.setter
    def state(self, value: int) -> None:
        self.set_state(value)
