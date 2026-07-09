"""Slack notifications for trust audit failures."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from trustline.exceptions import TrustlineError
from trustline.scorecard.types import ScorecardResult


def resolve_webhook_url(explicit_url: str | None = None) -> str:
    """Resolve a Slack webhook URL from CLI flag or environment."""
    webhook_url = explicit_url or os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        msg = "Slack webhook URL not configured; set --slack-webhook or SLACK_WEBHOOK_URL"
        raise TrustlineError(msg)
    return webhook_url


def _phase_summary_lines(result: ScorecardResult) -> list[str]:
    lines: list[str] = []
    for phase in result.phases:
        if phase.phase_id > 4:
            continue
        lines.append(f"• Phase {phase.phase_id} {phase.name}: {phase.status.upper()}")
    return lines


def build_failure_payload(result: ScorecardResult, *, title: str) -> dict[str, Any]:
    """Build a Slack incoming-webhook payload for a failed audit."""
    summary = "\n".join(_phase_summary_lines(result))
    text = f"Trustline audit failed for {title} (verdict: {result.verdict.upper()})."
    return {
        "text": text,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Trustline audit failed*\n*{title}* — verdict `{result.verdict.upper()}`"
                    ),
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": summary or "_No SQL phase results._"},
            },
        ],
    }


def notify_audit_failure(
    webhook_url: str,
    result: ScorecardResult,
    *,
    title: str,
    timeout_seconds: float = 10.0,
) -> None:
    """Post a Slack webhook notification for a failed audit."""
    payload = build_failure_payload(result, title=title)
    request = urllib.request.Request(  # noqa: S310
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310
            if response.status >= 400:
                msg = f"Slack webhook returned HTTP {response.status}"
                raise TrustlineError(msg)
    except urllib.error.URLError as exc:
        msg = f"failed to post Slack notification: {exc.reason}"
        raise TrustlineError(msg) from exc
