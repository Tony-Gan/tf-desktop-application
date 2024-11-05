import requests
from PyQt6.QtCore import QThread, pyqtSignal

class TFAPILoader(QThread):
    """A threaded API loader for making HTTP requests.

    This class extends QThread to perform API requests in a separate thread,
    preventing UI freezes during network operations.

    Args:
        url (str): The API endpoint URL to fetch data from.
        parent (QObject, optional): The parent object. Defaults to None.

    Signals: \n
        data_loaded (dict): Emitted when data is successfully loaded from the API.
            The signal contains the parsed JSON response data. \n
        error_occured (str): Emitted when an error occurs during the API request.
            The signal contains the error message. \n

    Example:
        >>> # Create and set up the loader
        >>> loader = TFAPILoader("https://api.example.com/data")
        >>> loader.data_loaded.connect(on_data_received)
        >>> loader.error_occured.connect(on_error)
        >>> loader.start()
        >>>
        >>> # In your callback functions
        >>> def on_data_received(data: dict):
        ...     print(f"Received data: {data}")
        >>> def on_error(message: str):
        ...     print(f"Error: {message}")

    Attributes:
        url (str): The target API endpoint URL.

    Note:
        - The class expects the API response to contain a "result" field with value "success"
        - The response must be valid JSON data
        - Network errors are caught and emitted through error_occured signal
        - Runs in a separate thread to prevent UI blocking
    """
    data_loaded = pyqtSignal(dict)
    error_occured = pyqtSignal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        """Execute the API request in a separate thread.
        
        Makes a GET request to the specified URL and processes the response.
        Successful responses must contain a "result": "success" field and
        valid JSON data.
        
        Signals:
            data_loaded: Emitted with parsed JSON data on successful request.
            error_occured: Emitted with error message on any failure.
        
        Note:
            All exceptions are caught and emitted via error_occured signal
            rather than being raised.
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            data = response.json()

            if data.get("result") == "success":
                self.data_loaded.emit(data)
            else:
                self.error_occurred.emit("Failed to fetch exchange rates")
        except requests.RequestException as e:
            self.error_occurred.emit(f"Error fetching data: {e}")
