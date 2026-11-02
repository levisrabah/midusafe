"""Evidence-backed intelligence briefs (Meta-generated, server-validated).

Every claim must cite source report ids that were actually provided.
If citation validation fails, we fall back to a locally built brief that
only quotes stored evidence - never model prose without sources.
"""

import json

from meta_service import MetaAPIError, meta_service
from sentinel_schemas import (BRIEF_JSON_SCHEMA, BRIEF_SYSTEM_PROMPT,
                              IntelligenceBrief)
from sentinel_store import get_incident, get_report, list_audit, now_iso

BANNED_MEDICAL_PHRASES = (
    "take aspirin", "take ibuprofen", "take antibiotics", "prescribe",
    "dosage", "inject ", "perform surgery", "diagnose ",
)


def _has_medical_advice(text):
    lowered = (text or "").lower()
    return any(p in lowered for p in BANNED_MEDICAL_PHRASES)


def build_brief_context(incident, linked_incidents):
    """Render stored evidence for the prompt. Returns (prompt_text, valid_ids)."""
    chunks = []
    valid_ids = set()
    for inc in [incident, *linked_incidents]:
        rep = get_report(inc["report_id"]) or {}
        valid_ids.add(inc["report_id"])
        ex = inc["extraction"]
        chunks.append(
            f"[report id: {inc['report_id']}] "
            f"type={ex.get('incident_type')} severity={ex.get('severity')} "
            f"urgency={ex.get('urgency')} lang={ex.get('detected_language')} "
            f"place={ex.get('location_mentioned') or 'not stated'} "
            f"reported_at={inc.get('created_at')}\n"
            f"Original: {rep.get('message', ex.get('original_report', ''))}\n"
            f"Summary: {ex.get('translated_summary')}\n"
            f"Missing info: {', '.join(ex.get('missing_information', [])) or 'none listed'}"
        )
    prompt = ("Write an intelligence brief for incident "
              f"{incident['id']} from these source reports:\n\n" + "\n\n".join(chunks))
    return prompt, valid_ids


def _validate_citations(brief_dict, valid_ids):
    for ev in brief_dict.get("evidence", []):
        for rid in ev.get("source_report_ids", []):
            if rid not in valid_ids:
                return False, rid
    return True, None


def _fallback_brief(incident, linked_incidents, reason):
    """Locally built brief quoting only stored evidence (no model prose)."""
    ex = incident["extraction"]
    evidence = []
    for inc in [incident, *linked_incidents]:
        e = inc["extraction"]
        evidence.append({
            "claim": f"{e.get('incident_type')} reported: {e.get('translated_summary')}",
            "source_report_ids": [inc["report_id"]],
        })
    return {
        "incident_id": incident["id"],
        "what_happened": f"Model brief unavailable ({reason}); showing stored evidence only. "
                          f"Primary report: {ex.get('translated_summary')}",
        "where": (incident.get("resolved_place")
                  or ex.get("location_mentioned") or "location not stated"),
        "when_reported": incident.get("created_at", ""),
        "evidence": evidence,
        "unknowns": list(ex.get("missing_information", [])) or ["Full situation unclear"],
        "to_verify": list(ex.get("follow_up_questions", [])) or ["Verify location and severity on site"],
        "next_steps": ["Human responder to review the source reports above before any action."],
        "generated_at": now_iso(),
    }


def generate_brief(incident_id, service=None):
    """Generate + validate a brief for an incident. Returns (brief_dict, method)."""
    service = service or meta_service
    incident = get_incident(incident_id)
    if not incident:
        raise ValueError(f"Unknown incident {incident_id}")
    linked = _linked_incidents(incident_id)
    prompt, valid_ids = build_brief_context(incident, linked)

    try:
        data = service.chat(
            messages=[{"role": "system", "content": BRIEF_SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_schema",
                             "json_schema": {"name": "IntelBrief",
                                             "schema": BRIEF_JSON_SCHEMA}},
        )
        content = service.extract_chat_text(data)
        brief_raw = json.loads(content)
        ok, bad = _validate_citations(brief_raw, valid_ids)
        if not ok:
            raise ValueError(f"cited unknown report id: {bad}")
        blob = json.dumps(brief_raw)
        if _has_medical_advice(blob):
            raise ValueError("brief contained medical advice; rejected")
        brief = IntelligenceBrief(incident_id=incident_id,
                                  generated_at=now_iso(), **brief_raw)
        return brief.model_dump(), "meta"
    except (MetaAPIError, ValueError, json.JSONDecodeError) as e:
        return _fallback_brief(incident, linked, str(e)[:120]), "fallback"


def _linked_incidents(incident_id):
    from sentinel_store import list_duplicate_links  # avoid import cycle at load
    linked = []
    for link in list_duplicate_links(status="confirmed"):
        other = None
        if link["incident_a"] == incident_id:
            other = link["incident_b"]
        elif link["incident_b"] == incident_id:
            other = link["incident_a"]
        if other:
            inc = get_incident(other)
            if inc:
                linked.append(inc)
    return linked
