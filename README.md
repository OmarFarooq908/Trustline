# Trustline

[![CI](https://github.com/omarfarooq908/trustline/actions/workflows/ci.yml/badge.svg)](https://github.com/omarfarooq908/trustline/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/trustline.svg)](https://pypi.org/project/trustline/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

**Business systems fail at the boundaries. Trustline verifies the boundaries.**

Trustline compiles YAML contracts into SQL checks and produces a measurable integrity scorecard. See [Why Trustline](docs/why-trustline.md) for the seam problem and compiler model.

## Quickstart

```bash
pip install trustline
ACME=$(python -c "from trustline.examples import acme_stream_dir; print(acme_stream_dir())")
trustline validate --contracts "$ACME/contracts"
trustline audit \
  --contracts "$ACME/contracts" \
  --target duckdb \
  --profiles "$ACME/profiles.yml.example"
```

The example audit exits `1` — the fixture intentionally includes failing checks.

Contributors: clone the repo and run `make install-dev`. See [Getting Started](docs/getting-started.md).

## What Trustline is not

- **Not an orchestrator** — integrates with Airflow and Dagster; does not replace them
- **Not a transform framework** — extends dbt; does not replace it
- **Not a model training runtime** — no training, inference, or feature store
- **Not a hosted SaaS** — CLI you run in CI or on a schedule
- **Not auto-remediation** — detects and reports; never auto-fixes

## Documentation

| Document | Description |
|----------|-------------|
| [Why Trustline](docs/why-trustline.md) | Problem statement and compiler model |
| [Patterns](docs/patterns/README.md) | Boundary failure catalog |
| [Stability](docs/STABILITY.md) | Contract and CLI semver policy |
| [Getting Started](docs/getting-started.md) | Install and CLI |
| [Overview](docs/index.md) | Commands, phases, architecture |
| [Contract Spec](docs/contract-spec.md) | YAML schema |
| [Contributing](docs/contributing.md) | Development |

## Development

```bash
make check    # format, lint, types, tests, coverage
make test
```

## License

[Apache 2.0](LICENSE)
