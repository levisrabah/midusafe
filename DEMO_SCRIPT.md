# DEMO SCRIPT — MIDUSAFE SENTINEL (3 minutes)

Setup before recording: backend + frontend running, freshly seeded:
`venv/bin/python scripts/seed_demo.py --reset` (8 fictional Mathare reports).

> Say upfront: "All data in this demo is fictional and labelled SIMULATED."

## 0:00–0:30 — The problem + report arrives (Sentinel tab)

- Show the dashboard: stats cards (8 total, 8 awaiting, 5 high priority, duplicates).
- Point at the feed: English, Swahili, Sheng reports with SIMULATED badges.
- Click "Report" (bottom-right), type a Swahili report, e.g.:
  "Maji yameingia nyumbani Mathare, watoto wako hatarini!"
  Submit. Within ~10s it appears in the feed with an English summary.

Talking point: "One report, any of our tested languages, structured by Meta AI in seconds."

## 0:30–1:15 — Inspect intelligence

- Click the new incident. Show: translation + original, urgency/severity/confidence,
  resolved location vs "Unresolved — not shown on map" for the vague report.
- Open a vague-location incident: no marker, amber warning. "We never invent coordinates."
- Show missing-info and follow-up questions.

Talking point: "What we know, what we don't, and what to ask next — with uncertainty shown, not hidden."

## 1:15–2:00 — Duplicates

- Open a Mathare flood incident → Possible duplicates section.
- Read the WHY reasons aloud (same type, 0.5 km apart, minutes apart).
- Confirm one as same incident, reject none. "The system suggests; the human decides.
  Originals are always preserved."

## 2:00–2:40 — Brief + verification

- Click "Generate brief". Show what/where/evidence-with-citations/unknowns/verify/next-steps.
- Mark verified, set priority 9, add note "Ward admin called".
- Scroll to audit trail: every action timestamped.

Talking point: "Every claim cites its source. Every action is logged. Nothing auto-dispatches."

## 2:40–3:00 — Voice + close

- In the Report modal, record 5 seconds of speech, stop, show the Meta transcript
  filling the text box. (If mic unavailable: show the transcribe endpoint response instead.)
- Close: "Fragmented reports in — traceable intelligence out, powered by Muse Spark
  and Muse Voice Transcribe. Fictional demo data; real pipeline."

## If something fails live

- Backend down: `curl localhost:8000/health`; restart `python3 main.py`.
- Meta slow: async path still accepts reports; feed updates when done.
- No mic: paste text "Voice fallback: typed report" and submit normally.
