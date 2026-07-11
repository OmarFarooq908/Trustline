# Getting Started

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip + venv

## Quick start

Path from install to a scaffolded workspace (no warehouse required for steps 1–3):

```bash
pip install trustline
trustline audit --demo
trustline init --preset ml-crm-boundary --non-interactive
trustline validate --contracts ./trustline/contracts
```

Step 1 runs the bundled ACME fixture. Exit code `1` is expected — see [acme-demo.md](acme-demo.md).

Step 3 writes `./trustline/contracts/`, `audit_profile.yaml`, and `profiles.yml`. Edit `{{ ref('table_name') }}` placeholders, set `duckdb_path` in `profiles.yml`, then:

```bash
trustline audit --contracts ./trustline/contracts --profiles ./trustline/profiles.yml
```

Snowflake and CI paths are below; start with DuckDB or `--demo` until contracts match your tables.

## Install

```bash
pip install trustline
trustline --version
```

### Pip-only demo (no clone)

```bash
trustline audit --demo
```

The audit exits `1` when seeded failures are present (expected for the bundled fixture).

For development from source:

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

### `trustline init`

Scaffold contracts and profiles from a bundled preset:

```bash
trustline init --preset ml-crm-boundary --non-interactive
trustline init --preset funnel-retention --product my_model --owner team@example.com
```

Presets: `ml-crm-boundary`, `funnel-retention`, `cohort-source-parity`. List all presets:

```bash
trustline init --list-presets
```

Output defaults to `./trustline/`. See [ADR-022](adr/022-trustline-init.md).

### `trustline validate`

Validates contract YAML files against JSON Schema.

```bash
trustline validate --contracts ./examples/acme_stream/contracts/
```

### `trustline audit`

Runs the five-phase scorecard.

**Bundled demo (recommended first run):**

```bash
trustline audit --demo
```

**Local or scaffolded contracts:**

```bash
trustline audit \
  --contracts ./trustline/contracts/ \
  --target duckdb \
  --profiles ./trustline/profiles.yml
```

**Repository clone (ACME fixture path):**

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

Requires `trustline[snowflake]` and environment variables. After `trustline init`, uncomment the Snowflake profile stub in `./trustline/profiles.yml`:

```bash
pip install 'trustline[snowflake]'
export SNOWFLAKE_ACCOUNT=...
export SNOWFLAKE_USER=...
export SNOWFLAKE_PASSWORD=...
export SNOWFLAKE_WAREHOUSE=...
trustline audit \
  --contracts ./trustline/contracts/ \
  --target snowflake \
  --profile acme_prod \
  --profiles ./trustline/profiles.yml
```

Integration tests are skipped by default; set `TRUSTLINE_RUN_INTEGRATION=1` to enable them.

### Slack

On audit failure (`verdict: fail`):

```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
trustline audit --contracts ./contracts/ --target duckdb --notify slack
```

### GitHub Actions

Consumer example (pip install, own `./trustline/` contracts): [examples/github-actions/trustline-audit/](../examples/github-actions/trustline-audit/).

Monorepo CI reference: [integrations/github-actions/trustline-audit.yml](../integrations/github-actions/trustline-audit.yml).

### dbt

Validate contracts in CI without a dbt macro: [examples/dbt-ci/](../examples/dbt-ci/README.md).

```bash
trustline init --preset ml-crm-boundary --non-interactive
# Copy examples/dbt-ci/validate-contracts.yml → .github/workflows/
```

A `trustline_funnel` dbt macro is planned for v0.3.

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

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `trustline audit --demo` exits `1` | Expected — seeded failures in the ACME fixture. See [acme-demo.md](acme-demo.md). |
| `contracts directory not found` | Run `trustline init --preset ml-crm-boundary` or `trustline audit --demo`. |
| `profiles file not found` | Run `trustline init` (writes `profiles.yml`) or use `--demo`. |
| `{{ ref('table_name') }}` in contracts | Replace with your warehouse table names. Automatic dbt `ref()` resolution is planned for v0.3. |
| Unknown init preset | Run `trustline init --list-presets` for available choices. |

Walkthroughs by scenario: [use-cases.md](use-cases.md).

## Example contract

[examples/acme_stream/contracts/training_positives.yaml](../examples/acme_stream/contracts/training_positives.yaml) — API reference in [contract-spec.md](contract-spec.md).

## Development

```bash
make test
make format
make check
```

See [contributing.md](contributing.md).
