# Trustline

[![CI](https://github.com/omarfarooq908/trustline/actions/workflows/ci.yml/badge.svg)](https://github.com/omarfarooq908/trustline/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

**Business systems fail at the boundaries. Trustline verifies the boundaries.**

Everything was green. Airflow passed. dbt passed. Great Expectations passed. The model passed evaluation. Customers still received the wrong data.

Existing tools validate *within* systems — row counts, null checks, model metrics. Failures happen *between* systems: identity joins that silently drop records, training tables that diverge from scoring tables, scores that never reach the CRM mirror, upstream source migrations that change semantics overnight.

Trustline is a **compiler for business invariants**. You declare what must remain true across those boundaries in YAML contracts; Trustline compiles them to SQL, runs them against your warehouse, and produces a measurable integrity scorecard.

## Quickstart

```bash
pip install trustline
trustline validate --contracts ./examples/acme_stream/contracts/
trustline audit \
  --contracts ./examples/acme_stream/contracts/ \
  --target duckdb \
  --profiles ./examples/acme_stream/profiles.yml.example
```

Clone the repository to run the bundled ACME Stream fixture locally:

```bash
git clone https://github.com/omarfarooq908/trustline.git
cd trustline
make install-dev
trustline audit \
  --contracts ./examples/acme_stream/contracts/ \
  --target duckdb \
  --profiles ./examples/acme_stream/profiles.yml.example
```

The example audit exits `1` — the fixture intentionally includes failing checks.

## What Trustline is not

- **Not an orchestrator** — integrates with Airflow and Dagster; does not replace them
- **Not a transform framework** — extends dbt; does not replace it
- **Not a model training runtime** — no training, inference, or feature store
- **Not a hosted SaaS** — CLI you run in CI or on a schedule
- **Not auto-remediation** — detects and reports; never auto-fixes

## Documentation

| Document | Description |
|----------|-------------|
| [Why Trustline](docs/why-trustline.md) | Problem, positioning, and moat |
| [Getting Started](docs/getting-started.md) | Install and CLI |
| [Overview](docs/index.md) | Commands, phases, architecture |
| [Contract Spec](docs/contract-spec.md) | YAML schema |
| [Architecture](docs/architecture.md) | Design |
| [Contributing](docs/contributing.md) | Development |

## Development

```bash
make check    # format, lint, types, tests, coverage
make test
```

## License

[Apache 2.0](LICENSE)
