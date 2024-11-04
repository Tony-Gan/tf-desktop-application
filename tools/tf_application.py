from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator
from database.tf_database import TFDatabase
from tools.tf_message_bar import TFMessageBar

class TFApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self._database = None
        self._translator = None
        self._message_bar = None
    
    @property
    def database(self) -> TFDatabase:
        return self._database
    
    @database.setter
    def database(self, db):
        self._database = db
        db.set_instance(db)
        
    @property
    def translator(self) -> QTranslator:
        return self._translator
    
    @translator.setter
    def translator(self, trans: QTranslator):
        self._translator = trans

    @property
    def message_bar(self) -> TFMessageBar:
        return self._message_bar
    
    @message_bar.setter
    def message_bar(self, bar: TFMessageBar):
        self._message_bar = bar

    def show_message(self, message: str, display_time=2000, colour='green'):
        if self._message_bar:
            self._message_bar.show_message(message, display_time, colour)
        
    @staticmethod
    def instance():
        return QApplication.instance()