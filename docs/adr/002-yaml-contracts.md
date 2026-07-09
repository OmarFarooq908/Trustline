# ADR-002: YAML + JSON Schema contracts

**Status:** Accepted

**Context:** Contracts could be YAML, JSON, or a Python DSL.

**Decision:** YAML authored by humans; JSON Schema for validation in CI.

**Rationale:** Readable in git; machine-validated; familiar Kubernetes-style envelope (`apiVersion`, `kind`, `spec`).

**Consequences:** Schema evolution requires RFC process and `apiVersion` bumps.
