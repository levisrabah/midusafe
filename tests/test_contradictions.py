"""Contradiction detection: Meta finds conflicts, Pydantic validates,
unknown cited ids are rejected."""

import contradictions as contra
from tests.conftest import FakeService, chat_payload, valid_extraction


def _incident(tmpdb, message, summary, rid="rep_a", iid="inc_a"):
    tmpdb.save_report(message, report_id=rid)
    tmpdb.save_incident(
        iid, rid,
        dict(valid_extraction(original_report=message,
                              translated_summary=summary)),
        {"resolved": True, "lat": -1.25, "lng": 36.87, "place": "Mathare"})
    return iid, rid


def test_contradiction_found_and_cited(tmpdb):
    _incident(tmpdb, "Daraja la miguu limefungwa, hampitiki kabisa.",
             "Footbridge is closed, totally impassable.",
             rid="rep_a", iid="inc_a")
    _incident(tmpdb, "Footbridge is passable, people crossing now.",
             "Footbridge is passable, people crossing now.",
             rid="rep_b", iid="inc_b")
    tmpdb.save_duplicate_candidate("inc_a", "inc_b", 0.8, ["same type"])
    svc = FakeService([chat_payload({
        "contradictions": [{
            "topic": "footbridge passability",
            "claim_a": "footbridge impassable",
            "report_id_a": "rep_a",
            "claim_b": "footbridge passable",
            "report_id_b": "rep_b",
        }]})])
    report, method = contra.generate_contradictions("inc_a", service=svc)
    assert method == "meta"
    assert len(report["contradictions"]) == 1
    c = report["contradictions"][0]
    assert c["report_id_a"] == "rep_a" and c["report_id_b"] == "rep_b"
    assert "impassable" in c["claim_a"] and "passable" in c["claim_b"]
    # trace recorded with real measured values
    trace = tmpdb.list_trace("inc_a")
    assert len(trace) == 1 and trace[0]["step"] == "contradiction_check"
    assert trace[0]["validation_passed"] == 1


def test_contradiction_rejects_unknown_ids(tmpdb):
    _incident(tmpdb, "Maji mengi hapa.", "Lots of water here.",
             rid="rep_a", iid="inc_a")
    _incident(tmpdb, "Water is receding.", "Water is receding.",
             rid="rep_b", iid="inc_b")
    tmpdb.save_duplicate_candidate("inc_a", "inc_b", 0.7, ["same type"])
    svc = FakeService([chat_payload({
        "contradictions": [{
            "topic": "water level",
            "claim_a": "lots of water",
            "report_id_a": "rep_a",
            "claim_b": "no water at all",
            "report_id_b": "rep_NOPE_unknown",
        }]})])
    report, method = contra.generate_contradictions("inc_a", service=svc)
    assert method == "fallback"
    assert report["contradictions"] == []
    assert "rep_NOPE_unknown" in report["note"]
    trace = tmpdb.list_trace("inc_a")
    assert trace[0]["validation_passed"] == 0


def test_contradiction_single_report_skipped(tmpdb):
    _incident(tmpdb, "Maji mengi hapa.", "Lots of water here.")
    report, method = contra.generate_contradictions(
        "inc_a", service=FakeService([]))
    assert method == "skipped_single_report"
    assert report["contradictions"] == []


def test_contradictions_endpoint_caches_and_audits(client, tmpdb):
    import contradictions as contramod
    _incident(tmpdb, "Daraja limefungwa.", "Bridge closed.",
             rid="rep_a", iid="inc_a")
    _incident(tmpdb, "Bridge is open.", "Bridge is open.",
             rid="rep_b", iid="inc_b")
    tmpdb.save_duplicate_candidate("inc_a", "inc_b", 0.8, ["same type"])
    svc = FakeService([chat_payload({"contradictions": []})])
    contramod.meta_service = svc
    try:
        r = client.get("/api/sentinel/incidents/inc_a/contradictions")
        assert r.status_code == 200
        assert r.json()["method"] == "meta"
        r2 = client.get("/api/sentinel/incidents/inc_a/contradictions")
        assert r2.json()["method"] == "cached"
        assert len(svc.calls) == 1
        actions = [a["action"] for a in tmpdb.list_audit()]
        assert "contradictions_checked" in actions
    finally:
        import meta_service as ms
        contramod.meta_service = ms.meta_service
