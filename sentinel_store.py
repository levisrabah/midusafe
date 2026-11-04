"""SQLite persistence for Sentinel (stdlib sqlite3, no new dependency)."""

import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone

DB_PATH = os.getenv("SENTINEL_DB", "data/sentinel.db")

_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    message TEXT NOT NULL,
    location_hint TEXT,
    is_simulated INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS incidents (
    id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL REFERENCES reports(id),
    extraction TEXT NOT NULL,
    location_resolved INTEGER NOT NULL DEFAULT 0,
    latitude REAL,
    longitude REAL,
    resolved_place TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    priority INTEGER,
    classification TEXT,
    created_at TEXT NOT NULL,
    is_simulated INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS duplicate_links (
    id TEXT PRIMARY KEY,
    incident_a TEXT NOT NULL,
    incident_b TEXT NOT NULL,
    score REAL NOT NULL,
    reasons TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    decided_at TEXT,
    UNIQUE(incident_a, incident_b)
);
CREATE TABLE IF NOT EXISTS audit (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    actor TEXT NOT NULL DEFAULT 'responder',
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS briefs (
    incident_id TEXT PRIMARY KEY,
    brief TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS contradictions (
    incident_id TEXT PRIMARY KEY,
    report TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ai_trace (
    id TEXT PRIMARY KEY,
    incident_id TEXT,
    step TEXT NOT NULL,
    model TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    validation_passed INTEGER NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS followup_drafts (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    language TEXT NOT NULL,
    draft_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    decided_at TEXT
);
"""


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def _connect():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _lock, _connect() as conn:
        conn.executescript(SCHEMA)


def new_id(prefix=""):
    return f"{prefix}{uuid.uuid4().hex[:12]}"


# ---- reports / incidents ----

def save_report(message, location_hint=None, is_simulated=False, report_id=None):
    init_db()
    rid = report_id or new_id("rep_")
    with _lock, _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO reports (id, message, location_hint, is_simulated, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (rid, message, location_hint, int(bool(is_simulated)), now_iso()),
        )
    return rid


def get_report(report_id):
    init_db()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    return dict(row) if row else None


def save_incident(incident_id, report_id, extraction: dict, geo: dict,
                  is_simulated=False):
    init_db()
    with _lock, _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO incidents (id, report_id, extraction, location_resolved,"
            " latitude, longitude, resolved_place, status, created_at, is_simulated)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)",
            (incident_id, report_id, json.dumps(extraction),
             int(bool(geo.get("resolved"))), geo.get("lat"), geo.get("lng"),
             geo.get("place"), now_iso(), int(bool(is_simulated))),
        )
    return incident_id


def get_incident(incident_id):
    init_db()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["extraction"] = json.loads(d["extraction"])
    return d


def list_incidents(limit=200):
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM incidents ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    out = []
    for row in rows:
        d = dict(row)
        d["extraction"] = json.loads(d["extraction"])
        out.append(d)
    return out


def update_incident(incident_id, **fields):
    allowed = {"status", "priority", "classification"}
    sets = {k: v for k, v in fields.items() if k in allowed}
    if not sets:
        return False
    init_db()
    with _lock, _connect() as conn:
        conn.execute(
            f"UPDATE incidents SET {', '.join(f'{k} = ?' for k in sets)} WHERE id = ?",
            (*sets.values(), incident_id),
        )
    return True


# ---- duplicates ----

def _canon(a, b):
    return (a, b) if a < b else (b, a)


def save_duplicate_candidate(incident_a, incident_b, score, reasons):
    init_db()
    a, b = _canon(incident_a, incident_b)
    if a == b:
        return None
    with _lock, _connect() as conn:
        row = conn.execute(
            "SELECT id FROM duplicate_links WHERE incident_a = ? AND incident_b = ?",
            (a, b)).fetchone()
        if row:
            return row["id"]
        lid = new_id("dup_")
        conn.execute(
            "INSERT INTO duplicate_links (id, incident_a, incident_b, score, reasons, status, created_at)"
            " VALUES (?, ?, ?, ?, ?, 'pending', ?)",
            (lid, a, b, score, json.dumps(reasons), now_iso()),
        )
    return lid


def list_duplicate_links(status=None):
    init_db()
    with _connect() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM duplicate_links WHERE status = ? ORDER BY score DESC",
                (status,)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM duplicate_links ORDER BY created_at DESC").fetchall()
    out = []
    for row in rows:
        d = dict(row)
        d["reasons"] = json.loads(d["reasons"])
        out.append(d)
    return out


def decide_duplicate(link_id, decision):
    assert decision in ("confirmed", "rejected")
    init_db()
    with _lock, _connect() as conn:
        conn.execute(
            "UPDATE duplicate_links SET status = ?, decided_at = ? WHERE id = ?",
            (decision, now_iso(), link_id),
        )
    return True


# ---- audit ----

def log_audit(action, target_type, target_id, detail="", actor="responder"):
    init_db()
    aid = new_id("aud_")
    with _lock, _connect() as conn:
        conn.execute(
            "INSERT INTO audit (id, timestamp, actor, action, target_type, target_id, detail)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (aid, now_iso(), actor, action, target_type, target_id, detail),
        )
    return aid


def list_audit(limit=200):
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM audit ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


# ---- briefs ----

def save_brief(incident_id, brief: dict):
    init_db()
    with _lock, _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO briefs (incident_id, brief, created_at) VALUES (?, ?, ?)",
            (incident_id, json.dumps(brief), now_iso()),
        )


def get_brief(incident_id):
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT brief FROM briefs WHERE incident_id = ?", (incident_id,)).fetchone()
    return json.loads(row["brief"]) if row else None


# ---- contradictions cache ----

def save_contradictions(incident_id, report: dict):
    init_db()
    with _lock, _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO contradictions (incident_id, report, created_at)"
            " VALUES (?, ?, ?)",
            (incident_id, json.dumps(report), now_iso()),
        )


def get_contradictions(incident_id):
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT report FROM contradictions WHERE incident_id = ?",
            (incident_id,)).fetchone()
    return json.loads(row["report"]) if row else None


# ---- Meta AI trace (real measured values only) ----

def log_trace(incident_id, step, model, latency_ms, validation_passed,
              detail=""):
    init_db()
    tid = new_id("trc_")
    with _lock, _connect() as conn:
        conn.execute(
            "INSERT INTO ai_trace (id, incident_id, step, model, latency_ms,"
            " validation_passed, detail, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (tid, incident_id, step, model, int(latency_ms),
             int(bool(validation_passed)), detail or "", now_iso()),
        )
    return tid


def list_trace(incident_id, limit=50):
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM ai_trace WHERE incident_id = ?"
            " ORDER BY created_at ASC LIMIT ?", (incident_id, limit)).fetchall()
    return [dict(r) for r in rows]


# ---- follow-up drafts (approval queue; nothing is ever auto-sent) ----

def save_followup_draft(incident_id, language, draft_text, draft_id=None):
    init_db()
    did = draft_id or new_id("fup_")
    with _lock, _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO followup_drafts (id, incident_id, language,"
            " draft_text, status, created_at)"
            " VALUES (?, ?, ?, ?, 'pending', ?)",
            (did, incident_id, language, draft_text, now_iso()),
        )
    return did


def list_followup_drafts(incident_id=None, status=None):
    init_db()
    q = "SELECT * FROM followup_drafts"
    clauses, params = [], []
    if incident_id:
        clauses.append("incident_id = ?")
        params.append(incident_id)
    if status:
        clauses.append("status = ?")
        params.append(status)
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY created_at DESC"
    with _connect() as conn:
        rows = conn.execute(q, params).fetchall()
    return [dict(r) for r in rows]


def decide_followup_draft(draft_id, decision, edited_text=None):
    assert decision in ("approved", "discarded")
    init_db()
    with _lock, _connect() as conn:
        if edited_text is not None:
            conn.execute(
                "UPDATE followup_drafts SET draft_text = ?, status = ?,"
                " decided_at = ? WHERE id = ?",
                (edited_text, decision, now_iso(), draft_id),
            )
        else:
            conn.execute(
                "UPDATE followup_drafts SET status = ?, decided_at = ? WHERE id = ?",
                (decision, now_iso(), draft_id),
            )
    return True


def stats():
    init_db()
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM incidents").fetchone()["c"]
        pending = conn.execute(
            "SELECT COUNT(*) c FROM incidents WHERE status = 'pending'").fetchone()["c"]
        verified = conn.execute(
            "SELECT COUNT(*) c FROM incidents WHERE status = 'verified'").fetchone()["c"]
        dups = conn.execute(
            "SELECT COUNT(*) c FROM duplicate_links WHERE status = 'pending'").fetchone()["c"]
        rows = conn.execute("SELECT extraction FROM incidents").fetchall()
    by_type = {}
    high = 0
    for r in rows:
        try:
            ex = json.loads(r["extraction"])
        except Exception:  # noqa: BLE001
            continue
        t = ex.get("incident_type", "other")
        by_type[t] = by_type.get(t, 0) + 1
        if ex.get("severity") in ("critical", "high") or (ex.get("urgency") or 0) >= 7:
            high += 1
    return {"total": total, "pending_verification": pending, "verified": verified,
            "high_priority": high, "possible_duplicates": dups,
            "by_category": by_type}
