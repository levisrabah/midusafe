# HACKATHON BUILD LOG — MIDUSAFE SENTINEL

Baseline: commit tagged `pre-hackathon`. Everything below is new hackathon work.

## Existing before hackathon (kept, not rewritten)
- FastAPI backend (`main.py`): `POST /report` (Gemini), `GET /alerts`, `GET /health`, `WS /ws/alerts`
- `triage.py` (Gemini 2.0 Flash), `language_intelligence.py`, `urgency_intelligence.py`, `disaster_severity.py`
- `simulation.py`, `live_demo.py`, `data/mock-incidents.json` (45+ scenarios)
- Next.js dashboard: live feed, Leaflet map, community report modal w/ placeholder voice transcription, toasts, navbar
- No database (in-memory list), no verification workflow, no duplicate detection, no briefs, no tests

## New: Phase 2 — Meta API verification (measured, not guessed)
- Docs source: https://dev.meta.ai/docs (Models, Quickstart, Structured output)
- Base URL `https://api.meta.ai/v1`, Bearer auth, default model `muse-spark-1.3`
- `scripts/meta_smoke_test.py`: GET /models=200, POST /responses=200, POST /chat/completions+json_schema=200
- Key accesses: muse-wonder-1.0, muse-spark-1.3/1.2/1.1 (+contributors), muse-image-1.0, muse-voice-transcribe-1.0, sam-3.1
- Structured output: Responses API uses `text.format`; Chat Completions uses `response_format`+`json_schema` (used here)

## New: Step 1 — Backend Meta AI service
- `meta_service.py`: server-side key only (META_API_KEY/MODEL_API_KEY), META_BASE_URL/META_MODEL swappable,
  timeouts (45s), retries w/ backoff on 408/429/5xx, typed errors, key redaction everywhere

## New: Step 2 — Core slice (verified live)
- `sentinel_schemas.py`: strict Pydantic extraction schema; model NEVER outputs coords/casualties
- `gazetteer.py`: coords only for listed known places, else unresolved (never guessed)
- `sentinel_store.py`: SQLite (`data/sentinel.db`) incidents/reports/duplicates/audit/briefs
- `sentinel_pipeline.py`: report -> Meta extract -> validate -> resolve -> store -> dup-check -> audit
- `main.py`: `POST /api/sentinel/reports` (+?sync), `GET /api/sentinel/incidents[/{id}]`,
  `/stats`, `/audit`, `/health`; broadcasts over existing WS `/ws/alerts` w/ legacy-compatible fields
- Live test: Swahili Mathare flood report -> flood/sw/critical/urgency 9, Mathare resolved,
  stored, stats+audit OK, legacy /health intact

## New: Step 3 — Demo dataset (fictional flood scenario)
- `data/sentinel_flood_scenario.json`: 8 fictional Mathare reports, EN/SW/Sheng, vague locations,
  one fire control; labelled fictional in data + UI
- `scripts/seed_demo.py`: seeds via real Meta extraction. Live: 8/8 ok, langs en/sw/sh detected,
  vague locations UNRESOLVED, fire control typed `fire` with 0 dup candidates

## New: Step 4 — Duplicate candidate detection
- `duplicates.py`: type + location (3km/15km or same place) + 6h window + wording overlap;
  threshold 0.55 so type+time alone never flags; reasons explain WHY; never merges
- Live: 10 candidates with reasons like "Same incident type: flood / Locations match (0.5 km) / Reported 0 min apart";
  `GET /api/sentinel/duplicates`, `POST .../decision` (confirm/reject, audit-logged)

## New: Step 5 — Evidence-backed intelligence briefs
- `briefs.py`: Meta generates brief w/ json_schema; server rejects unknown cited ids + medical advice;
  fallback brief quotes stored evidence only. `GET /api/sentinel/incidents/{id}/brief` (+cache)
- Live: method=meta, all claims cited real rep_* ids, unknowns/to_verify/next-steps for human review

## New: Step 6 — Human verification workflow + audit trail
- `POST /api/sentinel/incidents/{id}/verify`: verify|request_info|reclassify|priority|note;
  every action audit-logged with timestamp; no auto-dispatch anywhere
- Live: verify->verified, priority=9, note, dup confirm all in audit (13 entries)

## New: Step 7 — Dashboard and map polish
- Sentinel Intel tab (default): stats cards (total/awaiting/high/dups/verified+categories),
  intel feed w/ SIMULATED badges, unresolved-location warnings, loading/empty/error states
- Incident detail slide-over: extraction, original+translation, location certainty, dup
  candidates w/ WHY reasons + confirm/reject, on-demand brief, verify/request-info/
  reclassify/priority/note controls, audit trail, missing-info + follow-ups
- Map: markers ONLY for resolved locations + "N unresolved not shown" notice
- Community report modal now submits to Sentinel (Meta) endpoint; legacy WS path skips
  sentinel messages; live-feed null-coord guard
- Fixed pre-existing build breakers in `ai-triage-card.tsx` (missing icon keys, bad
  AIAnalysis props, optional-field access) + unexported ToastNotification. `npm run build` green,
  production page serves HTTP 200 with Sentinel UI present

## New: Step 8 — Voice (VERIFIED working on this key)
- `muse-voice-transcribe-1.0` confirmed: real speech sample transcribed exactly ("Liberia")
- Documented contract: `POST /v1/asr/transcribe?sessionId=` + multipart `request` JSON + `audio` WAV
  (mono 16-bit PCM 16/24kHz); implemented in `MetaService.transcribe_file`
- `POST /api/sentinel/voice/transcribe`: accepts webm/wav/mp3/ogg, ffmpeg-converts, returns
  transcript; tested live with ogg upload -> "Liberia." (also tests conversion path)
- Report modal: real transcribe-on-stop with loading/error states, transcript fills editable
  report text, then normal Sentinel extraction on submit
- Image analysis: SKIPPED as stretch goal (key lists muse-image-1.0 but time prioritized elsewhere)

## New: Step 9 — Tests + measured eval
- `tests/` (19 pytest, all passing): multilingual extraction, invalid JSON + schema
  violations rejected, missing/unknown location stays unresolved, dup scoring + reasons +
  no-merge + confirm flow, verify/request_info/reclassify/priority/note + audit trail,
  brief citation enforcement w/ fallback, Meta timeout/retries/rate-limit/auth/key-redaction
- `requirements.txt`: added requests, httpx==0.27.2 (TestClient compat), python-multipart, pytest
- `data/sentinel_eval.jsonl` (18 fictional reports) + `scripts/run_eval.py`, MEASURED live:
  validity 1.0, type acc 1.0 (18/18), lang acc 0.944 (17/18; one sh/sw code-switch),
  location match 1.0, severity-band acc 0.778 (14/18, all adjacent-band judgment calls),
  urgency MAE 0.67, avg latency 8.0s. Full per-item results in `data/sentinel_eval_results.json`

## New: Step 10 — Docs
- `README.md` (Sentinel-first, measured numbers only), `ARCHITECTURE.md`,
  `DEMO_SCRIPT.md` (3-min), `.env.example` (no secrets), this log
- `.env` confirmed gitignored (`git check-ignore .env` → ignored)

## Known limitations
- Gazetteer is Kenya-demo-scoped (~25 places); unlisted places stay unresolved by design
- Languages tested live: English, Swahili, Sheng only; no broader coverage claimed
- Voice tested on English speech sample; Swahili/Sheng voice not measured
- Image analysis skipped (stretch goal); key lists muse-image-1.0 but unused
- SQLite single-file store; no auth/multi-user; audit actor is a label, not identity
- venv/ is tracked in git from before the hackathon (pre-existing); env churn left uncommitted
- data/sentinel.db + data/sentinel_eval.db are local runtime state, intentionally uncommitted

## Assumptions
- META_API_KEY in .env is the Model API key (48 chars, LLM_ prefix matches docs format) — confirmed working
- Gazetteer over model coords: deliberate anti-fabrication design
