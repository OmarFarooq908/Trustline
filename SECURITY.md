# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.0.x   | :white_check_mark: |
| < 0.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub Issues.**

Use [GitHub private vulnerability reporting](https://github.com/omarfarooq908/trustline/security/advisories/new) on this repository.

Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You should receive a response within 72 hours. If the report is accepted, we will:

1. Confirm the issue and assign severity
2. Develop and test a fix
3. Release a patch version
4. Credit the reporter in CHANGELOG (unless you prefer anonymity)

## Security practices

- Warehouse credentials via environment variables only — never in contract YAML
- `profiles.yml` and `.env` are gitignored
- Dependency audits run weekly via `security.yml` (pip-audit, bandit)
- Fork PR workflows do not receive repository secrets

## Scope

In scope:

- Trustline CLI and library code
- Contract parsing and SQL generation
- Credential handling in warehouse adapters

Out of scope:

- Vulnerabilities in third-party warehouses (Snowflake, DuckDB)
- User misconfiguration of warehouse permissions
