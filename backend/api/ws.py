"""
Step 10 — Real-time Dashboard Alert.

Simple in-memory WebSocket broadcaster. Every connected browser tab gets
pushed a JSON payload the moment alert_engine.raise_event() fires.
"""
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

_connections: list[WebSocket] = []


@router.websocket("/ws/events")
async def events_ws(websocket: WebSocket):
    await websocket.accept()
    _connections.append(websocket)
    try:
        while True:
            # keep the connection open; dashboard doesn't need to send anything
            await websocket.receive_text()
    except WebSocketDisconnect:
        _connections.remove(websocket)


def broadcast_event(event) -> None:
    payload = json.dumps({
        "event_id": event.id,
        "camera_id": event.camera_id,
        "track_id": event.track_id,
        "event_type": event.event_type,
        "alert_level": event.alert_level,
        "timestamp": event.timestamp.isoformat(),
        "snapshot": event.snapshot,
    })
    for ws in list(_connections):
        try:
            asyncio.create_task(ws.send_text(payload))
        except Exception:
            _connections.remove(ws)
