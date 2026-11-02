import json

import pytest

import sentinel_store as store


class FakeService:
    """Stub MetaService: canned chat() payloads, records calls."""

    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.calls = []

    def chat(self, messages, **kwargs):
        self.calls.append({"messages": messages, "kwargs": kwargs})
        if not self.payloads:
            raise AssertionError("FakeService out of payloads")
        return self.payloads.pop(0)

    @staticmethod
    def extract_chat_text(data):
        return data["choices"][0]["message"]["content"]


def chat_payload(content_dict_or_str):
    content = (content_dict_or_str if isinstance(content_dict_or_str, str)
               else json.dumps(content_dict_or_str))
    return {"choices": [{"message": {"content": content}}]}


def valid_extraction(**overrides):
    base = {
        "incident_type": "flood",
        "description": "Flooding with water entering homes.",
        "original_report": "Mafuriko hapa Mathare!",
        "detected_language": "sw",
        "translated_summary": "Flooding here in Mathare!",
        "location_mentioned": "Mathare",
        "time_mentioned": None,
        "severity": "high",
        "urgency": 8,
        "people_affected": None,
        "confidence": 0.9,
        "missing_information": ["water depth"],
        "follow_up_questions": ["How deep is the water?"],
    }
    base.update(overrides)
    return base


@pytest.fixture()
def tmpdb(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB_PATH", str(tmp_path / "t.db"))
    store.init_db()
    return store


@pytest.fixture()
def client(tmpdb, monkeypatch):
    """FastAPI TestClient with pipeline + briefs pointed at the tmp DB service."""
    import briefs
    import sentinel_pipeline as pipe
    from fastapi.testclient import TestClient

    import main
    monkeypatch.setattr(pipe, "meta_service", FakeService([]))
    monkeypatch.setattr(briefs, "meta_service", FakeService([]))
    return TestClient(main.app)
