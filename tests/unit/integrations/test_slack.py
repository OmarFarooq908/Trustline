"""Tests for Slack audit notifications."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from trustline.exceptions import TrustlineError
from trustline.executors.base import CheckResult
from trustline.integrations.slack import (
    build_failure_payload,
    notify_audit_failure,
    resolve_webhook_url,
)
from trustline.scorecard.types import PhaseResult, ScorecardResult


def test_resolve_webhook_url_prefers_explicit_value() -> None:
    """Explicit webhook URL should take precedence over environment."""
    with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": "https://example.com/env"}, clear=True):
        assert resolve_webhook_url("https://example.com/cli") == "https://example.com/cli"


def test_resolve_webhook_url_reads_environment() -> None:
    """Webhook URL should fall back to SLACK_WEBHOOK_URL."""
    with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": "https://example.com/env"}, clear=True):
        assert resolve_webhook_url() == "https://example.com/env"


def test_resolve_webhook_url_raises_when_missing() -> None:
    """Missing webhook configuration should raise TrustlineError."""
    with patch.dict("os.environ", {}, clear=True), pytest.raises(TrustlineError, match="webhook"):
        resolve_webhook_url()


def test_resolve_webhook_url_rejects_non_https() -> None:
    """Webhook URL must use https."""
    with pytest.raises(TrustlineError, match="https URL"):
        resolve_webhook_url("http://hooks.slack.com/services/test")


def test_build_failure_payload_includes_phase_summary() -> None:
    """Slack payload should summarize failed SQL phases."""
    phase = PhaseResult(
        phase_id=2,
        name="Population Funnel",
        status="fail",
        checks=(
            CheckResult(
                check_id="funnel.retention.training_positives.app_identity_match",
                status="fail",
                actual=35.0,
                expected=40.0,
                evidence={},
            ),
        ),
    )
    result = ScorecardResult(verdict="fail", phases=(phase,))
    payload = build_failure_payload(result, title="ACME Stream")

    assert "ACME Stream" in payload["text"]
    assert "Population Funnel" in payload["blocks"][1]["text"]["text"]


def test_notify_audit_failure_posts_json_payload() -> None:
    """notify_audit_failure should POST JSON to the Slack webhook."""
    result = ScorecardResult(verdict="fail", phases=())
    response = MagicMock()
    response.status = 200
    response.__enter__.return_value = response
    response.__exit__.return_value = False

    with patch("urllib.request.urlopen", return_value=response) as urlopen:
        notify_audit_failure("https://hooks.slack.com/services/test", result, title="Demo")

    request = urlopen.call_args.args[0]
    assert request.get_full_url() == "https://hooks.slack.com/services/test"
    assert request.method == "POST"
    body = json.loads(request.data.decode("utf-8"))
    assert body["text"].startswith("Trustline audit failed")
