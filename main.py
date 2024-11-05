import os
import sys

from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import QTranslator

from ui.tf_application import TFApplication
from ui.tf_mainwindow import TFMainWindow
from ui.tf_output_panel import TFOutputPanel
from tools.tf_message_bar import TFMessageBar
from tools.tf_logger import TFLogger
from utils.helper import resource_path
from database.tf_database import TFDatabase

def main():
    app = TFApplication(sys.argv)
    
    # Get the root directory of the application
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Initialize logger with default directory
    app.logger = TFLogger()
    
    # Log application start
    app.logger.info("Application starting...")
    
    translator = QTranslator()
    if translator.load("translations/zh_CN.qm"):
        app.installTranslator(translator)
        app.logger.debug("Translator loaded successfully")
    app.translator = translator

    app.setStyleSheet(load_styles())
    app.logger.debug("Styles loaded")
    
    load_font()
    app.logger.debug("Fonts loaded")

    # Database initialization
    db_folder = os.path.join(base_dir, 'database')
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
        app.logger.debug(f"Created database directory: {db_folder}")
    
    db_path = os.path.join(db_folder, 'tf_database.db')
    db_url = f'sqlite:///{db_path}'
    app.database = TFDatabase(db_url=db_url, db_path=db_path)
    app.logger.debug("Database initialized")

    output_panel = TFOutputPanel()
    app.output_panel = output_panel
    app.logger.debug("Output panel initialized")

    window = TFMainWindow()
    output_panel.setParent(window)
    app.logger.debug("Main window created")

    app.message_bar = TFMessageBar(window)
    app.logger.debug("Message bar initialized")

    app.logger.info("Application initialized successfully")
    window.show()
    
    sys.exit(app.exec())

def load_font():
    QFontDatabase.addApplicationFont("fonts/Nunito-Bold.ttf")
    QFontDatabase.addApplicationFont("fonts/Nunito-Italic.ttf")
    QFontDatabase.addApplicationFont("fonts/Nunito-Light.ttf")
    QFontDatabase.addApplicationFont("fonts/Nunito-Regular.ttf")
    QFontDatabase.addApplicationFont("fonts/OpenSans-Bold.ttf")
    QFontDatabase.addApplicationFont("fonts/OpenSans-Italic.ttf")
    QFontDatabase.addApplicationFont("fonts/OpenSans-Light.ttf")
    QFontDatabase.addApplicationFont("fonts/OpenSans-Regular.ttf")
    QFontDatabase.addApplicationFont("fonts/Montserrat-Bold.ttf")
    QFontDatabase.addApplicationFont("fonts/Montserrat-Italic.ttf")
    QFontDatabase.addApplicationFont("fonts/Montserrat-Light.ttf")
    QFontDatabase.addApplicationFont("fonts/Montserrat-Regular.ttf")

def load_styles():
    with open(resource_path("styles/styles.qss"), "r", encoding='utf-8') as f:
        return f.read()

if __name__ == '__main__':
    main()
    