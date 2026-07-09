# Trustline

Trustline is a CLI that validates YAML contracts and runs a five-phase trust audit against a warehouse. Contracts describe cross-boundary checks — identity funnels, cohort definitions, and delivery coverage — that compile to SQL and produce a pass/fail scorecard.

| | |
|---|---|
| Repository | [github.com/omarfarooq908/trustline](https://github.com/omarfarooq908/trustline) |
| License | Apache 2.0 |
| Python | 3.11+ |

## Commands

```bash
trustline validate --contracts ./contracts/
trustline audit --contracts ./contracts/ --target duckdb
trustline audit --contracts ./contracts/ --target snowflake --profile acme_prod
```

See [getting-started.md](getting-started.md) for install and options.

## Contract kinds (v0.1)

| Kind | Purpose |
|------|---------|
| `FunnelContract` | Multi-hop join stages with count and retention thresholds |
| `CohortManifest` | Observation/outcome windows, label definition, training vs scoring sources |
| `audit_profile.yaml` | Product-scoped checks (CRM coverage, source swap volume) — see [ADR-019](adr/019-v01-audit-profile.md) |

Specification: [contract-spec.md](contract-spec.md).

## Audit phases

| Phase | Checks |
|-------|--------|
| 1 — Pipeline truth | Staging counts, CRM mirror coverage |
| 2 — Population funnel | `FunnelContract` stage counts and retention |
| 3 — Score semantics | Score distribution, source swap volume |
| 4 — Training autopsy | `CohortManifest` source parity, positive rate |
| 5 — Leadership brief | Aggregated verdict and recommended actions |

## Architecture

```mermaid
flowchart LR
    YAML[Contract YAML] --> Validate[JSON Schema]
    Validate --> Compile[SQL compiler]
    Compile --> Executor[Warehouse executor]
    Executor --> Scorecard[Scorecard]
    Scorecard --> Report[Markdown / JSON]
```

Details: [architecture.md](architecture.md).

## Example data

The `examples/acme_stream/` directory contains a DuckDB fixture with seeded check failures for local development and CI. Fixture reference: [mvp-scope.md](mvp-scope.md#acme-stream-demo-scenario).

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](getting-started.md) | Install, CLI, example run |
| [Contract Spec](contract-spec.md) | YAML schema and examples |
| [Architecture](architecture.md) | Module layout and data flow |
| [MVP Scope](mvp-scope.md) | v0.1 deliverables |
| [Roadmap](roadmap.md) | Planned versions |
| [Contributing](contributing.md) | Development workflow |
