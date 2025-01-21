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

    def __init__(self, room_id: str, role: str, display_name: str = "", parent=None):
        super().__init__(parent)
        self.room_id = room_id
        self.role = role
        self.display_name = display_name
        self.ws = None
        self.sid = None
        self.server_url = "ws://127.0.0.1:8765"
        self.loop = None

    async def _connect_ws(self):
        """ Connect and send 'join' message """
        try:
            self.ws = await websockets.connect(self.server_url, ping_interval=None)  # 禁用ping来测试
            join_payload = {
                "type": "join",
                "role": "admin" if self.role == "admin" else "player",
                "token": self.room_id,
                "display_name": self.display_name
            }
            await self.ws.send(json.dumps(join_payload))
            response = await self.ws.recv()
            data = json.loads(response)
            if data.get("type") == "error":
                raise Exception(data.get("message", "Unknown error"))
            elif data.get("type") == "joined":
                self.sid = data.get("sid")
                self.joined_room.emit(self.sid)
        except Exception as e:
            raise Exception(f"WebSocket连接失败: {str(e)}")

    async def _handle_message(self, message: str):
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'error':
                self.connection_error.emit(data.get('message', 'Unknown error'))
                
            elif msg_type == 'joined':
                sid = data.get('sid')
                if sid:
                    self.sid = sid
                    self.joined_room.emit(sid)
                    
            elif msg_type == 'user_joined':
                sid = data.get('sid')
                if sid:
                    self.user_joined.emit(sid)
                    
            elif msg_type == 'user_left':
                sid = data.get('sid')
                if sid:
                    self.user_left.emit(sid)
                    
            elif msg_type == 'disconnect':
                reason = data.get('reason')
                if reason == 'admin_closed':
                    self.admin_closed.emit()
                    
        except json.JSONDecodeError:
            self.connection_error.emit('Invalid message format')

    async def _listen_loop(self):
        try:
            while True:
                try:
                    message = await self.ws.recv()
                    await self._handle_message(message)
                except websockets.exceptions.ConnectionClosedOK:
                    break
                except websockets.exceptions.ConnectionClosedError as e:
                    self.connection_error.emit(f"连接异常关闭: {str(e)}")
                    break
                except Exception as e:
                    self.connection_error.emit(f"消息处理错误: {str(e)}")
        except asyncio.CancelledError:
            pass
        finally:
            self.disconnected.emit()

    async def _close_ws(self):
        if self.ws:
            try:
                await self.ws.close()
            except:
                pass
            self.ws = None

    def stop(self):
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
            
    def close(self):
        self.stop()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self._connect_ws())
        except Exception as e:
            self.connection_error.emit(f"连接失败：{str(e)}")
            self.loop.close()
            return

        try:
            listen_task = self.loop.create_task(self._listen_loop())
        except Exception as e:
            self.connection_error.emit(f"启动监听失败：{str(e)}")
            self.loop.close()
            return

        try:
            self.loop.run_forever()
        finally:
            # 清理
            self.loop.run_until_complete(self._close_ws())
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    def send_message(self, data: dict):
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
