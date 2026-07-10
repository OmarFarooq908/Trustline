# Boundary patterns

Catalog of cross-boundary failure modes Trustline checks detect. Each pattern maps to a contract kind and a scorecard check.

| Pattern | Contract | Check | When to use |
|---------|----------|-------|-------------|
| [Queue vs state](queue-vs-state.md) | `audit_profile` (`crm_coverage`) | Phase 1 — `audit.crm_coverage` | Scores or events land in a sync queue but not in the downstream mirror |
| [Identity funnel collapse](identity-funnel-collapse.md) | `FunnelContract` | Phase 2 — `funnel.retention.{name}.{stage}` | Population shrinks silently across join stages |
| [Training/serving divergence](training-serving-divergence.md) | `CohortManifest` (`sources`) | Phase 4 — `cohort.source_parity.{name}` | Training and scoring read from different feature tables |
| [Source swap](source-swap.md) | `audit_profile.source_swap` | Phase 3 — `audit.source_swap_volume` | Upstream source migration changes event volumes |
| [Cohort freeze](cohort-freeze.md) | `CohortManifest.frozen_at` | Phase 4 — `cohort.positive_rate.{name}` | Cohort definition or label rate drifts after freeze |

Specification: [contract-spec.md](../contract-spec.md). Example fixture: [examples/acme_stream/](../../examples/acme_stream/).
