# Trustline audit in GitHub Actions (consumer)

Copy this example into your repository's `.github/workflows/` directory. It installs Trustline from PyPI and runs validate + audit against the bundled ACME Stream fixture.

## Setup

1. Copy `workflow.yml` to `.github/workflows/trustline-audit.yml`.
2. Adjust `contracts` and `profiles` paths to your own contracts when ready.

## Demo behavior

The bundled ACME fixture **intentionally fails** audit (exit code `1`). This workflow treats exit `1` as success for the demo — it proves Trustline detected seeded failures.

For production contracts, fail the job when `trustline audit` exits non-zero:

```yaml
- name: Run trust audit
  run: |
    trustline audit \
      --contracts ./contracts/ \
      --target duckdb \
      --profiles ./profiles.yml
```

## Production notes

- Use `pip install 'trustline[snowflake]'` for Snowflake targets.
- Store `SNOWFLAKE_*` credentials as GitHub Actions secrets.
- Run `trustline validate` on every PR; run full audit on merge or schedule.

## Monorepo development

If you develop Trustline itself, use `uv sync` instead — see `.github/workflows/trustline-audit.yml` in the Trustline repository.
