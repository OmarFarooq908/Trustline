# Engineering Foundation — Trustline

**Authoritative engineering plan for repository structure, tooling, CI/CD, and contributor workflow.**

| Field | Value |
|-------|-------|
| Package | `trustline` |
| Python | 3.11+ |
| Owner | `omarfarooq908` |
| License | Apache 2.0 |

Related: [architecture.md](architecture.md), [mvp-scope.md](mvp-scope.md), [adr/](adr/).

---

## 1. Repository Layout

Monorepo layout scaling from MVP CLI to future integrations (dbt macros, GitHub Action) without rewrites.

```
trustline/                          # repository root
├── .devcontainer/                  # Phase 2 — planned
│   └── devcontainer.json
├── .editorconfig
├── .env.example
├── .github/
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── ci.yml                  # required: lint, typecheck, test, coverage
│       ├── security.yml            # pip-audit, bandit
│       ├── release.yml             # stub until v0.1.0
│       └── docs.yml                # stub — MkDocs Phase 3
├── .gitignore
├── .pre-commit-config.yaml
├── .vscode/
│   └── extensions.json
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── GOVERNANCE.md
├── LICENSE
├── Makefile
├── README.md
├── SECURITY.md
├── docs/
│   ├── index.md
│   ├── getting-started.md
│   ├── architecture.md
│   ├── contract-spec.md
│   ├── roadmap.md
│   ├── mvp-scope.md
│   ├── contributing.md
│   ├── engineering-foundation.md   # this document
│   ├── review-checklist.md
│   ├── triage.md
│   └── adr/                        # technical ADRs only
├── examples/
│   └── acme_stream/
│       └── contracts/
├── integrations/                   # stubs for dbt, GitHub Actions
├── mkdocs.yml                      # stub
├── pyproject.toml                  # canonical version and tool config
├── schemas/                        # JSON Schema (Phase 1)
├── scripts/
│   └── bootstrap.sh
├── src/
│   └── trustline/
│       ├── __init__.py             # __version__, public API surface
│       ├── cli/
│       ├── contracts/
│       ├── compiler/
│       ├── executors/
│       ├── scorecard/
│       ├── reporters/
│       ├── integrations/
│       └── exceptions.py
├── templates/sql/
├── tests/
└── uv.lock                         # committed lockfile
```

### Directory purposes

| Directory | Purpose |
|-----------|---------|
| `src/trustline/` | Installable Python package |
| `tests/` | Unit and integration tests (mirror `src/` as modules grow) |
| `docs/` | All documentation (not wiki) |
| `examples/` | Synthetic ACME Stream demos and contract samples |
| `integrations/` | dbt macros, GitHub Actions (optional deps on core) |
| `schemas/` | JSON Schema for contract validation |
| `templates/sql/` | Jinja2 SQL check templates (Phase 1+) |
| `scripts/` | Dev-only helpers; not part of installed package |

### Versioning

- **Canonical version:** `pyproject.toml` `[project].version`
- **Runtime:** `trustline.__version__` reads via `importlib.metadata.version("trustline")`
- **No drift:** Do not hardcode version strings elsewhere

### Public API surface

v0.0.1 skeleton exports `__version__` only. Future public API (v0.2+): `validate`, `audit`. Document planned exports in `src/trustline/__init__.py` docstring.

---

## 2. Development Environment

**Goal:** A new contributor follows [contributing.md](contributing.md) and gets green `make check` in under 15 minutes without asking questions.

### Blessed path: uv + Make

**Prerequisites:**

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) package manager
- Optional: Docker (for devcontainer, Phase 2)
- Optional: Snowflake credentials (integration tests only; skipped by default)

**Clone → install → verify:**

```bash
git clone https://github.com/omarfarooq908/trustline.git
cd trustline
make install-dev
make check
```

`make install-dev` runs `uv sync --all-extras --dev`, creating `.venv` and installing the package in editable mode.

**Fallback (pip):**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make check
```

### Makefile targets

| Target | Command | Purpose |
|--------|---------|---------|
| `install-dev` | `uv sync --all-extras --dev` | Create venv, install deps |
| `lint` | `ruff check src tests` | Lint |
| `format` | `ruff format src tests` | Auto-format |
| `format-check` | `ruff format --check src tests` | CI format gate |
| `typecheck` | `mypy src` | Static types on package |
| `test` | `pytest tests/ -m "not integration"` | Fast unit tests |
| `test-integration` | `pytest tests/ -m integration` | Warehouse tests (needs creds) |
| `coverage` | `pytest --cov=trustline --cov-report=term-missing --cov-fail-under=85` | Coverage gate |
| `check` | `format-check lint typecheck coverage` | All PR gates |
| `clean` | Remove caches, `dist/`, `htmlcov/` | Reset build artifacts |

### Pre-commit hooks (mandatory)

Install: `uv run pre-commit install`

| Hook | Purpose |
|------|---------|
| `ruff` | Lint + format |
| `ruff-format` | Format check |
| `mypy` | Type check `src/` |
| `trailing-whitespace` | Clean whitespace |
| `end-of-file-fixer` | Ensure newline at EOF |
| `check-yaml` | Valid YAML |
| `check-added-large-files` | Block files > 500KB |
| `no-commit-to-branch` | Block direct commits to `main` |

### Editor config

- `.editorconfig` — indent, charset, trim trailing whitespace
- `.vscode/extensions.json` — recommends Python, Ruff, Mypy extensions (no secrets)

### Environment variables

See `.env.example`. Copy to `.env` (gitignored). Never commit `.env` or warehouse credentials.

| Variable | Required | Purpose |
|----------|----------|---------|
| `TRUSTLINE_LOG_LEVEL` | No | Logging level (default: INFO) |
| `SNOWFLAKE_*` | Integration only | Snowflake connection |
| `SLACK_WEBHOOK_URL` | No | Audit failure notifications |
| `TRUSTLINE_RUN_INTEGRATION` | No | Set to `1` to run integration tests |

### Devcontainer (Phase 2)

Planned `.devcontainer/devcontainer.json`:

- Base image: `mcr.microsoft.com/devcontainers/python:3.12`
- Features: uv pre-installed
- `postCreateCommand`: `make install-dev`

---

## 3. Code Quality Standards

| Area | Tool | Policy |
|------|------|--------|
| Formatter | Ruff format | Line length 100; 100% enforced in CI |
| Linter | Ruff | Rules: `E`, `F`, `I`, `UP`, `B`, `SIM`; ignores only with inline comment + justification |
| Type hints | mypy | `strict = true` on `src/trustline/`; tests excluded or relaxed |
| Docstrings | Google style | All public modules, classes, functions |
| Security | bandit + pip-audit | `security.yml`; fail on high severity |
| Dependencies | `uv.lock` committed | Dependabot weekly updates |
| Logging | stdlib `logging` | No `print()` in library code |
| Errors | `exceptions.py` | `TrustlineError` hierarchy (see below) |

### Exception hierarchy

```
TrustlineError
├── ValidationError      # contract/schema validation failures
├── AuditError           # scorecard execution failures
└── ExecutorError        # warehouse adapter failures
```

Cross-reference: [architecture.md](architecture.md) for component boundaries.

### Code review

Reviewers use [review-checklist.md](review-checklist.md) (12 items).

---

## 4. Testing Strategy

### Testing pyramid

```
        /\
       /  \  Integration (optional, creds required)
      /----\
     /      \  Unit + CLI smoke (every PR)
    /--------\
   / Snapshot \  SQL generation golden files (Phase 1+)
  /------------\
```

### Test layout

- Mirror `src/trustline/` structure as modules grow
- `tests/conftest.py` — shared fixtures
- `tests/fixtures/acme_contracts/` — synthetic YAML only (ACME Stream)
- Naming: `test_<unit>_<behavior>`

### Markers

```python
@pytest.mark.integration
def test_snowflake_audit():
    ...
```

Skipped unless `TRUSTLINE_RUN_INTEGRATION=1` is set.

### Coverage

- Minimum: **85%** on `src/trustline/`
- Enforced: `pytest --cov-fail-under=85` in `make coverage`
- CI runs coverage on every PR

### Snapshot tests (Phase 1+)

- Tool: syrupy or inline snapshots
- Policy: SQL generation outputs use ACME Stream fixtures
- Update flow: `make test-snap-update` (documented when introduced)
- PRs changing snapshots must explain why in description

### Running tests

```bash
make test              # fast suite only
make test-integration  # requires TRUSTLINE_RUN_INTEGRATION=1 + creds
make coverage          # with coverage gate
```

### CI integration tests

- Default CI: integration tests **skipped** (no secrets on fork PRs)
- Optional manual workflow_dispatch with secrets for maintainer validation
- No `pull_request_target` (security)

---

## 5. CI/CD (GitHub Actions)

### Branch strategy

| Branch | Purpose |
|--------|---------|
| `main` | Protected; always green |
| `feat/*`, `fix/*`, `docs/*`, `chore/*` | Short-lived feature branches |
| `v*.*.*` tags | Releases |

### Workflows

#### `ci.yml` — required

| Setting | Value |
|---------|-------|
| Trigger | `pull_request`, `push` to `main` |
| Concurrency | `ci-${{ github.ref }}`, cancel in-progress |
| Matrix | `ubuntu-latest` × Python 3.11, 3.12, 3.13 |
| Steps | checkout → setup uv → `uv sync --dev` → `make check` |
| Job name | **`CI`** (use for branch protection) |

#### `security.yml` — recommended

| Setting | Value |
|---------|-------|
| Trigger | Weekly cron (Monday 06:00 UTC), `pull_request` |
| Jobs | `pip-audit`, `bandit -r src -ll` |
| Job name | **`Security`** |

#### `release.yml` — stub

| Setting | Value |
|---------|-------|
| Trigger | Push tags `v*` |
| Planned | `uv build` → PyPI (`PYPI_API_TOKEN`) → GitHub Release |
| Status | Stub with comments until v0.1.0 |

#### `docs.yml` — stub

| Setting | Value |
|---------|-------|
| Trigger | Push to `main` (when enabled) |
| Planned | MkDocs Material → GitHub Pages |
| Status | Phase 3 |

### Branch protection (required checks)

Configure on `main`:

1. **`CI`** — required
2. **`Security`** — recommended by Week 1

Additional settings:

- Require linear history (squash merge)
- Require conversation resolution before merge
- Do not allow bypassing

### Fork PR safety

- No secrets exposed to fork PR workflows
- No `pull_request_target` with checkout of PR code
- Integration tests remain skipped in CI

### Caching

- `astral-sh/setup-uv` with built-in cache
- `uv sync` uses `uv.lock` for reproducible installs

### Artifacts

- Optional: upload coverage HTML as artifact (not required v0.0.1)

---

## 6. Git, Commits, and PR Workflow

Documented in [contributing.md](contributing.md).

### Commits

- **Format:** [Conventional Commits](https://www.conventionalcommits.org/)
  - `feat:` new feature
  - `fix:` bug fix
  - `docs:` documentation
  - `test:` tests
  - `chore:` maintenance
  - `ci:` CI changes
  - `schema:` contract schema changes
- **Atomic:** one logical change per commit where possible
- **No WIP** on `main`
- **DCO:** Developer Certificate of Origin via `Signed-off-by: Name <email>` in commit message
- **No CLA** required for v0.1

### PR process

1. Open issue for non-trivial changes (link in PR)
2. Fork → branch from `main` → `make check` locally
3. Open PR using template
4. Wait for green `CI` (+ `Security`)
5. Squash merge to `main`
6. Delete branch after merge

### Solo maintainer policy

Until a second maintainer is added:

- Self-merge permitted after green CI + Security
- No human approval required
- Document decision in PR if bypassing any check (never bypass CI)

### PR size

- Prefer **< 400 lines** changed
- Split large changes into stacked PRs

---

## 7. Issues, Labels, and Triage

See [triage.md](triage.md) for full process.

### Issue templates

| Template | File | Use |
|----------|------|-----|
| Bug report | `.github/ISSUE_TEMPLATE/bug_report.yml` | Defects |
| Feature request | `.github/ISSUE_TEMPLATE/feature_request.yml` | Enhancements |
| Questions | GitHub Discussions | Not issues |

### Labels

| Label | Color (suggested) | Purpose |
|-------|-------------------|---------|
| `bug` | red | Defect |
| `enhancement` | blue | New feature |
| `documentation` | green | Docs only |
| `good first issue` | purple | < 2h, code pointer included |
| `help wanted` | yellow | Maintainer welcomes PR |
| `question` | gray | Redirect to Discussions |
| `priority: critical` | dark red | Drop everything |
| `priority: high` | orange | Next sprint |
| `priority: medium` | yellow | Backlog |
| `priority: low` | gray | Someday |
| `area: cli` | — | CLI commands |
| `area: contracts` | — | Contract parsing/validation |
| `area: compiler` | — | SQL generation |
| `area: integrations` | — | dbt, Airflow, GHA |
| `area: ci` | — | CI/CD |
| `area: docs` | — | Documentation |
| `status: needs-triage` | — | New, unreviewed |
| `status: needs-info` | — | Awaiting reporter |
| `status: accepted` | — | Will be worked |
| `status: blocked` | — | External dependency |

### Triage SLA (aspirational)

| Metric | Target |
|--------|--------|
| First response | 72 hours |
| `good first issue` scope | < 2 hours work |
| `good first issue` requirement | Linked file path in issue body |

### Stale policy

- v0.0.1: manual triage
- Post-v0.1: GitHub Stale Action at 30 days inactive (plan only)

---

## 8. Community and Governance

| File | Purpose |
|------|---------|
| [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | Contributor Covenant v2.1 |
| [SECURITY.md](../SECURITY.md) | Vulnerability reporting |
| [GOVERNANCE.md](../GOVERNANCE.md) | Maintainer roles and decisions |
| [CHANGELOG.md](../CHANGELOG.md) | Keep a Changelog format |

### GitHub repository settings checklist

- [ ] Default branch: `main`
- [ ] Discussions: enabled (Q&A category)
- [ ] Issues: enabled
- [ ] Wiki: **disabled** (docs live in repo)
- [ ] Projects: optional
- [ ] Auto-delete head branches after merge: **enabled**
- [ ] Branch protection on `main` with required `CI` check
- [ ] CODEOWNERS: `* @omarfarooq908`

---

## 9. Releases and Versioning

### Semver

- Start at **v0.1.0** for MVP launch
- Scaffold uses **v0.0.1** (pre-release)
- 0.x allows breaking changes; document in CHANGELOG

### PyPI

- Package name: **`trustline`**
- Verify availability before first publish (see [adr/016-pypi-package-name.md](adr/016-pypi-package-name.md))
- Dev install: `uv sync --dev` or `pip install -e ".[dev]"`

### Release flow

```
main → tag v0.1.0 → release.yml → PyPI + GitHub Release
```

1. Update `CHANGELOG.md` and `pyproject.toml` version
2. PR to `main`
3. Tag `v0.1.0` on merge commit
4. `release.yml` builds wheel, publishes PyPI, creates GitHub Release

---

## 10. Documentation Site (Plan)

| Item | Choice |
|------|--------|
| Tool | MkDocs Material |
| Config | `mkdocs.yml` (stub in repo) |
| Structure | User guide, CLI reference, contract spec, contributing |
| Source | `docs/` directory |
| Deploy | GitHub Pages via `docs.yml` |
| Status | Phase 3 (post-MVP) |

Existing product docs remain in `docs/` and will be included in the site navigation.

---

## 11. Security and Supply Chain

| Control | Implementation |
|---------|----------------|
| Vulnerability reporting | [SECURITY.md](../SECURITY.md) — GitHub private advisories |
| Dependency updates | `.github/dependabot.yml` — pip + github-actions weekly |
| Dependency audit | `pip-audit` in `security.yml` |
| Static analysis | `bandit` in `security.yml` |
| Secret scanning | GitHub native; optional gitleaks in Phase 1 |
| No secrets in repo | `.env` gitignored; `profiles.yml` gitignored |
| SBOM | Not required v0.1; note for future |

---

## 12. Observability of the Project

### README badges

- CI status (`CI` workflow)
- Coverage (when Codecov or similar added; placeholder until then)
- PyPI version (after first publish)
- License: Apache 2.0

### Roadmap sync

- Public roadmap: [roadmap.md](roadmap.md)
- Link from README
- Update roadmap in same PR as feature merges when possible

### Contributor stats

Not required v0.1.

---

## 13. Anti-Patterns

This repository will **not**:

| Anti-pattern | Why |
|--------------|-----|
| Commit virtualenvs (`.venv/`) | Reproducible via `uv.lock` |
| Commit `.env`, keys, or `profiles.yml` | Security |
| Use 500-line PR templates | Contributor friction |
| Require CLA for v0.1 | DCO is sufficient |
| Split into multiple packages prematurely | Monorepo until scale demands it |
| Ship generated SQL without snapshot tests | Regression risk (Phase 1+) |
| Commit directly to `main` bypassing CI | Quality gate |
| Use `print()` in library code | Use `logging` |

---

## 14. Foundation Rollout Phases

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Phase 0** | Day 1 | `engineering-foundation.md` + scaffold + green `make check` + CI |
| **Phase 1** | Post-scaffold | JSON Schema in `schemas/`, contract parser, `trustline validate` |
| **Phase 2** | Post-scaffold | MVP scope per [mvp-scope.md](mvp-scope.md) |
| **Phase 3** | Post-MVP | dbt macro, GitHub Action, MkDocs deploy, devcontainer |

### Phase 0 exit criteria

- [ ] `make install-dev && make check` passes locally
- [ ] `CI` workflow green on `main`
- [ ] `trustline --help` and `trustline --version` work
- [ ] contributing.md enables 15-minute onboarding
- [ ] No secrets in artifacts

---

## Related Documents

| Document | Description |
|----------|-------------|
| [contributing.md](contributing.md) | Contributor onboarding |
| [adr/](adr/) | Technical architecture decision records |
| [review-checklist.md](review-checklist.md) | Code review checklist |
| [triage.md](triage.md) | Issue triage process |
| [architecture.md](architecture.md) | Product technical architecture |
| [mvp-scope.md](mvp-scope.md) | Public MVP scope |
