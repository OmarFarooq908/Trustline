# Trustline v0.1 — Implementation Plan

**Status:** Approved for implementation  
**Authoritative scope:** [mvp-scope.md](mvp-scope.md)  
**Architecture:** [architecture.md](architecture.md)  
**Milestones:** [MILESTONES.md](MILESTONES.md)

This document is the master implementation plan for Trustline v0.1. It is executable by another engineer without guessing — file paths, function signatures, test files, and acceptance criteria are specified throughout.

---

## 1. Current state audit

Facts recorded on **2026-07-09** after `make check` on commit scaffold `v0.0.1`.

### Baseline CI status

| Gate | Command | Status |
|------|---------|--------|
| Docs publishing | `make check-docs` | PASS |
| Format | `make format-check` | PASS (18 files) |
| Lint | `make lint` | PASS |
| Typecheck | `make typecheck` | PASS (12 source files) |
| Coverage | `make coverage` | PASS — **94.44%** on `src/trustline/`, 10 tests, 85% threshold |

### Gap table

| Area | Exists today | Gap for MVP |
|------|--------------|-------------|
| CLI | Typer app in `cli/main.py`; `--version` works; stub `validate`/`audit` exit 1 | Real validation + audit; exit codes 0/1/2/3; `--profile`, `-o`, `--output-dir`, `--notify slack`, `--dry-run` |
| Contract parser | Empty `contracts/` package (`__init__.py` only) | Loader, JSON Schema validator, Pydantic models for `FunnelContract` + `CohortManifest` |
| Schema validation | Inline JSON Schema in [contract-spec.md](contract-spec.md); **no `schemas/` directory** | `schemas/funnel.schema.json`, `cohort.schema.json`, `common.schema.json`, `audit_profile.schema.json` |
| Scorecard engine | Empty `scorecard/` package | 5-phase orchestrator + phase modules; aggregate pass/fail/warn |
| Warehouse adapter | Empty `executors/` package | `Executor` protocol, `DuckDBExecutor` (primary), `SnowflakeExecutor` (optional) |
| SQL compiler | Empty `compiler/` package | Jinja2 templates in `templates/sql/`; funnel, cohort, audit_profile compilers |
| Reporters | Empty `reporters/` package | Markdown + JSON scorecard output |
| Examples | `examples/acme_stream/contracts/training_positives.yaml` only | Cohort contract, `audit_profile.yaml`, `seed_data.sql`, `demo.duckdb`, `profiles.yml.example` |
| Tests | 10 flat tests in `tests/` (CLI, version, exceptions) | Mirror `src/` layout; unit + snapshot + e2e; 4 failure-mode assertions |
| CI | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs `make check-docs` + format/lint/mypy/coverage | Integration marker skip; optional Snowflake job; coverage bump as modules land |
| Integrations | Empty `integrations/` stub | `integrations/github-actions/trustline-audit.yml`; optional Slack in `src/trustline/integrations/slack.py` |

### Doc conflicts resolved

See [ADR-019](adr/019-v01-audit-profile.md). Phase 1 (CRM) and Phase 3 (source swap) demo checks use `audit_profile.yaml`, not v0.2/v0.3 contract kinds.

Module layout follows [ADR-009](adr/009-module-layout.md): `compiler/`, `executors/`, `reporters/` — not `checks/` or `warehouse/`.

CLI surface follows [mvp-scope.md](mvp-scope.md): `trustline audit` — not `trustline scorecard run`.

---

## 2. MVP definition

Copied from [mvp-scope.md](mvp-scope.md). Do not reinterpret.

### Wedge name

**ML Trust Scorecard CLI** — a command-line tool that runs a five-phase trust audit against declarative contracts and produces a pass/fail scorecard with evidence.

### v0.1 in scope

- CLI: `trustline validate`, `trustline audit`
- Contracts: `FunnelContract`, `CohortManifest` (read-only consumption)
- Scorecard: Five phases; markdown + JSON output
- Executors: DuckDB (local demo), Snowflake (production)
- Integrations: GitHub Actions example, optional Slack webhook
- Artifacts: `examples/acme_stream/`, README quickstart

### v0.1 out of scope

| Item | Target version |
|------|----------------|
| dbt macro (`trustline_funnel`) | v0.2 |
| Airflow operator | v0.3 |
| Standalone source swap detector | v0.2 |
| BigQuery / Postgres adapters | v0.2 |
| Web UI / hosted service | v1.0 |
| Auto-fix or remediation | Never (v0.x) |
| Transfer pack generator | v0.3 |
| Delivery lineage contract (formal kind) | v0.3 |
| Formal `SourceSwapAnnotation` contract kind | v0.2 |
| Python library public API | v0.2 |

### Exit criteria

| # | Criterion | Test / CLI verification |
|---|-----------|---------------------------|
| 1 | ACME demo runs end-to-end in < 5 minutes from clone | Manual quickstart + `tests/e2e/test_acme_audit.py` |
| 2 | All 4 seeded failure modes detected in automated tests | `tests/e2e/test_acme_audit.py::test_four_seeded_failures` |
| 3 | Valid contracts pass `trustline validate` in CI | `tests/unit/contracts/test_validator.py` + CI job |
| 4 | Broken contracts fail `trustline validate` in CI | `tests/fixtures/invalid_contracts/` + CI job |
| 5 | `trustline audit` exits non-zero on failure | `tests/unit/cli/test_audit.py` |
| 6 | Markdown + JSON report generated | `tests/unit/reporters/test_markdown.py`, `test_json_report.py` |
| 7 | README quickstart is copy-paste accurate | README + [getting-started.md](getting-started.md) |

### Seeded failure modes (ACME demo)

| # | Failure | Phase | Expected |
|---|---------|-------|----------|
| 1 | Funnel retention drop | Phase 2 | FAIL |
| 2 | Cohort source mismatch | Phase 4 | FAIL |
| 3 | Source swap volume drift | Phase 3 | WARN |
| 4 | CRM coverage gap | Phase 1 | FAIL |

### Demo scenario (≤5 commands)

```bash
make install-dev
trustline validate --contracts ./examples/acme_stream/contracts/
trustline audit --contracts ./examples/acme_stream/contracts/ --target duckdb
trustline audit --contracts ./examples/acme_stream/contracts/ --target duckdb -o json --output-dir ./reports
cat ./reports/scorecard.md
```

---

## 3. Target architecture for v0.1

Matches [architecture.md](architecture.md). Differs from generic `checks/` / `warehouse/` layout per [ADR-009](adr/009-module-layout.md).

```
src/trustline/
├── __init__.py
├── config.py                    # profiles + env loading
├── exceptions.py
├── cli/
│   ├── __init__.py
│   ├── main.py                  # typer app entrypoint
│   ├── validate.py              # trustline validate
│   └── audit.py                 # trustline audit
├── contracts/
│   ├── __init__.py
│   ├── loader.py                # YAML load + parse
│   ├── validator.py             # JSON Schema validation
│   └── models.py                # Pydantic models
├── compiler/
│   ├── __init__.py
│   ├── funnel.py                # FunnelContract → SQL
│   ├── cohort.py                # CohortManifest → SQL
│   ├── audit_profile.py         # AuditProfile → SQL
│   └── templates.py             # Jinja2 template rendering
├── executors/
│   ├── __init__.py
│   ├── base.py                  # Executor protocol
│   ├── duckdb.py                # DuckDB local executor
│   └── snowflake.py             # Snowflake connector
├── scorecard/
│   ├── __init__.py
│   ├── orchestrator.py          # 5-phase audit runner
│   ├── phase1_pipeline.py
│   ├── phase2_funnel.py
│   ├── phase3_semantics.py
│   ├── phase4_training.py
│   └── phase5_brief.py
├── reporters/
│   ├── __init__.py
│   ├── markdown.py
│   ├── json_report.py
│   └── brief.py
└── integrations/
    ├── __init__.py
    ├── slack.py
    └── github_actions.py        # helper constants; workflow in integrations/
```

Supporting directories:

```
schemas/
├── common.schema.json
├── funnel.schema.json
├── cohort.schema.json
└── audit_profile.schema.json

templates/sql/
├── funnel_stage_count.sql.j2
├── funnel_retention.sql.j2
├── cohort_source_parity.sql.j2
├── score_distribution.sql.j2
├── crm_coverage_gap.sql.j2
└── source_swap_volume.sql.j2

examples/acme_stream/
├── contracts/
├── audit_profile.yaml
├── profiles.yml.example
├── sql/seed_data.sql
└── demo.duckdb
```

### Module specifications

#### `config.py`

| Symbol | Signature / type | I/O | Depends on | Errors |
|--------|------------------|-----|------------|--------|
| `Profile` | `@dataclass`: `target: str`, `database: str`, `schema: str`, `duckdb_path: str \| None` | — | — | — |
| `load_profile` | `(name: str, profiles_path: Path = Path("profiles.yml")) -> Profile` | YAML file → Profile | `pyyaml` | `ValidationError`, `TrustlineError` |

#### `contracts/loader.py`

| Symbol | Signature | I/O | Depends on | Errors |
|--------|-----------|-----|------------|--------|
| `load_contract` | `(path: Path) -> ContractDocument` | YAML file → typed model | `validator`, `models` | `ValidationError`, `FileNotFoundError` |
| `load_contracts_dir` | `(directory: Path) -> list[ContractDocument]` | Directory glob `*.yaml` → list | `load_contract` | `ValidationError`, `FileNotFoundError` |
| `load_audit_profile` | `(path: Path) -> AuditProfile` | YAML → AuditProfile | `validator` | `ValidationError` |

#### `contracts/validator.py`

| Symbol | Signature | I/O | Depends on | Errors |
|--------|-----------|-----|------------|--------|
| `validate_contract` | `(doc: dict, schema_dir: Path) -> list[str]` | dict → error strings | `jsonschema` | — |
| `validate_contract_strict` | `(doc: dict) -> ContractDocument` | dict → model | `models` | `ValidationError` |
| `validate_contracts_dir` | `(directory: Path, *, strict: bool = False) -> ValidationSummary` | dir → summary | `loader` | `ValidationError` |

`ValidationSummary`: `total: int`, `passed: int`, `failed: int`, `results: list[FileValidationResult]`

#### `contracts/models.py` (Pydantic v2)

| Model | Key fields |
|-------|------------|
| `ContractMetadata` | `name`, `product`, `owner`, `labels: dict[str, str]` |
| `JoinSpec` | `table`, `on`, `type: Literal["inner","left"]` |
| `FunnelStage` | `name`, `sql`, `from_stage`, `join`, `expect_min_count`, `expect_retention_pct`, `description` |
| `AlertSpec` | `on`, `threshold_pct`, `notify`, `channel` |
| `FunnelContractSpec` | `stages: list[FunnelStage]`, `alerts: list[AlertSpec]` |
| `FunnelContract` | `api_version`, `kind`, `metadata`, `spec` |
| `DateWindow` | `start`, `end` |
| `LabelSpec` | `definition`, `sql` |
| `CohortSources` | `training`, `scoring` |
| `CohortManifestSpec` | `observation_window`, `outcome_window`, `label`, `sources`, `expected_positive_rate`, `positive_rate_tolerance`, `frozen_at`, `model_ref`, `notes` |
| `CohortManifest` | `api_version`, `kind`, `metadata`, `spec` |
| `AuditProfile` | `crm_coverage`, `source_swap` (see ADR-019) |
| `ContractDocument` | `FunnelContract \| CohortManifest` |

#### `compiler/templates.py`

| Symbol | Signature | Depends on | Errors |
|--------|-----------|------------|--------|
| `render_template` | `(name: str, context: dict, dialect: str) -> str` | Jinja2 | `AuditError` |
| `resolve_ref` | `(expr: str, profile: Profile) -> str` | regex + profile | `ValidationError` |

#### `compiler/funnel.py`, `cohort.py`, `audit_profile.py`

| Symbol | Signature | Output |
|--------|-----------|--------|
| `compile_funnel_checks` | `(contract: FunnelContract, profile: Profile, dialect: str) -> list[CompiledCheck]` | Phase 2 SQL checks |
| `compile_cohort_checks` | `(contract: CohortManifest, profile: Profile, dialect: str) -> list[CompiledCheck]` | Phase 4 SQL checks |
| `compile_audit_profile_checks` | `(doc: AuditProfile, profile: Profile, dialect: str) -> list[CompiledCheck]` | Phase 1 + 3 SQL checks |

`CompiledCheck`: `check_id: str`, `phase: int`, `sql: str`, `expect: CheckExpectation`, `evidence_key: str`

`CheckExpectation`: `kind: Literal["min_count","min_retention_pct","max_drift_pct","min_sync_pct","source_parity"]`, `value: float`, `tolerance: float | None`

#### `executors/base.py`

```python
class Executor(Protocol):
    def execute(self, sql: str) -> list[dict[str, Any]]: ...
    def execute_check(self, check: CompiledCheck) -> CheckResult: ...
```

`CheckResult`: `check_id`, `status: Literal["pass","fail","warn"]`, `actual: float | int | None`, `expected: float | int | None`, `evidence: dict`

#### `executors/duckdb.py`

| Symbol | Signature | Errors |
|--------|-----------|--------|
| `DuckDBExecutor` | `(database: str \| Path = ":memory:")` | `ExecutorError` |

#### `executors/snowflake.py`

| Symbol | Signature | Errors |
|--------|-----------|--------|
| `SnowflakeExecutor.from_env` | `() -> SnowflakeExecutor` | `ExecutorError` |

#### `scorecard/orchestrator.py`

| Symbol | Signature | Output |
|--------|-----------|--------|
| `run_audit` | `(contracts: list[ContractDocument], audit_profile: AuditProfile \| None, executor: Executor, profile: Profile) -> ScorecardResult` | Full scorecard |

`ScorecardResult`: `verdict: Literal["pass","warn","fail"]`, `phases: list[PhaseResult]`, `evidence: dict`, `generated_at: datetime`

`PhaseResult`: `phase_id: int`, `name: str`, `status: Literal["pass","fail","warn","skip"]`, `checks: list[CheckResult]`

#### `reporters/`

| Module | Function | Output |
|--------|----------|--------|
| `markdown.py` | `render_scorecard(result: ScorecardResult) -> str` | Markdown report |
| `json_report.py` | `render_scorecard_json(result: ScorecardResult) -> dict` | JSON-serializable dict |
| `brief.py` | `render_brief(result: ScorecardResult) -> str` | Phase 5 leadership brief |

#### `exceptions.py` (exists)

```
TrustlineError
├── ValidationError      # contract/schema validation failures
├── AuditError           # scorecard execution failures
└── ExecutorError        # warehouse adapter failures
```

---

## 4. Contract spec → code mapping

### FunnelContract

| Spec field | Python model field | Validator | Used by check |
|------------|-------------------|-----------|---------------|
| `apiVersion` | `api_version: Literal["trustline.io/v1"]` | JSON Schema `const` | validate only |
| `kind` | `kind: Literal["FunnelContract"]` | JSON Schema `const` | validate only |
| `metadata.name` | `metadata.name` | pattern `^[a-z][a-z0-9-]{0,62}$` | reporting |
| `metadata.product` | `metadata.product` | `minLength: 1` | reporting |
| `metadata.owner` | `metadata.owner` | `format: email` | reporting |
| `metadata.labels` | `metadata.labels` | optional object | reporting |
| `spec.stages[].name` | `FunnelStage.name` | pattern + unique | phase 2 |
| `spec.stages[].sql` | `FunnelStage.sql` | oneOf (first stage) | `funnel_stage_count.sql.j2` |
| `spec.stages[].from_stage` | `FunnelStage.from_stage` | oneOf (subsequent) | `funnel_retention.sql.j2` |
| `spec.stages[].join.table` | `JoinSpec.table` | required with `from_stage` | retention SQL |
| `spec.stages[].join.on` | `JoinSpec.on` | required | retention SQL |
| `spec.stages[].join.type` | `JoinSpec.type` | enum `inner`/`left` | retention SQL |
| `spec.stages[].expect_min_count` | `FunnelStage.expect_min_count` | int ≥ 0 | phase 2 count |
| `spec.stages[].expect_retention_pct` | `FunnelStage.expect_retention_pct` | 0–100 | phase 2 retention (**failure #1**) |
| `spec.stages[].description` | `FunnelStage.description` | optional | evidence |
| `spec.alerts[].on` | `AlertSpec.on` | enum | v0.1: report only |
| `spec.alerts[].threshold_pct` | `AlertSpec.threshold_pct` | 0–100 | v0.1: report only |
| `spec.alerts[].notify` | `AlertSpec.notify` | enum | deferred to v0.2 |
| `spec.alerts[].channel` | `AlertSpec.channel` | optional | deferred to v0.2 |

### CohortManifest

| Spec field | Python model field | Validator | Used by check |
|------------|-------------------|-----------|---------------|
| `apiVersion` | `api_version` | const | validate only |
| `kind` | `kind: Literal["CohortManifest"]` | const | validate only |
| `metadata.*` | `ContractMetadata` | same as funnel | reporting |
| `spec.observation_window` | `DateWindow` | date format | phase 4 context |
| `spec.outcome_window` | `DateWindow` | date format; semantic: start ≥ obs.end | phase 4 |
| `spec.label.definition` | `LabelSpec.definition` | required | phase 5 brief |
| `spec.label.sql` | `LabelSpec.sql` | optional | phase 4 |
| `spec.sources.training` | `CohortSources.training` | required | `cohort_source_parity.sql.j2` (**failure #2**) |
| `spec.sources.scoring` | `CohortSources.scoring` | required | cohort parity |
| `spec.expected_positive_rate` | `expected_positive_rate` | 0–1 | phase 4 rate check |
| `spec.positive_rate_tolerance` | `positive_rate_tolerance` | 0–1, default 0.02 | phase 4 |
| `spec.frozen_at` | `frozen_at` | date-time | reporting |
| `spec.model_ref` | `model_ref` | optional | phase 5 brief |
| `spec.notes` | `notes` | optional | phase 5 brief |

### AuditProfile (ADR-019; not in contract-spec.md)

| Field | Python model field | Validator | Used by check |
|-------|-------------------|-----------|---------------|
| `crm_coverage.sync_table` | `CrmCoverage.sync_table` | required string | `crm_coverage_gap.sql.j2` (**failure #4**) |
| `crm_coverage.mirror_table` | `CrmCoverage.mirror_table` | required string | phase 1 |
| `crm_coverage.expect_sync_pct` | `CrmCoverage.expect_sync_pct` | 0–100 | phase 1 |
| `source_swap.table` | `SourceSwap.table` | required string | `source_swap_volume.sql.j2` (**failure #3**) |
| `source_swap.migration.from_source` | `Migration.from_source` | required | phase 3 |
| `source_swap.migration.to_source` | `Migration.to_source` | required | phase 3 |
| `source_swap.migration.cutover_date` | `Migration.cutover_date` | date | phase 3 |
| `source_swap.volume_threshold_pct` | `SourceSwap.volume_threshold_pct` | 0–100, default 10 | phase 3 WARN |

**Spec gap:** No amendment to [contract-spec.md](contract-spec.md) required. ADR-019 documents `audit_profile.yaml` as the v0.1 mechanism for Phase 1/3 checks without introducing v0.2/v0.3 contract kinds.

---

## 5. CLI command tree (v0.1)

### `trustline --version` / `-V`

| | |
|-|-|
| **Arguments** | None |
| **Exit 0** | Prints package version from `importlib.metadata` |
| **stdout** | `0.0.1` (or current version) |

### `trustline validate`

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--contracts` / `-c` | path | `./contracts` | Directory of contract YAML files |
| `--file` / `-f` | path | — | Single contract file (mutually exclusive with dir-only mode) |
| `--strict` | bool | false | Treat warnings as errors |

| Exit code | Meaning |
|-----------|---------|
| 0 | All contracts valid |
| 1 | One or more contracts invalid |
| 2 | User error (bad path, missing directory) |
| 3 | Internal error |

**stdout example:**

```
Validating 2 contracts...

  training_positives.yaml              FunnelContract       PASS
  propensity_training_cohort_q2.yaml   CohortManifest       PASS

All contracts valid.
```

**stderr (on failure):**

```
ERROR training_positives.yaml: spec.stages[1].expect_retention_pct: 150 is greater than maximum 100
```

### `trustline audit`

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--contracts` / `-c` | path | `./contracts` | Contract directory |
| `--target` / `-t` | choice | `duckdb` | `duckdb` or `snowflake` |
| `--profile` / `-p` | string | `default` | Profile name in `profiles.yml` |
| `--audit-profile` | path | auto | Path to `audit_profile.yaml` (default: sibling of contracts dir) |
| `--output-dir` | path | `.` | Write `scorecard.md` / `scorecard.json` |
| `-o` / `--output` | choice | `text` | `text`, `json`, or `both` |
| `--dry-run` | bool | false | Compile checks only; do not execute SQL |
| `--notify` | choice | — | `slack` (optional) |
| `--slack-webhook` | string | env | `SLACK_WEBHOOK_URL` fallback |

| Exit code | Meaning |
|-----------|---------|
| 0 | Verdict `pass` or `warn` only |
| 1 | Verdict `fail` (any phase failed) |
| 2 | User error (bad profile, missing contracts) |
| 3 | Internal / executor error |

**stdout example:**

```
Trustline Audit — ACME Stream
Verdict: FAIL (2 failures, 1 warning)

Phase 1 Pipeline Truth .............. FAIL
Phase 2 Population Funnel ........... FAIL
Phase 3 Score Semantics ............. WARN
Phase 4 Training Autopsy ............ FAIL
Phase 5 Leadership Brief ............ PASS

Reports written to ./reports/
```

**JSON snippet (`scorecard.json`):**

```json
{
  "verdict": "fail",
  "generated_at": "2025-07-09T12:00:00Z",
  "phases": [
    {
      "id": 2,
      "name": "Population Funnel",
      "status": "fail",
      "checks": [
        {
          "id": "funnel.retention.app_identity_match",
          "status": "fail",
          "expected_pct": 40.0,
          "actual_pct": 31.25,
          "evidence": {"stage_count": 625, "prior_stage_count": 2000}
        }
      ]
    }
  ]
}
```

---

## 6. Implementation phases

Vertical slices — each ships working, tested, documented increments.

| Phase | Name | Deliverable | Depends on | Est. size |
|-------|------|-------------|------------|-----------|
| 1 | Contract load + validate | Schemas, models, loader, `trustline validate` | — | M |
| 2 | Config + DuckDB executor | `config.py`, `DuckDBExecutor`, profiles | 1 | M |
| 3 | SQL compiler | Jinja2 templates, compilers, snapshot tests | 1, 2 | L |
| 4 | Scorecard phases 1–4 | Phase modules + orchestrator | 3 | L |
| 5 | Reporters + phase 5 brief | Markdown/JSON/brief | 4 | M |
| 6 | `trustline audit` E2E | CLI wired; ACME demo data + `demo.duckdb` | 4, 5 | L |
| 7 | Snowflake executor | Optional integration tests | 6 | M |
| 8 | Integrations + docs polish | GHA workflow, Slack, README | 6 | S |

### Phase 1 — Contract load + validate

**Files to create:**

- `schemas/common.schema.json`, `funnel.schema.json`, `cohort.schema.json`
- `src/trustline/contracts/loader.py`, `validator.py`, `models.py`
- `tests/unit/contracts/test_loader.py`, `test_validator.py`, `test_models.py`
- `tests/fixtures/invalid_contracts/` (missing field, bad threshold, wrong kind)

**Files to modify:**

- `src/trustline/cli/validate.py`
- `pyproject.toml` (add `pydantic>=2`)

**Docs:** `getting-started.md` — validate command works

**Definition of done:**

- [ ] `trustline validate --contracts ./examples/acme_stream/contracts/` passes
- [ ] Invalid fixtures fail with actionable errors
- [ ] `make check` passes
- [ ] Unit tests ≥90% on `contracts/`

**Risk:** JSON Schema `format: email` requires `jsonschema[format-nongpl]` or manual check — verify in TRUST-001.

### Phase 2 — Config + DuckDB executor

**Files to create:**

- `src/trustline/config.py`
- `src/trustline/executors/base.py`, `duckdb.py`
- `examples/acme_stream/profiles.yml.example`
- `tests/unit/config/test_profiles.py`
- `tests/unit/executors/test_duckdb.py`, `test_base.py`

**Files to modify:**

- `pyproject.toml` (add `duckdb>=1.0`)

**Definition of done:**

- [ ] `DuckDBExecutor` runs `SELECT 1` and returns rows
- [ ] `load_profile("default")` reads example profiles
- [ ] `make check` passes

**Risk:** None significant.

### Phase 3 — SQL compiler

**Files to create:**

- `templates/sql/*.sql.j2` (6 templates)
- `src/trustline/compiler/templates.py`, `funnel.py`, `cohort.py`, `audit_profile.py`
- `schemas/audit_profile.schema.json`
- `tests/unit/compiler/test_*.py`
- `tests/fixtures/sql_snapshots/`

**Files to modify:**

- `pyproject.toml` (add `jinja2>=3.1`)

**Definition of done:**

- [ ] Funnel contract compiles to expected SQL (snapshot tests)
- [ ] `ref()` resolves via profile
- [ ] `--dry-run` path testable without warehouse

**Risk:** Dialect differences — use Jinja2 `{% if dialect %}` per architecture.md.

### Phase 4 — Scorecard phases 1–4

**Files to create:**

- `src/trustline/scorecard/orchestrator.py`, `phase1_pipeline.py` … `phase4_training.py`
- `tests/unit/scorecard/test_*.py`

**Definition of done:**

- [ ] Orchestrator runs all 4 SQL phases against in-memory DuckDB
- [ ] Verdict aggregation: FAIL > WARN > PASS
- [ ] Each phase returns evidence dict

**Risk:** Phase logic complexity — keep phases thin; delegate SQL to compiler.

### Phase 5 — Reporters + phase 5 brief

**Files to create:**

- `src/trustline/scorecard/phase5_brief.py`
- `src/trustline/reporters/markdown.py`, `json_report.py`, `brief.py`
- `tests/unit/reporters/test_markdown.py`, `test_json_report.py`
- `tests/unit/scorecard/test_phase5_brief.py`

**Definition of done:**

- [ ] Markdown and JSON render from `ScorecardResult`
- [ ] Phase 5 generates leadership brief (template-only, no SQL)
- [ ] Redacts connection strings from evidence

### Phase 6 — `trustline audit` E2E

**Files to create:**

- `examples/acme_stream/contracts/propensity_training_cohort_q2.yaml`
- `examples/acme_stream/audit_profile.yaml`
- `examples/acme_stream/sql/seed_data.sql`
- `examples/acme_stream/demo.duckdb`
- `tests/e2e/test_acme_audit.py`
- `tests/fixtures/acme_funnel_mock_results.json`

**Files to modify:**

- `src/trustline/cli/audit.py`
- `tests/unit/cli/test_audit.py`
- `README.md`, `getting-started.md`

**Definition of done:**

- [ ] All 4 seeded failures detected
- [ ] `trustline audit` exits 1 on ACME demo
- [ ] Reports written to `--output-dir`
- [ ] E2E completes in < 30s in CI

**Risk:** `demo.duckdb` binary size — must stay < 500KB (pre-commit hook).

### Phase 7 — Snowflake executor

**Files to create:**

- `src/trustline/executors/snowflake.py`
- `tests/integration/test_snowflake_executor.py`

**Files to modify:**

- `pyproject.toml` (optional extra: `snowflake = ["snowflake-connector-python>=3.0"]`)

**Definition of done:**

- [ ] Integration test skipped without `TRUSTLINE_RUN_INTEGRATION=1`
- [ ] `trustline audit --target snowflake` works with creds

**Risk:** CI secrets on fork PRs — keep skipped by default.

### Phase 8 — Integrations + docs polish

**Files to create:**

- `integrations/github-actions/trustline-audit.yml`
- `src/trustline/integrations/slack.py`

**Files to modify:**

- `README.md` quickstart
- `CHANGELOG.md` (v0.1.0 prep)

**Definition of done:**

- [ ] GHA example runs validate + audit with DuckDB
- [ ] `--notify slack` posts on failure when webhook set
- [ ] README quickstart matches actual commands

---

## 7. Testing plan

| Module | Unit tests | Integration tests | Fixtures |
|--------|------------|-------------------|----------|
| `contracts/` | `test_loader`, `test_validator`, `test_models` | — | `tests/fixtures/acme_contracts/`, `invalid_contracts/` |
| `config.py` | `test_profiles` | — | `profiles.yml` snippets |
| `compiler/` | `test_funnel`, `test_cohort`, `test_audit_profile`, `test_templates` | — | `sql_snapshots/` |
| `executors/` | `test_duckdb`, `test_base` | `test_snowflake_executor` | in-memory DuckDB |
| `scorecard/` | `test_orchestrator`, `test_phase1`–`test_phase5` | — | `acme_funnel_mock_results.json` |
| `reporters/` | `test_markdown`, `test_json_report` | — | golden md/json |
| `cli/` | `test_validate`, `test_audit` | — | CliRunner |
| e2e | — | `test_acme_audit` | full `examples/acme_stream/` |

### Requirements

- DuckDB in-memory is the default test executor (no network)
- Snapshot tests for SQL generation (`tests/fixtures/sql_snapshots/`)
- Coverage: ≥85% repo-wide; ≥90% on new v0.1 modules before v0.1.0 tag
- One end-to-end test: ACME contracts → audit → expected fail with 4 seeded modes

### Test files to create

```
tests/unit/contracts/test_loader.py
tests/unit/contracts/test_validator.py
tests/unit/contracts/test_models.py
tests/unit/config/test_profiles.py
tests/unit/compiler/test_funnel.py
tests/unit/compiler/test_cohort.py
tests/unit/compiler/test_audit_profile.py
tests/unit/compiler/test_templates.py
tests/unit/executors/test_duckdb.py
tests/unit/executors/test_base.py
tests/unit/scorecard/test_orchestrator.py
tests/unit/scorecard/test_phase1_pipeline.py
tests/unit/scorecard/test_phase2_funnel.py
tests/unit/scorecard/test_phase3_semantics.py
tests/unit/scorecard/test_phase4_training.py
tests/unit/scorecard/test_phase5_brief.py
tests/unit/reporters/test_markdown.py
tests/unit/reporters/test_json_report.py
tests/unit/cli/test_validate.py
tests/unit/cli/test_audit.py
tests/integration/test_snowflake_executor.py
tests/e2e/test_acme_audit.py
```

Migrate existing `tests/test_cli*.py`, `tests/test_version*.py`, `tests/test_exceptions.py` → `tests/unit/cli/` and `tests/unit/` as modules grow.

---

## 8. Data fixtures (synthetic only)

All fixtures use fictional **ACME Stream** data. No real employer names, schemas, tickets, or metrics.

### `examples/acme_stream/`

| File | Purpose |
|------|---------|
| `contracts/training_positives.yaml` | FunnelContract (exists) |
| `contracts/propensity_training_cohort_q2.yaml` | CohortManifest with source mismatch seeded |
| `audit_profile.yaml` | Phase 1 CRM + Phase 3 source swap config |
| `profiles.yml.example` | DuckDB + Snowflake profile templates |
| `sql/seed_data.sql` | DDL + seed rows for all ACME tables |
| `demo.duckdb` | Committed binary built from seed SQL (< 500KB) |

### `tests/fixtures/`

| File / directory | Purpose |
|------------------|---------|
| `acme_contracts/` | Copy of valid ACME YAML for unit tests |
| `invalid_contracts/missing_metadata.yaml` | Missing required `metadata.owner` |
| `invalid_contracts/bad_retention.yaml` | `expect_retention_pct: 150` |
| `invalid_contracts/wrong_kind.yaml` | `kind: UnknownContract` |
| `sql_snapshots/funnel_stage_count.sql` | Golden SQL for funnel compile |
| `acme_funnel_mock_results.json` | Expected stage counts for assertions |

### Seeded table inventory (DuckDB `main` schema)

| Table | Rows (approx) | Role |
|-------|---------------|------|
| `donor_gifts` | 2000 | Funnel source stage |
| `app_users` | 800 matched | Identity join |
| `watch_events` | 625 users | Feature stage (retention fail) |
| `features_training` | — | Cohort training source |
| `features_scoring` | — | Cohort scoring source (mismatch) |
| `crm_push_queue` | 300000 | CRM sync queue |
| `crm_contacts_mirror` | 80000 | CRM mirror (coverage fail) |
| `user_events_silver` | — | Source swap volume drift |
| `propensity_scores_staging` | — | Score distribution |

No real warehouse DDL in v0.1 beyond DuckDB seed SQL.

---

## 9. Snowflake adapter strategy

| Approach | v0.1? | CI behavior |
|----------|-------|-------------|
| **DuckDB primary** | Yes — demo + all unit/e2e tests | Always run |
| Snowflake optional | Yes — `--target snowflake` | Skip `@pytest.mark.integration` without `TRUSTLINE_RUN_INTEGRATION=1` |
| `--dry-run` (SQL only) | Yes — compile without execute | Snapshot tests always run |
| In-memory DuckDB mock | Yes — unit tests | Always run |

**Primary path for v0.1 demo:** DuckDB with committed `examples/acme_stream/demo.duckdb`.

**Stretch (Phase 7):** Snowflake executor for production audits; integration tests run manually by maintainers with `SNOWFLAKE_*` env vars.

Documented in [ADR-019](adr/019-v01-audit-profile.md).

---

## 10. Documentation updates (implementation-triggered)

| Phase | Doc file | Change |
|-------|----------|--------|
| 1 | `getting-started.md` | `trustline validate` works; remove stub note |
| 1 | `contract-spec.md` | Update "planned" note under Validation Usage when validate ships |
| 3 | `architecture.md` | No structural change; optional note on audit_profile |
| 6 | `getting-started.md` | Full audit quickstart; 5-command demo |
| 6 | `README.md` | Copy-paste quickstart; v0.1 feature list |
| 6 | `CHANGELOG.md` | v0.1.0 release notes |
| 8 | `contributing.md` | Integration test instructions |
| 8 | `docs/index.md` | Link to IMPLEMENTATION_PLAN / MILESTONES if useful |

Do **not** update `docs/internal/` or private planning docs.

---

## 11. CI/CD changes

Planned workflow changes (no implementation in this planning PR):

| Change | When | Detail |
|--------|------|--------|
| Integration marker | Phase 7 | `@pytest.mark.integration` + optional `@pytest.mark.snowflake` |
| Coverage threshold | Phase 4+ | Consider `--cov-fail-under=90` when v0.1 modules dominate |
| `workflow_dispatch` Snowflake job | Phase 7 | Manual maintainer validation with secrets |
| `check-docs` | No change | No new forbidden patterns; grep IMPLEMENTATION_PLAN for client IP |
| PR size | All phases | < 400 lines changed per PR per engineering-foundation |

Existing [ci.yml](../.github/workflows/ci.yml) continues running `make check` on Python 3.11–3.13.

---

## 12. Milestones and tracking

GitHub-issue-ready tasks are in [MILESTONES.md](MILESTONES.md) (`TRUST-001` … `TRUST-022`).

Each task includes phase, files, acceptance criteria, and dependencies. Do not create GitHub issues automatically from this document.

---

## 13. Out of scope guardrails

Engineers must **not** build during v0.1:

- dbt macro (`trustline_funnel`)
- GitHub Action PR comments (v0.2) — example workflow only in v0.1
- PyPI publish automation (release.yml stays stub until v0.1.0 tag)
- Web UI / hosted service
- Multi-warehouse beyond Snowflake/DuckDB
- BigQuery / Postgres adapters
- Airflow `TrustlineAuditOperator`
- Standalone source swap detector
- Formal `DeliveryLineageContract` / `SourceSwapAnnotation` contract kinds
- Auto-fix or remediation
- Transfer pack generator
- Python library public API (`from trustline import audit`)
- Contract-level alert dispatch (Slack notify on audit failure only in v0.1)
- `DeliveryLineageContract` in `trustline validate`

Defer all above to [roadmap.md](roadmap.md) with explicit version labels.

---

## 14. Implementation sequence (day-by-day sketch)

Not a commitment — ordering guide for a solo developer assuming foundation stays green.

| Day | Focus | Output |
|-----|-------|--------|
| 1 | Phase 1: JSON schemas + Pydantic models | `schemas/`, `contracts/models.py` |
| 2 | Phase 1: loader, validator, `trustline validate` CLI | TRUST-001–005 complete |
| 3 | Phase 2: config + DuckDB executor | Profiles load; SQL executes |
| 4 | Phase 3: Jinja2 templates + funnel compiler | Snapshot tests green |
| 5 | Phase 3: cohort + audit_profile compilers | All SQL templates covered |
| 6 | Phase 4: scorecard phase 1–2 | CRM + funnel checks run |
| 7 | Phase 4: scorecard phase 3–4 + orchestrator | Verdict aggregation works |
| 8 | Phase 5: reporters + phase 5 brief | md/json output |
| 9 | Phase 6: ACME seed data + `demo.duckdb` | Seeded failures in data |
| 10 | Phase 6: `trustline audit` CLI + e2e test | 4 failures detected |
| 11 | Phase 7: Snowflake executor (stretch) | Integration test (skipped in CI) |
| 12 | Phase 8: GHA example + Slack + README | Quickstart accurate |
| 13–15 | Buffer: coverage polish, v0.1.0 version bump | Release candidate |

---

## 15. Open questions

**None — proceed.**

ADR-019 (`audit_profile.yaml`) resolves the Phase 1/3 contract-kind conflict. DuckDB-primary strategy is accepted per [ADR-001](adr/001-snowflake-first.md) and ADR-019.

---

## Related documents

| Document | Description |
|----------|-------------|
| [MILESTONES.md](MILESTONES.md) | TRUST-001 … TRUST-022 task list |
| [ADR-019](adr/019-v01-audit-profile.md) | Audit profile + DuckDB-first strategy |
| [mvp-scope.md](mvp-scope.md) | Authoritative v0.1 scope |
| [architecture.md](architecture.md) | Technical architecture |
| [contract-spec.md](contract-spec.md) | Contract YAML API |
| [engineering-foundation.md](engineering-foundation.md) | Quality gates and conventions |
