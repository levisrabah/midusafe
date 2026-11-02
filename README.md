# MIDUSAFE SENTINEL

### Turning community reports into actionable disaster intelligence.

Built for the **Meta Global AI Developer Hackathon 2026**. Sentinel takes fragmented
community emergency reports — text in English, Swahili, or Sheng, plus voice recordings —
and turns them into structured, traceable incident intelligence for human responders,
powered by Meta's models.

> **Demo data is fictional.** Anything labelled SIMULATED in the UI or data files is a
> scripted scenario, not live emergency data.

## Problem

During disasters, critical information arrives fragmented: texts in different languages,
voice notes, incomplete locations, conflicting and duplicate reports. Responders need to
know what is happening, where, how urgent it is — and what is still uncertain.

## Solution

A real-time command center where every report flows through Meta AI:

1. Community member submits a report (text or voice).
2. **Muse Spark** extracts structured incident data (validated Pydantic schema).
3. Server resolves location from a known-place gazetteer — unknown stays unresolved, never guessed.
4. Duplicate candidates are flagged with WHY explanations; a human confirms or rejects.
5. **Muse Spark** drafts an evidence-backed intel brief; every claim cites source report ids.
6. Responders verify, reclassify, reprioritize, and annotate — every action audit-logged.
7. Nothing is ever auto-dispatched. The system advises; humans decide.

## Meta AI integration (all verified live on this repo's key)

| Capability | Model | Status |
|---|---|---|
| Structured extraction | `muse-spark-1.3` (Chat Completions + `json_schema`) | ✅ tested |
| Intel briefs | `muse-spark-1.3` (citation-validated) | ✅ tested |
| Voice transcription | `muse-voice-transcribe-1.0` (`POST /v1/asr/transcribe`) | ✅ tested, exact transcript |
| Plain reasoning | `muse-spark-1.3` (Responses API) | ✅ tested |

Docs source: https://dev.meta.ai/docs. Base URL `https://api.meta.ai/v1`, Bearer auth.
Key also lists `muse-wonder-1.0`, `muse-spark-1.2/1.1`, `muse-image-1.0`, `sam-3.1`;
image analysis was intentionally skipped as a stretch goal.

Measured eval (18 fictional reports, `scripts/run_eval.py`, full results in
`data/sentinel_eval_results.json`): structured validity **1.0**, type accuracy
**1.0**, language accuracy **0.944**, location-resolution agreement **1.0**,
severity-band agreement **0.778**, urgency MAE **0.67**, avg latency **8.0s**.
Reference labels are the author's judgment, not ground truth.

## Architecture

```
browser ──text/voice──▶ FastAPI ──▶ Meta Model API (Spark / Voice Transcribe)
                              ├─▶ Pydantic validate ─▶ SQLite ─▶ WebSocket broadcast
                              ├─▶ gazetteer resolve (known places only)
                              ├─▶ duplicate candidates (advisory, never merge)
                              ├─▶ intel brief (citation-checked, fallback if invalid)
                              └─▶ verification actions ─▶ audit trail
```

See [ARCHITECTURE.md](ARCHITECTURE.md). API key stays server-side; frontend never sees it.

## Installation

```bash
# Backend
cd /home/levis/midusafe
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set META_API_KEY

# Frontend
cd dashboard && npm install
```

Requires: Python 3.10+, Node 18+, `ffmpeg` (voice uploads only).

## Running

```bash
# Terminal 1: backend
source venv/bin/activate && python3 main.py        # http://localhost:8000

# Terminal 2: frontend
cd dashboard && npm run dev                        # http://localhost:3000

# Terminal 3 (optional): seed the fictional flood scenario
venv/bin/python scripts/seed_demo.py --reset
```

Legacy simulation still works: `python3 simulation.py` posts to `/report` (Gemini path).

## Testing

```bash
venv/bin/python -m pytest tests/ -q          # 19 tests, no network needed (stubbed Meta)
venv/bin/python scripts/meta_smoke_test.py   # live Meta API check (responses + models)
venv/bin/python scripts/run_eval.py          # live 18-report eval, writes results JSON
cd dashboard && npm run build                # frontend type-check + build
```

## API (new in hackathon)

- `POST /api/sentinel/reports` — submit report (`?sync=true` processes inline)
- `GET /api/sentinel/incidents` / `/{id}` — list / detail
- `GET /api/sentinel/incidents/{id}/brief` — intel brief (`?refresh=true`)
- `GET /api/sentinel/duplicates` — candidates · `POST .../{link}/decision` — confirm/reject
- `POST /api/sentinel/incidents/{id}/verify` — verify|request_info|reclassify|priority|note
- `POST /api/sentinel/voice/transcribe` — audio upload → transcript
- `GET /api/sentinel/stats` · `/audit` · `/health`

Legacy endpoints (`/report`, `/alerts`, `/ws/alerts`) unchanged; Sentinel incidents also
broadcast over `/ws/alerts` with legacy-compatible fields.

## What was built during the hackathon

Baseline tag: `pre-hackathon`. See [HACKATHON_BUILD_LOG.md](HACKATHON_BUILD_LOG.md) and
[DEMO_SCRIPT.md](DEMO_SCRIPT.md) (3-minute demo).

New: `meta_service.py`, `sentinel_schemas.py`, `sentinel_pipeline.py`,
`sentinel_store.py`, `gazetteer.py`, `duplicates.py`, `briefs.py`, Sentinel REST API,
SQLite persistence, flood scenario + seed script, eval set + runner, pytest suite,
dashboard Sentinel tab (stats, feed, detail panel, verification UI, voice wiring).

Pre-existing (kept): Gemini `/report` triage, urgency/language/severity engines,
mock incidents, simulation, legacy live feed + map + voice recorder shell.

## Screenshots

Run the app and seed the demo, then capture: (1) Sentinel Intel tab with stats +
feed, (2) incident detail with brief + duplicates, (3) map with resolved markers.
(Shots omitted from repo; UI verified via production build + served-page check.)
