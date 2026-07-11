"""trustline init — scaffold contracts and profiles from presets."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from trustline.exceptions import TrustlineError
from trustline.init.scaffold import build_init_variables, run_init
from trustline.templates.presets import PRESETS, list_presets

app = typer.Typer(help="Scaffold Trustline contracts and profiles from a preset.")


def _interactive_variables() -> dict[str, str]:
    product = typer.prompt("Product name", default="my_product")
    owner = typer.prompt("Owner email", default="team@example.com")
    return build_init_variables(product=product, owner=owner)


def _print_presets() -> None:
    for name in list_presets():
        preset = PRESETS[name]
        typer.echo(f"{name}\n  {preset.description}")


@app.callback(invoke_without_command=True)
def init(  # noqa: PLR0913
    preset: str | None = typer.Option(
        None,
        "--preset",
        help=f"Template preset. Choices: {', '.join(list_presets())}.",
    ),
    list_presets_flag: bool = typer.Option(
        False,
        "--list-presets",
        help="List bundled template presets and exit.",
    ),
    output_dir: str = typer.Option(
        "./trustline",
        "--output-dir",
        help="Directory for generated contracts and profiles.yml.",
    ),
    product: str | None = typer.Option(
        None,
        "--product",
        help="Product name for contract metadata (non-interactive).",
    ),
    owner: str | None = typer.Option(
        None,
        "--owner",
        help="Owner email for contract metadata (non-interactive).",
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        help="Skip prompts; use --product and --owner or defaults.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite generated files in an existing output directory.",
    ),
) -> None:
    """Generate contract YAML and profiles from a bundled preset."""
    if list_presets_flag:
        _print_presets()
        return

    if preset is None:
        typer.echo("ERROR: --preset is required (or use --list-presets).", err=True)
        _print_presets()
        raise typer.Exit(code=2)

    try:
        destination = Path(output_dir)
        interactive = sys.stdin.isatty() and not non_interactive

        if interactive:
            variables = _interactive_variables()
        else:
            variables = build_init_variables(
                product=product or "my_product",
                owner=owner or "team@example.com",
            )

        result = run_init(preset, destination, variables=variables, force=force)

        typer.echo(f"Initialized Trustline workspace at {result.output_dir.resolve()}/")
        typer.echo("\nNext:")
        typer.echo(f"  trustline validate --contracts {result.contracts_dir}")
        typer.echo(
            f"  trustline audit --contracts {result.contracts_dir} "
            f"--profiles {result.profiles_path}"
        )
        typer.echo("  Edit table names: replace {{ ref('...') }} in YAML with your tables")
    except TrustlineError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=2) from exc
