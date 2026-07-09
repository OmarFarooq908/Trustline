# Getting Started

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

Validates contract YAML files against JSON Schema.

```bash
trustline validate --contracts ./examples/acme_stream/contracts/
```

### `trustline audit`

Runs the five-phase scorecard. For the bundled example, pass the example profiles file:

```bash
trustline audit \
  --contracts ./examples/acme_stream/contracts/ \
  --target duckdb \
  --profiles ./examples/acme_stream/profiles.yml.example
```

The example audit exits with code `1` when seeded failures are present (expected). Reports are written to the current directory (`scorecard.md`, `scorecard.json`, `brief.md`) unless `--output-dir` is set.

```bash
trustline audit \
  --contracts ./examples/acme_stream/contracts/ \
  --target duckdb \
  --profiles ./examples/acme_stream/profiles.yml.example \
  --output-dir ./reports \
  -o json
```

Compile checks without executing SQL:

```bash
trustline audit \
  --contracts ./examples/acme_stream/contracts/ \
  --target duckdb \
  --profiles ./examples/acme_stream/profiles.yml.example \
  --dry-run
```

### Snowflake

Requires `trustline[snowflake]` and `SNOWFLAKE_*` environment variables:

```bash
pip install 'trustline[snowflake]'
export SNOWFLAKE_ACCOUNT=...
export SNOWFLAKE_USER=...
export SNOWFLAKE_PASSWORD=...
export SNOWFLAKE_WAREHOUSE=...
trustline audit --contracts ./contracts/ --target snowflake --profile acme_prod
```

Integration tests are skipped by default; set `TRUSTLINE_RUN_INTEGRATION=1` to enable them.

### Slack

On audit failure (`verdict: fail`):

```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
trustline audit --contracts ./contracts/ --target duckdb --notify slack
```

### GitHub Actions

Copy [integrations/github-actions/trustline-audit.yml](../integrations/github-actions/trustline-audit.yml) into `.github/workflows/`.

## Example fixture (`examples/acme_stream/`)

Synthetic DuckDB database used in tests and CI. Layout:

```
examples/acme_stream/
├── contracts/           # FunnelContract, CohortManifest
├── audit_profile.yaml   # CRM coverage, source swap checks
├── profiles.yml.example
├── demo.duckdb
└── sql/seed_data.sql
```

Rebuild after editing seed SQL:

```bash
./scripts/build-demo-duckdb.sh
```

### Seeded failures (reference)

| Phase | Check | Expected result |
|-------|-------|-----------------|
| 1 | `audit.crm_coverage` | FAIL — 27% sync vs 95% threshold |
| 2 | `funnel.retention...behavioral_features` | FAIL — 9% vs 25% |
| 3 | `audit.source_swap_volume` | WARN |
| 4 | `cohort.source_parity` | FAIL |

Full fixture spec: [mvp-scope.md](mvp-scope.md#acme-stream-demo-scenario).

### Profiles troubleshooting

If you see `DuckDB database not found`, pass `--profiles ./examples/acme_stream/profiles.yml.example` or set `duckdb_path: examples/acme_stream/demo.duckdb` in `profiles.yml`.

## Example contract

[examples/acme_stream/contracts/training_positives.yaml](../examples/acme_stream/contracts/training_positives.yaml) — API reference in [contract-spec.md](contract-spec.md).

## Development

```bash
make test
make format
make check
```

See [contributing.md](contributing.md).
