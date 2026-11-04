"""Follow-up drafts in the reporter's own language (human-in-the-loop).

For incidents with missing information, the Meta model drafts ONE short
follow-up question in the reporter's detected language (en/sw/sh/...).
Drafts land in an approval queue: a responder approves, edits, or discards
each one. Approved drafts are only marked "approved, ready to send" -
nothing is ever sent anywhere. Every action is audit-logged.
"""

import json
import time

from meta_service import MetaAPIError, meta_service
from sentinel_schemas import (FOLLOWUP_JSON_SCHEMA, FOLLOWUP_SYSTEM_PROMPT,
                              FollowupDraftText)
from sentinel_store import get_incident, log_trace, now_iso

LANG_NAMES = {"en": "English", "sw": "Swahili", "sh": "Sheng"}


def generate_followup(incident_id, service=None):
    """Draft one follow-up question. Returns (draft_dict, method).

    method is "meta", "fallback" (stored question reused verbatim, no model
    prose), or "skipped_complete" (nothing missing). Raises ValueError for
    unknown incidents.
    """
    service = service or meta_service
    incident = get_incident(incident_id)
    if not incident:
        raise ValueError(f"Unknown incident {incident_id}")
    ex = incident["extraction"]
    lang = ex.get("detected_language") or "en"
    missing = ex.get("missing_information") or []
    questions = ex.get("follow_up_questions") or []
    if not missing and not questions:
        return {
            "incident_id": incident_id,
            "language": lang,
            "draft_text": "",
            "created_at": now_iso(),
            "note": "Nothing missing; no follow-up needed.",
        }, "skipped_complete"

    lang_name = LANG_NAMES.get(lang, lang)
    prompt = (
        f"Reporter language: {lang_name} ({lang}).\n"
        f"Incident summary: {ex.get('translated_summary')}\n"
        f"Original report: {ex.get('original_report')}\n"
        f"Missing information: {'; '.join(missing) or 'none listed'}\n"
        f"Candidate questions: {' | '.join(questions) or 'none'}\n\n"
        f"Write the follow-up question in {lang_name}."
    )
    model = getattr(service, "model", "stub")
    t0 = time.perf_counter()
    try:
        data = service.chat(
            messages=[{"role": "system", "content": FOLLOWUP_SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_schema",
                             "json_schema": {"name": "FollowupDraft",
                                             "schema": FOLLOWUP_JSON_SCHEMA}},
        )
        raw = json.loads(service.extract_chat_text(data))
        draft = FollowupDraftText.model_validate(raw)
        if draft.language != lang:
            raise ValueError(
                f"draft in '{draft.language}', reporter uses '{lang}'")
        log_trace(incident_id, "followup_draft", model,
                  (time.perf_counter() - t0) * 1000, True, f"lang={lang}")
        return {
            "incident_id": incident_id,
            "language": lang,
            "draft_text": draft.draft_text,
            "created_at": now_iso(),
        }, "meta"
    except (MetaAPIError, ValueError, json.JSONDecodeError) as e:
        log_trace(incident_id, "followup_draft", model,
                  (time.perf_counter() - t0) * 1000, False, str(e)[:200])
        fallback_text = questions[0] if questions else f"Please confirm: {missing[0]}"
        return {
            "incident_id": incident_id,
            "language": "en",
            "draft_text": fallback_text,
            "created_at": now_iso(),
            "note": f"Model draft unavailable ({str(e)[:120]}); "
                    "reused stored question instead.",
        }, "fallback"
