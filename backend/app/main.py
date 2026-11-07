from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import database
from .neural_network import GestureRecognizer

app = FastAPI(title="AirMotion AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database.initialize_database()
recognizer = GestureRecognizer()
studio_clients = set()
navigator_clients = set()

GESTURES = ["UP", "DOWN", "LEFT", "RIGHT", "CIRCLE", "SHAKE", "UNKNOWN"]
ACTIONS = [
    "SCROLL_UP",
    "SCROLL_DOWN",
    "GO_BACK",
    "GO_FORWARD",
    "NEW_TAB",
    "CLOSE_TAB",
    "RELOAD_PAGE",
    "NONE",
]

DEFAULT_MAPPINGS = {
    "UP": "SCROLL_UP",
    "DOWN": "SCROLL_DOWN",
    "LEFT": "GO_BACK",
    "RIGHT": "GO_FORWARD",
    "CIRCLE": "NEW_TAB",
    "SHAKE": "RELOAD_PAGE",
    "UNKNOWN": "NONE",
}


class PredictionRequest(BaseModel):
    window: list[list[float]]
    device_id: str = "simulator"


class MappingUpdate(BaseModel):
    mappings: dict[str, str]


class PredictionResponse(BaseModel):
    gesture_id: str
    action_id: str
    confidence: float
    device_id: str
    detected_at: str
    event_id: str
    sequence_number: int


def create_event_payload(gesture_id: str, confidence: float, device_id: str):
    return {
        "event_id": str(uuid4()),
        "gesture_id": gesture_id,
        "confidence": float(confidence),
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "device_id": device_id,
        "sequence_number": int(datetime.now(timezone.utc).timestamp() * 1000),
    }


async def emit_event(event):
    event_payload = database.save_event(event)
    event_json = __import__("json").dumps(event_payload)

    for client in list(studio_clients):
        try:
            await client.send_text(event_json)
        except Exception:
            pass

    for client in list(navigator_clients):
        if event_payload.get("action_id"):
            try:
                await client.send_text(__import__("json").dumps({"action_id": event_payload["action_id"]}))
            except Exception:
                pass


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_loaded": True,
        "message": "neural_network: loaded",
    }


@app.get("/api/status")
def get_status():
    return {
        "status": "ok",
        "model_loaded": True,
        "gesture_count": len(GESTURES),
        "supported_actions": ACTIONS,
    }


@app.get("/api/events")
def fetch_events(limit: int = 100):
    return database.get_events(limit=limit)


@app.get("/api/mappings")
def fetch_mappings():
    return database.get_mappings()


@app.put("/api/mappings")
def save_mappings(payload: MappingUpdate):
    mappings = payload.mappings
    normalized = {}
    for key, val in mappings.items():
        if key in GESTURES:
            normalized[key] = val
    saved = database.update_mappings(normalized)
    return saved


@app.post("/api/predict")
async def predict(payload: PredictionRequest):
    if len(payload.window) != 50 or len(payload.window[0]) != 6:
        raise HTTPException(status_code=400, detail="Expected window shape (50, 6)")

    result = recognizer.predict(payload.window)
    gesture_id = result["gesture_id"]
    confidence = result["confidence"]

    event = create_event_payload(gesture_id, confidence, payload.device_id)
    event["action_id"] = database.get_mappings().get(gesture_id, "NONE")
    await emit_event(event)

    return {
        "gesture_id": gesture_id,
        "action_id": event["action_id"],
        "confidence": confidence,
        "device_id": payload.device_id,
        "detected_at": event["detected_at"],
        "event_id": event["event_id"],
        "sequence_number": event["sequence_number"],
    }


@app.post("/api/demo")
async def demo_predict():
    import random
    import numpy as np

    gesture = random.choice(["UP", "DOWN", "LEFT", "RIGHT", "CIRCLE", "SHAKE", "UNKNOWN"])
    t = np.linspace(0, 1, 50)
    window = np.zeros((50, 6), dtype=np.float32)
    window[:, 2] = 9.81
    amplitude = 2.5

    if gesture == "UP":
        window[:, 2] += amplitude * np.sin(np.pi * t)
        window[:, 4] = 70 * np.sin(np.pi * t)
    elif gesture == "DOWN":
        window[:, 2] -= amplitude * np.sin(np.pi * t)
        window[:, 4] = -70 * np.sin(np.pi * t)
    elif gesture == "LEFT":
        window[:, 0] -= amplitude * np.sin(np.pi * t)
        window[:, 3] = -65 * np.sin(np.pi * t)
    elif gesture == "RIGHT":
        window[:, 0] += amplitude * np.sin(np.pi * t)
        window[:, 3] = 65 * np.sin(np.pi * t)
    elif gesture == "CIRCLE":
        window[:, 0] = amplitude * np.sin(2 * np.pi * t)
        window[:, 1] = amplitude * np.cos(2 * np.pi * t)
    elif gesture == "SHAKE":
        window[:, 0] += amplitude * np.sin(2 * np.pi * 4 * t)
        window[:, 1] += amplitude * np.cos(2 * np.pi * 4 * t)

    result = recognizer.predict(window)
    event = create_event_payload(result["gesture_id"], result["confidence"], "demo")
    event["action_id"] = database.get_mappings().get(result["gesture_id"], "NONE")
    await emit_event(event)

    return {
        "gesture_id": result["gesture_id"],
        "action_id": event["action_id"],
        "confidence": result["confidence"],
        "device_id": "demo",
        "detected_at": event["detected_at"],
        "event_id": event["event_id"],
        "sequence_number": event["sequence_number"],
    }


@app.websocket("/ws/studio")
async def studio_socket(websocket: WebSocket):
    await websocket.accept()
    studio_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        studio_clients.discard(websocket)


@app.websocket("/ws/navigator")
async def navigator_socket(websocket: WebSocket):
    await websocket.accept()
    navigator_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        navigator_clients.discard(websocket)
