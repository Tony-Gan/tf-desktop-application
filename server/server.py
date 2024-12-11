import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosed

rooms = {}
#  rooms[token] = {
#     "admin": websocket or None,
#     "admin_sid": str,
#     "clients": { "sid": websocket },
#     "typing_timer": asyncio.Task or None,
#     "last_content": str
# }
global_sid_counter = 0

def get_new_sid():
    global global_sid_counter
    global_sid_counter += 1
    return str(global_sid_counter)

async def broadcast_to_clients(token, message):
    room = rooms.get(token)
    if room and room["clients"]:
        msg = json.dumps(message)
        tasks = [asyncio.create_task(ws.send(msg)) for ws in room["clients"].values()]
        if tasks:
            await asyncio.wait(tasks)

async def send_to_admin(token, message):
    room = rooms.get(token)
    if room and room["admin"]:
        await room["admin"].send(json.dumps(message))

async def handle_typing_timeout(token):
    room = rooms.get(token)
    if room and room["admin"] and room["last_content"] is not None:
        update_msg = {
            "type": "update",
            "content": room["last_content"]
        }
        await broadcast_to_clients(token, update_msg)

async def handle_message(ws, msg):
    data = json.loads(msg)
    msg_type = data.get("type")

    if msg_type == "join":
        role = data.get("role")
        token = data.get("token")
        if not token:
            await ws.send(json.dumps({"type":"error","message":"no token provided"}))
            return

        if token not in rooms:
            if role == "admin":
                sid = get_new_sid()
                rooms[token] = {
                    "admin": ws,
                    "admin_sid": sid,
                    "clients": {},
                    "typing_timer": None,
                    "last_content": ""
                }
                await ws.send(json.dumps({"type":"joined","sid":sid}))
            else:
                await ws.send(json.dumps({"type":"error","message":"no such room"}))
        else:
            room = rooms[token]
            if role == "admin":
                if room["admin"] is not None and room["admin"] != ws:
                    await ws.send(json.dumps({"type":"error","message":"admin already exists"}))
                else:
                    await ws.send(json.dumps({"type":"error","message":"admin already set"}))
            else:
                if room["admin"] is None:
                    await ws.send(json.dumps({"type":"error","message":"no admin in this room"}))
                else:
                    sid = get_new_sid()
                    room["clients"][sid] = ws
                    await ws.send(json.dumps({"type":"joined","sid":sid}))
                    await send_to_admin(token, {"type":"user_joined","sid":sid})

    elif msg_type == "typing":
        token = data.get("token")
        content = data.get("content","")
        if token in rooms:
            room = rooms[token]
            if room["admin"] == ws:
                room["last_content"] = content
                if room["typing_timer"] and not room["typing_timer"].done():
                    room["typing_timer"].cancel()
                room["typing_timer"] = asyncio.create_task(
                    asyncio.sleep(2)
                )
                def done_callback(task):
                    asyncio.create_task(handle_typing_timeout(token))
                room["typing_timer"].add_done_callback(done_callback)

async def remove_connection(ws):
    for token, room in list(rooms.items()):
        if room["admin"] == ws:
            await broadcast_to_clients(token, {"type":"disconnect","reason":"admin closed"})
            del rooms[token]
            break
        else:
            for sid, cws in list(room["clients"].items()):
                if cws == ws:
                    del room["clients"][sid]
                    if room["admin"]:
                        await send_to_admin(token, {"type":"user_left","sid":sid})
                    break

async def handler(ws):
    try:
        async for message in ws:
            await handle_message(ws, message)
    except ConnectionClosed:
        pass
    finally:
        await remove_connection(ws)

async def main():
    async with websockets.serve(handler, "", 8765):
        print("Server started on ws://0.0.0.0:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
