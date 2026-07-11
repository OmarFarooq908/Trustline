# dbt CI integration

Validate Trustline contracts on every PR that touches `./trustline/` without a dbt macro dependency.

## Setup

1. Scaffold contracts in your dbt repo:

   ```bash
   trustline init --preset ml-crm-boundary --non-interactive
   ```

2. Copy [validate-contracts.yml](validate-contracts.yml) to `.github/workflows/trustline-validate.yml`.

3. Commit `./trustline/contracts/` alongside dbt models.

## What this checks

`trustline validate` runs JSON Schema validation only — no warehouse connection required. Use a separate scheduled job or merge gate for `trustline audit` against Snowflake/DuckDB.

## dbt macro

A `trustline_funnel` dbt macro is planned for v0.3. Until then, keep funnel SQL in `FunnelContract` YAML and validate in CI with this workflow.
