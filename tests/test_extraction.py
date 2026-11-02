"""Multilingual extraction, invalid output, missing location."""

import pytest

import sentinel_pipeline as pipe
from conftest import FakeService, chat_payload, valid_extraction


def test_swahili_extraction_validated(tmpdb):
    svc = FakeService([chat_payload(valid_extraction())])
    inc, cands = pipe.process_report_sync("Mafuriko hapa Mathare!", service=svc)
    ex = inc["extraction"]
    assert ex["incident_type"] == "flood"
    assert ex["detected_language"] == "sw"
    assert inc["location_resolved"] == 1
    assert inc["latitude"] == pytest.approx(-1.2618, abs=0.01)


def test_sheng_and_english_extraction(tmpdb):
    svc = FakeService([
        chat_payload(valid_extraction(
            detected_language="sh", location_mentioned="Huruma",
            translated_summary="Flooding on the Huruma side.")),
        chat_payload(valid_extraction(
            incident_type="fire", detected_language="en",
            location_mentioned="Kimathi Street", severity="low", urgency=3,
            translated_summary="Small kiosk fire.")),
    ])
    inc1, _ = pipe.process_report_sync("Maji imeflood Huruma sides", service=svc)
    assert inc1["extraction"]["detected_language"] == "sh"
    assert inc1["resolved_place"] == "Huruma, Nairobi"
    inc2, _ = pipe.process_report_sync("Small fire at a kiosk", "Kimathi Street",
                                       service=svc)
    assert inc2["extraction"]["incident_type"] == "fire"
    assert inc2["extraction"]["detected_language"] == "en"


def test_invalid_json_rejected(tmpdb):
    svc = FakeService([chat_payload("not json {{{")])
    with pytest.raises(ValueError, match="invalid JSON"):
        pipe.process_report_sync("hello", service=svc)


def test_schema_violation_rejected(tmpdb):
    bad = valid_extraction()
    bad["urgency"] = 99  # out of range
    svc = FakeService([chat_payload(bad)])
    with pytest.raises(ValueError, match="schema validation"):
        pipe.process_report_sync("hello", service=svc)


def test_missing_location_stays_unresolved(tmpdb):
    svc = FakeService([chat_payload(
        valid_extraction(location_mentioned=None, confidence=0.5))])
    inc, _ = pipe.process_report_sync(
        "Flooding somewhere near the river, not sure where", service=svc)
    assert inc["location_resolved"] == 0
    assert inc["latitude"] is None
    assert inc["longitude"] is None
    assert inc["resolved_place"] is None


def test_unknown_place_name_stays_unresolved(tmpdb):
    svc = FakeService([chat_payload(
        valid_extraction(location_mentioned="Kwa Njuguna village"))])
    inc, _ = pipe.process_report_sync("Maji hapa Kwa Njuguna village", service=svc)
    assert inc["location_resolved"] == 0
    assert inc["latitude"] is None
