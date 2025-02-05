from typing import List

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTranslator

from core.database.tf_database import TFDatabase
from ui.components.tf_message_bar import TFMessageBar
from utils.logging.tf_logger import TFLogger
from ui.components.tf_message_box import TFMessageBox

class TFApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self._database = None
        self._translator = None
        self._message_bar = None
        self._output_panel = None
        self._logger = None
        self._message_box = None

    @property
    def database(self) -> TFDatabase:
        return self._database
    
    @database.setter
    def database(self, db: TFDatabase):
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

    @property
    def logger(self) -> TFLogger:
        return self._logger
    
    @logger.setter
    def logger(self, logger: TFLogger):
        self._logger = logger

    @property
    def message_box(self) -> TFMessageBox:
        return self._logger
    
    @message_box.setter
    def message_box(self, messaage_box: TFMessageBox):
        self._message_box = messaage_box

    def show_message(self, message: str, display_time: int=2000, colour: str='green'):
        if self._message_bar:
            self._message_bar.show_message(message, display_time, colour)

    def display_output(self, text: str):
        if self._output_panel:
            self._output_panel.display_output(text)

    def log_debug(self, message: str, *args, **kwargs):
        if self._logger:
            if args or kwargs:
                message = message.format(*args, **kwargs)
            self._logger.debug(message)

    def log_info(self, message: str, *args, **kwargs):
        if self._logger:
            if args or kwargs:
                message = message.format(*args, **kwargs)
            self._logger.info(message)
            
            self.display_output(message)

    def log_warning(self, message: str, *args, **kwargs):
        if self._logger:
            if args or kwargs:
                message = message.format(*args, **kwargs)
            self._logger.warning(message)
            
            self.show_message(message, colour='orange')

    def log_error(self, message: str, *args, **kwargs):
        if self._logger:
            if args or kwargs:
                message = message.format(*args, **kwargs)
            self._logger.error(message)
            
            self.show_message(message, colour='red')

    def log_critical(self, message: str, *args, **kwargs):
        if self._logger:
            if args or kwargs:
                message = message.format(*args, **kwargs)
            self._logger.critical(message)
            
            self.show_message(message, colour='red', display_time=5000)
            self.display_output(f"CRITICAL ERROR: {message}")

    def show_custom(
            self,
            title: str,
            message: str,
            icon=None,
            button_text: str = "OK",
            parent=None
    ) -> None:
        if parent is None:
            parent = self.activeWindow()
        return self._message_box.custom(parent, title, message, icon, button_text)

    def show_question(
        self,
        title: str,
        message: str,
        buttons: List[str] = None,
        default_button: str = None,
        parent = None
    ) -> str:
        if parent is None:
            parent = self.activeWindow()
        return self._message_box.question(parent, title, message, buttons, default_button)
    
    def show_warning(
        self,
        title: str,
        message: str,
        buttons: List[str] = None,
        parent = None
    ) -> str:
        if parent is None:
            parent = self.activeWindow()
        return self._message_box.warning(parent, title, message, buttons)
    
    def show_information(
        self,
        title: str,
        message: str,
        buttons: List[str] = None,
        parent = None
    ) -> str:
        if parent is None:
            parent = self.activeWindow()
        return self._message_box.information(parent, title, message, buttons)
    
    def show_error(
        self,
        title: str,
        message: str,
        buttons: List[str] = None,
        parent = None
    ) -> str:
        if parent is None:
            parent = self.activeWindow()
        return self._message_box.error(parent, title, message, buttons)
        
    @staticmethod
    def instance() -> 'TFApplication':
        return QApplication.instance()
        
    