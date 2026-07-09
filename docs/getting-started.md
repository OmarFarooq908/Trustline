# Getting Started

Install Trustline, validate contracts, and run the ACME Stream trust audit locally.

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

### `trustline audit`

Copy the example profiles file, then run the DuckDB demo audit:

```bash
cp examples/acme_stream/profiles.yml.example profiles.yml
trustline audit --contracts ./examples/acme_stream/contracts/ --target duckdb
```

The ACME demo uses the committed `examples/acme_stream/demo.duckdb` database and exits with code `1` when seeded failures are detected (expected for the demo).

Write reports to a directory:

```bash
trustline audit \
  --contracts ./examples/acme_stream/contracts/ \
  --target duckdb \
  --output-dir ./reports \
  -o json
cat ./reports/scorecard.md
```

Compile checks without executing SQL:

```bash
trustline audit --contracts ./examples/acme_stream/contracts/ --target duckdb --dry-run
```

Snowflake execution is planned for a later release:

```bash
trustline audit --contracts ./contracts/ --target snowflake --profile acme_prod
```

## Example contract

See [examples/acme_stream/contracts/training_positives.yaml](../examples/acme_stream/contracts/training_positives.yaml) — a funnel contract for the ACME Stream demo.

Full specification: [contract-spec.md](contract-spec.md).

## Development

```bash
make test          # fast unit tests
make format        # auto-format
make check         # all CI gates
./scripts/build-demo-duckdb.sh   # rebuild demo.duckdb from seed SQL
```

See [contributing.md](contributing.md) for the full workflow.

## Next steps

- Read [index.md](index.md) for product overview
- Review [mvp-scope.md](mvp-scope.md) for v0.1 deliverables
- Browse [adr/](adr/) for technical decisions
