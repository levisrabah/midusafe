"""Sentinel pipeline: report -> Meta extract -> validate -> store -> dup-check.

Synchronous core (`process_report_sync`) so tests and the seed script get
deterministic results; main.py runs it in a background task by default.
"""

import json
import logging
import time

from pydantic import ValidationError

import duplicates as dup
import gazetteer
import sentinel_store as store
from meta_service import MetaAPIError, meta_service
from sentinel_schemas import (EXTRACTION_JSON_SCHEMA, EXTRACTION_SYSTEM_PROMPT,
                              IncidentExtraction)

logger = logging.getLogger("sentinel.pipeline")


def extract_with_meta(message, location_hint=None, service=None):
    """Call Meta for structured extraction; returns validated IncidentExtraction."""
    service = service or meta_service
    user_content = message
    if location_hint:
        user_content += f"\n\n[Reporter-provided location hint: {location_hint}]"
    data = service.chat(
        messages=[{"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                  {"role": "user", "content": user_content}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "IncidentExtraction",
                                         "schema": EXTRACTION_JSON_SCHEMA}},
    )
    content = service.extract_chat_text(data)
    try:
        raw = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model returned invalid JSON: {e}. Raw: {content[:300]}")
    try:
        return IncidentExtraction.model_validate(raw)
    except ValidationError as e:
        raise ValueError(f"Model output failed schema validation: {e}")


def process_report_sync(message, location_hint=None, is_simulated=False,
                        service=None, voice_trace_id=None):
    """Full pipeline for one report. Returns stored incident dict + dup candidates."""
    service = service or meta_service
    model = getattr(service, "model", "stub")
    t0 = time.perf_counter()
    try:
        extraction = extract_with_meta(message, location_hint, service=service)
    except ValueError as e:
        # No incident exists yet; record the failed extraction unlinked.
        store.log_trace(None, "extraction", model,
                        (time.perf_counter() - t0) * 1000, False, str(e)[:200])
        raise
    latency_ms = (time.perf_counter() - t0) * 1000

    display, lat, lng, resolved = gazetteer.resolve_from_parts(
        location_hint, extraction.location_mentioned, message)

    report_id = store.save_report(message, location_hint,
                                  is_simulated=is_simulated)
    incident_id = store.new_id("inc_")
    store.save_incident(
        incident_id, report_id, extraction.model_dump(),
        {"resolved": resolved, "lat": lat, "lng": lng, "place": display},
        is_simulated=is_simulated)
    store.log_audit("report_submitted", "incident", incident_id,
                    f"type={extraction.incident_type} lang={extraction.detected_language} "
                    f"resolved={resolved} simulated={bool(is_simulated)}",
                    actor="system")
    store.log_trace(incident_id, "extraction", model, latency_ms, True,
                    f"type={extraction.incident_type} lang={extraction.detected_language}")
    if voice_trace_id:
        store.claim_trace(voice_trace_id, incident_id)

    incident = store.get_incident(incident_id)
    candidates = dup.find_candidates(incident, store.list_incidents(limit=500))
    for cand in candidates:
        store.save_duplicate_candidate(cand["incident_id"], cand["other_incident_id"],
                                       cand["score"], cand["reasons"])
    return incident, candidates
