"""Server-side Meta Model API client for MIDUSAFE Sentinel.

Docs: https://dev.meta.ai/docs (Responses, Chat Completions, Models, Voice).
  - Base URL : https://api.meta.ai/v1            (override: META_BASE_URL)
  - Auth     : Authorization: Bearer <key>       (META_API_KEY, fallback MODEL_API_KEY)
  - Model    : muse-spark-1.3                    (override: META_MODEL)

The API key NEVER leaves the backend: it is read from env, never logged,
never returned, and redacted from every error message.
"""

import logging
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("sentinel.meta")

DEFAULT_BASE_URL = "https://api.meta.ai/v1"
DEFAULT_MODEL = "muse-spark-1.3"
DEFAULT_TIMEOUT = 45
DEFAULT_RETRIES = 2
RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}


class MetaAPIError(Exception):
    """Base error for Meta API failures (key already redacted)."""

    def __init__(self, message, status_code=None, code=None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class MetaAuthError(MetaAPIError):
    """401/403 - bad or missing key."""


class MetaTimeoutError(MetaAPIError):
    """Request timed out."""


class MetaRateLimitError(MetaAPIError):
    """429 - rate limited."""


class MetaModelError(MetaAPIError):
    """404 model_not_found or bad request."""


def _redact(text, key):
    if key and text:
        return str(text).replace(key, "[REDACTED]")
    return str(text) if text is not None else ""


class MetaService:
    """Thin, swappable client over the documented Meta Model API."""

    def __init__(self, api_key=None, base_url=None, model=None,
                 timeout=DEFAULT_TIMEOUT, max_retries=DEFAULT_RETRIES,
                 session=None):
        self.api_key = (
            api_key or os.getenv("META_API_KEY") or os.getenv("MODEL_API_KEY")
        )
        self.base_url = (base_url or os.getenv("META_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.model = model or os.getenv("META_MODEL", DEFAULT_MODEL)
        self.timeout = float(os.getenv("META_TIMEOUT", timeout))
        self.max_retries = int(os.getenv("META_RETRIES", max_retries))
        self._session = session or requests.Session()

    @property
    def configured(self):
        return bool(self.api_key)

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"}

    def _request(self, method, path, payload=None, timeout=None):
        if not self.configured:
            raise MetaAuthError("Meta API key is not configured (set META_API_KEY).")
        url = f"{self.base_url}{path}"
        timeout = timeout or self.timeout
        last_err = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self._session.request(
                    method, url,
                    headers=self._headers(),
                    json=payload,
                    timeout=timeout,
                )
            except requests.Timeout as e:
                last_err = MetaTimeoutError(
                    f"Meta API timed out after {timeout}s (attempt {attempt + 1}).")
                logger.warning("meta timeout attempt=%d err=%s", attempt + 1, e)
            except requests.RequestException as e:
                last_err = MetaAPIError(
                    f"Meta API connection failed: {_redact(e, self.api_key)}")
                logger.warning("meta connection error attempt=%d err=%s", attempt + 1, e)
            else:
                if resp.status_code == 200:
                    return resp.json()
                last_err = self._error_for_status(resp)
                if resp.status_code not in RETRYABLE_STATUS:
                    raise last_err
                logger.warning("meta retryable status=%d attempt=%d",
                               resp.status_code, attempt + 1)
            if attempt < self.max_retries:
                time.sleep(2 ** attempt)
        raise last_err

    def _error_for_status(self, resp):
        try:
            body = resp.json()
        except Exception:  # noqa: BLE001
            body = {}
        err = body.get("error", {}) if isinstance(body, dict) else {}
        code = err.get("code") or body.get("code")
        msg = (_redact(err.get("message"), self.api_key)
               or _redact(resp.text[:300], self.api_key)
               or f"HTTP {resp.status_code}")
        if resp.status_code in (401, 403):
            return MetaAuthError(f"Meta auth failed ({resp.status_code}): {msg}",
                                 resp.status_code, code)
        if resp.status_code == 429:
            return MetaRateLimitError(f"Meta rate limited: {msg}",
                                      resp.status_code, code)
        if resp.status_code == 404:
            return MetaModelError(f"Meta model/endpoint not found: {msg}",
                                  resp.status_code, code)
        return MetaAPIError(f"Meta API error ({resp.status_code}): {msg}",
                            resp.status_code, code)

    # ---- documented endpoints ----

    def list_models(self):
        """GET /models - models this key can access."""
        return self._request("GET", "/models")

    def respond(self, user_input, model=None, instructions=None, timeout=None):
        """POST /responses - plain text answer (Responses API)."""
        payload = {"model": model or self.model, "input": user_input}
        if instructions:
            payload["instructions"] = instructions
        data = self._request("POST", "/responses", payload, timeout=timeout)
        return self.extract_response_text(data), data

    def chat(self, messages, model=None, response_format=None,
             timeout=None, **kwargs):
        """POST /chat/completions - optionally with json_schema response_format."""
        payload = {"model": model or self.model, "messages": messages}
        if response_format is not None:
            payload["response_format"] = response_format
        payload.update(kwargs)
        return self._request("POST", "/chat/completions", payload, timeout=timeout)

    def transcribe_file(self, audio_bytes, filename="report.wav",
                        language=None, timeout=None):
        """POST /v1/asr/transcribe - file transcription (Muse Voice Transcribe).

        Verified against the key at runtime; raises MetaAPIError on failure.
        """
        if not self.configured:
            raise MetaAuthError("Meta API key is not configured (set META_API_KEY).")
        url = f"{self.base_url}/asr/transcribe"
        last_err = None
        for attempt in range(self.max_retries + 1):
            try:
                files = {"file": (filename, audio_bytes)}
                form = {"model": "muse-voice-transcribe-1.0"}
                if language:
                    form["language"] = language
                resp = self._session.post(
                    url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files=files,
                    data=form,
                    timeout=timeout or 90,
                )
            except requests.Timeout as e:
                last_err = MetaTimeoutError(f"Voice transcribe timed out: {e}")
            except requests.RequestException as e:
                last_err = MetaAPIError(
                    f"Voice transcribe failed: {_redact(e, self.api_key)}")
            else:
                if resp.status_code == 200:
                    return resp.json()
                last_err = self._error_for_status(resp)
                if resp.status_code not in RETRYABLE_STATUS:
                    raise last_err
            if attempt < self.max_retries:
                time.sleep(2 ** attempt)
        raise last_err

    # ---- helpers ----

    @staticmethod
    def extract_response_text(data):
        """Pull assistant text out of a Responses API object."""
        for item in data.get("output", []) or []:
            if item.get("type") == "message":
                for part in item.get("content", []) or []:
                    if part.get("type") == "output_text":
                        return part.get("text", "")
        return ""

    @staticmethod
    def extract_chat_text(data):
        """Pull assistant text out of a Chat Completions object."""
        choices = data.get("choices", []) or []
        if choices:
            return (choices[0].get("message", {}) or {}).get("content", "") or ""
        return ""


# Shared instance used by the app (tests inject their own service/stub).
meta_service = MetaService()
