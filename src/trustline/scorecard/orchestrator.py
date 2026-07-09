"""Five-phase scorecard orchestrator."""

from __future__ import annotations

from typing import Any

from trustline.config import Profile
from trustline.contracts.audit_profile import AuditProfile
from trustline.contracts.models import CohortManifest, FunnelContract
from trustline.executors.base import Executor
from trustline.scorecard._common import aggregate_verdict
from trustline.scorecard.phase1_pipeline import run_phase1_pipeline
from trustline.scorecard.phase2_funnel import run_phase2_funnel
from trustline.scorecard.phase3_semantics import run_phase3_semantics
from trustline.scorecard.phase4_training import run_phase4_training
from trustline.scorecard.phase5_brief import run_phase5_brief
from trustline.scorecard.types import PhaseResult, ScorecardResult


def run_audit(
    contracts: list[FunnelContract | CohortManifest],
    audit_profile: AuditProfile | None,
    executor: Executor,
    profile: Profile,
) -> ScorecardResult:
    """Run phases 1–4 and aggregate pass/fail/warn verdict."""
    funnel_contracts = [contract for contract in contracts if isinstance(contract, FunnelContract)]
    cohort_contracts = [contract for contract in contracts if isinstance(contract, CohortManifest)]

    phase1 = run_phase1_pipeline(audit_profile, executor, profile)
    phase2 = run_phase2_funnel(funnel_contracts, executor, profile)
    phase3 = run_phase3_semantics(audit_profile, executor, profile)
    phase4 = run_phase4_training(cohort_contracts, executor, profile)

    phases = (phase1, phase2, phase3, phase4)
    evidence: dict[str, Any] = {
        phase.name: {
            "status": phase.status,
            "checks": [
                {
                    "check_id": check.check_id,
                    "status": check.status,
                    "actual": check.actual,
                    "expected": check.expected,
                }
                for check in phase.checks
            ],
        }
        for phase in phases
    }

    return ScorecardResult(
        verdict=aggregate_verdict([phase.status for phase in phases]),
        phases=phases,
        evidence=evidence,
    )


def _phase_evidence(phases: tuple[PhaseResult, ...]) -> dict[str, Any]:
    return {
        phase.name: {
            "status": phase.status,
            "checks": [
                {
                    "check_id": check.check_id,
                    "status": check.status,
                    "actual": check.actual,
                    "expected": check.expected,
                }
                for check in phase.checks
            ],
        }
        for phase in phases
    }


def run_full_audit(
    contracts: list[FunnelContract | CohortManifest],
    audit_profile: AuditProfile | None,
    executor: Executor,
    profile: Profile,
) -> ScorecardResult:
    """Run phases 1–5 and return the complete scorecard."""
    result = run_audit(contracts, audit_profile, executor, profile)
    phase5 = run_phase5_brief(result.phases)
    phases = (*result.phases, phase5)
    return ScorecardResult(
        verdict=result.verdict,
        phases=phases,
        evidence=_phase_evidence(phases),
        generated_at=result.generated_at,
    )
