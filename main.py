import os
import sys

from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import QTranslator

from ui.tf_application import TFApplication
from ui.views.tf_mainwindow import TFMainWindow
from ui.views.tf_output_panel import TFOutputPanel
from ui.components.tf_message_bar import TFMessageBar
from ui.components.tf_message_box import TFMessageBox
from utils.logging.tf_logger import TFLogger
from utils.registry.tf_tool_registry import TFToolRegistry
from utils.helper import resource_path
from core.database.tf_database import TFDatabase

def main():
    app = TFApplication(sys.argv)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    app.logger = TFLogger()
    
    translator = QTranslator()
    if translator.load("resources/translations/zh_CN.qm"):
        app.installTranslator(translator)
    app.translator = translator

    app.setStyleSheet(load_styles())
    app.logger.debug("Styles loaded")
    
    load_font()
    app.logger.debug("Fonts loaded")

    db_folder = os.path.join(base_dir, 'core', 'database')
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
    
    db_path = os.path.join(db_folder, 'tf_database.db')
    db_url = f'sqlite:///{db_path}'
    app.database = TFDatabase(db_url=db_url, db_path=db_path)

    TFToolRegistry.auto_discover_tools()

    output_panel = TFOutputPanel()
    app.output_panel = TFOutputPanel()

    message_box = TFMessageBox()
    app.message_box = message_box

    window = TFMainWindow()
    output_panel.setParent(window)

    app.message_bar = TFMessageBar(window)

    app.logger.info("Application initialized successfully.")
    window.show()
    
    sys.exit(app.exec())

def load_font():
    font_paths = [
        resource_path("resources/fonts/Nunito-Bold.ttf"),
        resource_path("resources/fonts/Nunito-Italic.ttf"),
        resource_path("resources/fonts/Nunito-Light.ttf"),
        resource_path("resources/fonts/Nunito-Regular.ttf"),
        resource_path("resources/fonts/OpenSans-Bold.ttf"),
        resource_path("resources/fonts/OpenSans-Italic.ttf"),
        resource_path("resources/fonts/OpenSans-Light.ttf"),
        resource_path("resources/fonts/OpenSans-Regular.ttf"),
        resource_path("resources/fonts/Montserrat-Bold.ttf"),
        resource_path("resources/fonts/Montserrat-Italic.ttf"),
        resource_path("resources/fonts/Montserrat-Light.ttf"),
        resource_path("resources/fonts/Montserrat-Regular.ttf"),
        resource_path("resources/fonts/Inconsolata-Bold.ttf"),
        resource_path("resources/fonts/Inconsolata-Light.ttf"),
        resource_path("resources/fonts/Inconsolata-Regular.ttf"),
        resource_path("resources/fonts/Inconsolata-SemiBold.ttf"),
        resource_path("resources/fonts/Inconsolata_SemiCondensed-Regular.ttf")
    ]

    loaded_fonts = []

    for font_path in font_paths:
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Failed to load font: {font_path}")
        else:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            loaded_fonts.extend(font_families)


def load_styles():
    with open(resource_path("resources/styles/styles.qss"), "r", encoding='utf-8') as f:
        return f.read()

if __name__ == '__main__':
    main()
    