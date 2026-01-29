import os
import json
import uuid
import re
import time
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
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
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"WebSocket send error: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

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

@app.get("/health")
async def health_check():
    return {"ok": True}

@app.post("/report")
async def create_report(report: IncidentReport, background_tasks: BackgroundTasks):
    start_time = time.time()
    alert_id = str(uuid.uuid4())
    
    print(f"[{time.strftime('%H:%M:%S')}] 📥 Received report: {report.message[:50]}...")
    
    # Return immediately, process AI in background
    background_tasks.add_task(process_report_background, report, alert_id)
    
    elapsed = (time.time() - start_time) * 1000
    print(f"[{time.strftime('%H:%M:%S')}] ✅ Report accepted in {elapsed:.1f}ms - ID: {alert_id}")
    
    return {
        "status": "accepted",
        "id": alert_id,
        "message": "Report queued for AI processing"
    }

async def process_report_background(report: IncidentReport, alert_id: str):
    start_time = time.time()
    try:
        print(f"[{time.strftime('%H:%M:%S')}] 🤖 Starting AI analysis for {alert_id}")
        
        # Get AI analysis
        ai_start = time.time()
        raw_ai_response = analyze_report(report.message)
        ai_elapsed = (time.time() - ai_start) * 1000
        print(f"[{time.strftime('%H:%M:%S')}] 🧠 AI analysis completed in {ai_elapsed:.1f}ms")
        
        ai_data = clean_json_string(raw_ai_response)
        
        new_alert = {
            "id": alert_id,
            "message": report.message,
            "analysis": ai_data,
            "detected_language": ai_data.get("detected_language", "english"),
            "original_text": ai_data.get("original_text", report.message),
            "english_summary": ai_data.get("english_summary", ai_data.get("translated_summary", "Emergency report received")),
            "urgency_score": ai_data.get("urgency_score", ai_data.get("urgency", 5)),
            "suggested_actions": ai_data.get("suggested_actions", "Deploy emergency response team"),
            "cultural_context": ai_data.get("cultural_context", ""),
            "location": {
                "lat": report.lat if report.lat is not None else ai_data.get("location_lat", 0.0),
                "lng": report.lng if report.lng is not None else ai_data.get("location_lng", 0.0)
            },
            "disaster_type": ai_data.get("disaster_type", ai_data.get("type", "other")),
            "confidence": ai_data.get("confidence", 0.8),
            "summary": ai_data.get("english_summary", "Emergency report received"),
            "timestamp": "Just now"
        }
        
        alerts_db.insert(0, new_alert)
        
        # PUSH to all connected dashboards instantly!
        await manager.broadcast(new_alert)
        
        total_elapsed = (time.time() - start_time) * 1000
        print(f"[{time.strftime('%H:%M:%S')}] 📡 Alert broadcasted in {total_elapsed:.1f}ms total")
        
    except Exception as e:
        error_elapsed = (time.time() - start_time) * 1000
        print(f"[{time.strftime('%H:%M:%S')}] ❌ Background processing failed in {error_elapsed:.1f}ms: {str(e)}")

@app.get("/alerts")
async def get_alerts():
    return alerts_db

if __name__ == "__main__":
    import uvicorn
    print("System Audit Complete: Pan-African Resilience Engine Online")
    uvicorn.run(app, host="0.0.0.0", port=8000)