# Contract templates

Copy-paste YAML starters for Trustline contracts. Each template maps to a [pattern doc](../../docs/patterns/README.md).

| Preset | Pattern | Contract kinds |
|--------|---------|----------------|
| `ml-crm-boundary` | ML → CRM boundary checks (composite preset) | `FunnelContract`, `CohortManifest`, `audit_profile.yaml` |
| `funnel-retention` | [Identity funnel collapse](../../docs/patterns/identity-funnel-collapse.md) | `FunnelContract` |
| `cohort-source-parity` | [Training/serving divergence](../../docs/patterns/training-serving-divergence.md) | `CohortManifest` |

## Generate from a preset

```bash
trustline init --preset ml-crm-boundary --non-interactive
trustline validate --contracts ./trustline/contracts
```

Bundled template sources live in `src/trustline/templates/contracts/` and ship in the PyPI wheel.

## Customize

1. Replace `{{ ref('table_name') }}` with your warehouse tables (or dbt `ref()` if using dbt).
2. Edit thresholds (`expect_retention_pct`, `expect_sync_pct`, etc.) to match model review sign-off.
3. Run `trustline audit --contracts ./trustline/contracts --profiles ./trustline/profiles.yml`.

For a runnable demo without your warehouse, use `trustline audit --demo`.
