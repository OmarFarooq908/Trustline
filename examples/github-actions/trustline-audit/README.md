# Trustline audit in GitHub Actions (consumer)

Copy this example into your repository's `.github/workflows/` directory. It validates your `./trustline/` contracts and smoke-tests the bundled demo.

## Setup

1. Scaffold contracts in your repo:

   ```bash
   trustline init --preset ml-crm-boundary --non-interactive
   git add trustline/
   ```

2. Copy `workflow.yml` to `.github/workflows/trustline-audit.yml`.

## What the workflow does

| Job | Step | Purpose |
|-----|------|---------|
| `validate` | `trustline validate` | Schema-check contract YAML on every PR |
| `audit` | `trustline audit --demo` | Smoke-test PyPI install (exit `1` expected) |
| `audit` | `trustline audit --dry-run` | Compile SQL for your contracts without a warehouse |

## Production audit against your warehouse

Add a job with warehouse credentials and fail on non-zero exit:

```yaml
- name: Run trust audit
  run: |
    trustline audit \
      --contracts ./trustline/contracts \
      --profiles ./trustline/profiles.yml
```

Use `pip install 'trustline[snowflake]'` and `SNOWFLAKE_*` secrets for Snowflake targets.

## dbt projects

See [examples/dbt-ci/](../../dbt-ci/README.md) for validate-only CI without warehouse access.

## Monorepo development

If you develop Trustline itself, use `uv sync` instead — see `.github/workflows/trustline-audit.yml` in the Trustline repository.
