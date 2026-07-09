"""Redact secrets from scorecard evidence before reporting."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

_REDACTED = "[REDACTED]"
_CONNECTION_URI = re.compile(r"(\w+://)([^:@/\s]+):([^@/\s]+)@")
_SECRET_KV = re.compile(
    r"(?i)\b(password|passwd|token|secret|api[_-]?key)\s*=\s*\S+",
)


def _redact_string(value: str) -> str:
    """Redact connection strings and secret key-value pairs from a string."""
    redacted = _CONNECTION_URI.sub(rf"\1{_REDACTED}@", value)
    return _SECRET_KV.sub(lambda match: f"{match.group(1)}={_REDACTED}", redacted)


def _looks_like_connection_string(value: str) -> bool:
    """Return True when a string resembles a warehouse connection URI."""
    if "://" not in value:
        return False
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)


def redact_secrets(value: Any) -> Any:
    """Recursively redact secrets from evidence payloads."""
    if isinstance(value, str):
        if _looks_like_connection_string(value):
            return _REDACTED
        return _redact_string(value)
    if isinstance(value, dict):
        return {key: redact_secrets(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_secrets(item) for item in value)
    return value
