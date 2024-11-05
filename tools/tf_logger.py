import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class TFLogger:
    def __init__(self, log_dir: str="logs"):
        self._logger = logging.getLogger('TFApplication')
        self._logger.setLevel(logging.DEBUG)

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

    def debug(self, message: str):
        self._logger.debug(message)
        
    def info(self, message: str):
        self._logger.info(message)
        
    def warning(self, message: str):
        self._logger.warning(message)
        
    def error(self, message: str):
        self._logger.error(message)
        
    def critical(self, message: str):
        self._logger.critical(message)
