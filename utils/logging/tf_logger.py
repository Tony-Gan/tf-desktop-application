import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class TFLogger:
    """
    A custom application logger providing both file and console output capabilities.
    
    This logger is designed to be integrated with TFApplication and provides a dual-output
    logging system. It writes detailed logs to rotating files while displaying important
    messages to the console. When used with TFApplication, it automatically integrates
    with the message bar and output panel for visual feedback.

    Args:
        log_dir (str, optional): Directory path for log files. Defaults to "logs".
            Will be created if it doesn't exist.

    File Logging Configuration:
        - Files are named 'app_YYYYMMDD.log'
        - Rotation occurs at 5MB with 5 backup files kept
        - Includes all levels (DEBUG and above)
        - Format: '%(asctime)s - %(levelname)s - %(module)s - %(message)s'

    Console Output Configuration:
        - Shows INFO level and above
        - Simplified format: '%(levelname)s: %(message)s'

    Integration with TFApplication:
        - DEBUG: Written to log file only
        - INFO: Log file + console + output panel
        - WARNING: Log file + console + orange message bar
        - ERROR: Log file + console + red message bar
        - CRITICAL: Log file + console + red message bar (5s) + output panel

    Example:
        >>> logger = TFLogger("app_logs")
        >>> app = TFApplication.instance()
        >>> app.logger = logger
        >>> 
        >>> # Using via application
        >>> app.log_debug("Database query executed")  # File only
        >>> app.log_info("Process completed")  # File + console + output
        >>> app.log_error("Connection failed")  # File + console + red message
    """
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
        """
        Log a debug message to file only.
        
        These messages are intended for detailed diagnostic information
        and are only written to the log file.

        Args:
            message: The debug message to log.
        """
        self._logger.debug(message)
        
    def info(self, message: str):
        """
        Log an informational message.
        
        When used with TFApplication, these messages appear in:
        - Log file
        - Console
        - Output panel

        Args:
            message: The information message to log.
        """
        self._logger.info(message)
        
    def warning(self, message: str):
        """
        Log a warning message.
        
        When used with TFApplication, these messages appear in:
        - Log file
        - Console
        - Orange message bar

        Args:
            message: The warning message to log.
        """
        self._logger.warning(message)
        
    def error(self, message: str):
        """
        Log an error message.
        
        When used with TFApplication, these messages appear in:
        - Log file
        - Console
        - Red message bar

        Args:
            message: The error message to log.
        """
        self._logger.error(message)
        
    def critical(self, message: str):
        """
        Log a critical error message.
        
        When used with TFApplication, these messages appear in:
        - Log file
        - Console
        - Red message bar (5 second duration)
        - Output panel (prefixed with "CRITICAL ERROR: ")

        Args:
            message: The critical message to log.
        """
        self._logger.critical(message)
