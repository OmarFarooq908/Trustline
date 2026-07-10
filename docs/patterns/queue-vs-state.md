# Queue vs state

## Symptoms

- ML scores appear in a staging or push queue table.
- The CRM mirror (or customer-facing state table) has far fewer rows.
- Support tickets report missing scores; the scoring job shows success.
- Dashboards on the queue look healthy; dashboards on the mirror do not.

## Why table DQ misses it

dbt `unique` and `not_null` tests validate a single table. Soda and Great Expectations row checks do the same. None of them assert that **rows written to the queue eventually appear in the mirror** — that is a cross-table invariant at the delivery seam.

## Pattern

**Queue vs state** — the sync queue (intent to deliver) must match the mirror (observed customer state) within a coverage threshold.

## Contract

From [examples/acme_stream/audit_profile.yaml](../../examples/acme_stream/audit_profile.yaml):

```yaml
crm_coverage:
  sync_table: "{{ ref('crm_push_queue') }}"
  mirror_table: "{{ ref('crm_contacts_mirror') }}"
  expect_sync_pct: 95
```

Plain English: at least 95% of rows in the push queue must appear in the contacts mirror.

## Check

| Field | Value |
|-------|-------|
| Phase | 1 — Pipeline truth |
| Check ID | `audit.crm_coverage` |
| ACME expected | FAIL — ~27% sync vs 95% threshold |

## Run it

From a repository clone:

```bash
trustline validate --contracts ./examples/acme_stream/contracts/
trustline audit \
  --contracts ./examples/acme_stream/contracts/ \
  --target duckdb \
  --profiles ./examples/acme_stream/profiles.yml.example
```

After installing from PyPI (v0.1.1+):

```bash
pip install trustline
ACME=$(python -c "from trustline.examples import acme_stream_dir; print(acme_stream_dir())")
trustline audit \
  --contracts "$ACME/contracts" \
  --target duckdb \
  --profiles "$ACME/profiles.yml.example"
```

The ACME fixture exits `1` — the CRM gap is intentional.

## Related

- [Identity funnel collapse](identity-funnel-collapse.md) — population loss earlier in the pipeline
- [Training/serving divergence](training-serving-divergence.md) — feature table mismatch before scoring
