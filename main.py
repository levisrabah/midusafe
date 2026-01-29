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
from urgency_intelligence import calculate_urgency_score, urgency_intelligence
from language_intelligence import detect_language_enhanced, language_intelligence as lang_intel
from disaster_severity import classify_disaster_severity, disaster_classifier

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
    base_urgency: int = None  # Base urgency from mock data
    disaster_type: str = None  # Disaster type from mock data
    severity: str = None  # Severity level from mock data

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
        
        # Enhanced language detection
        lang_detection = detect_language_enhanced(report.message)
        
        # Disaster severity classification
        disaster_type = report.disaster_type or ai_data.get("disaster_type", "other")
        severity_analysis = classify_disaster_severity(
            disaster_type=disaster_type,
            location=report.location,
            infrastructure_impact="moderate",  # Default, can be enhanced
            affected_population="medium",  # Default, can be enhanced
            season="normal",  # Default, can be enhanced
            confidence=ai_data.get("confidence", 0.8)
        )
        
        # Calculate intelligent urgency score
        ai_urgency = ai_data.get("urgency_score", ai_data.get("urgency", None))
        intelligent_urgency = calculate_urgency_score(
            report.message, 
            disaster_type, 
            report.location
        )
        
        # Use base_urgency from mock data if available, otherwise AI or intelligent fallback
        if report.base_urgency and report.base_urgency != 5:
            final_urgency = report.base_urgency
            urgency_source = "Mock Data"
        elif ai_urgency and ai_urgency != 5:
            final_urgency = ai_urgency
            urgency_source = "AI"
        else:
            final_urgency = intelligent_urgency
            urgency_source = "Intelligent Fallback"
        
        print(f"[{time.strftime('%H:%M:%S')}] 📊 Urgency scores - AI: {ai_urgency}, Intelligent: {intelligent_urgency}, Final: {final_urgency} ({urgency_source})")
        print(f"[{time.strftime('%H:%M:%S')}] 🌍 Language detected: {lang_detection['primary_language']} ({lang_detection['confidence']:.2f})")
        print(f"[{time.strftime('%H:%M:%S')}] ⚠️  Disaster severity: {severity_analysis['severity_level']} ({severity_analysis['severity_score']}/10)")
        
        new_alert = {
            "id": alert_id,
            "message": report.message,
            "analysis": ai_data,
            "detected_language": lang_detection['language_code'],
            "detected_language_label": lang_intel.get_language_display_name(lang_detection['language_code']),
            "language_flag": lang_intel.get_language_flag(lang_detection['language_code']),
            "language_confidence": lang_detection['confidence'],
            "code_switching": lang_detection['code_switching'],
            "emergency_detected": lang_detection['emergency_detected'],
            "original_text": ai_data.get("original_text", report.message),
            "english_summary": ai_data.get("english_summary", ai_data.get("translated_summary", "Emergency report received")),
            "urgency_score": final_urgency,
            "urgency": final_urgency,  # For frontend compatibility
            "urgency_source": urgency_source,
            "severity_analysis": severity_analysis,
            "severity_level": severity_analysis['severity_level'],
            "severity_score": severity_analysis['severity_score'],
            "disaster_category": severity_analysis['disaster_category'],
            "response_priority": severity_analysis['response_priority'],
            "cascade_risks": severity_analysis['cascade_risks'],
            "estimated_duration": severity_analysis['estimated_duration'],
            "regional_risk_factors": severity_analysis['regional_risk_factors'],
            "suggested_actions": ai_data.get("suggested_actions", "Deploy emergency response team"),
            "cultural_context": ai_data.get("cultural_context", ""),
            "location": {
                "lat": report.lat if report.lat is not None else ai_data.get("location_lat", 0.0),
                "lng": report.lng if report.lng is not None else ai_data.get("location_lng", 0.0)
            },
            "disaster_type": ai_data.get("disaster_type", ai_data.get("type", "other")),
            "confidence": ai_data.get("confidence", 0.8),
            "summary": ai_data.get("english_summary", "Emergency report received"),
            "timestamp": "Just now",
            "urgency_level": urgency_intelligence.get_urgency_level(final_urgency),
            "urgency_color": urgency_intelligence.get_urgency_color(final_urgency)
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