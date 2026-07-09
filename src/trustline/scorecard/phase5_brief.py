"""Phase 5 leadership brief (template-only, no SQL)."""

from __future__ import annotations

from trustline.executors.base import CheckResult
from trustline.scorecard.types import PHASE_NAMES, PhaseResult

_RISK_CATALOG: tuple[tuple[str, str, str], ...] = (
    (
        "audit.crm_coverage",
        "CRM mirror sync gap threatens downstream identity joins",
        "Review CRM ETL sync lag and reconcile mirror table coverage",
    ),
    (
        "funnel.retention.",
        "Population funnel retention dropped below contract thresholds",
        "Investigate stage-to-stage join coverage and upstream data freshness",
    ),
    (
        "funnel.count.",
        "Funnel stage counts fell below minimum contract thresholds",
        "Validate source table freshness and stage SQL definitions",
    ),
    (
        "audit.source_swap_volume",
        "Source migration shows elevated post-cutover volume drift",
        "Compare Legacy vs New player event volumes and confirm cutover timing",
    ),
    (
        "audit.score_distribution",
        "Score distribution check returned insufficient data",
        "Verify propensity score staging table population and scoring pipeline",
    ),
    (
        "cohort.source_parity",
        "Training and scoring feature sources are not aligned",
        "Reconcile features_training vs features_scoring table lineage before retrain",
    ),
    (
        "cohort.positive_rate",
        "Observed positive rate diverged from frozen cohort expectation",
        "Audit label SQL and outcome window against the approved cohort manifest",
    ),
)


def _matches_prefix(check_id: str, prefix: str) -> bool:
    """Return True when a check id belongs to a catalog prefix."""
    normalized = prefix.rstrip(".")
    return check_id == normalized or check_id.startswith(f"{normalized}.")


def _match_catalog_entry(check_id: str) -> tuple[str, str, str] | None:
    for prefix, risk, action in _RISK_CATALOG:
        if _matches_prefix(check_id, prefix):
            return prefix, risk, action
    return None


def _extract_risks_and_actions(
    prior_phases: tuple[PhaseResult, ...],
) -> tuple[list[dict[str, str]], list[str]]:
    """Collect top risks and recommended actions from failed or warned checks."""
    risks: list[dict[str, str]] = []
    actions: list[str] = []
    seen_actions: set[str] = set()

    for phase in prior_phases:
        if phase.status == "skip":
            continue
        for check in phase.checks:
            if check.status not in {"fail", "warn"}:
                continue
            entry = _match_catalog_entry(check.check_id)
            if entry is None:
                risk = f"{check.check_id} reported {check.status}"
                action = f"Investigate failing check {check.check_id}"
            else:
                _, risk, action = entry
            risks.append(
                {
                    "phase": phase.name,
                    "check_id": check.check_id,
                    "status": check.status,
                    "risk": risk,
                }
            )
            if action not in seen_actions:
                seen_actions.add(action)
                actions.append(action)

    return risks, actions


def run_phase5_brief(prior_phases: tuple[PhaseResult, ...]) -> PhaseResult:
    """Aggregate prior phase outcomes into a leadership brief."""
    risks, actions = _extract_risks_and_actions(prior_phases)
    check = CheckResult(
        check_id="brief.leadership_summary",
        status="pass",
        actual=len(risks),
        expected=0,
        evidence={"risks": risks, "actions": actions},
    )
    return PhaseResult(
        phase_id=5,
        name=PHASE_NAMES[5],
        status="pass",
        checks=(check,),
    )
