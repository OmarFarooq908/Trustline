"""trustline validate — contract YAML validation (stub)."""

import typer

app = typer.Typer(help="Validate contract YAML against JSON Schema.")


@app.callback(invoke_without_command=True)
def validate(
    contracts: str = typer.Option(
        "./contracts",
        "--contracts",
        "-c",
        help="Directory containing contract YAML files.",
    ),
) -> None:
    """Validate contracts (not yet implemented)."""
    typer.echo(f"validate: not yet implemented (contracts={contracts})")
    raise typer.Exit(code=1)
