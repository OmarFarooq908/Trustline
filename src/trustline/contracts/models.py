"""Pydantic models for Trustline contract documents."""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

JoinType = Literal["inner", "left"]
AlertOn = Literal["retention_drop", "count_below_min", "stage_empty"]
NotifyChannel = Literal["slack", "email", "pagerduty"]


class ContractMetadata(BaseModel):
    """Shared contract metadata envelope."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    name: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,62}$")
    product: str = Field(min_length=1)
    owner: EmailStr
    labels: dict[str, str] = Field(default_factory=dict)


class JoinSpec(BaseModel):
    """Join specification for a funnel stage."""

    model_config = ConfigDict(extra="forbid")

    table: str
    on: str
    type: JoinType = "inner"


class FunnelStage(BaseModel):
    """Single stage in an identity funnel contract."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(pattern=r"^[a-z][a-z0-9_]{0,62}$")
    sql: str | None = None
    from_stage: str | None = None
    join: JoinSpec | None = None
    expect_min_count: int | None = Field(default=None, ge=0)
    expect_retention_pct: float | None = Field(default=None, ge=0, le=100)
    description: str | None = None


class AlertSpec(BaseModel):
    """Alert rule attached to a funnel contract."""

    model_config = ConfigDict(extra="forbid")

    on: AlertOn
    threshold_pct: float = Field(ge=0, le=100)
    notify: NotifyChannel
    channel: str | None = None


class FunnelContractSpec(BaseModel):
    """Funnel contract specification."""

    model_config = ConfigDict(extra="forbid")

    stages: list[FunnelStage] = Field(min_length=1, max_length=20)
    alerts: list[AlertSpec] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_stages(self) -> FunnelContractSpec:
        """Enforce unique stage names and source/join stage shape."""
        names = [stage.name for stage in self.stages]
        if len(names) != len(set(names)):
            msg = "stage names must be unique within the contract"
            raise ValueError(msg)

        for index, stage in enumerate(self.stages):
            if index == 0:
                if stage.from_stage is not None:
                    msg = "first stage must not have from_stage"
                    raise ValueError(msg)
                if stage.sql is None or stage.expect_min_count is None:
                    msg = "first stage requires sql and expect_min_count"
                    raise ValueError(msg)
            else:
                if stage.from_stage is None or stage.join is None:
                    msg = f"stage {stage.name!r} requires from_stage and join"
                    raise ValueError(msg)
                if stage.expect_retention_pct is None:
                    msg = f"stage {stage.name!r} requires expect_retention_pct"
                    raise ValueError(msg)
                if stage.from_stage not in names[:index]:
                    msg = f"stage {stage.name!r} references unknown from_stage"
                    raise ValueError(msg)
        return self


class FunnelContract(BaseModel):
    """Identity funnel contract document."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    api_version: Literal["trustline.io/v1"] = Field(alias="apiVersion")
    kind: Literal["FunnelContract"]
    metadata: ContractMetadata
    spec: FunnelContractSpec


class DateWindow(BaseModel):
    """Inclusive date window."""

    model_config = ConfigDict(extra="forbid")

    start: date
    end: date

    @model_validator(mode="after")
    def validate_order(self) -> DateWindow:
        """Ensure start is on or before end."""
        if self.start > self.end:
            msg = "window start must be on or before end"
            raise ValueError(msg)
        return self


class LabelSpec(BaseModel):
    """Label definition for a cohort manifest."""

    model_config = ConfigDict(extra="forbid")

    definition: str
    sql: str | None = None


class CohortSources(BaseModel):
    """Training and scoring source table references."""

    model_config = ConfigDict(extra="forbid")

    training: str
    scoring: str


class CohortManifestSpec(BaseModel):
    """Cohort manifest specification."""

    model_config = ConfigDict(extra="forbid")

    observation_window: DateWindow
    outcome_window: DateWindow
    label: LabelSpec
    sources: CohortSources
    expected_positive_rate: float = Field(ge=0, le=1)
    positive_rate_tolerance: float = Field(default=0.02, ge=0, le=1)
    frozen_at: datetime
    model_ref: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_windows(self) -> CohortManifestSpec:
        """Outcome window must not start before observation window ends."""
        if self.outcome_window.start < self.observation_window.end:
            msg = "outcome_window.start must be on or after observation_window.end"
            raise ValueError(msg)
        return self


class CohortManifest(BaseModel):
    """Frozen training cohort manifest."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    api_version: Literal["trustline.io/v1"] = Field(alias="apiVersion")
    kind: Literal["CohortManifest"]
    metadata: ContractMetadata
    spec: CohortManifestSpec


ContractDocument = Annotated[FunnelContract | CohortManifest, Field(discriminator="kind")]

KNOWN_KINDS = frozenset({"FunnelContract", "CohortManifest"})
