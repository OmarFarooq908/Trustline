"""Compile audit profile documents into SQL checks."""

from __future__ import annotations

from trustline.compiler.templates import render_template, resolve_refs
from trustline.config import Profile
from trustline.contracts.audit_profile import AuditProfile
from trustline.executors.base import CheckExpectation, CompiledCheck


def compile_audit_profile_checks(
    profile_doc: AuditProfile,
    profile: Profile,
    dialect: str,
) -> list[CompiledCheck]:
    """Compile Phase 1 and Phase 3 checks from an audit profile."""
    checks: list[CompiledCheck] = []

    sync_table = resolve_refs(profile_doc.crm_coverage.sync_table, profile)
    mirror_table = resolve_refs(profile_doc.crm_coverage.mirror_table, profile)
    checks.append(
        CompiledCheck(
            check_id="audit.crm_coverage",
            phase=1,
            sql=render_template(
                "crm_coverage_gap.sql.j2",
                {"sync_table": sync_table, "mirror_table": mirror_table},
                dialect,
            ),
            expect=CheckExpectation(
                kind="min_sync_pct",
                value=profile_doc.crm_coverage.expect_sync_pct,
            ),
            evidence_key="crm_coverage",
        )
    )

    swap_table = resolve_refs(profile_doc.source_swap.table, profile)
    migration = profile_doc.source_swap.migration
    checks.append(
        CompiledCheck(
            check_id="audit.source_swap_volume",
            phase=3,
            sql=render_template(
                "source_swap_volume.sql.j2",
                {
                    "table_ref": swap_table,
                    "from_source": migration.from_source,
                    "to_source": migration.to_source,
                    "cutover_date": migration.cutover_date.isoformat(),
                },
                dialect,
            ),
            expect=CheckExpectation(
                kind="max_drift_pct",
                value=profile_doc.source_swap.volume_threshold_pct,
                tolerance=2.0,
            ),
            evidence_key="source_swap",
        )
    )

    if profile_doc.score_distribution is not None:
        table_ref = resolve_refs(profile_doc.score_distribution.table, profile)
        checks.append(
            CompiledCheck(
                check_id="audit.score_distribution",
                phase=3,
                sql=render_template(
                    "score_distribution.sql.j2",
                    {"table_ref": table_ref},
                    dialect,
                ),
                expect=CheckExpectation(kind="min_count", value=1.0),
                evidence_key="score_distribution",
            )
        )

    return checks
