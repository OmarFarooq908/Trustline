# Roadmap — Trustline

Feature roadmap with coarse milestones.

## Version overview

| Version | Theme | Key deliverable |
|---------|-------|-----------------|
| **v0.1** | Trust Scorecard CLI | Five-phase audit against Snowflake/DuckDB |
| **v0.2** | Contract authoring | dbt macro, source swap detector, BigQuery/Postgres |
| **v0.3** | Delivery lineage | CRM mirror checks, transfer pack, Airflow operator |
| **v0.5** | Ecosystem | Dagster integration, DataHub export |
| **v1.0** | Production ready | Web UI, stable API, multi-maintainer governance |

## Feature matrix

| Feature | v0.1 | v0.2 | v0.3 | v0.5 | v1.0 |
|---------|------|------|------|------|------|
| Trust Scorecard CLI | Yes | Enhanced | — | — | Stable API |
| Funnel contracts | Read | Author + dbt macro | — | — | — |
| Cohort manifests | Read | Full spec + drift detect | — | — | — |
| Source swap detector | Partial (P3) | Standalone | — | — | — |
| ML delivery lineage | — | Basic | Full CRM check | — | — |
| Transfer pack generator | — | — | Yes | Enhanced | — |
| Snowflake adapter | Yes | Yes | Yes | Yes | Yes |
| DuckDB adapter | Yes | Yes | Yes | Yes | Yes |
| BigQuery adapter | — | Yes | Yes | Yes | Yes |
| Postgres adapter | — | Yes | — | Yes | Yes |
| Airflow operator | — | — | Yes | — | — |
| Dagster integration | — | — | — | Yes | — |
| Web UI (read-only) | — | — | — | — | Yes |
| Python library API | — | Yes | — | — | Stable |

## v0.1 — Trust Scorecard CLI

- `trustline validate` — JSON Schema validation
- `trustline audit` — five-phase scorecard
- FunnelContract and CohortManifest (read-only)
- Snowflake + DuckDB executors
- ACME Stream demo with 4 seeded failures

Exit criteria: see [mvp-scope.md](mvp-scope.md).

## v0.2 — Contract authoring

- `trustline_funnel` dbt macro
- Standalone source swap detector
- BigQuery and Postgres adapters
- Python library API (`from trustline import audit, validate`)
- GitHub Actions PR comment with scorecard

## v0.3 — Delivery lineage

- `DeliveryLineageContract`
- CRM mirror coverage check
- Transfer pack generator (`trustline transfer-pack`)
- Airflow `TrustlineAuditOperator`

## v0.5 — Ecosystem

- Dagster asset check integration
- DataHub export
- PagerDuty alerts
- Enhanced source swap (semantic drift)

## v1.0 — Production ready

- Read-only web UI
- Stable Python API (semver-guaranteed)
- Multi-maintainer governance
- Published docs site

## Integration priority

1. dbt macros (v0.2)
2. GitHub Actions (v0.1 basic, v0.2 PR comments)
3. Slack (v0.1 webhook, v0.2 contract alerts)
4. Airflow (v0.3)
5. DataHub export (v0.5)
6. Dagster (v0.5)

## Contract spec roadmap

| Version | Contract kinds |
|---------|----------------|
| v0.1 | `FunnelContract`, `CohortManifest` |
| v0.2 | + `SourceSwapAnnotation` |
| v0.3 | + `DeliveryLineageContract` |
| v1.0 | `trustline.io/v1` frozen |

## Non-goals

- Orchestration engine (integrate with Airflow/Dagster, do not replace)
- Transform framework (extend dbt)
- Model training runtime
- Hosted/managed SaaS
- Auto-remediation

## Related documents

- [mvp-scope.md](mvp-scope.md) — v0.1 scope
- [architecture.md](architecture.md) — Technical design
- [contract-spec.md](contract-spec.md) — Contract API
- [adr/](adr/) — Technical decision records
