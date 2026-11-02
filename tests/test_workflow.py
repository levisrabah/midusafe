"""Verification workflow + audit trail + evidence traceability."""

import briefs
import sentinel_pipeline as pipe
import sentinel_store as store
from conftest import FakeService, chat_payload, valid_extraction


def _seed(tmpdb):
    svc = FakeService([chat_payload(valid_extraction())])
    inc, _ = pipe.process_report_sync("Mafuriko Mathare", "Mathare", service=svc)
    return inc


def test_verify_and_request_info(client, tmpdb):
    inc = _seed(tmpdb)
    r = client.post(f"/api/sentinel/incidents/{inc['id']}/verify",
                    json={"action": "verify"})
    assert r.status_code == 200
    assert r.json()["incident"]["status"] == "verified"
    r = client.post(f"/api/sentinel/incidents/{inc['id']}/verify",
                    json={"action": "request_info"})
    assert r.json()["incident"]["status"] == "needs_info"


def test_reclassify_priority_note(client, tmpdb):
    inc = _seed(tmpdb)
    r = client.post(f"/api/sentinel/incidents/{inc['id']}/verify",
                    json={"action": "reclassify", "value": "flash_flood"})
    assert r.json()["incident"]["classification"] == "flash_flood"
    r = client.post(f"/api/sentinel/incidents/{inc['id']}/verify",
                    json={"action": "priority", "value": "9"})
    assert r.json()["incident"]["priority"] == 9
    r = client.post(f"/api/sentinel/incidents/{inc['id']}/verify",
                    json={"action": "note", "value": "called ward admin"})
    assert r.status_code == 200
    r = client.post(f"/api/sentinel/incidents/{inc['id']}/verify",
                    json={"action": "priority", "value": "99"})
    assert r.status_code == 400


def test_every_action_audit_logged(client, tmpdb):
    inc = _seed(tmpdb)
    before = len(store.list_audit())
    client.post(f"/api/sentinel/incidents/{inc['id']}/verify", json={"action": "verify"})
    client.post(f"/api/sentinel/incidents/{inc['id']}/verify",
                json={"action": "note", "value": "hi"})
    entries = store.list_audit()
    assert len(entries) == before + 2
    actions = [e["action"] for e in entries]
    assert "verify" in actions and "note" in actions
    assert all(e["timestamp"] and e["target_id"] == inc["id"]
               for e in entries if e["action"] in ("verify", "note"))


def test_brief_citations_must_be_real(tmpdb, monkeypatch):
    inc = _seed(tmpdb)
    good = {"what_happened": "Flooding in Mathare.", "where": "Mathare",
            "when_reported": inc["created_at"],
            "evidence": [{"claim": "Water in homes",
                          "source_report_ids": [inc["report_id"]]}],
            "unknowns": ["depth"], "to_verify": ["depth"],
            "next_steps": ["Human review."]}
    monkeypatch.setattr(briefs, "meta_service", FakeService([chat_payload(good)]))
    brief, method = briefs.generate_brief(inc["id"])
    assert method == "meta"
    assert brief["evidence"][0]["source_report_ids"] == [inc["report_id"]]

    bad = dict(good)
    bad["evidence"] = [{"claim": "Fake", "source_report_ids": ["rep_nonexistent"]}]
    monkeypatch.setattr(briefs, "meta_service", FakeService([chat_payload(bad)]))
    brief2, method2 = briefs.generate_brief(inc["id"])
    assert method2 == "fallback"  # unknown citation rejected
    assert brief2["evidence"][0]["source_report_ids"] == [inc["report_id"]]


def test_stats_endpoint(client, tmpdb):
    _seed(tmpdb)
    r = client.get("/api/sentinel/stats")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["by_category"] == {"flood": 1}
