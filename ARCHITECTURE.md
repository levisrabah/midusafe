# ARCHITECTURE — MIDUSAFE SENTINEL

## System overview

```
┌─────────────┐  text/voice   ┌──────────────────┐  Bearer (server)  ┌─────────────────┐
│  Next.js 14 │ ────────────▶ │  FastAPI backend │ ────────────────▶ │ Meta Model API  │
│  dashboard  │ ◀──────────── │  + SQLite        │ ◀──────────────── │ api.meta.ai/v1  │
└─────────────┘  WS + REST    └──────────────────┘   JSON / audio    └─────────────────┘
```

## Backend modules (all new except triage path)

| Module | Responsibility |
|---|---|
| `meta_service.py` | `MetaService`: chat, responses, transcribe, list-models. Env-swappable base URL/model, 45s timeout, retries w/ backoff on 408/429/5xx, typed errors, key redaction |
| `sentinel_schemas.py` | Strict Pydantic contracts + JSON Schemas sent to Meta (`json_schema` mode). Model never outputs coords/casualties |
| `gazetteer.py` | Known-place table. Coords only for listed places; everything else unresolved |
| `sentinel_store.py` | SQLite (`data/sentinel.db`): reports, incidents, duplicate_links, audit, briefs |
| `sentinel_pipeline.py` | `process_report_sync`: extract → validate → resolve → store → dup-check → audit |
| `duplicates.py` | Candidate scoring (type 0.30, location 0.35/0.15/0.25, time 0.15, wording ~0.20; threshold 0.55). Advisory only |
| `briefs.py` | Brief prompt + citation validation + medical-advice rejection + evidence-only fallback |
| `main.py` | Legacy endpoints untouched + `/api/sentinel/*` REST + WS broadcast of new incidents |

## Data flow: one report

1. `POST /api/sentinel/reports` → (background, or inline with `?sync=true`)
2. `MetaService.chat` with `response_format: json_schema` (IncidentExtraction)
3. Pydantic validation; invalid JSON/schema → 502, nothing stored
4. Gazetteer resolution from hint + mentioned place + message
5. Store report + incident; audit `report_submitted`
6. Duplicate scan vs stored incidents; candidates stored as `pending` links
7. Broadcast `{type: sentinel_incident, ...legacy-compatible fields}` on `/ws/alerts`

## Voice flow

Browser MediaRecorder → `POST /api/sentinel/voice/transcribe` (multipart) →
ffmpeg to 16kHz mono WAV → `POST /v1/asr/transcribe?sessionId=` (parts: `request`
JSON + `audio` WAV) → transcript returned → user reviews → submits as text report.

## Duplicate + brief + verification

- Duplicates: pairs scored on type/location/time/wording with human-readable reasons.
  Links are `pending` until a responder confirms/rejects. Originals are never modified.
- Briefs: generated on demand, cached in SQLite. Server rejects briefs citing unknown
  report ids or containing medical-advice phrases; fallback brief quotes stored evidence.
- Verification: `verify | request_info | reclassify | priority | note`. Each writes an
  audit row (timestamp, actor, action, target, detail). No endpoint dispatches responders.

## Frontend

- `Sentinel Intel` tab (default): `sentinel-stats` (5 cards), `sentinel-feed`
  (SIMULATED badges, unresolved warnings, loading/empty/error states), both polling
  REST every 5s.
- `incident-detail` slide-over: extraction, evidence, duplicates + decisions, brief,
  responder actions, audit trail.
- Map markers only for `location_resolved` incidents; unresolved count shown as notice.
- Legacy `Live Alerts` tab unchanged. Community report modal submits to Sentinel;
  voice recorder transcribes via Meta then fills editable text.

## Security considerations

- `META_API_KEY` server-side only (env). Never logged, never returned, redacted from
  errors. No `NEXT_PUBLIC_*` secrets.
- `.env` gitignored; `.env.example` documents vars without values.
- Voice uploads capped at 10MB, converted in temp files, temp files removed.
- SQLite file is local runtime state, not committed.
- Brief/verify endpoints are human-in-the-loop by design; nothing auto-dispatches.

## Failure handling

| Failure | Behaviour |
|---|---|
| Meta timeout / 5xx / 429 | Retries w/ backoff, then typed error; report endpoint 502s (sync) or broadcasts `sentinel_error` (async) |
| Invalid model JSON/schema | 502, nothing stored |
| Unknown cited report id | Brief rejected → evidence-only fallback |
| Unresolvable location | Stored unresolved, excluded from map, flagged in UI |
| Missing ffmpeg / no speech | 501 / warning string, typed text path always available |
