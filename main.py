import os
import sys

from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import QTranslator

from ui.tf_application import TFApplication
from ui.views.tf_mainwindow import TFMainWindow
from ui.views.tf_output_panel import TFOutputPanel
from ui.components.tf_message_bar import TFMessageBar
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
    app.output_panel = output_panel

    window = TFMainWindow()
    output_panel.setParent(window)

    app.message_bar = TFMessageBar(window)

    app.logger.info("Application initialized successfully.")
    window.show()
    
    sys.exit(app.exec())

def load_font():
    QFontDatabase.addApplicationFont("resources/fonts/Nunito-Bold.ttf")
    QFontDatabase.addApplicationFont("resources/fonts/Nunito-Italic.ttf")
    QFontDatabase.addApplicationFont("resources/fonts/Nunito-Light.ttf")
    QFontDatabase.addApplicationFont("resources/fonts/Nunito-Regular.ttf")
    QFontDatabase.addApplicationFont("resources/fonts/OpenSans-Bold.ttf")
    QFontDatabase.addApplicationFont("resources/fonts/OpenSans-Italic.ttf")
    QFontDatabase.addApplicationFont("resources/fonts/OpenSans-Light.ttf")
    QFontDatabase.addApplicationFont("resources/fonts/OpenSans-Regular.ttf")
    QFontDatabase.addApplicationFont("resources/fonts/Montserrat-Bold.ttf")
    QFontDatabase.addApplicationFont("resources/fonts/Montserrat-Italic.ttf")
    QFontDatabase.addApplicationFont("resources/fonts/Montserrat-Light.ttf")
    QFontDatabase.addApplicationFont("resources/fonts/Montserrat-Regular.ttf")

def load_styles():
    with open(resource_path("resources/styles/styles.qss"), "r", encoding='utf-8') as f:
        return f.read()

if __name__ == '__main__':
    main()
    