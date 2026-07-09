"""Tests for exception hierarchy."""

import pytest

from trustline.exceptions import AuditError, ExecutorError, TrustlineError, ValidationError


def test_exception_hierarchy() -> None:
    """Custom exceptions should inherit from TrustlineError."""
    assert issubclass(ValidationError, TrustlineError)
    assert issubclass(AuditError, TrustlineError)
    assert issubclass(ExecutorError, TrustlineError)


def test_validation_error_message() -> None:
    """ValidationError should carry a message."""
    with pytest.raises(ValidationError, match="invalid contract"):
        raise ValidationError("invalid contract")
