from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QDateEdit
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

class TFDateEntry(QWidget):
    """
    A customizable date entry widget combining a label with a calendar-enabled date picker.

    This widget provides a labeled date field with a popup calendar for easy date selection.
    It supports configurable sizing, alignment, and date formatting. The date picker defaults
    to the current date and uses the ISO format (YYYY-MM-DD) for date representation.

    Args:
        label_text (str): Text for the label.
        label_size (int, optional): Width of the label in pixels. If None, uses auto-sizing.
        value_size (int, optional): Width of the date field in pixels. If None, uses auto-sizing.
        alignment (Qt.AlignmentFlag, optional): Horizontal alignment of the widget components.
            Defaults to Qt.AlignmentFlag.AlignLeft.
        parent (QWidget, optional): Parent widget. Defaults to None.

    Attributes:
        label (QLabel): The label widget.
        date_field (QDateEdit): The date picker widget with calendar popup.

    Example:
        >>> # Create a basic date entry
        >>> date_entry = TFDateEntry(
        ...     label_text="Start Date:",
        ...     label_size=100,
        ...     value_size=120
        ... )
        >>>
        >>> # Create a right-aligned date entry
        >>> aligned_entry = TFDateEntry(
        ...     label_text="End Date:",
        ...     alignment=Qt.AlignmentFlag.AlignRight
        ... )
        >>>
        >>> # Get the selected date
        >>> selected_date = date_entry.get_value()  # Returns "2024-11-18"
        >>>
        >>> # Set a specific date
        >>> date_entry.set_value("2024-12-25")
    """
    def __init__(self, 
                 label_text: str,
                 label_size: int = None,
                 value_size: int = None,
                 alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
                 parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(0)

        self.setFixedHeight(24)
        font = QFont("Inconsolata", 10)
        font.setWeight(QFont.Weight.DemiBold)
        
        self.label = QLabel(label_text)
        self.label.setFont(font)
        self.label.setFixedHeight(24)
        if label_size:
            self.label.setFixedWidth(label_size)
        self.label.setAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
        
        self.date_field = QDateEdit()
        self.date_field.setStyleSheet("QLineEdit { padding: 1px; }")
        self.date_field.setFixedHeight(24)
        self.date_field.setCalendarPopup(True)
        self.date_field.setDate(QDate.currentDate())
        if value_size:
            self.date_field.setFixedWidth(value_size)
            
        layout.addWidget(self.label)
        layout.addWidget(self.date_field)
        
        if alignment == Qt.AlignmentFlag.AlignLeft:
            layout.addStretch()
            
    def get_value(self) -> str:
        """
        Get the currently selected date as a string.

        Returns:
            str: The selected date in ISO format (YYYY-MM-DD).
        """
        return self.date_field.date().toString("yyyy-MM-dd")
        
    def set_value(self, date_str: str):
        """
        Set the date field to a specific date.

        Args:
            date_str (str): Date string in ISO format (YYYY-MM-DD).
                If the date string is invalid, the current value remains unchanged.
        """
        try:
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            if date.isValid():
                self.date_field.setDate(date)
        except:
            pass
            
    def set_enabled(self, enabled: bool):
        """
        Enable or disable the date picker widget.

        Args:
            enabled (bool): True to enable the widget, False to disable it.
        """
        self.date_field.setEnabled(enabled)
