# Source swap

## Symptoms

- Event volumes spike or drop after an upstream migration date.
- A new player or SDK version replaced a legacy source identifier.
- Model scores shift; feature engineering still runs green.
- Analysts notice `LegacyPlayer` rows stopped and `NewPlayer` rows started.

## Why table DQ misses it

Volume checks on a single table without migration context cannot distinguish a planned cutover from drift. dbt source freshness does not compare pre- and post-cutover distributions against a declared migration timeline.

## Pattern

**Source swap** — after a declared cutover date, post-migration source volume must stay within a drift threshold relative to pre-cutover baseline.

## Contract

From [examples/acme_stream/audit_profile.yaml](../../examples/acme_stream/audit_profile.yaml):

```yaml
source_swap:
  table: "{{ ref('user_events_silver') }}"
  migration:
    from_source: LegacyPlayer
    to_source: NewPlayer
    cutover_date: "2025-03-15"
  volume_threshold_pct: 10
```

## Check

| Field | Value |
|-------|-------|
| Phase | 3 — Score semantics |
| Check ID | `audit.source_swap_volume` |
| ACME expected | WARN — post-cutover volume drift above threshold |

## Run it

```bash
trustline validate --contracts ./examples/acme_stream/contracts/
trustline audit \
  --contracts ./examples/acme_stream/contracts/ \
  --target duckdb \
  --profiles ./examples/acme_stream/profiles.yml.example
```

## Related

- [Identity funnel collapse](identity-funnel-collapse.md) — downstream population effects
- [Training/serving divergence](training-serving-divergence.md) — feature table changes after migration
