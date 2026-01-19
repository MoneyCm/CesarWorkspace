from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio, json, time

app = FastAPI(title="Panic Backend (Demo)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Almacenamiento en memoria (demo)
ALERTS: List[dict] = []
SUBSCRIBERS: List[asyncio.Queue] = []


@app.get("/api/alerts")
def list_alerts(limit: int = 100, offset: int = 0):
    return ALERTS[offset : offset + limit]


@app.post("/api/alerts")
async def create_alert(
    request: Request,
    payload: Optional[UploadFile] = File(None),
    media: Optional[List[UploadFile]] = File(None),
):
    # Permite JSON directo o multipart con campo 'payload' (application/json)
    if payload is None:
        body = await request.body()
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            return JSONResponse({"error": "invalid json"}, status_code=400)
    else:
        data = json.loads((await payload.read()).decode("utf-8"))

    data.setdefault("id", int(time.time() * 1000))
    data.setdefault("kind", "panic")
    data.setdefault("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    if media:
        data["media"] = [m.filename for m in media]
    ALERTS.insert(0, data)

    # Notificar por SSE
    await broadcast({"type": "alert", "data": data})
    return {"id": data["id"]}


@app.post("/api/broadcasts")
async def send_broadcast(payload: dict):
    msg = {"type": "broadcast", "message": payload.get("message", "")}
    await broadcast(msg)
    return {"ok": True}


@app.get("/api/events")
async def sse_events():
    queue: asyncio.Queue = asyncio.Queue()
    SUBSCRIBERS.append(queue)

    async def event_stream():
        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if queue in SUBSCRIBERS:
                SUBSCRIBERS.remove(queue)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


async def broadcast(msg: dict):
    for q in list(SUBSCRIBERS):
        try:
            q.put_nowait(msg)
        except Exception:
            pass

