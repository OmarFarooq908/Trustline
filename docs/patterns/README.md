# Boundary patterns

Catalog of cross-boundary failure modes Trustline checks detect. Each pattern maps to a contract kind, a scorecard check, and an init preset.

## Pattern ↔ template ↔ check matrix

| Pattern | Init preset | Template file | Contract kind | Check ID |
|---------|-------------|---------------|---------------|----------|
| [Queue vs state](queue-vs-state.md) | `ml-crm-boundary` | `audit_profile_ml_crm.yaml` | `audit_profile` | `audit.crm_coverage` |
| [Identity funnel collapse](identity-funnel-collapse.md) | `funnel-retention`, `ml-crm-boundary` | `funnel_retention.yaml` | `FunnelContract` | `funnel.retention.{name}.{stage}` |
| [Training/serving divergence](training-serving-divergence.md) | `cohort-source-parity`, `ml-crm-boundary` | `cohort_source_parity.yaml` | `CohortManifest` | `cohort.source_parity.{name}` |
| [Source swap](source-swap.md) | `ml-crm-boundary` | `audit_profile_ml_crm.yaml` | `audit_profile` | `audit.source_swap_volume` |
| [Cohort freeze](cohort-freeze.md) | `cohort-source-parity`, `ml-crm-boundary` | `cohort_source_parity.yaml` | `CohortManifest` | `cohort.positive_rate.{name}` |

Generate templates:

```bash
trustline init --preset ml-crm-boundary --non-interactive
```

Template sources: [examples/templates/](../../examples/templates/README.md). Runnable demo: `trustline audit --demo`.

## When to use each pattern

| Pattern | When to use |
|---------|-------------|
| [Queue vs state](queue-vs-state.md) | Scores or events land in a sync queue but not in the downstream mirror |
| [Identity funnel collapse](identity-funnel-collapse.md) | Population shrinks silently across join stages |
| [Training/serving divergence](training-serving-divergence.md) | Training and scoring read from different feature tables |
| [Source swap](source-swap.md) | Upstream source migration changes event volumes |
| [Cohort freeze](cohort-freeze.md) | Cohort definition or label rate drifts after freeze |

Specification: [contract-spec.md](../contract-spec.md). Example fixture: [examples/acme_stream/](../../examples/acme_stream/).
