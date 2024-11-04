from PyQt6.QtWidgets import QComboBox, QCompleter
from PyQt6.QtGui import QFont

class TFComboBox(QComboBox):
    def __init__(self, parent=None, case_sensitive=False, reset_on_focus_out=True, font_family="Montserrat", font_size=12):
        super().__init__(parent)
        self.case_sensitive = case_sensitive
        self.reset_on_focus_out = reset_on_focus_out
        
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        
        self.setFont(QFont(font_family, font_size))
        
        self._all_items = []
        
        self.lineEdit().textChanged.connect(self.filter_items)
        
    def setup_items(self, items):
        self._all_items = items
        self.clear()
        self.addItems(items)
        
    def filter_items(self, text):
        self.clear()
        if self.case_sensitive:
            filtered_items = [item for item in self._all_items if text in item]
        else:
            filtered_items = [item for item in self._all_items if text.lower() in item.lower()]
        self.addItems(filtered_items)
        self.showPopup()
        
    def focusOutEvent(self, e):
        super().focusOutEvent(e)
        if self.reset_on_focus_out and self.currentText() not in self._all_items:
            self.clear()
            self.addItems(self._all_items)
            self.setCurrentIndex(0)
            
    def get_all_items(self):
        return self._all_items.copy()
        
    def add_item(self, item):
        if item not in self._all_items:
            self._all_items.append(item)
            self.addItem(item)
            
    def remove_item(self, item):
        if item in self._all_items:
            self._all_items.remove(item)
            index = self.findText(item)
            if index >= 0:
                self.removeItem(index)
