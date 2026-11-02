"""Meta service: timeout, retries, auth errors, key redaction."""

import pytest
import requests

from meta_service import (MetaAPIError, MetaAuthError, MetaRateLimitError,
                          MetaTimeoutError, MetaService)


class _TimeoutSession:
    def __init__(self):
        self.calls = 0

    def request(self, *a, **k):
        self.calls += 1
        raise requests.Timeout("slow")


class _FlakySession:
    """429 once, then 200."""

    def __init__(self):
        self.calls = 0

    def request(self, *a, **k):
        self.calls += 1
        if self.calls == 1:
            return _Resp(429, {"error": {"code": "rate_limited", "message": "slow down"}})
        return _Resp(200, {"ok": True})


class _Resp:
    def __init__(self, status, payload):
        self.status_code = status
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload


def test_timeout_raises_typed_error_after_retries():
    svc = MetaService(api_key="SECRETKEY", max_retries=1, timeout=1)
    svc._session = _TimeoutSession()
    with pytest.raises(MetaTimeoutError):
        svc.list_models()
    assert svc._session.calls == 2  # initial + 1 retry


def test_retry_on_429_then_success():
    svc = MetaService(api_key="SECRETKEY", max_retries=2)
    svc._session = _FlakySession()
    assert svc.list_models() == {"ok": True}
    assert svc._session.calls == 2


def test_429_exhausted_raises_rate_limit():
    class Always429:
        def request(self, *a, **k):
            return _Resp(429, {"error": {"code": "rate_limited", "message": "slow"}})

    svc = MetaService(api_key="SECRETKEY", max_retries=0)
    svc._session = Always429()
    with pytest.raises(MetaRateLimitError):
        svc.list_models()


def test_missing_key_raises_auth_error():
    svc = MetaService(api_key=None, base_url="https://api.meta.ai/v1")
    svc.api_key = None
    assert not svc.configured
    with pytest.raises(MetaAuthError):
        svc.list_models()


def test_key_never_in_error_text():
    class Boom:
        def request(self, *a, **k):
            raise requests.ConnectionError("boom SECRETKEY-visible")

    svc = MetaService(api_key="SECRETKEY-visible", max_retries=0)
    svc._session = Boom()
    with pytest.raises(MetaAPIError) as ei:
        svc.list_models()
    assert "SECRETKEY-visible" not in str(ei.value)
    assert "[REDACTED]" in str(ei.value)
