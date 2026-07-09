# Issue Triage — Trustline

Process for triaging GitHub Issues and maintaining label hygiene.

## Channels

| Channel | Use for |
|---------|---------|
| GitHub Issues | Bugs, feature requests |
| GitHub Discussions | Questions, ideas, show-and-tell |
| Security | Vulnerabilities (see [SECURITY.md](../SECURITY.md)) |

Redirect `question`-labeled issues to Discussions.

## Triage workflow

1. **New issue arrives** → apply `status: needs-triage`
2. **Read issue** → verify it's not a duplicate
3. **Classify:**
   - Bug → `bug` + `area:*` + `priority:*`
   - Feature → `enhancement` + `area:*`
   - Docs → `documentation`
   - Question → close with link to Discussions
4. **Scope `good first issue`:**
   - Must be < 2 hours work
   - Must include file path pointer (e.g., `src/trustline/contracts/loader.py`)
   - Must have clear acceptance criteria
5. **Update status** → `status: accepted` or `status: needs-info`

## Labels

### Type

| Label | When to apply |
|-------|---------------|
| `bug` | Something is broken |
| `enhancement` | New feature or improvement |
| `documentation` | Docs only |
| `good first issue` | Small, scoped, newcomer-friendly |
| `help wanted` | Maintainer wants community PR |
| `question` | Redirect to Discussions |

### Priority

| Label | When to apply |
|-------|---------------|
| `priority: critical` | Production breakage, security |
| `priority: high` | Blocks MVP or core workflow |
| `priority: medium` | Important but not blocking |
| `priority: low` | Nice to have |

### Area

| Label | Scope |
|-------|-------|
| `area: cli` | `trustline` commands |
| `area: contracts` | YAML parsing, validation |
| `area: compiler` | SQL generation |
| `area: integrations` | dbt, Airflow, GHA, Slack |
| `area: ci` | Workflows, Makefile, tooling |
| `area: docs` | Documentation |

### Status

| Label | Meaning |
|-------|---------|
| `status: needs-triage` | Unreviewed |
| `status: needs-info` | Waiting on reporter |
| `status: accepted` | Will be implemented |
| `status: blocked` | External dependency |

## SLA (aspirational)

| Metric | Target |
|--------|--------|
| First response | 72 hours |
| Triage decision | 7 days |
| `good first issue` grooming | Before labeling |

## Stale issues

- **v0.0.1:** Manual review monthly
- **Post-v0.1:** Plan GitHub Stale Action — 30 days inactive → `stale` label → 7 days → close

## RFC process (contract schema)

For breaking contract schema changes:

1. Open issue with `RFC` label
2. 7-day comment period
3. Maintainer accepts or rejects
4. If accepted: PR updates `schemas/`, [contract-spec.md](contract-spec.md), and [adr/](adr/) if needed
