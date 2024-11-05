from PyQt6.QtWidgets import QComboBox, QCompleter
from PyQt6.QtGui import QFont

class TFComboBox(QComboBox):
    """
    A custom combo box with dynamic filtering and item management capabilities.

    This combo box extends QComboBox to provide real-time filtering of items as the user
    types, with options for case sensitivity and focus behavior.

    Args:
        parent (QWidget, optional): Parent widget. Defaults to None.
        case_sensitive (bool, optional): Whether filtering is case sensitive. Defaults to False.
        reset_on_focus_out (bool, optional): Reset to full list when focus lost. Defaults to True.
        font_family (str, optional): Font family to use. Defaults to "Montserrat".
        font_size (int, optional): Font size to use. Defaults to 12.

    Example:
        >>> # Create a filtered combo box
        >>> combo = TFComboBox(
        ...     parent=widget,
        ...     case_sensitive=True,
        ...     font_size=14
        ... )
        >>> combo.setup_items(['Apple', 'Banana', 'Cherry'])
        >>> combo.add_item('Date')
    """
    def __init__(self, parent=None, case_sensitive=False, reset_on_focus_out=True, font_family="Montserrat", font_size=12):
        super().__init__(parent)
        self.case_sensitive = case_sensitive
        self.reset_on_focus_out = reset_on_focus_out
        
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        
        self.setFont(QFont(font_family, font_size))
        
        self._all_items = []
        
        self.lineEdit().textChanged.connect(self._filter_items)
        
    def setup_items(self, items):
        """
        Set up the initial list of items.
        
        Args:
            items (list): List of items to populate the combo box.
        """
        self._all_items = items
        self.clear()
        self.addItems(items)
        
    def _filter_items(self, text):
        self.clear()
        if self.case_sensitive:
            filtered_items = [item for item in self._all_items if text in item]
        else:
            filtered_items = [item for item in self._all_items if text.lower() in item.lower()]
        self.addItems(filtered_items)
        self.showPopup()
        
    def focusOutEvent(self, e):
        """
        Handle focus loss event.
        
        Resets items to full list if reset_on_focus_out is True and
        current text isn't in the items list.

        Args:
            e: Focus event object.
        """
        super().focusOutEvent(e)
        if self.reset_on_focus_out and self.currentText() not in self._all_items:
            self.clear()
            self.addItems(self._all_items)
            self.setCurrentIndex(0)
            
    def get_all_items(self):
        """
        Get a copy of all items in the combo box.
        
        Returns:
            list: Copy of all items, including filtered ones.
        """
        return self._all_items.copy()
        
    def add_item(self, item):
        """
        Add a new item to the combo box.
        
        Only adds the item if it's not already in the list.

        Args:
            item (str): Item to add.
        """
        if item not in self._all_items:
            self._all_items.append(item)
            self.addItem(item)
            
    def remove_item(self, item):
        """
        Remove an item from the combo box.
        
        Removes the item from both the visible list and internal storage.

        Args:
            item (str): Item to remove.
        """
        if item in self._all_items:
            self._all_items.remove(item)
            index = self.findText(item)
            if index >= 0:
                self.removeItem(index)
