# Governance — Trustline

Lightweight governance for the Trustline open-source project.

## Maintainers

| Role | Responsibility |
|------|----------------|
| **Lead maintainer** | `@omarfarooq908` — roadmap, releases, final merge authority |
| **Maintainer** | Triage, review, merge (added as project grows) |

Current maintainers: `@omarfarooq908`

## Decision process

| Decision type | Process |
|---------------|---------|
| Bug fixes, docs, tests | Maintainer discretion; green CI required |
| New features | Issue discussion; align with [roadmap.md](docs/roadmap.md) |
| Contract schema changes | RFC process (7-day comment period) |
| Breaking API changes | ADR in [docs/adr/](docs/adr/); semver bump |
| New maintainers | Invitation after sustained contributions (10+ merged PRs) |

## Adding maintainers

Criteria:

- Consistent quality contributions over 3+ months
- Alignment with project values and code of conduct
- Agreement to triage and review responsibilities

Process: existing maintainer proposes → discussion in private → update CODEOWNERS and this file.

## Releases

- Lead maintainer tags releases
- Semver per [CHANGELOG.md](CHANGELOG.md)
- 0.x series: breaking changes allowed with documentation

## Conflict resolution

1. Discuss in GitHub Issue or PR
2. If unresolved, lead maintainer decides
3. Document decision in ADR if architectural

## Relation to product docs

- [index.md](docs/index.md) — Product overview
- [roadmap.md](docs/roadmap.md) — feature roadmap
- [engineering-foundation.md](docs/engineering-foundation.md) — engineering standards

Maintainers should not override accepted product ADRs without new ADR and community notice.
