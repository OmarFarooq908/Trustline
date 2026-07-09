"""Tests for cohort SQL compilation."""

from pathlib import Path

from trustline.compiler.cohort import compile_cohort_checks
from trustline.config import Profile
from trustline.contracts.loader import load_contract

SNAPSHOT_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "sql_snapshots"


def test_compile_cohort_checks_emits_parity_and_positive_rate(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """ACME cohort should compile source parity and positive rate checks."""
    contract = load_contract(acme_contracts_dir / "propensity_training_cohort_q2.yaml")
    checks = compile_cohort_checks(contract, duckdb_profile, "duckdb")
    assert len(checks) == 2
    assert {check.expect.kind for check in checks} == {"source_parity", "positive_rate"}


def test_compile_cohort_source_parity_snapshot(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Golden SQL snapshot for cohort source parity."""
    contract = load_contract(acme_contracts_dir / "propensity_training_cohort_q2.yaml")
    checks = compile_cohort_checks(contract, duckdb_profile, "duckdb")
    parity = next(check for check in checks if "source_parity" in check.check_id)
    expected = (SNAPSHOT_DIR / "acme_cohort_source_parity.sql").read_text(encoding="utf-8").strip()
    assert parity.sql.strip() == expected


def test_compile_cohort_positive_rate_uses_label_sql(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Positive rate SQL should reference the training table and label expression."""
    contract = load_contract(acme_contracts_dir / "propensity_training_cohort_q2.yaml")
    checks = compile_cohort_checks(contract, duckdb_profile, "duckdb")
    rate_check = next(check for check in checks if "positive_rate" in check.check_id)
    assert "main.features_training" in rate_check.sql
    assert "subscription_date" in rate_check.sql
    assert rate_check.expect.tolerance == 0.02
