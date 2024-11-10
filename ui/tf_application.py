from typing import List

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator

from core.database.tf_database import TFDatabase
from ui.components.tf_message_bar import TFMessageBar
from utils.logging.tf_logger import TFLogger
from ui.views.tf_output_panel import TFOutputPanel
from ui.components.tf_message_box import TFMessageBox

class TFApplication(QApplication):
    """
    A custom application class extending QApplication to manage core application components.
    
    This class serves as the central application manager, handling database connections,
    translations, message displays, output management, and logger. It provides a singleton pattern
    for accessing the application instance and manages core UI components like message bars
    and output panels.

    Args:
        argv: Command line arguments passed to the application.

    Example:
        >>> # Creating the application instance
        >>> app = TFApplication(sys.argv)
        >>> app.database = TFDatabase()
        >>> app.translator = QTranslator()
        >>> 
        >>> # Accessing the instance in any other class
        >>> app = TFApplication.instance()
        >>> app.display_output("Processing complete")
        >>> app.show_message("Operation completed", 2000, "green")

    Attributes:
        _database (TFDatabase): Internal database connection manager.
        _translator (QTranslator): Internal translator for i18n.
        _message_bar (TFMessageBar): Internal message bar component.
        _output_panel (TFOutputPanel): Internal output panel component.
        _logger (TFLogger): Internal logger component.
    """

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
        """
        Get the application's database manager.

        Returns:
            TFDatabase: The database manager instance.
        """
        return self._database
    
    @database.setter
    def database(self, db: TFDatabase):
        """
        Set the application's database manager.

        Args:
            db (TFDatabase): Database manager to use.
        """
        self._database = db
        db.set_instance(db)
        
    @property
    def translator(self) -> QTranslator:
        """
        Get the application's translator.

        Returns:
            QTranslator: The translator instance.
        """
        return self._translator
    
    @translator.setter
    def translator(self, trans: QTranslator):
        """
        Set the application's translator.

        Args:
            trans (QTranslator): Translator to use.
        """
        self._translator = trans

    @property
    def message_bar(self) -> TFMessageBar:
        """
        Get the application's message bar.

        Returns:
            TFMessageBar: The message bar instance.
        """
        return self._message_bar
    
    @message_bar.setter
    def message_bar(self, bar: TFMessageBar):
        """
        Set the application's message bar.

        Args:
            bar (TFMessageBar): Message bar to use.
        """
        self._message_bar = bar

    @property
    def output_panel(self) -> TFOutputPanel:
        """
        Get the application's output panel.

        Returns:
            TFOutputPanel: The output panel instance.
        """
        return self._output_panel
    
    @output_panel.setter
    def output_panel(self, panel: TFOutputPanel):
        """
        Set the application's output panel.

        Args:
            panel (TFOutputPanel): Output panel to use.
        """
        self._output_panel = panel

    @property
    def logger(self) -> TFLogger:
        """
        Get the application's logger.

        Returns:
            TFLogger: The logger instance.
        """
        return self._logger
    
    @logger.setter
    def logger(self, logger: TFLogger):
        """
        Set the application's logger.

        Args:
            logger (TFLogger): Logger to use.
        """
        self._logger = logger

    @property
    def message_box(self) -> TFMessageBox:
        """
        Get the application's message box.

        Returns:
            TFMessageBox: The message box instance.
        """
        return self._logger
    
    @message_box.setter
    def message_box(self, messaage_box: TFMessageBox):
        """
        Set the application's logger.

        Args:
            messaage_box (TFMessageBox): TFMessageBox to use.
        """
        self._message_box = messaage_box

    def show_message(self, message: str, display_time: int=2000, colour: str='green'):
        """
        Display a temporary message in the application's message bar.

        Args:
            message (str): Text to display in the message bar.
            display_time (int, optional): Duration to show message in milliseconds. 
                Defaults to 2000.
            colour (str, optional): Color of the message. Defaults to 'green'.
        """
        if self._message_bar:
            self._message_bar.show_message(message, display_time, colour)

    def display_output(self, text: str):
        """
        Display text in the application's output panel.

        Args:
            text (str): Text to display in the output panel.
        """
        if self._output_panel:
            self._output_panel.display_output(text)

    def log_debug(self, message: str, *args, **kwargs):
        """
        Log a debug message.
        
        Args:
            message (str): The message to log
            *args: Variable length argument list to format the message
            **kwargs: Arbitrary keyword arguments to format the message

        Examples:
            >>> app = TFApplication.instance()
            >>> 
            >>> # Basic debug message
            >>> app.log_debug("Database connection established")
            >>> 
            >>> # With formatting arguments
            >>> app.log_debug("Query executed in {} ms", 45)
            >>> 
            >>> # With multiple parameters
            >>> app.log_debug("Request {} completed in {} ms with status {}", 
            ...              "GET /api/data", 150, 200)
            >>> 
            >>> # With keyword arguments
            >>> app.log_debug("Processing file {name} of size {size}KB", 
            ...              name="data.csv", size=1024)
        """
        if self._logger:
            if args or kwargs:
                message = message.format(*args, **kwargs)
            self._logger.debug(message)

    def log_info(self, message: str, *args, **kwargs):
        """
        Log an info message.
        
        Args:
            message (str): The message to log
            *args: Variable length argument list to format the message
            **kwargs: Arbitrary keyword arguments to format the message
            
        Examples:
            >>> app = TFApplication.instance()
            >>> 
            >>> # Basic info message
            >>> app.log_info("Application started successfully")
            >>> 
            >>> # With formatting arguments
            >>> app.log_info("Processed {} records", 100)
            >>> 
            >>> # With multiple parameters
            >>> app.log_info("User {} logged in from {}", "john_doe", "192.168.1.1")
            >>> 
            >>> # With keyword arguments
            >>> app.log_info("Export completed: {files} files, {size}MB total", 
            ... 
        """
        if self._logger:
            if args or kwargs:
                message = message.format(*args, **kwargs)
            self._logger.info(message)
            
            self.display_output(message)

    def log_warning(self, message: str, *args, **kwargs):
        """
        Log a warning message.
        
        Args:
            message (str): The message to log
            *args: Variable length argument list to format the message
            **kwargs: Arbitrary keyword arguments to format the message
        """
        if self._logger:
            if args or kwargs:
                message = message.format(*args, **kwargs)
            self._logger.warning(message)
            
            self.show_message(message, colour='orange')

    def log_error(self, message: str, *args, **kwargs):
        """
        Log an error message.
        
        Args:
            message (str): The message to log
            *args: Variable length argument list to format the message
            **kwargs: Arbitrary keyword arguments to format the message
        """
        if self._logger:
            if args or kwargs:
                message = message.format(*args, **kwargs)
            self._logger.error(message)
            
            self.show_message(message, colour='red')

    def log_critical(self, message: str, *args, **kwargs):
        """
        Log a critical message.
        
        Args:
            message (str): The message to log
            *args: Variable length argument list to format the message
            **kwargs: Arbitrary keyword arguments to format the message
        """
        if self._logger:
            if args or kwargs:
                message = message.format(*args, **kwargs)
            self._logger.critical(message)
            
            self.show_message(message, colour='red', display_time=5000)
            self.display_output(f"CRITICAL ERROR: {message}")

    def show_question(
        self,
        title: str,
        message: str,
        buttons: List[str] = None,
        default_button: str = None,
        parent = None
    ) -> str:
        """
        Show a question dialog box.
        
        Args:
            title (str): Dialog title
            message (str): Message to display
            buttons (List[str], optional): List of button texts.
                Defaults to ["Yes", "No", "Cancel"].
            default_button (str, optional): Text of the default button
            parent: Parent widget. If None, uses active window
            
        Returns:
            str: Text of the clicked button
            
        Example:
            >>> app = TFApplication.instance()
            >>> response = app.show_question(
            ...     "Save Changes?",
            ...     "Do you want to save your changes?",
            ...     buttons=["Save", "Don't Save", "Cancel"],
            ...     default_button="Save"
            ... )
            >>> if response == "Save":
            ...     # save changes
            ...     pass
        """
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
        """
        Show a warning dialog box.

        Args:
            title (str): Dialog title.
            message (str): Message to display.
            buttons (List[str], optional): List of button texts.
                Defaults to ["OK"].
            parent: Parent widget. If None, uses active window.

        Returns:
            str: Text of the clicked button.
        """
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
        """
        Show an information dialog box.

        Args:
            title (str): Dialog title.
            message (str): Message to display.
            buttons (List[str], optional): List of button texts.
                Defaults to ["OK"].
            parent: Parent widget. If None, uses active window.

        Returns:
            str: Text of the clicked button.
        """
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
        """
        Show an error dialog box.

        Args:
            title (str): Dialog title.
            message (str): Message to display.
            buttons (List[str], optional): List of button texts.
                Defaults to ["OK"].
            parent: Parent widget. If None, uses active window.

        Returns:
            str: Text of the clicked button.
        """
        if parent is None:
            parent = self.activeWindow()
        return self._message_box.error(parent, title, message, buttons)
        
    @staticmethod
    def instance() -> 'TFApplication':
        """
        Get the singleton instance of the application.

        Returns:
            TFApplication: The current application instance.

        Example:
            >>> app = TFApplication.instance()
            >>> app.show_message("Hello!")
        """
        return QApplication.instance()
        
    