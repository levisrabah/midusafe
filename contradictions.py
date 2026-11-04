"""Contradiction detection between reports in an incident cluster.

For one incident, the Meta model compares its report against reports from
linked incidents (confirmed or pending duplicate links) and flags genuinely
conflicting factual claims. Every citation must reference a report id that
was actually provided; unknown ids are rejected. Advisory only: conflicts
are flagged for a human to verify on the ground, never auto-resolved.
"""

import json
import time

from meta_service import MetaAPIError, meta_service
from sentinel_schemas import (CONTRADICTION_JSON_SCHEMA,
                              CONTRADICTION_SYSTEM_PROMPT,
                              ContradictionReport)
from sentinel_store import get_incident, get_report, log_trace, now_iso


def cluster_incidents(incident_id):
    """Return (incident, [linked incidents]) for the cluster. Raises ValueError."""
    from sentinel_store import list_duplicate_links  # avoid import cycle at load
    incident = get_incident(incident_id)
    if not incident:
        raise ValueError(f"Unknown incident {incident_id}")
    others = {}
    for link in list_duplicate_links():
        other = None
        if link["incident_a"] == incident_id:
            other = link["incident_b"]
        elif link["incident_b"] == incident_id:
            other = link["incident_a"]
        if other and other != incident_id and other not in others:
            inc = get_incident(other)
            if inc:
                others[other] = inc
    return incident, list(others.values())


def build_contradiction_context(incident, linked_incidents):
    """Render stored evidence for the prompt. Returns (prompt_text, valid_ids)."""
    chunks = []
    valid_ids = set()
    for inc in [incident, *linked_incidents]:
        rep = get_report(inc["report_id"]) or {}
        valid_ids.add(inc["report_id"])
        ex = inc["extraction"]
        chunks.append(
            f"[report id: {inc['report_id']}] "
            f"type={ex.get('incident_type')} lang={ex.get('detected_language')} "
            f"reported_at={inc.get('created_at')}\n"
            f"Original: {rep.get('message', ex.get('original_report', ''))}\n"
            f"Summary: {ex.get('translated_summary')}"
        )
    prompt = ("Compare these reports from one incident cluster and list any "
              "conflicting factual claims:\n\n" + "\n\n".join(chunks))
    return prompt, valid_ids


def generate_contradictions(incident_id, service=None):
    """Run the contradiction check. Returns (report_dict, method).

    method is "meta" (model checked the cluster), "skipped_single_report"
    (fewer than 2 reports to compare), or "fallback" (check unavailable;
    empty list with a note - never fabricated conflicts).
    """
    service = service or meta_service
    incident, linked = cluster_incidents(incident_id)
    if not linked:
        return {
            "incident_id": incident_id,
            "contradictions": [],
            "checked_at": now_iso(),
            "note": "Only one report in this cluster; nothing to compare.",
        }, "skipped_single_report"

    prompt, valid_ids = build_contradiction_context(incident, linked)
    model = getattr(service, "model", "stub")
    t0 = time.perf_counter()
    try:
        data = service.chat(
            messages=[{"role": "system", "content": CONTRADICTION_SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_schema",
                             "json_schema": {"name": "ContradictionCheck",
                                             "schema": CONTRADICTION_JSON_SCHEMA}},
        )
        content = service.extract_chat_text(data)
        raw = json.loads(content)
        for c in raw.get("contradictions", []):
            for rid in (c.get("report_id_a"), c.get("report_id_b")):
                if rid not in valid_ids:
                    raise ValueError(f"cited unknown report id: {rid}")
        report = ContradictionReport(
            incident_id=incident_id, checked_at=now_iso(),
            contradictions=raw.get("contradictions", []))
        log_trace(incident_id, "contradiction_check", model,
                  (time.perf_counter() - t0) * 1000, True,
                  f"{len(report.contradictions)} conflict(s)")
        return report.model_dump(), "meta"
    except (MetaAPIError, ValueError, json.JSONDecodeError) as e:
        log_trace(incident_id, "contradiction_check", model,
                  (time.perf_counter() - t0) * 1000, False, str(e)[:200])
        return {
            "incident_id": incident_id,
            "contradictions": [],
            "checked_at": now_iso(),
            "note": f"Contradiction check unavailable ({str(e)[:120]}).",
        }, "fallback"
