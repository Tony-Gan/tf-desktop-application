from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QApplication
from ui.tf_widgets.tf_settings_widget import TFCloseButton, TFMenuButton

class TFOutputPanel(QWidget):
    """
    This singleton instance has been integrated into TFApplication

    A panel widget for displaying output text in the application. 

    This panel provides a resizable text area for displaying output messages,
    with controls for visibility and clearing content. It automatically adjusts
    its size based on the parent widget and screen dimensions.

    Args:
        parent (QWidget, optional): Parent widget. Defaults to None but should be set as the window container.

    Example:
        >>> # You should use TFApplication to access it
        >>> self.app = TFApplication()
        >>> self.app.output_panel.display_output("Processing started...")
        >>> self.app.output_panel.clear_output()

    Attributes:
        is_enable (bool): Flag indicating if panel is enabled.
        text_display (QTextEdit): Widget displaying the output text.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_enable = False
        self._init_ui()
        self._init_buttons()
        self.hide()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setMinimumHeight(100)
        screen = QApplication.primaryScreen()
        if screen:
            default_height = screen.size().height() // 2
        else:
            default_height = 300
            
        self.text_display.setMaximumHeight(default_height)
        layout.addWidget(self.text_display)

    def _init_buttons(self):
        width = self.width() or self.parent().width() if self.parent() else 300
        self._close_button = TFCloseButton(parent=self, position=(width - 25, 5))
        self._menu_button = TFMenuButton(parent=self, position=(width - 50, 5))

    def display_output(self, text):
        """
        Display text in the output panel.

        Appends text to the display area and scrolls to the bottom.

        Args:
            text (str): Text to display.
        """
        self.text_display.append(text)
        scrollbar = self.text_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_output(self):
        """
        Clear all text from the output panel.
        """
        self.text_display.clear()

    def toggle_panel(self):
        """
        Toggle the panel's visibility state.
        
        Switches between showing and hiding the panel.
        """
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def resizeEvent(self, event):
        """
        Handle panel resize events.
        
        Adjusts panel width to match parent and limits height to half of parent height.

        Args:
            event: Resize event to handle.
        """
        if self.parent():
            self.setFixedWidth(self.parent().width())
            self.text_display.setMaximumHeight(self.parent().height() // 2)
        super().resizeEvent(event)
        