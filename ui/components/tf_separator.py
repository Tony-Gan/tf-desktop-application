from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QPalette, QColor


class TFSeparator(QFrame):
    """
    A customizable separator widget for creating visual dividers in the UI.
    
    This class provides a configurable separator line that can be either horizontal
    or vertical, with customizable margins and thickness. It's used to create
    visual boundaries between UI elements.

    Args:
        orientation (str, optional): Direction of the separator, either 'horizontal' or
            'vertical'. Defaults to 'horizontal'.
        margin_left (int, optional): Left margin in pixels. Defaults to 20.
        margin_right (int, optional): Right margin in pixels. Defaults to 20.
        margin_top (int, optional): Top margin in pixels. Defaults to 0.
        margin_bottom (int, optional): Bottom margin in pixels. Defaults to 0.
        height (int, optional): Thickness of the separator line in pixels. Defaults to 1.
        parent (QWidget, optional): Parent widget. Defaults to None.

    Example:
        >>> # Create a horizontal separator with default settings
        >>> separator = TFSeparator()
        >>> 
        >>> # Create a vertical separator with custom margins
        >>> v_separator = TFSeparator(
        ...     orientation='vertical',
        ...     margin_top=10,
        ...     margin_bottom=10
        ... )
    """
    
    def __init__(self, 
                 orientation='horizontal',
                 margin_left=20,
                 margin_right=20,
                 margin_top=0,
                 margin_bottom=0,
                 height=1,
                 parent=None):
        super().__init__(parent)
        
        if orientation == 'horizontal':
            self.setFrameShape(QFrame.Shape.HLine)
            self.setMaximumHeight(height)
        else:
            self.setFrameShape(QFrame.Shape.VLine)
            self.setMaximumWidth(height)
        
        self.setFrameShadow(QFrame.Shadow.Sunken)

        self.setStyleSheet("""
            QFrame {
                background-color: #2A2E3A;  /* 浅灰色，比背景稍亮 */
                border: none;
            }
        """)
        
        self.setContentsMargins(margin_left, margin_top, 
                              margin_right, margin_bottom)
        
    @classmethod
    def horizontal(cls, parent=None):
        """
        Create a standard horizontal separator with default margins.
        
        This is a convenience method for creating a horizontal separator with
        predefined margins (20px on left and right).

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.

        Returns:
            TFSeparator: A horizontal separator instance.
        """
        return cls(orientation='horizontal', parent=parent)
    
    @classmethod
    def vertical(cls, parent=None):
        """
        Create a standard vertical separator with default margins.
        
        This is a convenience method for creating a vertical separator with
        predefined margins (20px on top and bottom).

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.

        Returns:
            TFSeparator: A vertical separator instance with 20px top and bottom margins.
        """
        return cls(orientation='vertical', 
                  margin_left=0, margin_right=0,
                  margin_top=20, margin_bottom=20,
                  parent=parent)
    
    @classmethod
    def compact(cls, parent=None):
        """
        Create a compact horizontal separator without margins.
        
        This is a convenience method for creating a horizontal separator with
        no margins, useful for tight layouts where space is limited.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.

        Returns:
            TFSeparator: A horizontal separator instance with no margins.
        """
        return cls(orientation='horizontal',
                  margin_left=0, margin_right=0,
                  margin_top=0, margin_bottom=0,
                  parent=parent)