"""trustline audit — five-phase trust scorecard (stub)."""

import typer

app = typer.Typer(help="Run five-phase trust scorecard audit.")


@app.callback(invoke_without_command=True)
def audit(
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
) -> None:
    """Run trust audit (not yet implemented)."""
    typer.echo(f"audit: not yet implemented (contracts={contracts}, target={target})")
    raise typer.Exit(code=1)
