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
        tasks = []
        for client_info in room["clients"].values():
            ws_client = client_info["ws"]
            tasks.append(asyncio.create_task(ws_client.send(msg)))
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
        display_name = data.get("display_name", "")
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
                    room["clients"][sid] = {
                        "ws": ws, 
                        "display_name": display_name
                    }
                    await ws.send(json.dumps({"type":"joined","sid":sid}))
                    await send_to_admin(token, {
                        "type": "user_joined",
                        "sid": sid,
                        "display_name": display_name
                    })

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

    elif msg_type == "name_update":
        token = data.get("token")
        if not token:
            await ws.send(json.dumps({"type": "error", "message": "No token in name_update"}))
            return

        room = rooms.get(token)
        if not room:
            await ws.send(json.dumps({"type": "error", "message": "Room not found"}))
            return

        old_name = data.get("old_name", "")
        new_name = data.get("new_name", "")
        user_sid = data.get("sid", "")

        if user_sid in room["clients"] and room["clients"][user_sid]["ws"] == ws: 
            room["clients"][user_sid]["display_name"] = new_name   ### ← (需要修改，更新display_name)

            if room["admin"]:
                await send_to_admin(token, {
                    "type": "name_update",
                    "old_name": old_name,
                    "new_name": new_name,
                    "sid": user_sid
                })
        else:
            await ws.send(json.dumps({"type": "error", "message": "Invalid sid for name_update"}))

    elif msg_type == "name_update_confirmed":
        token = data.get("token")
        old_name = data.get("old_name", "")
        new_name = data.get("new_name", "")
        sid = data.get("sid", "")

        room = rooms.get(token)
        if not room:
            return

        if sid in room["clients"]:
            ws_pl = room["clients"][sid]["ws"]
            await ws_pl.send(json.dumps({
                "type": "name_update_confirmed",
                "old_name": old_name,
                "new_name": new_name
            }))

    elif msg_type == "dice_result":
        token = data.get("token")
        dice_text = data.get("dice_text", "")
        if token in rooms:
            await broadcast_to_clients(token, {
                "type": "dice_result",
                "dice_text": dice_text
            })

async def remove_connection(ws):
    for token, room in list(rooms.items()):
        if room["admin"] == ws:
            await broadcast_to_clients(token, {"type":"disconnect","reason":"admin closed"})
            del rooms[token]
            break
        else:
            for sid, cws_dict in list(room["clients"].items()):
                if cws_dict["ws"] == ws:
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
