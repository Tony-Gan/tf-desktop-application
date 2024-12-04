from dataclasses import dataclass
from typing import Tuple

@dataclass
class TFToolMetadata:
    """
    Class for defining tool metadata used in registration and menu creation.
    
    This dataclass holds configuration information for tool windows, including
    display settings, menu placement, and instance limitations.

    Attributes:
        name (str): Display name shown in the menu.
        menu_path (str): Full menu path where the tool should appear (e.g. "File/Converters").
        window_title (str): Title text displayed in the tool window's title bar.
        menu_title (str): Title text shown in the menu item.
        window_size (Tuple[int, int]): Window dimensions as (width, height) in pixels.
        description (str, optional): Tool description or tooltip text. Defaults to empty string.
        icon_path (str, optional): Path to the tool's icon file. Defaults to empty string.
        max_instances (int, optional): Maximum number of simultaneous instances allowed. Defaults to 1.

    Example:
        >>> metadata = TFToolMetadata(
        ...     name="Convert Files",
        ...     menu_path="Tools/Converters",
        ...     window_title="File Converter",
        ...     menu_title="Convert Files...",
        ...     window_size=(400, 300),
        ...     description="Convert files between different formats",
        ...     icon_path="icons/convert.png",
        ...     max_instances=3
        ... )
    """
    name: str  # Display name in menu
    window_title: str  # Title shown in window
    window_size: Tuple[int, int]  # Window dimensions (width, height)
    description: str = ""  # Tool description/tooltip
    icon_path: str = ""  # Path to tool icon
    max_instances: int = 1  # Maximum number of instances allowed