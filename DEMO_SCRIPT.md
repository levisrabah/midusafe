# DEMO SCRIPT — MIDUSAFE SENTINEL (3 minutes)

Setup before recording: backend + frontend running, freshly seeded:
`venv/bin/python scripts/seed_demo.py --reset` (10 fictional Mathare reports,
incl. a footbridge contradiction pair).

> Say upfront: "All data in this demo is fictional and labelled SIMULATED."

## 0:00–0:25 — Report in (Sentinel tab)

- Show the dashboard: stats cards, feed with SIMULATED badges, keyless OSM map.
- Click "Report" (bottom-right), type a Swahili report, e.g.:
  "Maji yameingia nyumbani Mathare, watoto wako hatarini!"
  (Or record 5s of voice: the Meta transcript fills the text box on stop.)
- Submit. Within ~10–20s it appears in the feed with an English summary.

Talking point: "One report, any of our tested languages, structured by Meta AI in seconds."

## 0:25–0:55 — Structured extraction + duplicate WHY

- Click the new incident: translation + original, urgency/severity/confidence,
  resolved location vs "Unresolved — not shown on map".
- Open a Mathare flood incident → Possible duplicates. Read one WHY aloud
  (same type, 0.5 km apart, minutes apart). Confirm one as same incident.
  "The system suggests; the human decides. Originals are always preserved."

## 0:55–1:30 — Conflicting reports

- Open the footbridge incident (seeded pair) → "Conflicting reports" → Check for conflicts.
- Show the two claims side by side with cited report ids:
  "footbridge impassable" vs "footbridge passable if careful".
- Point at the "verify on the ground" prompt. "Conflicts are flagged, never auto-resolved."

## 1:30–2:00 — Follow-up approval queue

- On a Swahili incident → Approval queue → "Draft follow-up in reporter's language [sw]".
- Show the Swahili draft, then Approve one draft ("approved, ready to send"),
  Edit another, Discard a third.
- "Every draft waits for a human. Approved means ready — nothing is sent anywhere."

## 2:00–2:40 — Cited brief + human verify + audit trail

- Click "Generate brief": what/where/evidence-with-citations/unknowns/verify/next-steps.
- Mark verified, set priority 9, add note "Ward admin called".
- Scroll to audit trail: every action timestamped, incl. draft and conflict checks.

Talking point: "Every claim cites its source. Every action is logged. Nothing auto-dispatches."

## 2:40–3:00 — Meta AI trace + close

- Expand "Meta AI trace": voice transcribe → extraction → brief → contradiction
  check → follow-up draft, each with its real model, measured latency, and
  validation outcome.
- Close: "Fragmented reports in — traceable intelligence out, powered by Muse Spark
  and Muse Voice Transcribe, with a human in every loop. Fictional demo data; real pipeline."

## If something fails live

- Backend down: `curl localhost:8000/health`; restart `python3 main.py`.
- Meta slow: async path still accepts reports; feed updates when done.
- No mic: paste text "Voice fallback: typed report" and submit normally.
- Conflict check empty: use `?refresh=true` on the footbridge incident; it needs 2+ linked reports.
