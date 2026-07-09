# ADR-001: Snowflake-first warehouse adapter

**Status:** Accepted

**Context:** Teams use Snowflake, BigQuery, and Postgres for ML and analytics workloads.

**Decision:** Snowflake primary adapter in v0.1; DuckDB for local/offline demo. BigQuery and Postgres in v0.2.

**Rationale:** Strong dbt Snowflake ecosystem; in-warehouse ML patterns; DuckDB enables CI and demo without credentials.

**Consequences:** Warehouse-specific SQL isolated in adapter layer with Jinja2 templates.
