"""Tests for funnel SQL compilation."""

from pathlib import Path

from trustline.compiler.funnel import compile_funnel_checks
from trustline.config import Profile
from trustline.contracts.loader import load_contract

SNAPSHOT_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "sql_snapshots"


def test_compile_funnel_checks_emits_count_and_retention(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """ACME funnel should compile one count and two retention checks."""
    contract = load_contract(acme_contracts_dir / "training_positives.yaml")
    checks = compile_funnel_checks(contract, duckdb_profile, "duckdb")
    assert len(checks) == 3
    kinds = {check.expect.kind for check in checks}
    assert kinds == {"min_count", "min_retention_pct"}


def test_compile_funnel_source_donors_snapshot(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Golden SQL snapshot for the first funnel stage count check."""
    contract = load_contract(acme_contracts_dir / "training_positives.yaml")
    checks = compile_funnel_checks(contract, duckdb_profile, "duckdb")
    source_check = next(check for check in checks if check.check_id.endswith("source_donors"))
    snapshot_path = SNAPSHOT_DIR / "acme_funnel_source_donors_count.sql"
    expected = snapshot_path.read_text(encoding="utf-8").strip()
    assert source_check.sql.strip() == expected
    assert source_check.phase == 2
    assert source_check.expect.value == 2000


def test_compile_funnel_resolves_table_refs(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Compiled SQL should contain qualified table names."""
    contract = load_contract(acme_contracts_dir / "training_positives.yaml")
    checks = compile_funnel_checks(contract, duckdb_profile, "duckdb")
    combined_sql = "\n".join(check.sql for check in checks)
    assert "main.donor_gifts" in combined_sql
    assert "main.app_users" in combined_sql
    assert "main.watch_events" in combined_sql
