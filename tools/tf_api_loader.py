import requests
from PyQt6.QtCore import QThread, pyqtSignal

class TFAPILoader(QThread):
    """A threaded API loader for making HTTP requests.

    This class extends QThread to perform API requests in a separate thread,
    preventing UI freezes during network operations.

    Args:
        url (str): The API endpoint URL to fetch data from.
        parent (QObject, optional): The parent object. Defaults to None.

    Signals:
        data_loaded (dict): Emitted when data is successfully loaded from the API.
            The signal contains the parsed JSON response data.\n
        error_occured (str): Emitted when an error occurs during the API request.
            The signal contains the error message.\n

    Example:
        >>> loader = TFAPILoader("https://api.example.com/data")
        >>> loader.data_loaded.connect(on_data_received)
        >>> loader.error_occured.connect(on_error)
        >>> loader.start()

    Note:
        - The class expects the API response to contain a "result" field with value "success"
        - The response must be valid JSON data
        - Network errors are caught and emitted through error_occured signal
    """
    data_loaded = pyqtSignal(dict)
    error_occured = pyqtSignal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        """Execute the API request in a separate thread.
        
        Makes a GET request to the specified URL and processes the response.
        Emits either data_loaded with parsed JSON data on success,
        or error_occured with error message on failure.
        
        Raises:
            No exceptions are raised; all errors are emitted via error_occured signal.
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
