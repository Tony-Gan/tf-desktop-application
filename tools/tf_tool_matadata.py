from dataclasses import dataclass
from typing import Tuple

@dataclass
class TFToolMetadata:
    """Metadata for tool registration and menu creation"""
    name: str  # Display name in menu
    menu_path: str  # Menu path (e.g. "File/Converters")
    window_title: str  # Title shown in window
    menu_title: str # Title shown in menu
    window_size: Tuple[int, int]  # Window dimensions (width, height)
    description: str = ""  # Tool description/tooltip
    icon_path: str = ""  # Path to tool icon
    max_instances: int = 1  # Maximum number of instances allowed