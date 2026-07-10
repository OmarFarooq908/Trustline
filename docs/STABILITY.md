# Stability policy — Trustline v0.1

This document defines stability promises for `trustline.io/v1` contracts and the `trustline` CLI package.

---

## Scope

| Artifact | Governed by |
|----------|-------------|
| Contract YAML (`apiVersion: trustline.io/v1`) | JSON Schema in `schemas/` |
| `audit_profile.yaml` shape | `schemas/audit_profile.schema.json` |
| CLI commands and exit codes | Semver on PyPI package `trustline` |

Specification reference: [contract-spec.md](contract-spec.md).

---

## Stable in v0.1

The following are stable for the lifetime of `trustline.io/v1`:

| Kind / file | Purpose |
|-------------|---------|
| `FunnelContract` | Multi-stage funnel with count and retention thresholds |
| `CohortManifest` | Observation/outcome windows, label, training/scoring sources |
| `audit_profile.yaml` | Product-scoped CRM coverage, source swap, score distribution |

See [ADR-019](adr/019-v01-audit-profile.md) for audit profile fields.

---

## `apiVersion: trustline.io/v1`

- All contract files must declare `apiVersion: trustline.io/v1` for this spec generation.
- **No breaking changes** to required fields or field types without:
  1. A new `apiVersion` (e.g. `trustline.io/v2`)
  2. A migration guide in `docs/`
  3. A minor CLI release minimum (`0.x.0`) documenting the change

Optional fields may be added in patch releases if they do not change validation of existing files.

---

## Semver policy

### Contract schema (`schemas/`)

| Change | Version bump |
|--------|--------------|
| New optional JSON Schema field | Patch (e.g. schema note in CHANGELOG) |
| New required field | New `apiVersion` + migration doc |
| Remove or rename field | New `apiVersion` + migration doc |
| Change field type | New `apiVersion` + migration doc |

### CLI package (`trustline` on PyPI)

| Change | Version bump |
|--------|--------------|
| Bug fix, docs, non-breaking check behavior | Patch (`0.1.x`) |
| New check for existing contract fields; new optional CLI flags | Minor (`0.x.0`) |
| Remove CLI flag; change exit code contract; rename JSON report fields | Major (`x.0.0`) |

JSON report field `trust_score` is stable in v0.1.x. A rename to `integrity_score` requires minor release with deprecation notice (see [contract-spec.md#terminology](contract-spec.md#terminology)).

---

## Breaking change process

1. Open a GitHub Issue with the `RFC` label (7-day comment period).
2. Write an ADR in `docs/adr/` describing the change and migration path.
3. Update `schemas/` and [contract-spec.md](contract-spec.md).
4. Ship migration guide alongside the release.
5. Deprecation window: at least one minor release before removing support for old `apiVersion`.

See also [contributing.md](contributing.md#contract-schema-changes).

---

## Experimental

Nothing is marked experimental in v0.1. Future experimental kinds or fields will be listed in this section with an explicit expiry or promotion criteria.

---

## Field addition rule

Do not add new **required** contract fields unless **two independent production examples** need them. The ACME Stream fixture counts as one example. Wait for an external adopter before generalizing schema changes.

---

## Related documents

- [ADR-002](adr/002-yaml-contracts.md) — YAML + JSON Schema contracts
- [contract-spec.md](contract-spec.md) — Full contract specification
- [roadmap.md](roadmap.md) — Planned contract kinds for v0.2+
