"""Jinja2 SQL template rendering and ref() resolution."""

from __future__ import annotations

import re
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from trustline.compiler.paths import template_dir
from trustline.config import Profile
from trustline.exceptions import AuditError, ValidationError

_REF_PATTERN = re.compile(r"\{\{\s*ref\('([^']+)'\)\s*\}\}")
_ENVIRONMENT: Environment | None = None


def qualify_table(model: str, profile: Profile) -> str:
    """Resolve a model name to a fully qualified warehouse table."""
    if not model:
        msg = "model name must be non-empty"
        raise ValidationError(msg)
    if profile.target == "duckdb":
        return f"{profile.schema}.{model}"
    return f"{profile.database}.{profile.schema}.{model}"


def resolve_refs(expr: str, profile: Profile) -> str:
    """Replace ``ref('model')`` expressions with qualified table names."""

    def _replace(match: re.Match[str]) -> str:
        return qualify_table(match.group(1), profile)

    return _REF_PATTERN.sub(_replace, expr)


def _environment() -> Environment:
    """Return a cached Jinja2 environment for SQL templates."""
    global _ENVIRONMENT
    if _ENVIRONMENT is None:
        _ENVIRONMENT = Environment(
            loader=FileSystemLoader(template_dir()),
            autoescape=select_autoescape(default=False, enabled_extensions=()),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )
    return _ENVIRONMENT


def render_template(name: str, context: dict[str, Any], dialect: str) -> str:
    """Render a named SQL template with dialect-aware context."""
    if not name.endswith(".sql.j2"):
        name = f"{name}.sql.j2"
    try:
        template = _environment().get_template(name)
    except Exception as exc:
        msg = f"SQL template not found: {name}"
        raise AuditError(msg) from exc

    render_context = {**context, "dialect": dialect}
    try:
        return template.render(**render_context).strip()
    except Exception as exc:
        msg = f"failed to render SQL template {name}: {exc}"
        raise AuditError(msg) from exc
