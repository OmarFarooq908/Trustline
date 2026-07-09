# MVP Scope — Trustline v0.1

Scope definition for the minimum viable product.

## Focus: ML Trust Scorecard CLI

Trustline v0.1 is a command-line tool that runs a five-phase trust audit against declarative contracts and produces a pass/fail scorecard with evidence.

```bash
trustline validate --contracts ./examples/acme_stream/contracts/
trustline audit --contracts ./examples/acme_stream/contracts/ --target duckdb
trustline audit --contracts ./contracts/ --target snowflake --profile acme_prod
```

The scorecard is the **verdict engine**. Contracts are the **spec**.

## ACME Stream demo scenario

Synthetic fixture in `examples/acme_stream/`.

| Attribute | Value |
|-----------|-------|
| Product | `propensity_score` |
| Identity funnel | 2,000 donors → 800 app matches → 250 with watch features |
| Source swap | `LegacyPlayer` → `NewPlayer` on `user_events_silver` |
| CRM gap | Push queue: 300 rows; contacts mirror: 80 (demo scale) |

### Seeded failure modes (demo)

| # | Failure | Scorecard phase | Expected |
|---|---------|-----------------|----------|
| 1 | Funnel retention drop | Phase 2 | FAIL |
| 2 | Cohort source mismatch | Phase 4 | FAIL |
| 3 | Source swap volume drift | Phase 3 | WARN |
| 4 | CRM coverage gap | Phase 1 | FAIL |

## v0.1 in scope

| Area | Deliverable |
|------|-------------|
| CLI | `trustline validate`, `trustline audit` |
| Contracts | `FunnelContract`, `CohortManifest` (read-only consumption) |
| Scorecard | Five phases; markdown + JSON output |
| Executors | DuckDB (local demo), Snowflake (production) |
| Integrations | GitHub Actions example, optional Slack webhook |
| Artifacts | `examples/acme_stream/`, README quickstart |

## v0.1 out of scope

| Item | Target version |
|------|----------------|
| dbt macro (`trustline_funnel`) | v0.2 |
| Airflow operator | v0.3 |
| Standalone source swap detector | v0.2 |
| BigQuery / Postgres adapters | v0.2 |
| Web UI / hosted service | v1.0 |
| Auto-fix or remediation | Never (v0.x) |
| Transfer pack generator | v0.3 |
| Delivery lineage contract | v0.3 |

## Exit criteria

v0.1 is **done** when:

| # | Criterion |
|---|-----------|
| 1 | ACME demo runs end-to-end in < 5 minutes from clone |
| 2 | All 4 seeded failure modes detected in automated tests |
| 3 | Valid contracts pass `trustline validate` in CI |
| 4 | Broken contracts fail `trustline validate` in CI |
| 5 | `trustline audit` exits non-zero on failure |
| 6 | Markdown + JSON report generated |
| 7 | README quickstart is copy-paste accurate |

## Related documents

- [index.md](index.md) — Overview
- [architecture.md](architecture.md) — Technical architecture
- [contract-spec.md](contract-spec.md) — Contract specification
- [roadmap.md](roadmap.md) — Post-MVP features
