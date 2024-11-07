import os
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from core.windows.tf_draggable_window import TFDraggableWindow

class TFWebView(TFDraggableWindow):
    """
    A draggable window containing a web view for displaying HTML content.

    This class extends TFDraggableWindow to provide a window with embedded web browser
    capabilities, allowing display of local HTML files in a movable window.

    Args:
        parent (QWidget): Parent widget. Should be set as the window container
        size (tuple): Window size as (width, height).
        title (str): Window title.
        max_count (int, optional): Maximum number of instances allowed. Defaults to 1.
        html (str, optional): Path to HTML file to load. Defaults to None.

    Example:
        >>> # Create web view window with custom HTML
        >>> web_view = TFWebView(
        ...     parent=main_window,
        ...     size=(800, 600),
        ...     title="Documentation",
        ...     html="path/to/doc.html"
        ... )
        >>> web_view.show()

    Attributes:
        web_view (QWebEngineView): The embedded web browser widget.
    """
    def __init__(self, parent, size, title, max_count=1, html=None):
        super().__init__(parent, size=size, title=title, max_count=max_count)

        self.web_view = QWebEngineView(self)
        self.layout.addWidget(self.web_view)
        self.load_html_from_file(html)

    def load_html_from_file(self, html_path):
        """
        Load HTML content from a local file into the web view.

        Converts the file path to an absolute URL and loads it into the web view.

        Args:
            html_path (str): Path to the HTML file to load.
        """
        file_url = QUrl.fromLocalFile(os.path.abspath(html_path))
        self.web_view.setUrl(file_url)
        