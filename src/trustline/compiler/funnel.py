"""Compile FunnelContract documents into SQL checks."""

from __future__ import annotations

from trustline.compiler.templates import render_template, resolve_refs
from trustline.config import Profile
from trustline.contracts.models import FunnelContract, FunnelStage
from trustline.exceptions import AuditError
from trustline.executors.base import CheckExpectation, CompiledCheck


def _stage_subquery(
    stage: FunnelStage,
    stage_queries: dict[str, str],
    profile: Profile,
    dialect: str,
) -> str:
    """Build the SQL subquery that materializes a funnel stage."""
    if stage.sql is not None:
        return resolve_refs(stage.sql, profile)

    if stage.from_stage is None or stage.join is None:
        msg = f"stage {stage.name!r} is missing sql or join configuration"
        raise AuditError(msg)

    return render_template(
        "funnel_stage_join.sql.j2",
        {
            "prior_stage_sql": stage_queries[stage.from_stage],
            "join_table": resolve_refs(stage.join.table, profile),
            "join_type": stage.join.type.upper(),
            "join_on": stage.join.on,
        },
        dialect,
    )


def _build_stage_queries(
    contract: FunnelContract, profile: Profile, dialect: str
) -> dict[str, str]:
    """Compile all stage subqueries in funnel order."""
    queries: dict[str, str] = {}
    for stage in contract.spec.stages:
        queries[stage.name] = _stage_subquery(stage, queries, profile, dialect)
    return queries


def compile_funnel_checks(
    contract: FunnelContract,
    profile: Profile,
    dialect: str,
) -> list[CompiledCheck]:
    """Compile funnel stage count and retention checks."""
    checks: list[CompiledCheck] = []
    stage_queries = _build_stage_queries(contract, profile, dialect)

    for index, stage in enumerate(contract.spec.stages):
        stage_sql = stage_queries[stage.name]
        contract_name = contract.metadata.name

        if stage.expect_min_count is not None:
            sql = render_template(
                "funnel_stage_count.sql.j2",
                {"stage_sql": stage_sql, "stage_name": stage.name},
                dialect,
            )
            checks.append(
                CompiledCheck(
                    check_id=f"funnel.count.{contract_name}.{stage.name}",
                    phase=2,
                    sql=sql,
                    expect=CheckExpectation(kind="min_count", value=float(stage.expect_min_count)),
                    evidence_key=stage.name,
                )
            )

        if stage.expect_retention_pct is not None and index > 0:
            prior_stage = contract.spec.stages[index - 1]
            sql = render_template(
                "funnel_retention.sql.j2",
                {
                    "stage_sql": stage_sql,
                    "prior_stage_sql": stage_queries[prior_stage.name],
                },
                dialect,
            )
            checks.append(
                CompiledCheck(
                    check_id=f"funnel.retention.{contract_name}.{stage.name}",
                    phase=2,
                    sql=sql,
                    expect=CheckExpectation(
                        kind="min_retention_pct",
                        value=float(stage.expect_retention_pct),
                    ),
                    evidence_key=stage.name,
                )
            )

    return checks
