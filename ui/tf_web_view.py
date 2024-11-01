from ui.tf_draggable_window import TFDraggableWindow

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

import os

class TFWebView(TFDraggableWindow):
    def __init__(self, parent=None, size=(600, 400), title="Web View Window", max_count=1, message_bar=None, html=None):
        super().__init__(parent, size=size, title=title, max_count=max_count, message_bar=message_bar)

        self.web_view = QWebEngineView(self)
        self.layout.addWidget(self.web_view)
        self.load_html_from_file(html)

    def load_html_from_file(self, html_path):
        file_url = QUrl.fromLocalFile(os.path.abspath(html_path))
        self.web_view.setUrl(file_url)
