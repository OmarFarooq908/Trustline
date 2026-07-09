"""trustline audit — five-phase trust scorecard."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Annotated, Literal

import typer

from trustline.compiler.audit_profile import compile_audit_profile_checks
from trustline.compiler.cohort import compile_cohort_checks
from trustline.compiler.funnel import compile_funnel_checks
from trustline.config import (
    Profile,
    load_profile,
    resolve_duckdb_path,
    resolve_profiles_path,
)
from trustline.contracts.audit_profile import AuditProfile, load_audit_profile
from trustline.contracts.loader import load_contracts_dir
from trustline.contracts.models import CohortManifest, FunnelContract
from trustline.exceptions import AuditError, ExecutorError, TrustlineError, ValidationError
from trustline.executors.base import CompiledCheck, Executor
from trustline.executors.duckdb import DuckDBExecutor
from trustline.reporters.brief import render_brief
from trustline.reporters.json_report import render_scorecard_json
from trustline.reporters.markdown import render_scorecard
from trustline.reporters.rich_console import render_scorecard_console
from trustline.scorecard._common import dialect_for_profile
from trustline.scorecard.orchestrator import run_full_audit
from trustline.scorecard.types import ScorecardResult

logger = logging.getLogger(__name__)

app = typer.Typer(help="Run five-phase trust scorecard audit.")
OutputFormat = Literal["text", "json", "both"]


def _default_audit_profile_path(contracts_dir: Path) -> Path:
    return contracts_dir.parent / "audit_profile.yaml"


def _load_audit_profile(path: Path) -> AuditProfile | None:
    if not path.is_file():
        return None
    return load_audit_profile(path)


def _compile_checks(
    contracts: list[FunnelContract | CohortManifest],
    audit_profile: AuditProfile | None,
    profile: Profile,
) -> list[CompiledCheck]:
    dialect = dialect_for_profile(profile.target)
    checks: list[CompiledCheck] = []
    if audit_profile is not None:
        checks.extend(compile_audit_profile_checks(audit_profile, profile, dialect))
    for contract in contracts:
        if isinstance(contract, FunnelContract):
            checks.extend(compile_funnel_checks(contract, profile, dialect))
        elif isinstance(contract, CohortManifest):
            checks.extend(compile_cohort_checks(contract, profile, dialect))
    return checks


def _build_executor(profile: Profile, profiles_path: Path) -> Executor:
    if profile.target == "duckdb":
        database = resolve_duckdb_path(profile, profiles_path)
        if not database.is_file():
            msg = f"DuckDB database not found: {database}"
            raise TrustlineError(msg)
        return DuckDBExecutor(database)
    if profile.target == "snowflake":
        from trustline.executors.snowflake import SnowflakeExecutor

        return SnowflakeExecutor.from_env(profile)
    msg = f"unsupported warehouse target: {profile.target!r}"
    raise TrustlineError(msg)


def _print_text_summary(
    result: ScorecardResult,
    *,
    title: str,
    no_color: bool = False,
) -> None:
    render_scorecard_console(result, title=title, no_color=no_color)


def _write_reports(result: ScorecardResult, output_dir: Path, *, title: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "scorecard.md").write_text(
        render_scorecard(result, title=title),
        encoding="utf-8",
    )
    (output_dir / "scorecard.json").write_text(
        json.dumps(render_scorecard_json(result), indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "brief.md").write_text(render_brief(result), encoding="utf-8")


def _exit_code_for_verdict(verdict: str) -> int:
    return 1 if verdict == "fail" else 0


def _maybe_notify_slack(
    notify: str | None,
    slack_webhook: str | None,
    result: ScorecardResult,
    *,
    title: str,
) -> None:
    """Send Slack notification when configured and the audit failed."""
    if notify is None:
        return
    if notify != "slack":
        msg = f"unsupported notification channel: {notify!r}"
        raise TrustlineError(msg)
    if result.verdict != "fail":
        return

    from trustline.integrations.slack import notify_audit_failure, resolve_webhook_url

    webhook_url = resolve_webhook_url(slack_webhook)
    notify_audit_failure(webhook_url, result, title=title)


@app.callback(invoke_without_command=True)
def audit(  # noqa: PLR0913
    contracts: str = typer.Option(
        "./contracts",
        "--contracts",
        "-c",
        help="Directory containing contract YAML files.",
    ),
    target: str = typer.Option(
        "duckdb",
        "--target",
        "-t",
        help="Warehouse target: duckdb or snowflake.",
    ),
    profile_name: str = typer.Option(
        "default",
        "--profile",
        "-p",
        help="Profile name in profiles.yml.",
    ),
    audit_profile_path: str | None = typer.Option(
        None,
        "--audit-profile",
        help="Path to audit_profile.yaml (default: sibling of contracts directory).",
    ),
    profiles_path: str | None = typer.Option(
        None,
        "--profiles",
        help="Path to profiles.yml (default: ./profiles.yml or ACME example).",
    ),
    output_dir: str = typer.Option(
        ".",
        "--output-dir",
        help="Directory for scorecard.md and scorecard.json.",
    ),
    output_format: Annotated[
        OutputFormat,
        typer.Option("--output", "-o", help="Output format: text, json, or both."),
    ] = "text",
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Compile checks only; do not execute SQL.",
    ),
    notify: str | None = typer.Option(
        None,
        "--notify",
        help="Notification channel on failure (slack).",
    ),
    slack_webhook: str | None = typer.Option(
        None,
        "--slack-webhook",
        envvar="SLACK_WEBHOOK_URL",
        help="Slack incoming webhook URL.",
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        help="Disable ANSI colors in terminal output.",
    ),
) -> None:
    """Run the five-phase trust scorecard against contract YAML."""
    try:
        contracts_dir = Path(contracts)
        if not contracts_dir.is_dir():
            typer.echo(f"ERROR: contracts directory not found: {contracts_dir}", err=True)
            raise typer.Exit(code=2)

        resolved_profiles = resolve_profiles_path(
            Path(profiles_path) if profiles_path is not None else None
        )
        if not resolved_profiles.is_file():
            typer.echo(f"ERROR: profiles file not found: {resolved_profiles}", err=True)
            raise typer.Exit(code=2)

        profile = load_profile(profile_name, resolved_profiles)
        if profile.target != target:
            typer.echo(
                f"ERROR: profile {profile_name!r} target {profile.target!r} "
                f"does not match --target {target!r}",
                err=True,
            )
            raise typer.Exit(code=2)

        documents = load_contracts_dir(contracts_dir)
        if not documents:
            typer.echo("ERROR: no contract files found.", err=True)
            raise typer.Exit(code=2)

        audit_path = (
            Path(audit_profile_path)
            if audit_profile_path is not None
            else _default_audit_profile_path(contracts_dir)
        )
        audit_profile = _load_audit_profile(audit_path)

        if dry_run:
            compiled = _compile_checks(documents, audit_profile, profile)
            typer.echo(f"Compiled {len(compiled)} checks (dry run).")
            raise typer.Exit(code=0)

        executor = _build_executor(profile, resolved_profiles)
        try:
            result = run_full_audit(documents, audit_profile, executor, profile)
        finally:
            if hasattr(executor, "close"):
                executor.close()

        title = contracts_dir.parent.name.replace("_", " ").title()
        reports_dir = Path(output_dir)
        _write_reports(result, reports_dir, title=title)

        if output_format in {"text", "both"}:
            _print_text_summary(result, title=title, no_color=no_color)
            typer.echo(f"\nReports written to {reports_dir.resolve()}/")
        if output_format in {"json", "both"}:
            typer.echo(json.dumps(render_scorecard_json(result), indent=2))

        _maybe_notify_slack(notify, slack_webhook, result, title=title)

        raise typer.Exit(code=_exit_code_for_verdict(result.verdict))
    except typer.Exit:
        raise
    except FileNotFoundError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    except (ValidationError, TrustlineError, AuditError) as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    except ExecutorError as exc:
        logger.exception("audit executor failure")
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=3) from exc
    except Exception as exc:
        logger.exception("unexpected audit failure")
        typer.echo(f"ERROR: internal error: {exc}", err=True)
        raise typer.Exit(code=3) from exc
