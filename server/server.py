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

# 全局SID计数器
global_sid_counter = 0

def get_new_sid():
    global global_sid_counter
    global_sid_counter += 1
    return str(global_sid_counter)

async def broadcast_to_clients(token, message):
    """向房间内所有clients广播消息"""
    room = rooms.get(token)
    if room and room["clients"]:
        msg = json.dumps(message)
        await asyncio.wait([ws.send(msg) for ws in room["clients"].values()])

async def send_to_admin(token, message):
    """向房间的admin发送消息"""
    room = rooms.get(token)
    if room and room["admin"]:
        await room["admin"].send(json.dumps(message))

async def handle_typing_timeout(token):
    # 在2秒防抖后执行的函数：向B广播最终内容
    room = rooms.get(token)
    if room and room["admin"] and room["last_content"] is not None:
        # 广播给B
        update_msg = {
            "type": "update",
            "content": room["last_content"]
        }
        await broadcast_to_clients(token, update_msg)

async def handle_message(ws, msg):
    # msg是JSON格式的字符串
    data = json.loads(msg)
    msg_type = data.get("type")

    if msg_type == "join":
        role = data.get("role")
        token = data.get("token")
        if not token:
            await ws.send(json.dumps({"type":"error","message":"no token provided"}))
            return

        # 检查房间
        if token not in rooms:
            # 若admin加入，创建新房间
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
                # 客户端试图加入一个不存在的房间
                await ws.send(json.dumps({"type":"error","message":"no such room"}))
        else:
            # 房间存在
            room = rooms[token]
            if role == "admin":
                # 已经有admin了？
                if room["admin"] is not None and room["admin"] != ws:
                    await ws.send(json.dumps({"type":"error","message":"admin already exists"}))
                else:
                    # 重复admin加入暂不处理，可扩展
                    await ws.send(json.dumps({"type":"error","message":"admin already set"}))
            else:
                # role = client
                if room["admin"] is None:
                    # 无admin
                    await ws.send(json.dumps({"type":"error","message":"no admin in this room"}))
                else:
                    sid = get_new_sid()
                    room["clients"][sid] = ws
                    # 通知client加入成功
                    await ws.send(json.dumps({"type":"joined","sid":sid}))
                    # 通知admin有新用户加入
                    await send_to_admin(token, {"type":"user_joined","sid":sid})

    elif msg_type == "typing":
        # 收到admin的typing消息
        token = data.get("token")
        content = data.get("content","")
        if token in rooms:
            room = rooms[token]
            if room["admin"] == ws:
                # 是admin发送的typing
                room["last_content"] = content
                # 重置定时器
                if room["typing_timer"] and not room["typing_timer"].done():
                    room["typing_timer"].cancel()
                # 设置2秒后触发广播
                room["typing_timer"] = asyncio.create_task(
                    asyncio.sleep(2)
                )
                # 在2秒后调用 handle_typing_timeout
                def done_callback(task):
                    # 任务完成后执行广播
                    asyncio.create_task(handle_typing_timeout(token))
                room["typing_timer"].add_done_callback(done_callback)

    # 可以扩展更多类型的消息，如 A 请求用户列表等
    # 当实现用户列表时，我们可以遍历 room["clients"].keys()


async def remove_connection(ws):
    # 查找ws属于哪个房间，并处理离线逻辑
    for token, room in list(rooms.items()):
        # 检查admin
        if room["admin"] == ws:
            # admin断开
            # 通知所有客户端admin离线
            await broadcast_to_clients(token, {"type":"disconnect","reason":"admin closed"})
            # 关闭房间
            del rooms[token]
            break
        else:
            # 检查clients
            for sid, cws in list(room["clients"].items()):
                if cws == ws:
                    # 这个client断开
                    del room["clients"][sid]
                    # 通知admin有用户离开
                    if room["admin"]:
                        await send_to_admin(token, {"type":"user_left","sid":sid})
                    break

async def handler(ws, path):
    try:
        async for message in ws:
            await handle_message(ws, message)
    except ConnectionClosed:
        pass
    finally:
        await remove_connection(ws)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
