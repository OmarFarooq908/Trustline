# ADR-021: Contract diff governance

**Status:** Proposed

**Date:** 2026-07-10

## Context

Business assumptions are encoded in contract YAML: retention thresholds, positive rates, observation windows, and CRM coverage percentages. These values change in pull requests alongside code. Reviewers may approve SQL refactors without noticing that `expected_positive_rate` moved from `0.12` to `0.15`, silently redefining what "pass" means.

Today there is no structured diff of contract semantics at review time.

## Problem

- Contract threshold changes lack visibility in PR review.
- Breaking assumption changes ship without migration notes.
- No machine-readable summary of what changed between two contract versions.

## Proposed UX (design only)

```bash
trustline diff base/contracts/ head/contracts/
```

Example output:

```
cohort.propensity-training-cohort-q2:
  expected_positive_rate: 0.12 → 0.15  [BREAKING: threshold]
  frozen_at: unchanged

funnel.training_positives:
  stages.behavioral_features.expect_retention_pct: 25 → 20  [BREAKING: threshold]
```

Flags:
- `BREAKING` — threshold, window, or source reference changed
- `INFO` — metadata or label-only change

## GitHub PR integration (sketch)

```yaml
# .github/workflows/contract-diff.yml (future)
on:
  pull_request:
    paths: ['**/contracts/**', '**/audit_profile.yaml']
jobs:
  diff:
    steps:
      - run: trustline diff origin/main...HEAD --format markdown > contract-diff.md
      - uses: actions/github-script@v7  # post PR comment with diff
```

## Timeline

Deferred to Phase 2 (6–12 months) unless an external adopter requests it sooner. No implementation in v0.1.x.

## Non-goals

- SQL diff between compiled checks
- Auto-approve or auto-block PRs without human review
- AI-generated review comments
- Diff of warehouse query results (only contract YAML)

## Related

- [ADR-002](002-yaml-contracts.md) — YAML contracts
- [STABILITY.md](../STABILITY.md) — Breaking change process
- [contract-spec.md](../contract-spec.md) — Contract fields
