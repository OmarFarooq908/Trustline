# Identity funnel collapse

## Symptoms

- Model training completes; offline metrics look acceptable.
- Scoring population is much smaller than the business expects.
- Stakeholders ask "where did the users go?" between identity resolution steps.
- Each intermediate table has rows, but stage-to-stage retention dropped sharply.

## Why table DQ misses it

Per-table row counts do not encode **ordered join retention**. A donors table with 2,000 rows and a features table with 250 rows can both pass `count > 0` tests. The 87% drop across email and behavioral joins is invisible unless you measure retention between stages.

## Pattern

**Identity funnel collapse** — each funnel stage must retain at least the contracted percentage of rows from its parent stage.

## Contract

From [examples/acme_stream/contracts/training_positives.yaml](../../examples/acme_stream/contracts/training_positives.yaml):

```yaml
apiVersion: trustline.io/v1
kind: FunnelContract
metadata:
  name: training_positives
  product: acme_propensity_v2
  owner: platform-team@acme-stream.example
spec:
  stages:
    - name: source_donors
      expect_min_count: 2000
    - name: app_identity_match
      from_stage: source_donors
      expect_retention_pct: 40
    - name: behavioral_features
      from_stage: app_identity_match
      expect_retention_pct: 25
```

## Check

| Field | Value |
|-------|-------|
| Phase | 2 — Population funnel |
| Check ID | `funnel.retention.training_positives.behavioral_features` |
| ACME expected | FAIL — ~9% retention vs 25% threshold |

Related count check: `funnel.count.training_positives.source_donors` (first stage minimum).

## Run it

```bash
trustline validate --contracts ./examples/acme_stream/contracts/
trustline audit \
  --contracts ./examples/acme_stream/contracts/ \
  --target duckdb \
  --profiles ./examples/acme_stream/profiles.yml.example
```

## Related

- [Queue vs state](queue-vs-state.md) — delivery gap after scoring
- [Training/serving divergence](training-serving-divergence.md) — different population at train vs score time
