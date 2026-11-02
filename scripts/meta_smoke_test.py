"""Meta Model API smoke test (Phase 2 verification).

Uses ONLY documented endpoints from https://dev.meta.ai/docs:
  - POST {base}/responses          (Responses API, plain text)
  - POST {base}/chat/completions   (Chat Completions API, structured JSON output)
  - GET  {base}/models             (list accessible models)

Auth: Bearer key from META_API_KEY (fallback MODEL_API_KEY) env var.
The key is NEVER printed, logged, or included in output.

Usage:
    venv/bin/python scripts/meta_smoke_test.py
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("META_BASE_URL", "https://api.meta.ai/v1").rstrip("/")
KEY = os.getenv("META_API_KEY") or os.getenv("MODEL_API_KEY")

SWAHILI_REPORT = (
    "Mafuriko makubwa hapa Mathare, maji yameingia nyumbani na watu "
    "wamekwama darini. Tunahitaji msaada haraka!"
)

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "incident_type": {"type": "string"},
        "description": {"type": "string"},
        "detected_language": {"type": "string"},
        "translated_summary": {"type": "string"},
        "location_mentioned": {"type": "string"},
        "severity": {"type": "string"},
        "urgency": {"type": "integer"},
        "confidence": {"type": "number"},
    },
    "required": [
        "incident_type",
        "description",
        "detected_language",
        "translated_summary",
        "location_mentioned",
        "severity",
        "urgency",
        "confidence",
    ],
    "additionalProperties": False,
}


def redact(text: str) -> str:
    """Redact the key if it ever appears in an error/output string."""
    if KEY and text:
        return text.replace(KEY, "[REDACTED]")
    return text


def headers():
    return {"Authorization": "Bearer [REDACTED]", "Content-Type": "application/json"}


def real_headers():
    return {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def test_list_models():
    print("=" * 70)
    print("TEST 1: GET /models  (which models can this key access?)")
    print("=" * 70)
    try:
        r = requests.get(f"{BASE_URL}/models", headers=real_headers(), timeout=30)
        print(f"HTTP {r.status_code}")
        print(redact(r.text[:4000]))
        return r.status_code, r.text
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {redact(str(e))}")
        return None, None


def test_responses_plain():
    print()
    print("=" * 70)
    print("TEST 2: POST /responses with muse-spark-1.3 (plain Swahili report)")
    print("=" * 70)
    payload = {
        "model": "muse-spark-1.3",
        "input": (
            "You are an emergency dispatcher. A community member sent this "
            f"report: '{SWAHILI_REPORT}' Reply in English with one short "
            "sentence classifying the incident type and urgency."
        ),
    }
    try:
        r = requests.post(
            f"{BASE_URL}/responses", headers=real_headers(), json=payload, timeout=60
        )
        print(f"HTTP {r.status_code}")
        print(redact(r.text[:4000]))
        return r.status_code, r.text
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {redact(str(e))}")
        return None, None


def test_chat_structured():
    print()
    print("=" * 70)
    print("TEST 3: POST /chat/completions with response_format json_schema")
    print("=" * 70)
    payload = {
        "model": "muse-spark-1.3",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You extract structured incident data from emergency "
                    "reports. Never invent coordinates, casualty numbers, "
                    "or facts not stated in the report."
                ),
            },
            {"role": "user", "content": SWAHILI_REPORT},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "Incident", "schema": EXTRACTION_SCHEMA},
        },
    }
    try:
        r = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=real_headers(),
            json=payload,
            timeout=60,
        )
        print(f"HTTP {r.status_code}")
        body = redact(r.text[:6000])
        print(body)
        # Validate the returned JSON parses and matches schema keys
        if r.status_code == 200:
            try:
                content = r.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                missing = [
                    k for k in EXTRACTION_SCHEMA["required"] if k not in parsed
                ]
                print(f"\n>>> Structured JSON parsed OK. Missing keys: {missing or 'none'}")
            except Exception as e:  # noqa: BLE001
                print(f"\n>>> Could not parse structured content: {redact(str(e))}")
        return r.status_code, r.text
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {redact(str(e))}")
        return None, None


def main():
    if not KEY:
        print("FATAL: neither META_API_KEY nor MODEL_API_KEY is set. Cannot test.")
        sys.exit(2)
    print(f"Base URL: {BASE_URL}")
    print(f"Key present: yes (length {len(KEY)}, NOT shown)")
    print(f"Swahili test report: {SWAHILI_REPORT}")
    print()
    test_list_models()
    test_responses_plain()
    test_chat_structured()
    print()
    print("Smoke test finished.")


if __name__ == "__main__":
    main()
