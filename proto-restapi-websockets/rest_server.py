# rest_server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random, time

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# In-memory notification store
notifications = []
last_fetched = {}  # track per client what they last saw

def generate_notification():
    types = ["order", "alert", "message"]
    messages = {
        "order":   "New order #" + str(random.randint(1000, 9999)),
        "alert":   "CPU usage above 90%",
        "message": "You have a new message from user_" + str(random.randint(1, 50))
    }
    t = random.choice(types)
    return {"id": len(notifications)+1, "type": t, "text": messages[t], "time": time.time()}

# Background task — adds a notification every 3 seconds
import threading
def auto_generate():
    while True:
        time.sleep(3)
        notifications.append(generate_notification())

threading.Thread(target=auto_generate, daemon=True).start()

# Client must keep polling this endpoint
@app.get("/notifications")
def get_notifications(since: float = 0):
    new = [n for n in notifications if n["time"] > since]
    return {"notifications": new, "timestamp": time.time()}
