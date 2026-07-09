---
name: Implementation task
description: TRUST-xxx milestone from the v0.1 implementation plan
title: "[TRUST-XXX]: "
labels:
  - enhancement
body:
  - type: markdown
    attributes:
      value: |
        Copy the task block from [docs/MILESTONES.md](../../docs/MILESTONES.md).
        Link to [IMPLEMENTATION_PLAN.md](../../docs/IMPLEMENTATION_PLAN.md) for context.
  - type: input
    id: trust-id
    attributes:
      label: TRUST ID
      description: e.g. TRUST-001
      placeholder: TRUST-001
    validations:
      required: true
  - type: dropdown
    id: phase
    attributes:
      label: Phase
      description: Implementation phase from IMPLEMENTATION_PLAN.md
      options:
        - "1 — Contract load + validate"
        - "2 — Config + DuckDB executor"
        - "3 — SQL compiler"
        - "4 — Scorecard engine"
        - "5 — Reporters"
        - "6 — E2E audit"
        - "7 — Snowflake executor (stretch)"
        - "8 — Integrations + docs"
    validations:
      required: true
  - type: textarea
    id: files
    attributes:
      label: Files
      description: Exact paths to create or modify
      placeholder: |
        src/trustline/contracts/loader.py
        tests/unit/contracts/test_loader.py
    validations:
      required: true
  - type: textarea
    id: acceptance
    attributes:
      label: Acceptance criteria
      description: Checklist items that define done
      placeholder: |
        - [ ] Loads valid ACME contract from examples/contracts/
        - [ ] Raises ValidationError on missing required field
        - [ ] make check passes
    validations:
      required: true
  - type: input
    id: depends-on
    attributes:
      label: Depends on
      description: Prior TRUST tasks or "none"
      placeholder: TRUST-001, TRUST-002
  - type: textarea
    id: notes
    attributes:
      label: Notes
      description: Risks, scope boundaries, or links to ADRs
      placeholder: See ADR-019 for audit_profile scope.
