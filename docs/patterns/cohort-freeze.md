# Cohort freeze

## Symptoms

- Someone widens the observation window "just for this retrain."
- Positive rate in production diverges from what was validated at model review.
- `frozen_at` in the cohort manifest is ignored in practice.
- Backfills rewrite historical labels without ML team sign-off.

## Why table DQ misses it

Table-level checks do not bind **cohort semantics** to a point in time. A `CohortManifest` in git records windows, label SQL, and expected positive rate — but nothing enforces that scoring still matches unless you audit it.

## Pattern

**Cohort freeze** — after `frozen_at`, observation/outcome windows and label definition are immutable; the observed positive rate must stay within tolerance of the frozen expectation.

In v0.1, enforcement is via `cohort.positive_rate` and `cohort.source_parity` checks plus git review of `frozen_at`. There is no dedicated window/backfill SQL check yet.

## Contract

From [examples/acme_stream/contracts/propensity_training_cohort_q2.yaml](../../examples/acme_stream/contracts/propensity_training_cohort_q2.yaml):

```yaml
spec:
  observation_window:
    start: "2025-01-01"
    end: "2025-03-31"
  outcome_window:
    start: "2025-04-01"
    end: "2025-04-30"
  expected_positive_rate: 0.12
  positive_rate_tolerance: 0.02
  frozen_at: "2025-05-01T00:00:00Z"
```

Treat `frozen_at` as the governance timestamp: changes after this date require a new cohort manifest and model review.

## Check

| Field | Value |
|-------|-------|
| Phase | 4 — Training autopsy |
| Check ID | `cohort.positive_rate.propensity-training-cohort-q2` |
| ACME expected | Exercised with source parity failure in demo |

Related: `cohort.source_parity.propensity-training-cohort-q2`.

## Run it

```bash
trustline validate --contracts ./examples/acme_stream/contracts/
trustline audit \
  --contracts ./examples/acme_stream/contracts/ \
  --target duckdb \
  --profiles ./examples/acme_stream/profiles.yml.example
```

## Related

- [Training/serving divergence](training-serving-divergence.md) — source parity at the same seam
- [Identity funnel collapse](identity-funnel-collapse.md) — who is in the cohort
