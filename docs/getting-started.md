# Getting Started

Install Trustline, run the test suite, and explore the CLI skeleton.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip + venv

## Install

```bash
git clone https://github.com/omarfarooq908/trustline.git
cd trustline
make install-dev
make check
```

## CLI

```bash
trustline --help
trustline --version
```

### `trustline validate`

```bash
trustline validate --contracts ./examples/acme_stream/contracts/
```

Validates all contract YAML files in the directory against JSON Schema.

### Planned commands (v0.1)

```bash
# Validate contract YAML against JSON Schema
trustline validate --contracts ./examples/acme_stream/contracts/

# Run five-phase trust scorecard (DuckDB local demo — not yet implemented)
trustline audit --contracts ./examples/acme_stream/contracts/ --target duckdb

# Run against Snowflake
trustline audit --contracts ./contracts/ --target snowflake --profile acme_prod
```

The `audit` subcommand is not yet implemented. `validate` is available in v0.0.1+ development builds.

## Example contract

See [examples/acme_stream/contracts/training_positives.yaml](../examples/acme_stream/contracts/training_positives.yaml) — a funnel contract for the ACME Stream demo.

Copy [examples/acme_stream/profiles.yml.example](../examples/acme_stream/profiles.yml.example) to `profiles.yml` for warehouse connection settings during `trustline audit` (Phase 6+).

Full specification: [contract-spec.md](contract-spec.md).

## Development

```bash
make test          # fast unit tests
make format        # auto-format
make check         # all CI gates
```

See [contributing.md](contributing.md) for the full workflow.

## Next steps

- Read [index.md](index.md) for product overview
- Review [mvp-scope.md](mvp-scope.md) for v0.1 deliverables
- Browse [adr/](adr/) for technical decisions
