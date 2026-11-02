"""Measured evaluation: 18 fictional reports -> real Meta extraction -> scores.

Reports ONLY measured results. Writes per-item results to
data/sentinel_eval_results.json. Uses a throwaway DB (data/sentinel_eval.db).

Usage: venv/bin/python scripts/run_eval.py
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["SENTINEL_DB"] = "data/sentinel_eval.db"
if os.path.exists("data/sentinel_eval.db"):
    os.remove("data/sentinel_eval.db")

from sentinel_pipeline import process_report_sync  # noqa: E402

BANDS = {"critical": "high", "high": "high", "moderate": "mid",
         "low": "low", "minimal": "low"}


def main():
    items = [json.loads(line) for line in open("data/sentinel_eval.jsonl")
             if line.strip()]
    results = []
    ok = 0
    for i, item in enumerate(items, 1):
        exp = item["expected"]
        t0 = time.time()
        try:
            inc, _ = process_report_sync(
                item["message"], item.get("location_hint") or None,
                is_simulated=True)
            dt = time.time() - t0
            ex = inc["extraction"]
            got = {"incident_type": ex["incident_type"],
                   "detected_language": ex["detected_language"],
                   "resolved": bool(inc["location_resolved"]),
                   "severity": ex["severity"], "urgency": ex["urgency"]}
            valid = True
            err = ""
            ok += 1
        except Exception as e:  # noqa: BLE001
            dt = time.time() - t0
            got = {}
            valid = False
            err = str(e)[:200]
        row = {"id": i, "valid_json": valid, "latency_s": round(dt, 1),
               "expected": exp, "got": got, "error": err,
               "type_match": got.get("incident_type") == exp["incident_type"],
               "lang_match": got.get("detected_language") == exp["detected_language"],
               "resolved_match": got.get("resolved") == exp["resolved"],
               "sev_band_match": BANDS.get(got.get("severity")) == BANDS.get(exp["severity"]),
               "urgency_abs_err": (abs(got["urgency"] - exp["urgency"])
                                   if valid else None)}
        results.append(row)
        flag = "OK " if valid else "FAIL"
        print(f"[{i:2d}/{len(items)}] {flag} {dt:4.1f}s "
              f"type={got.get('incident_type', '?'):12s}({'Y' if row['type_match'] else 'n'}) "
              f"lang={got.get('detected_language', '?'):3s}({'Y' if row['lang_match'] else 'n'}) "
              f"res={str(got.get('resolved')):5s}({'Y' if row['resolved_match'] else 'n'}) "
              f"sev={got.get('severity', '?'):8s} u={got.get('urgency', '?')} {err}")

    n = len(results)
    summary = {
        "n": n,
        "structured_validity": round(sum(r["valid_json"] for r in results) / n, 3),
        "type_accuracy": round(sum(r["type_match"] for r in results) / n, 3),
        "language_accuracy": round(sum(r["lang_match"] for r in results) / n, 3),
        "location_resolution_match": round(sum(r["resolved_match"] for r in results) / n, 3),
        "severity_band_accuracy": round(sum(r["sev_band_match"] for r in results) / n, 3),
        "urgency_mae": round(sum(r["urgency_abs_err"] for r in results
                                 if r["urgency_abs_err"] is not None) / max(ok, 1), 2),
        "avg_latency_s": round(sum(r["latency_s"] for r in results) / n, 1),
        "note": ("Reference labels are the author's judgment on fictional reports, "
                 "not ground truth. Severity/urgency measure agreement, not correctness."),
    }
    with open("data/sentinel_eval_results.json", "w") as f:
        json.dump({"summary": summary, "items": results}, f, indent=2)
    print("\nEVAL SUMMARY (measured):")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    sys.exit(main())
