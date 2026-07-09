# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/omarfarooq908/trustline/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/omarfarooq908/trustline/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/omarfarooq908/trustline/releases/tag/v0.0.1
