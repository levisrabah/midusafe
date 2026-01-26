import os
import json
import uuid
import re
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from triage import analyze_report

app = FastAPI(title="MIDUSAFE Command Center")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. Real-time Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()
alerts_db = []

# --- 2. Data Models ---
class IncidentReport(BaseModel):
    message: str
    location: str = "Nairobi, Kenya" # Default for the hackathon context
    lat: float = None
    lng: float = None

# --- 3. Helper: Clean LLM Output ---
def clean_json_string(raw_string):
    """Removes markdown code blocks if the AI includes them."""
    cleaned = re.sub(r'```json\s?|\s?```', '', raw_string).strip()
    return json.loads(cleaned)

# --- 4. Endpoints ---

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/report")
async def create_report(report: IncidentReport):
    try:
        # Get AI analysis
        raw_ai_response = analyze_report(report.message)
        ai_data = clean_json_string(raw_ai_response)
        
        new_alert = {
            "id": str(uuid.uuid4()),
            "message": report.message,
            "analysis": ai_data,
            "location": {
                "lat": report.lat if report.lat is not None else ai_data.get("location_lat", 0.0),
                "lng": report.lng if report.lng is not None else ai_data.get("location_lng", 0.0)
            },
            "disaster_type": ai_data.get("type", "other"),
            "urgency": ai_data.get("urgency", 5),
            "confidence": ai_data.get("confidence", 0.8),
            "summary": ai_data.get("summary", "Emergency report received"),
            "timestamp": "Just now"
        }
        
        alerts_db.insert(0, new_alert)
        
        # PUSH to all connected dashboards instantly!
        await manager.broadcast(new_alert)
        
        return new_alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts")
async def get_alerts():
    return alerts_db

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)