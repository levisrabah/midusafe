"""Meta AI trace: every step records its real model, measured latency,
and validation outcome; trace endpoint serves them per incident."""

import sentinel_pipeline as pipe
from tests.conftest import FakeService, chat_payload, valid_extraction


def test_extraction_trace_logged(tmpdb):
    svc = FakeService([chat_payload(valid_extraction())])
    incident, _ = pipe.process_report_sync("Mafuriko hapa Mathare!",
                                           service=svc)
    trace = tmpdb.list_trace(incident["id"])
    assert len(trace) == 1
    t = trace[0]
    assert t["step"] == "extraction"
    assert t["validation_passed"] == 1
    assert isinstance(t["latency_ms"], int) and t["latency_ms"] >= 0
    assert t["model"]  # real model name (or stub in tests)


def test_voice_trace_claimed_to_incident(tmpdb):
    tid = tmpdb.log_trace(None, "voice_transcribe",
                          "muse-voice-transcribe-1.0", 1200, True, "15 chars")
    assert tmpdb.list_trace("inc_x") == []
    tmpdb.claim_trace(tid, "inc_x")
    rows = tmpdb.list_trace("inc_x")
    assert len(rows) == 1 and rows[0]["step"] == "voice_transcribe"
    assert rows[0]["model"] == "muse-voice-transcribe-1.0"


def test_trace_endpoint(client, tmpdb):
    tmpdb.save_report("Maji mengi.", report_id="rep_a")
    tmpdb.save_incident("inc_a", "rep_a", dict(valid_extraction()),
                        {"resolved": False, "lat": None, "lng": None,
                         "place": None})
    tmpdb.log_trace("inc_a", "extraction", "muse-spark-1.3", 8100, True,
                    "type=flood")
    r = client.get("/api/sentinel/incidents/inc_a/trace")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 1 and rows[0]["model"] == "muse-spark-1.3"
    assert client.get("/api/sentinel/incidents/inc_nope/trace").status_code == 404
