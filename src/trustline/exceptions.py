"""Custom exception hierarchy for Trustline."""


class TrustlineError(Exception):
    """Base exception for all Trustline errors."""


class ValidationError(TrustlineError):
    """Raised when contract or schema validation fails."""


class AuditError(TrustlineError):
    """Raised when scorecard audit execution fails."""


class ExecutorError(TrustlineError):
    """Raised when warehouse adapter execution fails."""
