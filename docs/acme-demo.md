# ACME Stream demo

The bundled ACME Stream fixture shows cross-boundary failures: upstream pipelines can look healthy while Trustline reports FAIL at the seams.

## Scenario

ACME Stream ships a propensity model. dbt models build. The training job completes. Airflow DAGs succeed. Warehouse row counts are non-zero.

Then Trustline runs:

| Phase | What looks fine | What Trustline catches |
|-------|-----------------|------------------------|
| 1 — Pipeline truth | CRM push queue has rows | Only ~27% of queued scores appear in the contacts mirror |
| 2 — Population funnel | Each stage table has data | Retention collapses from donors → app match → features |
| 3 — Score semantics | Events table still has volume | Post-cutover source swap drift (WARN) |
| 4 — Training autopsy | Cohort manifest frozen in git | Training and scoring read different feature tables |

**Business Integrity Score: 42/100 — FAIL**

That score is intentional. The fixture includes seeded failures that table-level DQ and per-job success runs do not surface.

## Run it

```bash
pip install trustline
trustline audit --demo
```

Exit code `1` is expected. See [patterns/README.md](patterns/README.md) for each failure mode.

## Scaffold your own contracts

```bash
trustline init --preset ml-crm-boundary --non-interactive
```

Edit `{{ ref('...') }}` table names, point `duckdb_path` or Snowflake profiles at your warehouse, and run `trustline audit`.

Fixture reference: [mvp-scope.md](mvp-scope.md#acme-stream-demo-scenario).
