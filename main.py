import os
import json
import uuid
import re
import time
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from triage import analyze_report
from urgency_intelligence import calculate_urgency_score, urgency_intelligence
from language_intelligence import detect_language_enhanced, language_intelligence as lang_intel
from disaster_severity import classify_disaster_severity, disaster_classifier
# --- Sentinel (hackathon) imports ---
import sentinel_store as sstore
from sentinel_schemas import ReportIn
from sentinel_pipeline import process_report_sync
from meta_service import MetaAPIError
import briefs as sbriefs

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

# =====================================================================
# SENTINEL (hackathon) API - Meta-powered incident intelligence
# =====================================================================

def _sentinel_broadcast(incident: dict, candidates: list):
    """Shape a Sentinel incident for the live WebSocket feed.

    Includes legacy-compatible fields so the existing dashboard keeps
    working, plus the full Sentinel payload for new UI.
    """
    ex = incident["extraction"]
    return {
        "type": "sentinel_incident",
        "sentinel": True,
        "id": incident["id"],
        "report_id": incident["report_id"],
        "message": ex.get("original_report", ""),
        "summary": ex.get("translated_summary", ""),
        "disaster_type": ex.get("incident_type", "other"),
        "urgency": ex.get("urgency", 5),
        "urgency_score": ex.get("urgency", 5),
        "confidence": ex.get("confidence", 0.0),
        "timestamp": incident.get("created_at", ""),
        "location": {
            "lat": incident.get("latitude"),
            "lng": incident.get("longitude"),
            "resolved": bool(incident.get("location_resolved")),
            "place": incident.get("resolved_place"),
            "mentioned": ex.get("location_mentioned"),
        },
        "detected_language": ex.get("detected_language"),
        "severity": ex.get("severity"),
        "status": incident.get("status", "pending"),
        "is_simulated": bool(incident.get("is_simulated")),
        "duplicate_candidates": len(candidates),
        "incident": incident,
    }


async def _process_sentinel_background(message: str, location_hint, is_simulated: bool):
    try:
        incident, candidates = process_report_sync(
            message, location_hint, is_simulated=is_simulated)
        await manager.broadcast(_sentinel_broadcast(incident, candidates))
        print(f"📡 Sentinel incident {incident['id']} broadcasted "
              f"({len(candidates)} dup candidates)")
    except (MetaAPIError, ValueError) as e:
        print(f"❌ Sentinel processing failed: {e}")
        await manager.broadcast({"type": "sentinel_error", "error": str(e)[:300]})


@app.post("/api/sentinel/reports")
async def submit_sentinel_report(report: ReportIn, background_tasks: BackgroundTasks,
                                 sync: bool = False):
    """Submit a community report. sync=true processes inline (seed/tests)."""
    if sync:
        try:
            incident, candidates = process_report_sync(
                report.message, report.location_hint,
                is_simulated=report.is_simulated)
        except MetaAPIError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=502, detail=str(e))
        await manager.broadcast(_sentinel_broadcast(incident, candidates))
        return {"status": "processed", "incident": incident,
                "duplicate_candidates": candidates}
    background_tasks.add_task(_process_sentinel_background, report.message,
                              report.location_hint, report.is_simulated)
    return {"status": "accepted", "message": "Report queued for Meta AI processing"}


@app.get("/api/sentinel/incidents")
async def list_sentinel_incidents(limit: int = 200):
    return sstore.list_incidents(limit=limit)


@app.get("/api/sentinel/incidents/{incident_id}")
async def get_sentinel_incident(incident_id: str):
    inc = sstore.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc


@app.get("/api/sentinel/incidents/{incident_id}/brief")
async def get_sentinel_brief(incident_id: str, refresh: bool = False):
    if not refresh:
        cached = sstore.get_brief(incident_id)
        if cached:
            return {"brief": cached, "method": "cached"}
    try:
        brief, method = sbriefs.generate_brief(incident_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    sstore.save_brief(incident_id, brief)
    sstore.log_audit("brief_generated", "incident", incident_id, f"method={method}")
    return {"brief": brief, "method": method}


@app.get("/api/sentinel/duplicates")
async def list_sentinel_duplicates(status: Optional[str] = None):
    return sstore.list_duplicate_links(status=status)


class DuplicateDecision(BaseModel):
    decision: str  # confirmed | rejected


@app.post("/api/sentinel/duplicates/{link_id}/decision")
async def decide_sentinel_duplicate(link_id: str, body: DuplicateDecision):
    if body.decision not in ("confirmed", "rejected"):
        raise HTTPException(status_code=400, detail="decision must be confirmed|rejected")
    links = [l for l in sstore.list_duplicate_links() if l["id"] == link_id]
    if not links:
        raise HTTPException(status_code=404, detail="Duplicate link not found")
    sstore.decide_duplicate(link_id, body.decision)
    sstore.log_audit(f"duplicate_{body.decision}", "duplicate", link_id,
                     f"{links[0]['incident_a']} ~ {links[0]['incident_b']}")
    return {"status": body.decision, "id": link_id}


class VerificationAction(BaseModel):
    action: str  # verify | request_info | reclassify | priority | note
    value: Optional[str] = None


@app.post("/api/sentinel/incidents/{incident_id}/verify")
async def verify_sentinel_incident(incident_id: str, body: VerificationAction):
    """Human verification workflow. Every action is audit-logged. Never auto-dispatches."""
    inc = sstore.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    if body.action == "verify":
        sstore.update_incident(incident_id, status="verified")
    elif body.action == "request_info":
        sstore.update_incident(incident_id, status="needs_info")
    elif body.action == "reclassify":
        if not body.value:
            raise HTTPException(status_code=400, detail="reclassify needs value")
        sstore.update_incident(incident_id, classification=body.value)
    elif body.action == "priority":
        try:
            p = int(body.value)
            assert 1 <= p <= 10
        except (TypeError, ValueError, AssertionError):
            raise HTTPException(status_code=400, detail="priority needs 1-10")
        sstore.update_incident(incident_id, priority=p)
    elif body.action == "note":
        if not body.value:
            raise HTTPException(status_code=400, detail="note needs value")
    else:
        raise HTTPException(status_code=400,
                            detail="action must be verify|request_info|reclassify|priority|note")
    sstore.log_audit(body.action, "incident", incident_id, body.value or "")
    return {"status": "ok", "action": body.action,
            "incident": sstore.get_incident(incident_id)}


@app.get("/api/sentinel/stats")
async def sentinel_stats():
    return sstore.stats()


@app.get("/api/sentinel/audit")
async def sentinel_audit(limit: int = 200):
    return sstore.list_audit(limit=limit)


@app.get("/api/sentinel/health")
async def sentinel_health():
    from meta_service import meta_service
    return {"ok": True, "meta_configured": meta_service.configured,
            "meta_model": meta_service.model, "meta_base_url": meta_service.base_url}

if __name__ == "__main__":
    import uvicorn
    print("System Audit Complete: Pan-African Resilience Engine Online")
    uvicorn.run(app, host="0.0.0.0", port=8000)