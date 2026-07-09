# ADR-010: CLI package structure

**Status:** Accepted

**Decision:** Use `cli/` package with Typer app in `main.py` and subcommand modules (`validate.py`, `audit.py`).

**Rationale:** Scales to MVP commands without a monolithic file.
