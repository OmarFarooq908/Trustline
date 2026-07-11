# Common use cases

Trustline verifies **boundaries** in data and ML pipelines. Each use case below maps to a bundled init preset or a CI-only workflow.

## ML → CRM boundary audit

**Problem:** Model scores land in a sync queue but not in the CRM mirror downstream.

**Preset:** `ml-crm-boundary` — funnel retention, cohort source parity, and CRM coverage checks.

```bash
trustline init --preset ml-crm-boundary --non-interactive
trustline validate --contracts ./trustline/contracts
```

1. Edit `{{ ref('table_name') }}` placeholders in `./trustline/contracts/` and `audit_profile.yaml`.
2. Set `duckdb_path` or Snowflake credentials in `./trustline/profiles.yml`.
3. Run the audit:

```bash
trustline audit --contracts ./trustline/contracts --profiles ./trustline/profiles.yml
```

Pattern reference: [queue vs state](patterns/queue-vs-state.md).

## Training/serving source parity

**Problem:** Training reads from one feature table; scoring reads from another without an explicit contract.

**Preset:** `cohort-source-parity`

```bash
trustline init --preset cohort-source-parity --non-interactive \
  --product my_model --owner ml@example.com
trustline validate --contracts ./trustline/contracts
```

Customize observation windows and `sources.training` / `sources.scoring` in the generated `CohortManifest`. Pattern: [training/serving divergence](patterns/training-serving-divergence.md).

## Identity funnel retention

**Problem:** Population shrinks silently across identity join stages before model training.

**Preset:** `funnel-retention`

```bash
trustline init --preset funnel-retention --non-interactive
trustline validate --contracts ./trustline/contracts
```

Adjust `expect_retention_pct` per stage to match model review sign-off. Pattern: [identity funnel collapse](patterns/identity-funnel-collapse.md).

## CI validate-only (no warehouse)

**Problem:** You want to block merges when contract YAML is invalid, without connecting to a warehouse.

```bash
trustline validate --contracts ./trustline/contracts
```

For dbt projects, see [examples/dbt-ci/](../examples/dbt-ci/). For GitHub Actions, see [examples/github-actions/trustline-audit/](../examples/github-actions/trustline-audit/).

## Try before you scaffold

Run the bundled ACME fixture with no configuration:

```bash
trustline audit --demo
```

Exit code `1` is expected — seeded failures demonstrate what each check detects. See [acme-demo.md](acme-demo.md).

## Choose a preset

```bash
trustline init --list-presets
```

Full preset catalog: [examples/templates/README.md](../examples/templates/README.md).
