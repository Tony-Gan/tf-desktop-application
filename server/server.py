import logging
from dataclasses import dataclass
from typing import Dict, Set
import uuid

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

@dataclass
class TokenRoom:
    admin_sid: str
    connected_users: Set[str]

token_rooms: Dict[str, TokenRoom] = {}
sid_to_token: Dict[str, str] = {}

@socketio.on('connect')
def handle_connect():
    logging.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in sid_to_token:
        token = sid_to_token[sid]
        if token in token_rooms:
            room = token_rooms[token]
            if sid == room.admin_sid:
                # Admin disconnected, notify all users and clean up
                emit('admin_disconnected', room=token)
                for user_sid in room.connected_users:
                    if user_sid in sid_to_token:
                        leave_room(token, user_sid)
                        del sid_to_token[user_sid]
                del token_rooms[token]
            elif sid in room.connected_users:
                # User disconnected
                room.connected_users.remove(sid)
                leave_room(token, sid)
                emit('user_disconnected', {'sid': sid}, room=token)
        del sid_to_token[sid]

@socketio.on('register_admin')
def handle_admin_register(data):
    sid = request.sid
    token = str(uuid.uuid4())[:6]  # 生成唯一的6位token

    token_rooms[token] = TokenRoom(admin_sid=sid, connected_users=set())
    sid_to_token[sid] = token

    join_room(token)
    return {'token': token}

@socketio.on('join_room')
def handle_join_room(data):
    token = data.get('token')
    sid = request.sid

    if token not in token_rooms:
        return {'status': 'error', 'message': 'Invalid Token'}

    # 如果用户已经在其他房间，先离开那个房间
    if sid in sid_to_token:
        old_token = sid_to_token[sid]
        if old_token in token_rooms:
            leave_room(old_token)
            if sid in token_rooms[old_token].connected_users:
                token_rooms[old_token].connected_users.remove(sid)

    room = token_rooms[token]
    room.connected_users.add(sid)
    sid_to_token[sid] = token

    join_room(token)
    emit('user_joined', {'sid': sid}, room=token)
    return {'status': 'success'}

@socketio.on('admin_message')
def handle_admin_message(data):
    sid = request.sid
    if sid not in sid_to_token:
        return

    token = sid_to_token[sid]
    if token not in token_rooms or token_rooms[token].admin_sid != sid:
        return

    message = data.get('message', '')
    emit('message', {'message': message}, room=token)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)