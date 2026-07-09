"""Tests for SQL template rendering and ref() resolution."""

from trustline.compiler.templates import qualify_table, render_template, resolve_refs
from trustline.config import Profile


def test_qualify_table_uses_profile_namespace() -> None:
    """Table refs should include database and schema from the profile."""
    profile = Profile(name="default", target="duckdb", database="main", schema="main")
    assert qualify_table("donor_gifts", profile) == "main.donor_gifts"


def test_resolve_refs_replaces_dbt_style_refs(duckdb_profile: Profile) -> None:
    """resolve_refs should replace ref() expressions in SQL strings."""
    resolved = resolve_refs("SELECT * FROM {{ ref('donor_gifts') }}", duckdb_profile)
    assert resolved == "SELECT * FROM main.donor_gifts"


def test_render_template_duckdb_dialect() -> None:
    """Templates should render dialect-specific SQL for DuckDB."""
    sql = render_template(
        "score_distribution.sql.j2",
        {"table_ref": "main.propensity_scores_staging"},
        "duckdb",
    )
    assert "INTERVAL 7 DAY" in sql
    assert "DATEADD" not in sql


def test_render_template_snowflake_dialect() -> None:
    """Templates should render dialect-specific SQL for Snowflake."""
    sql = render_template(
        "score_distribution.sql.j2",
        {"table_ref": "ANALYTICS.ML_STAGING.propensity_scores_staging"},
        "snowflake",
    )
    assert "DATEADD(day, -7, CURRENT_TIMESTAMP())" in sql


def test_render_template_funnel_stage_count() -> None:
    """Funnel stage count template should wrap stage SQL."""
    sql = render_template(
        "funnel_stage_count.sql.j2",
        {"stage_sql": "SELECT 1 AS donor_id", "stage_name": "source_donors"},
        "duckdb",
    )
    assert "SELECT COUNT(*) AS actual_count" in sql
    assert "source_donors" in sql
