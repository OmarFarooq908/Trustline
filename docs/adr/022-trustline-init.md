# ADR-022: trustline init workspace layout

**Status:** Accepted

**Date:** 2026-07-10

## Context

External engineers need a path from `pip install trustline` to editable contracts without reading the full contract spec. v0.1 requires hand-written YAML and manual `profiles.yml` setup.

## Decision

1. Add `trustline init --preset <name>` as the primary authoring entrypoint for v0.2.
2. Default output directory: `./trustline/` containing:
   - `contracts/` — rendered `FunnelContract` / `CohortManifest` YAML
   - `audit_profile.yaml` — when preset includes CRM/source checks (sibling of `contracts/`)
   - `profiles.yml` — DuckDB-first profile with commented Snowflake stub
   - `README.md` — generated next-step commands
3. Presets ship in the wheel under `trustline/templates/contracts/`.
4. Defer a separate `trustline generate` command; use `--preset` and future `init --add` if incremental authoring is needed.
5. Refuse to clobber an existing `./trustline/` unless `--force` is passed.

## Rationale

- Matches audit default resolution: `audit_profile.yaml` lives beside `contracts/` (parent of contracts dir).
- Keeps scorecard output out of the contracts tree.
- Presets encode ML → CRM boundary checks without new contract kinds.

## Consequences

- New minor CLI command (`trustline init`) per [STABILITY.md](../STABILITY.md).
- Template placeholders (`{{ product_slug }}`) are init-only; `{{ ref('...') }}` remains contract syntax.

## Related

- [ADR-010](010-cli-package-structure.md) — CLI module layout
- [ADR-003](003-cli-first.md) — CLI-first interface
