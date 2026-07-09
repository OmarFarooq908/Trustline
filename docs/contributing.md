# Contributing to Trustline

Thank you for your interest in contributing. This guide gets you from clone to a passing PR in under 15 minutes.

**Detailed engineering standards:** [engineering-foundation.md](engineering-foundation.md)

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip + venv
- git

Optional: Snowflake credentials for integration tests (`TRUSTLINE_RUN_INTEGRATION=1`).

Snowflake integration tests require:

```bash
export TRUSTLINE_RUN_INTEGRATION=1
export SNOWFLAKE_ACCOUNT=...
export SNOWFLAKE_USER=...
export SNOWFLAKE_PASSWORD=...
export SNOWFLAKE_WAREHOUSE=...
make test-integration
```

Slack notification tests use mocked HTTP and do not require a real webhook.

## Quickstart

```bash
git clone https://github.com/omarfarooq908/trustline.git
cd trustline
make install-dev
make check
```

### pip fallback

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make check
```

## Development workflow

1. **Find or open an issue** for non-trivial changes.
2. **Branch** from `main`: `feat/`, `fix/`, `docs/`, or `chore/` prefix.
3. **Install hooks:** `uv run pre-commit install`
4. **Make changes** with tests.
5. **Verify:** `make check`
6. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat: add contract validation for FunnelContract
   ```
7. **Sign off (DCO):** include in commit message:
   ```
   Signed-off-by: Your Name <your.email@example.com>
   ```
8. **Open a PR** using the template.

## Make targets

| Target | Purpose |
|--------|---------|
| `make install-dev` | Install dependencies |
| `make check` | All CI gates (format, lint, types, coverage) |
| `make test` | Fast tests only |
| `make format` | Auto-format code |

## Code style

- **Formatter/linter:** Ruff (line length 100)
- **Types:** mypy strict on `src/trustline/`
- **Docstrings:** Google style for public APIs
- **Logging:** stdlib `logging` — no `print()` in library code

## Testing

```bash
make test              # unit tests (default in CI)
make coverage          # with 85% coverage gate
make test-integration  # requires TRUSTLINE_RUN_INTEGRATION=1
```

Use `examples/acme_stream/` for tests and examples.

## Pull requests

- Run `make check` before opening
- Prefer PRs under 400 lines
- Link related issues
- Fill out the PR template completely
- Squash merge to `main` after green CI

### Solo maintainer policy

Until a second maintainer joins, the maintainer may self-merge after green `CI` and `Security` checks.

## Contract schema changes

Breaking changes to contract YAML schema require:

1. GitHub Issue with `RFC` label
2. 7-day comment period
3. Update `schemas/` and [contract-spec.md](contract-spec.md)
4. Entry in [adr/](adr/) for significant technical decisions

## Questions

- **Bugs and features:** GitHub Issues
- **General questions:** GitHub Discussions
- **Security:** see [SECURITY.md](../SECURITY.md) — do not open public issues

## Code of conduct

This project follows the [Contributor Covenant](../CODE_OF_CONDUCT.md). Please be respectful and constructive.
