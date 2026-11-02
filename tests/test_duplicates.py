"""Duplicate detection: scoring, reasons, no auto-merge, confirm/reject."""

import sentinel_pipeline as pipe
import sentinel_store as store
from conftest import FakeService, chat_payload, valid_extraction


def _seed_two(tmpdb):
    svc = FakeService([
        chat_payload(valid_extraction(location_mentioned="Mathare")),
        chat_payload(valid_extraction(location_mentioned="Mathare North",
                                       description="Flooding with water in houses.")),
    ])
    inc1, _ = pipe.process_report_sync("Mafuriko Mathare", "Mathare", service=svc)
    inc2, cands = pipe.process_report_sync("Mafuriko Mathare North",
                                           "Mathare North", service=svc)
    return inc1, inc2, cands


def test_similar_reports_flagged_with_reasons(tmpdb):
    inc1, inc2, cands = _seed_two(tmpdb)
    assert len(cands) >= 1
    top = cands[0]
    assert top["other_incident_id"] == inc1["id"]
    assert top["score"] >= 0.55
    assert any("Same incident type" in r for r in top["reasons"])
    assert any("Locations match" in r for r in top["reasons"])


def test_different_type_not_flagged(tmpdb):
    svc = FakeService([
        chat_payload(valid_extraction()),
        chat_payload(valid_extraction(
            incident_type="fire", location_mentioned="Kimathi Street",
            description="Small kiosk fire put out quickly.",
            translated_summary="Small kiosk fire.")),
    ])
    pipe.process_report_sync("Mafuriko Mathare", "Mathare", service=svc)
    _, cands = pipe.process_report_sync("Fire on Kimathi Street",
                                        "Kimathi Street", service=svc)
    assert cands == []


def test_originals_preserved_and_decision_recorded(tmpdb):
    inc1, inc2, cands = _seed_two(tmpdb)
    links = store.list_duplicate_links(status="pending")
    assert len(links) >= 1
    link = links[0]
    # originals untouched
    assert store.get_incident(inc1["id"])["extraction"]["location_mentioned"] == "Mathare"
    assert store.get_incident(inc2["id"])["extraction"]["location_mentioned"] == "Mathare North"
    store.decide_duplicate(link["id"], "confirmed")
    remaining = store.list_duplicate_links(status="pending")
    assert all(l["id"] != link["id"] for l in remaining)
    decided = [l for l in store.list_duplicate_links() if l["id"] == link["id"]][0]
    assert decided["status"] == "confirmed"
    assert decided["decided_at"]
