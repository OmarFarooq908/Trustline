"""External integrations (Slack, GitHub Actions)."""

from trustline.integrations.slack import (
    build_failure_payload,
    notify_audit_failure,
    resolve_webhook_url,
)

__all__ = ["build_failure_payload", "notify_audit_failure", "resolve_webhook_url"]
