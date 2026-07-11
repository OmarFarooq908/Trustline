# Roadmap — Trustline

Feature roadmap with coarse milestones.

## Version overview

| Version | Theme | Key deliverable |
|---------|-------|-----------------|
| **v0.1** | Trust Scorecard CLI | Five-phase audit against Snowflake/DuckDB |
| **v0.2** | Contract authoring | `init`, templates, `--demo`, quick-start docs |
| **v0.3** | Integrations & adapters | dbt macro, BigQuery/Postgres, Python API, GHA PR comments |
| **v0.4** | Delivery lineage | `DeliveryLineageContract`, transfer pack, Airflow operator |
| **v0.5** | Ecosystem | Dagster integration, DataHub export |
| **v1.0** | Production ready | Web UI, stable API, multi-maintainer governance |

## Feature matrix

| Feature | v0.1 | v0.2 | v0.3 | v0.4 | v0.5 | v1.0 |
|---------|------|------|------|------|------|------|
| Trust Scorecard CLI | Yes | `--demo`, error hints | — | — | — | Stable API |
| `trustline init` + templates | — | Yes | — | — | — | — |
| Funnel contracts | Read | Author via presets | dbt macro | — | — | — |
| Cohort manifests | Read | Author via presets | Drift detect | — | — | — |
| Source swap (audit_profile) | Partial | Templates | Standalone tool | — | — | — |
| BigQuery adapter | — | — | Yes | Yes | Yes | Yes |
| Postgres adapter | — | — | Yes | — | Yes | Yes |
| Python library API | — | — | Yes | — | — | Stable |
| GHA consumer workflow | Basic | Own-contracts example | PR comment | — | — | — |
| dbt CI validate recipe | — | Yes (v0.2.1) | Macro | — | — | — |
| Airflow operator | — | Example DAG (docs) | Operator | — | — | — |
| Snowflake adapter | Yes | Profile stub in init | Yes | Yes | Yes | Yes |
| DuckDB adapter | Yes | Yes | Yes | Yes | Yes | Yes |
| Dagster integration | — | — | — | — | Yes | — |
| Web UI (read-only) | — | — | — | — | — | Yes |

## v0.1 — Trust Scorecard CLI

- `trustline validate` — JSON Schema validation
- `trustline audit` — five-phase scorecard
- FunnelContract and CohortManifest (read-only)
- Snowflake + DuckDB executors
- ACME Stream demo with 4 seeded failures

Exit criteria: see [mvp-scope.md](mvp-scope.md).

## v0.2 — Contract authoring

- `trustline audit --demo` — bundled ACME without path flags
- `trustline init --preset` — scaffold `./trustline/` workspace
- Contract template library (3 presets: ml-crm-boundary, funnel-retention, cohort-source-parity)
- Actionable CLI error hints
- Quick-start path in getting-started and ACME demo doc
- Pattern ↔ template ↔ check matrix

Deferred to v0.2.1+: dbt CI recipe, GHA workflow for user contracts, Snowflake profile docs polish.

Deferred to v0.3+: dbt macro, BigQuery/Postgres, Python library API, GHA PR comment scorecard, new contract kinds.

## v0.3 — Integrations & adapters

- `trustline_funnel` dbt macro
- BigQuery and Postgres adapters
- Python library API (`from trustline import audit, validate`)
- GitHub Actions PR comment with scorecard

## v0.4 — Delivery lineage

- `DeliveryLineageContract`
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

1. Bundled demo + init templates (v0.2.0)
2. GitHub Actions consumer workflow for own contracts (v0.2.1)
3. dbt CI `trustline validate` recipe (v0.2.1)
4. dbt macros (v0.3)
5. Airflow example DAG (v0.2.1 docs) → operator (v0.4)
6. GHA PR comment scorecard (v0.3)
7. DataHub / Dagster (v0.5)

## Contract spec roadmap

| Version | Contract kinds |
|---------|----------------|
| v0.1 | `FunnelContract`, `CohortManifest`, `audit_profile.yaml` |
| v0.3 | + `SourceSwapAnnotation` (if production adopters require) |
| v0.4 | + `DeliveryLineageContract` |
| v1.0 | `trustline.io/v1` frozen spec |

No new contract kinds in v0.2 without two production examples ([STABILITY.md](STABILITY.md)).

## Non-goals

- Orchestration engine (integrate with Airflow/Dagster, do not replace)
- Transform framework (extend dbt)
- Model training runtime
- Hosted/managed SaaS
- Auto-remediation
- AI orchestration framework (contracts for LLM outputs yes; agent framework no)

## Related documents

- [mvp-scope.md](mvp-scope.md) — v0.1 scope
- [acme-demo.md](acme-demo.md) — ACME fixture walkthrough
- [architecture.md](architecture.md) — Technical design
- [contract-spec.md](contract-spec.md) — Contract API
- [adr/022-trustline-init.md](adr/022-trustline-init.md) — Init workspace layout
- [adr/](adr/) — Technical decision records
