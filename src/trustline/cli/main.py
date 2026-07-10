"""Trustline CLI entrypoint."""

from importlib.metadata import version

import typer

from trustline.cli import audit, validate

app = typer.Typer(
    name="trustline",
    help="Compiler for business invariants across data-product boundaries.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(version("trustline"))
        raise typer.Exit()


@app.callback()
def main(
    version_flag: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Trustline — compiler for business invariants across data-product boundaries."""


app.add_typer(validate.app, name="validate")
app.add_typer(audit.app, name="audit")
