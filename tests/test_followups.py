"""Follow-up drafts: generated in the reporter's language, queued for
human approval; approve/edit/discard audit-logged; nothing is ever sent."""

import followups as fup
from tests.conftest import FakeService, chat_payload, valid_extraction


def _incident(tmpdb, lang="sw", iid="inc_a", rid="rep_a"):
    tmpdb.save_report("Mafuriko hapa Mathare!", report_id=rid)
    tmpdb.save_incident(
        iid, rid,
        dict(valid_extraction(detected_language=lang)),
        {"resolved": True, "lat": -1.25, "lng": 36.87, "place": "Mathare"})


def test_followup_draft_in_swahili(tmpdb):
    _incident(tmpdb)
    svc = FakeService([chat_payload({
        "draft_text": "Maji yamefika kiwango gani nyumbani kwako?",
        "language": "sw"})])
    draft, method = fup.generate_followup("inc_a", service=svc)
    assert method == "meta"
    assert draft["language"] == "sw"
    assert "Maji" in draft["draft_text"]
    trace = tmpdb.list_trace("inc_a")
    assert trace[0]["step"] == "followup_draft"
    assert trace[0]["validation_passed"] == 1


def test_followup_wrong_language_falls_back(tmpdb):
    _incident(tmpdb)
    svc = FakeService([chat_payload({
        "draft_text": "How deep is the water?",
        "language": "en"})])  # reporter uses sw -> must reject
    draft, method = fup.generate_followup("inc_a", service=svc)
    assert method == "fallback"
    assert draft["draft_text"] == "How deep is the water?"  # stored q reused
    assert tmpdb.list_trace("inc_a")[0]["validation_passed"] == 0


def test_followup_approval_queue_flow(client, tmpdb):
    import followups as fupmod
    _incident(tmpdb, iid="inc_a")
    _incident(tmpdb, iid="inc_b", rid="rep_b")
    svc = FakeService([
        chat_payload({"draft_text": "Maji yako vipi sasa?", "language": "sw"}),
        chat_payload({"draft_text": "Maji yakoje leo?", "language": "sw"}),
    ])
    fupmod.meta_service = svc
    try:
        r = client.post("/api/sentinel/incidents/inc_a/followups")
        assert r.status_code == 200
        d1 = r.json()["draft"]
        assert d1["status"] == "pending" and d1["language"] == "sw"

        # approve with edit
        r = client.post(f"/api/sentinel/followups/{d1['id']}/decision",
                        json={"decision": "approved",
                              "edited_text": "Maji yako vipi sasa hivi?"})
        assert r.status_code == 200
        assert r.json()["status"] == "approved, ready to send"
        assert r.json()["draft"]["draft_text"] == "Maji yako vipi sasa hivi?"

        # second draft, discarded
        d2 = client.post("/api/sentinel/incidents/inc_b/followups").json()["draft"]
        r = client.post(f"/api/sentinel/followups/{d2['id']}/decision",
                        json={"decision": "discarded"})
        assert r.json()["status"] == "discarded"

        # double-decide rejected
        r = client.post(f"/api/sentinel/followups/{d2['id']}/decision",
                        json={"decision": "approved"})
        assert r.status_code == 409

        actions = [a["action"] for a in tmpdb.list_audit()]
        assert "followup_drafted" in actions
        assert "followup_approved" in actions
        assert "followup_discarded" in actions
    finally:
        import meta_service as ms
        fupmod.meta_service = ms.meta_service
