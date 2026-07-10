# Training/serving divergence

## Symptoms

- Model accuracy drops in production without an obvious code deploy.
- Feature distributions look similar table-by-table but row sets differ.
- Training notebook used `features_training`; scoring DAG reads `features_scoring`.
- Data engineering refactored one table; ML team was not notified.

## Why table DQ misses it

Schema tests on `features_training` and `features_scoring` independently pass. dbt tests do not assert that **the same logical population** backs both tables. Training-serving skew is a boundary between the training artifact and the scoring pipeline.

## Pattern

**Training/serving divergence** — the training and scoring feature sources referenced in the cohort manifest must refer to tables with matching row sets (source parity).

## Contract

From [examples/acme_stream/contracts/propensity_training_cohort_q2.yaml](../../examples/acme_stream/contracts/propensity_training_cohort_q2.yaml):

```yaml
apiVersion: trustline.io/v1
kind: CohortManifest
metadata:
  name: propensity-training-cohort-q2
  product: acme_propensity_v2
  owner: ml-team@acme-stream.example
spec:
  sources:
    training: "{{ ref('features_training') }}"
    scoring: "{{ ref('features_scoring') }}"
  expected_positive_rate: 0.12
  positive_rate_tolerance: 0.02
  frozen_at: "2025-05-01T00:00:00Z"
```

## Check

| Field | Value |
|-------|-------|
| Phase | 4 — Training autopsy |
| Check ID | `cohort.source_parity.propensity-training-cohort-q2` |
| ACME expected | FAIL — training and scoring sources diverge |

Companion check: `cohort.positive_rate.propensity-training-cohort-q2`.

## Run it

```bash
trustline validate --contracts ./examples/acme_stream/contracts/
trustline audit \
  --contracts ./examples/acme_stream/contracts/ \
  --target duckdb \
  --profiles ./examples/acme_stream/profiles.yml.example
```

## Related

- [Cohort freeze](cohort-freeze.md) — frozen windows and positive rate after parity
- [Identity funnel collapse](identity-funnel-collapse.md) — population loss before features
