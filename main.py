import os
import sys

from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import QTranslator

from tools.tf_application import TFApplication
from tools.tf_message_bar import TFMessageBar
from ui.tf_mainwindow import TFMainWindow
from utils.helper import resource_path
from database.tf_database import TFDatabase

def main():
    app = TFApplication(sys.argv)

    translator = QTranslator()
    if translator.load("translations/zh_CN.qm"):
        app.installTranslator(translator)
    app.translator = translator

    app.setStyleSheet(load_styles())
    load_font()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_folder = os.path.join(base_dir, 'database')
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
    db_path = os.path.join(db_folder, 'tf_database.db')
    db_url = f'sqlite:///{db_path}'
    app.database = TFDatabase(db_url=db_url, db_path=db_path)

    window = TFMainWindow()
    app.message_bar = TFMessageBar(window)
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
    