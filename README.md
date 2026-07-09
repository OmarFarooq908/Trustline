# Trustline

[![CI](https://github.com/omarfarooq908/trustline/actions/workflows/ci.yml/badge.svg)](https://github.com/omarfarooq908/trustline/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

Open-source trust layer for data products — machine-checkable contracts across ETL, ML, and delivery seams.

## Quickstart

```bash
git clone https://github.com/omarfarooq908/trustline.git
cd trustline
make install-dev
trustline validate --contracts ./examples/acme_stream/contracts/
cp examples/acme_stream/profiles.yml.example profiles.yml
trustline audit --contracts ./examples/acme_stream/contracts/ --target duckdb
```

The demo audit exits with code `1` because the ACME Stream dataset intentionally seeds trust failures across pipeline, funnel, semantics, and training checks.

## What is Trustline?

Trustline sits on top of dbt, Airflow, Snowflake ML, and CRM sync tools. It makes cross-boundary failures — identity funnel collapse, cohort drift, source swaps, queue-vs-state sync gaps — **machine-checkable, versioned, and transferable**.

The v0.1 MVP delivers a CLI Trust Scorecard (`trustline audit`) that runs a five-phase audit against declarative contracts. See [getting started](docs/getting-started.md) for the full walkthrough.

## Documentation

| Document | Description |
|----------|-------------|
| [Overview](docs/index.md) | What Trustline is and why |
| [Getting Started](docs/getting-started.md) | Install and first commands |
| [Contract Spec](docs/contract-spec.md) | Contract YAML API |
| [Architecture](docs/architecture.md) | Technical design |
| [Roadmap](docs/roadmap.md) | Feature roadmap |
| [Contributing](docs/contributing.md) | Contributor guide |
| [MVP Scope](docs/mvp-scope.md) | v0.1 deliverables |

## Development

```bash
make install-dev   # install dependencies
make check         # lint, typecheck, test, coverage
make test          # fast tests only
make format        # auto-format
```

See [contributing.md](docs/contributing.md) for full workflow.

## License

[Apache 2.0](LICENSE)

## Code of Conduct

[Contributor Covenant](CODE_OF_CONDUCT.md)
