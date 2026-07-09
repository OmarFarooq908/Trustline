"""Tests for contract Pydantic models."""

from datetime import date, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from trustline.contracts.models import CohortManifest, FunnelContract


def test_funnel_contract_parses_acme_example(acme_contracts_dir: Path) -> None:
    """ACME funnel fixture should parse with aliases."""
    from trustline.contracts.loader import load_contract_raw

    path = acme_contracts_dir / "training_positives.yaml"
    data = load_contract_raw(path)
    contract = FunnelContract.model_validate(data)
    assert contract.api_version == "trustline.io/v1"
    assert contract.kind == "FunnelContract"
    assert contract.metadata.name == "training_positives"
    assert len(contract.spec.stages) == 3


def test_funnel_stage_names_must_be_unique() -> None:
    """Duplicate stage names should fail semantic validation."""
    payload = {
        "apiVersion": "trustline.io/v1",
        "kind": "FunnelContract",
        "metadata": {
            "name": "dup-stages",
            "product": "acme",
            "owner": "team@acme-stream.example",
        },
        "spec": {
            "stages": [
                {
                    "name": "source_donors",
                    "sql": "SELECT 1",
                    "expect_min_count": 1,
                },
                {
                    "name": "source_donors",
                    "from_stage": "source_donors",
                    "join": {"table": "t", "on": "id"},
                    "expect_retention_pct": 50,
                },
            ]
        },
    }
    with pytest.raises(ValidationError, match="unique"):
        FunnelContract.model_validate(payload)


def test_cohort_outcome_window_must_follow_observation() -> None:
    """Outcome window cannot start before observation window ends."""
    payload = {
        "apiVersion": "trustline.io/v1",
        "kind": "CohortManifest",
        "metadata": {
            "name": "bad-windows",
            "product": "acme",
            "owner": "team@acme-stream.example",
        },
        "spec": {
            "observation_window": {"start": "2025-01-01", "end": "2025-03-31"},
            "outcome_window": {"start": "2025-03-01", "end": "2025-04-30"},
            "label": {"definition": "test"},
            "sources": {"training": "t", "scoring": "s"},
            "expected_positive_rate": 0.1,
            "frozen_at": "2025-05-01T00:00:00Z",
        },
    }
    with pytest.raises(ValidationError, match="outcome_window"):
        CohortManifest.model_validate(payload)


def test_cohort_manifest_parses_valid_windows() -> None:
    """Valid cohort windows should parse."""
    contract = CohortManifest.model_validate(
        {
            "apiVersion": "trustline.io/v1",
            "kind": "CohortManifest",
            "metadata": {
                "name": "cohort",
                "product": "acme",
                "owner": "team@acme-stream.example",
            },
            "spec": {
                "observation_window": {
                    "start": date(2025, 1, 1),
                    "end": date(2025, 3, 31),
                },
                "outcome_window": {
                    "start": date(2025, 4, 1),
                    "end": date(2025, 4, 30),
                },
                "label": {"definition": "subscribed"},
                "sources": {"training": "train", "scoring": "score"},
                "expected_positive_rate": 0.12,
                "frozen_at": datetime(2025, 5, 1),
            },
        }
    )
    assert contract.spec.expected_positive_rate == 0.12
