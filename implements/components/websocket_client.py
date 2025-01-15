import asyncio
import json
import random
import string
import websockets

from PyQt6.QtCore import QThread, pyqtSignal

class WebSocketClient(QThread):
    connection_error = pyqtSignal(str)
    joined_room = pyqtSignal(str)
    user_joined = pyqtSignal(str)
    user_left = pyqtSignal(str)
    admin_closed = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self, room_id: str, role: str, parent=None):
        super().__init__(parent)
        self.room_id = room_id
        self.role = role
        self.ws = None
        self.sid = None
        self.server_url = "ws://127.0.0.1:8765"
        self.loop = None

    async def _connect_ws(self):
        """ Connect and send 'join' message """
        self.ws = await websockets.connect(self.server_url)
        join_payload = {
            "type": "join",
            "role": "admin" if self.role == "admin" else "player",
            "token": self.room_id
        }
        await self.ws.send(json.dumps(join_payload))

    async def _handle_message(self, message: str):
        """ Process server->client messages (same as before) """
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            return
        # ... same logic for handling 'error', 'joined', 'user_joined', etc. ...

    async def _listen_loop(self):
        """
        Listen to messages until the connection is closed or the loop is stopped.
        """
        try:
            while True:
                message = await self.ws.recv()
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except asyncio.CancelledError:
            pass
        finally:
            self.disconnected.emit()

    async def _close_ws(self):
        """ Gracefully close the websocket """
        if self.ws:
            try:
                await self.ws.close()
            except:
                pass
            self.ws = None

    def stop(self):
        """
        Called externally to stop the event loop. 
        We'll call loop.stop() which unblocks run_forever().
        """
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

    def run(self):
        """
        QThread entry point.
        1) Create event loop
        2) Connect & start listening
        3) run_forever until stop() is called
        4) Cleanup
        """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # 1) Connect first
        try:
            self.loop.run_until_complete(self._connect_ws())
        except Exception as e:
            self.connection_error.emit(str(e))
            # If connect fails, just close the loop and return
            self.loop.close()
            return

        # 2) Start the listening loop in the background
        self.loop.create_task(self._listen_loop())

        # 3) run_forever() blocks until we call loop.stop()
        try:
            self.loop.run_forever()
        finally:
            # 4) Cleanup
            self.loop.run_until_complete(self._close_ws())
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    def send_message(self, data: dict):
        """
        Send a message (dict) to the server. This can be used for dice rolling, etc.
        """
        if self.ws and self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(
                asyncio.ensure_future, self._async_send(data)
            )

    async def _async_send(self, data: dict):
        if self.ws:
            await self.ws.send(json.dumps(data))

    @staticmethod
    def generate_room_id(length=6):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
