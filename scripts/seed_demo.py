"""Seed the FICTIONAL Mathare flood demo scenario into a running or fresh backend.

Spawns the server itself, POSTs each scenario report with sync=true
(real Meta extraction), prints per-report results, then stops the server.

Usage: venv/bin/python scripts/seed_demo.py [--reset]
--reset wipes data/sentinel.db first for a clean demo.
"""

import json
import subprocess
import sys
import time

import requests

BASE = "http://127.0.0.1:8000"


def wait_for_server(proc, timeout=40):
    for _ in range(timeout):
        try:
            r = requests.get(f"{BASE}/health", timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main():
    if "--reset" in sys.argv:
        import os
        if os.path.exists("data/sentinel.db"):
            os.remove("data/sentinel.db")
            print("wiped data/sentinel.db")

    with open("data/sentinel_flood_scenario.json") as f:
        scenario = json.load(f)
    reports = scenario["reports"]
    print(f"Seeding {len(reports)} FICTIONAL reports (Mathare flood scenario)...")

    proc = subprocess.Popen(["venv/bin/python", "main.py"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        if not wait_for_server(proc):
            print("SERVER DID NOT START")
            print(proc.stdout.read())
            sys.exit(1)
        ok, fail = 0, 0
        for i, rep in enumerate(reports, 1):
            payload = {"message": rep["message"],
                       "location_hint": rep.get("location_hint") or None,
                       "is_simulated": True}
            try:
                t0 = time.time()
                r = requests.post(f"{BASE}/api/sentinel/reports?sync=true",
                                  json=payload, timeout=120)
                dt = time.time() - t0
                if r.status_code != 200:
                    print(f"[{i}/{len(reports)}] HTTP {r.status_code}: {r.text[:200]}")
                    fail += 1
                    continue
                body = r.json()
                inc = body["incident"]
                ex = inc["extraction"]
                geo = inc["resolved_place"] if inc["location_resolved"] else "UNRESOLVED"
                print(f"[{i}/{len(reports)}] {dt:4.1f}s type={ex['incident_type']:12s} "
                      f"lang={ex['detected_language']:3s} sev={ex['severity']:8s} "
                      f"u={ex['urgency']:2d} geo={geo} "
                      f"dups={len(body['duplicate_candidates'])}")
                ok += 1
            except Exception as e:  # noqa: BLE001
                print(f"[{i}/{len(reports)}] ERROR: {e}")
                fail += 1
        print(f"\nSeeded: {ok} ok, {fail} failed")
        print("stats:", requests.get(f"{BASE}/api/sentinel/stats", timeout=10).json())
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
