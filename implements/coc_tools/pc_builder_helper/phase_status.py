from enum import auto, Enum

class PhaseStatus(Enum):
    NOT_START = auto()
    COMPLETING = auto()
    COMPLETED = auto()
