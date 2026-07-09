"""Tests for evidence redaction."""

from trustline.reporters.redact import redact_secrets


def test_redact_secrets_masks_connection_uri_credentials() -> None:
    """Connection URIs with embedded credentials should be redacted."""
    payload = {
        "dsn": "snowflake://user:supersecret@account/db/schema?warehouse=wh",
        "nested": ["postgresql://admin:pass@host:5432/db"],
    }
    redacted = redact_secrets(payload)
    assert "supersecret" not in str(redacted)
    assert "pass" not in redacted["nested"][0]
    assert "[REDACTED]" in redacted["dsn"]


def test_redact_secrets_masks_key_value_secrets() -> None:
    """password= and token= style secrets should be redacted."""
    value = "connect password=hunter2 token=abc123"
    assert "hunter2" not in redact_secrets(value)
    assert "abc123" not in redact_secrets(value)


def test_redact_secrets_preserves_table_names() -> None:
    """Benign table references should remain intact."""
    payload = {"table": "main.donor_gifts", "rows": [{"retention_pct": 31.25}]}
    assert redact_secrets(payload) == payload
