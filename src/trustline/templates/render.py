"""Substitute init placeholders in bundled contract templates."""

from __future__ import annotations

import re
from typing import Any

_PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def render_template(text: str, variables: dict[str, Any]) -> str:
    """Replace ``{{ key }}`` placeholders; leave ``{{ ref('...') }}`` unchanged."""

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key == "ref":
            return match.group(0)
        if key not in variables:
            return match.group(0)
        return str(variables[key])

    # Only replace simple word placeholders, not ref('...')
    return _PLACEHOLDER.sub(_replace, text)


DEFAULT_INIT_VARS: dict[str, str] = {
    "product_slug": "my_product",
    "product_name": "my_product",
    "owner_email": "team@example.com",
    "observation_start": "2025-01-01",
    "observation_end": "2025-03-31",
    "outcome_start": "2025-04-01",
    "outcome_end": "2025-04-30",
    "frozen_at": "2025-05-01T00:00:00Z",
    "cutover_date": "2025-03-15",
}
