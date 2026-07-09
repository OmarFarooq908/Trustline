# Code Review Checklist

Use this checklist when reviewing pull requests. Not every item applies to every PR (e.g., docs-only changes may skip test items).

## Functionality

- [ ] Change matches the linked issue or PR description
- [ ] Edge cases are handled (empty input, invalid contracts, missing files)
- [ ] No scope creep beyond stated PR goal

## Tests

- [ ] New behavior has unit tests
- [ ] Tests use ACME Stream fixtures
- [ ] `make check` passes locally
- [ ] Integration tests marked with `@pytest.mark.integration` if applicable

## Code quality

- [ ] Ruff lint and format pass
- [ ] mypy passes on `src/trustline/`
- [ ] Public functions have Google-style docstrings
- [ ] No `print()` in library code — use `logging`
- [ ] Exceptions use `TrustlineError` hierarchy

## Security

- [ ] No secrets, credentials, or `.env` values in diff
- [ ] Examples and fixtures use ACME Stream scenarios
- [ ] User-controlled input is not executed unsafely

## Documentation

- [ ] README or docs updated if behavior changes
- [ ] CHANGELOG updated under `[Unreleased]` for user-visible changes
- [ ] ADR added to `docs/adr/` for significant architectural choices

## Dependencies

- [ ] New dependencies justified in PR description or ADR
- [ ] `uv.lock` updated if dependencies changed

## PR hygiene

- [ ] Conventional Commit message format
- [ ] DCO sign-off present (`Signed-off-by`)
- [ ] PR size reasonable (< 400 lines preferred)
- [ ] Breaking changes called out explicitly
