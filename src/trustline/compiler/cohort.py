"""Compile CohortManifest documents into SQL checks."""

from __future__ import annotations

from trustline.compiler.templates import render_template, resolve_refs
from trustline.config import Profile
from trustline.contracts.models import CohortManifest
from trustline.executors.base import CheckExpectation, CompiledCheck


def compile_cohort_checks(
    contract: CohortManifest,
    profile: Profile,
    dialect: str,
) -> list[CompiledCheck]:
    """Compile cohort source parity and positive rate checks."""
    training_table = resolve_refs(contract.spec.sources.training, profile)
    scoring_table = resolve_refs(contract.spec.sources.scoring, profile)
    contract_name = contract.metadata.name

    source_parity_sql = render_template(
        "cohort_source_parity.sql.j2",
        {
            "training_table": training_table,
            "scoring_table": scoring_table,
        },
        dialect,
    )

    label_sql = contract.spec.label.sql or "1"
    positive_rate_sql = render_template(
        "cohort_positive_rate.sql.j2",
        {
            "label_sql": label_sql,
            "training_table": training_table,
        },
        dialect,
    )

    return [
        CompiledCheck(
            check_id=f"cohort.source_parity.{contract_name}",
            phase=4,
            sql=source_parity_sql,
            expect=CheckExpectation(kind="source_parity", value=1.0),
            evidence_key="sources",
        ),
        CompiledCheck(
            check_id=f"cohort.positive_rate.{contract_name}",
            phase=4,
            sql=positive_rate_sql,
            expect=CheckExpectation(
                kind="positive_rate",
                value=contract.spec.expected_positive_rate,
                tolerance=contract.spec.positive_rate_tolerance,
            ),
            evidence_key="positive_rate",
        ),
    ]
