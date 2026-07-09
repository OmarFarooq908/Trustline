"""trustline validate — contract YAML validation."""

from __future__ import annotations

import logging
from pathlib import Path

import typer

from trustline.contracts.validator import (
    ValidationSummary,
    validate_contract_file,
    validate_contracts_dir,
)
from trustline.exceptions import TrustlineError, ValidationError

logger = logging.getLogger(__name__)

app = typer.Typer(help="Validate contract YAML against JSON Schema.")


def _print_summary(summary: ValidationSummary) -> None:
    """Print per-file validation results."""
    typer.echo(f"Validating {summary.total} contracts...\n")
    for result in summary.results:
        status = "PASS" if result.passed else "FAIL"
        kind = result.kind or "Unknown"
        typer.echo(f"  {result.path.name:<40} {kind:<20} {status}")
        if not result.passed:
            for error in result.errors:
                typer.echo(error, err=True)


def _summary_from_file(path: Path) -> ValidationSummary:
    """Build a validation summary for a single file."""
    result = validate_contract_file(path)
    passed = 1 if result.passed else 0
    return ValidationSummary(
        total=1,
        passed=passed,
        failed=1 - passed,
        results=(result,),
    )


def _exit_code_for_summary(summary: ValidationSummary) -> int:
    """Map validation summary to CLI exit code."""
    if summary.failed:
        return 1
    return 0


@app.callback(invoke_without_command=True)
def validate(
    contracts: str = typer.Option(
        "./contracts",
        "--contracts",
        "-c",
        help="Directory containing contract YAML files.",
    ),
    file: str | None = typer.Option(
        None,
        "--file",
        "-f",
        help="Validate a single contract file instead of a directory.",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Treat warnings as errors (reserved for future use).",
    ),
) -> None:
    """Validate contract YAML files against JSON Schema."""
    del strict  # reserved for v0.1; schema errors already fail validation

    try:
        if file is not None:
            path = Path(file)
            if not path.is_file():
                typer.echo(f"ERROR: contract file not found: {path}", err=True)
                raise typer.Exit(code=2)
            summary = _summary_from_file(path)
        else:
            directory = Path(contracts)
            if not directory.is_dir():
                typer.echo(f"ERROR: contracts directory not found: {directory}", err=True)
                raise typer.Exit(code=2)
            summary = validate_contracts_dir(directory)

        _print_summary(summary)
        if summary.total == 0:
            typer.echo("\nNo contract files found.")
            raise typer.Exit(code=2)

        if summary.failed:
            typer.echo("\nValidation failed.")
            raise typer.Exit(code=_exit_code_for_summary(summary))

        typer.echo("\nAll contracts valid.")
    except typer.Exit:
        raise
    except FileNotFoundError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    except ValidationError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except TrustlineError as exc:
        logger.exception("validate command failed")
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=3) from exc
    except Exception as exc:
        logger.exception("unexpected validate failure")
        typer.echo(f"ERROR: internal error: {exc}", err=True)
        raise typer.Exit(code=3) from exc
