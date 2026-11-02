"""Duplicate candidate detection. Advisory only: never merges anything.

Signals: incident type match, location match (resolved coords or same
mentioned place), report-time proximity, description word overlap.
"""

import math
import re
from datetime import datetime

STOPWORDS = frozenset(
    "the a an and or of to in on at for with is are was were be been it its "
    "this that these those there here here hapa kuna na ya wa kwa za ni".split()
)

TIME_WINDOW_HOURS = 6
SCORE_THRESHOLD = 0.45


def _tokens(text):
    words = re.findall(r"[a-zA-Z\u00C0-\u024F']+", (text or "").lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _hours_between(a_iso, b_iso):
    try:
        a = datetime.fromisoformat(a_iso)
        b = datetime.fromisoformat(b_iso)
        return abs((a - b).total_seconds()) / 3600.0
    except Exception:  # noqa: BLE001
        return None


def _km_between(a, b):
    if not a["location_resolved"] or not b["location_resolved"]:
        return None
    lat1, lon1 = math.radians(a["latitude"]), math.radians(a["longitude"])
    lat2, lon2 = math.radians(b["latitude"]), math.radians(b["longitude"])
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * 6371 * math.asin(math.sqrt(h))


def score_pair(new_inc, old_inc):
    """Return (score 0..1, reasons[]) for two stored incident dicts."""
    reasons = []
    score = 0.0
    new_ex = new_inc["extraction"]
    old_ex = old_inc["extraction"]

    # 1. incident type
    if new_ex.get("incident_type") == old_ex.get("incident_type"):
        score += 0.30
        reasons.append(f"Same incident type: {new_ex.get('incident_type')}")

    # 2. location
    km = _km_between(new_inc, old_inc)
    if km is not None and km <= 3.0:
        score += 0.35
        place = new_inc.get("resolved_place") or "same area"
        reasons.append(f"Locations match: {place} ({km:.1f} km apart)")
    elif km is not None and km <= 15.0:
        score += 0.15
        reasons.append(f"Locations nearby ({km:.1f} km apart)")
    else:
        a = (new_ex.get("location_mentioned") or "").strip().lower()
        b = (old_ex.get("location_mentioned") or "").strip().lower()
        if a and b and (a in b or b in a):
            score += 0.25
            reasons.append(f"Same mentioned place: '{new_ex.get('location_mentioned')}'")

    # 3. time proximity
    hours = _hours_between(new_inc.get("created_at", ""), old_inc.get("created_at", ""))
    if hours is not None and hours <= TIME_WINDOW_HOURS:
        score += 0.15
        if hours < 1:
            reasons.append(f"Reported {int(hours * 60)} min apart")
        else:
            reasons.append(f"Reported {hours:.1f} h apart")

    # 4. description overlap
    overlap = _jaccard(_tokens(new_ex.get("description", "")),
                       _tokens(old_ex.get("description", "")))
    if overlap >= 0.25:
        score += 0.20 * min(1.0, overlap + 0.25)
        shared = sorted(_tokens(new_ex.get("description", ""))
                        & _tokens(old_ex.get("description", "")))[:5]
        reasons.append(f"Similar wording ({', '.join(shared)})")

    return round(min(1.0, score), 3), reasons


def find_candidates(new_incident, existing_incidents, threshold=SCORE_THRESHOLD):
    """Return candidate dicts sorted by score desc. Originals untouched."""
    out = []
    for old in existing_incidents:
        if old["id"] == new_incident["id"]:
            continue
        score, reasons = score_pair(new_incident, old)
        if score >= threshold and reasons:
            out.append({"incident_id": new_incident["id"],
                        "other_incident_id": old["id"],
                        "score": score, "reasons": reasons})
    out.sort(key=lambda c: -c["score"])
    return out
