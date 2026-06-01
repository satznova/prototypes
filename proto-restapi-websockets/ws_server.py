# ws_server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import random, time, asyncio

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Track all connected clients
connected_clients: list[WebSocket] = []

def generate_notification():
    types = ["order", "alert", "message"]
    messages = {
        "order":   "New order #" + str(random.randint(1000, 9999)),
        "alert":   "CPU usage above 90%",
        "message": "You have a new message from user_" + str(random.randint(1, 50))
    }
    t = random.choice(types)
    return {"type": t, "text": messages[t], "time": time.time()}

# Background task — pushes to ALL clients every 3 seconds
async def auto_push():
    while True:
        await asyncio.sleep(3)
        if connected_clients:
            notif = generate_notification()
            # Push to every connected client instantly
            for ws in connected_clients.copy():
                try:
                    await ws.send_json(notif)
                except:
                    connected_clients.remove(ws)

@app.on_event("startup")
async def startup():
    asyncio.create_task(auto_push())

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    print(f"Client connected. Total: {len(connected_clients)}")

    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await ws.receive_text()
            print(f"Client says: {data}")
    except WebSocketDisconnect:
        connected_clients.remove(ws)
        print(f"Client disconnected. Total: {len(connected_clients)}")
