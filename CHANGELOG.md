# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-07-10

### Added

- `trustline audit --demo` — run bundled ACME Stream fixture without path flags
- `trustline init --preset` — scaffold `./trustline/` from bundled templates
- `trustline init --list-presets` — list bundled template presets
- Contract template presets: `ml-crm-boundary`, `funnel-retention`, `cohort-source-parity`
- Actionable CLI error hints for common audit failures
- ADR-022 trustline init workspace layout
- [ACME demo](docs/acme-demo.md), [use cases](docs/use-cases.md), and quick-start path in getting-started
- Pattern ↔ template ↔ check matrix in [docs/patterns/README.md](docs/patterns/README.md)
- Root [CONTRIBUTING.md](CONTRIBUTING.md) pointer and `make pre-commit` target
- dbt CI validate example ([examples/dbt-ci/](examples/dbt-ci/))
- GitHub Actions consumer workflow for `./trustline/` contracts
- Snowflake profile stub in init output and getting-started env var table

### Changed

- README quickstart: `trustline audit --demo` replaces Python one-liner; adds when-to-use table
- Roadmap reprioritized: v0.2 focuses on contract authoring (BigQuery/dbt macro deferred to v0.3)

## [0.1.1] - 2026-07-10

### Added

- Boundary pattern catalog (`docs/patterns/`) — five cross-seam failure modes with ACME examples
- Stability policy (`docs/STABILITY.md`) for `trustline.io/v1` contracts and CLI semver
- ADR-021 contract diff governance (design only)
- `trustline.examples.acme_stream_dir()` — path to bundled ACME Stream fixture in the wheel
- Consumer GitHub Actions example (`examples/github-actions/trustline-audit/`)

### Changed

- ACME Stream fixture bundled in PyPI wheel (~270KB `demo.duckdb`)
- README: north star one-liner, PyPI badge, pip-only quickstart
- Contributor documentation section in `contributing.md`

## [0.1.0] - 2026-07-09

### Added

- Five-phase trust scorecard (`trustline audit`) with DuckDB and optional Snowflake execution
- Contract validation CLI (`trustline validate`) against JSON Schema
- Identity funnel, cohort manifest, and audit profile compilers
- Rich terminal scorecard output with `--no-color` support
- Markdown, JSON, and brief reporters for scorecard output
- ACME Stream demo dataset with seeded cross-boundary failures
- Profiles DuckDB path fallback for the bundled example fixture
- Slack failure notifications (`--notify slack`, `SLACK_WEBHOOK_URL`)
- Example GitHub Actions workflow (`integrations/github-actions/trustline-audit.yml`)

### Changed

- README and getting-started quickstart: `pip install trustline` for users, clone path for contributors

## [0.0.1] - 2026-07-09

### Added

- Initial repository scaffold (pre-MVP)

[Unreleased]: https://github.com/omarfarooq908/trustline/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/omarfarooq908/trustline/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/omarfarooq908/trustline/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/omarfarooq908/trustline/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/omarfarooq908/trustline/releases/tag/v0.0.1
