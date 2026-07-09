# ADR-019: v0.1 audit profile and DuckDB-first executor

**Status:** Accepted

**Date:** 2026-07-09

## Context

[mvp-scope.md](../mvp-scope.md) requires four seeded failure modes in the ACME Stream demo:

| Failure | Scorecard phase |
|---------|-----------------|
| Funnel retention drop | Phase 2 |
| Cohort source mismatch | Phase 4 |
| Source swap volume drift | Phase 3 |
| CRM coverage gap | Phase 1 |

Formal v0.1 contract kinds are only `FunnelContract` and `CohortManifest` ([mvp-scope.md](../mvp-scope.md), [roadmap.md](../roadmap.md)). [architecture.md](../architecture.md) maps Phase 1 to `DeliveryLineageContract` (v0.3) and Phase 3 to `SourceSwapAnnotation` (v0.2) — contract kinds not shipping until those versions.

Introducing preview contract kinds in v0.1 would expand schema surface area, blur the validate/audit boundary, and require amending [contract-spec.md](../contract-spec.md) before the v0.2/v0.3 RFC process.

## Decision

### 1. Audit profile for Phase 1 and Phase 3 checks

Add `examples/acme_stream/audit_profile.yaml` — a **demo configuration file**, not a contract kind.

- Validated against `schemas/audit_profile.schema.json` (mini-schema)
- Loaded only by `trustline audit` (not `trustline validate`)
- Holds CRM coverage table refs (Phase 1) and source swap migration metadata (Phase 3)
- Compiled by `src/trustline/compiler/audit_profile.py` using the same Jinja2 SQL templates planned in architecture.md (`crm_coverage_gap.sql.j2`, `source_swap_volume.sql.j2`)

`trustline validate` remains scoped to `FunnelContract` and `CohortManifest` only.

### 2. DuckDB-first executor strategy

- **Primary:** `DuckDBExecutor` with committed `examples/acme_stream/demo.duckdb` for demo, CI, and all unit/e2e tests
- **Optional:** `SnowflakeExecutor` for production `--target snowflake` (Phase 7 stretch)
- **Unit tests:** In-memory DuckDB (`:memory:`) — no network or credentials required
- **CI:** Integration tests marked `@pytest.mark.integration`; skipped unless `TRUSTLINE_RUN_INTEGRATION=1`

This aligns with [ADR-001](001-snowflake-first.md) (Snowflake for production, DuckDB for offline demo) and [engineering-foundation.md](../engineering-foundation.md) testing strategy.

## Consequences

### Positive

- MVP exit criteria met without premature v0.2/v0.3 contract kinds
- Clear separation: contracts in git for ML semantics; audit profile for demo-specific pipeline checks
- Contributors run full test suite without warehouse credentials
- Minimal spec churn — no `contract-spec.md` amendment required

### Negative

- Phase 1/3 checks are not yet expressible as first-class contracts (addressed in v0.2/v0.3)
- `audit_profile.yaml` is ACME-demo-oriented in v0.1; generalization deferred

### Migration path

| Version | Change |
|---------|--------|
| v0.2 | `SourceSwapAnnotation` contract kind replaces `audit_profile.source_swap` |
| v0.3 | `DeliveryLineageContract` replaces `audit_profile.crm_coverage` |
| v0.3+ | Deprecate `audit_profile.yaml`; migration guide in docs |

## Related

- [mvp-scope.md](../mvp-scope.md) — v0.1 audit profile scope and ACME fixture
- [architecture.md](../architecture.md) — Snowflake and DuckDB executor strategy
- [ADR-009](009-module-layout.md) — `compiler/`, `executors/` layout
