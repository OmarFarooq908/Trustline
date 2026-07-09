# Trustline

[![CI](https://github.com/omarfarooq908/trustline/actions/workflows/ci.yml/badge.svg)](https://github.com/omarfarooq908/trustline/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

CLI for validating YAML data-product contracts and running a five-phase trust audit (DuckDB or Snowflake).

## Quickstart

```bash
git clone https://github.com/omarfarooq908/trustline.git
cd trustline
make install-dev
trustline validate --contracts ./examples/acme_stream/contracts/
trustline audit \
  --contracts ./examples/acme_stream/contracts/ \
  --target duckdb \
  --profiles ./examples/acme_stream/profiles.yml.example
```

The example audit exits `1` — the fixture intentionally includes failing checks.

## Documentation

| Document | Description |
|----------|-------------|
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
