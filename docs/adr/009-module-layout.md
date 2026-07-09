# ADR-009: Repository module layout

**Status:** Accepted

**Context:** Foundation spec proposed `checks/` module. [architecture.md](../architecture.md) defines `compiler/`, `executors/`, `reporters/`.

**Decision:** Follow product architecture: `compiler/`, `executors/`, `reporters/` — not `checks/`.

**Rationale:** Aligns with contract-to-SQL compilation pipeline and warehouse adapter pattern.
