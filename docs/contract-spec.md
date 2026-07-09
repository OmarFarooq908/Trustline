# Contract Specification — Trustline

This document defines the formal specification for Trustline contracts: YAML format, JSON Schema validation rules, and complete ACME Stream examples.

---

## Overview

Trustline contracts are declarative YAML files that describe trust boundaries for data products. They are:

- **Human-readable** — authored and reviewed in git
- **Machine-validated** — checked against JSON Schema in CI
- **Executable** — compiled into SQL checks by the Trustline CLI

### Contract kinds

| Kind | `kind` value | Purpose | MVP version |
|------|-------------|---------|-------------|
| Funnel Contract | `FunnelContract` | Multi-hop join stages with retention thresholds | v0.1 |
| Cohort Manifest | `CohortManifest` | Frozen windows, label definition, source refs | v0.1 |
| Source Swap Annotation | `SourceSwapAnnotation` | Upstream migration timeline and drift thresholds | v0.2 |
| Delivery Lineage Contract | `DeliveryLineageContract` | Train → score → sync → CRM mirror chain | v0.3 |

### Common envelope

All contracts share a Kubernetes-inspired envelope:

```yaml
apiVersion: trustline.io/v1    # Required. Schema version.
kind: <ContractKind>            # Required. One of the kinds above.
metadata:                         # Required. Identification and ownership.
  name: <string>                  # Required. Unique within product.
  product: <string>               # Required. Product identifier.
  owner: <email>                  # Required. Team or individual owner.
  labels:                         # Optional. Key-value tags.
    <key>: <value>
spec:                             # Required. Kind-specific specification.
  ...
```

---

## Validation Rules

### Global rules

| Rule | Description |
|------|-------------|
| `apiVersion` | Must be `trustline.io/v1` for this spec version |
| `kind` | Must match a known contract kind |
| `metadata.name` | Lowercase alphanumeric + hyphens; max 63 chars |
| `metadata.owner` | Valid email format |
| File naming | `<metadata.name>.yaml` recommended |

### FunnelContract rules

| Rule | Description |
|------|-------------|
| `spec.stages` | Minimum 1 stage; maximum 20 stages |
| `spec.stages[0]` | First stage must not have `from_stage` (it is the source) |
| `spec.stages[n>0]` | Must reference a prior stage via `from_stage` |
| `expect_min_count` | Integer ≥ 0 |
| `expect_retention_pct` | Float 0.0–100.0 |
| Stage names | Unique within contract; lowercase alphanumeric + underscores |
| `alerts.threshold_pct` | Float 0.0–100.0 |

### CohortManifest rules

| Rule | Description |
|------|-------------|
| `observation_window` | `start` must be before `end` (ISO 8601 dates) |
| `outcome_window` | `start` must be on or after `observation_window.end` |
| `expected_positive_rate` | Float 0.0–1.0 |
| `sources.training` | Required; table reference |
| `sources.scoring` | Required; table reference |
| `frozen_at` | ISO 8601 datetime; immutable after initial commit |

---

## JSON Schema: FunnelContract

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://trustline.io/schemas/v1/funnel.schema.json",
  "title": "FunnelContract",
  "type": "object",
  "required": ["apiVersion", "kind", "metadata", "spec"],
  "additionalProperties": false,
  "properties": {
    "apiVersion": {
      "type": "string",
      "const": "trustline.io/v1"
    },
    "kind": {
      "type": "string",
      "const": "FunnelContract"
    },
    "metadata": {
      "$ref": "#/$defs/metadata"
    },
    "spec": {
      "type": "object",
      "required": ["stages"],
      "additionalProperties": false,
      "properties": {
        "stages": {
          "type": "array",
          "minItems": 1,
          "maxItems": 20,
          "items": {
            "$ref": "#/$defs/stage"
          }
        },
        "alerts": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/alert"
          }
        }
      }
    }
  },
  "$defs": {
    "metadata": {
      "type": "object",
      "required": ["name", "product", "owner"],
      "additionalProperties": false,
      "properties": {
        "name": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9-]{0,62}$"
        },
        "product": {
          "type": "string",
          "minLength": 1
        },
        "owner": {
          "type": "string",
          "format": "email"
        },
        "labels": {
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        }
      }
    },
    "stage": {
      "type": "object",
      "required": ["name"],
      "additionalProperties": false,
      "properties": {
        "name": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_]{0,62}$"
        },
        "sql": {
          "type": "string",
          "description": "SQL for the first stage (source). Uses ref() syntax."
        },
        "from_stage": {
          "type": "string",
          "description": "Name of the prior stage to join from."
        },
        "join": {
          "type": "object",
          "required": ["table", "on"],
          "additionalProperties": false,
          "properties": {
            "table": {
              "type": "string",
              "description": "Table to join. Uses ref() syntax."
            },
            "on": {
              "type": "string",
              "description": "Join key column name."
            },
            "type": {
              "type": "string",
              "enum": ["inner", "left"],
              "default": "inner"
            }
          }
        },
        "expect_min_count": {
          "type": "integer",
          "minimum": 0,
          "description": "Minimum row count at this stage."
        },
        "expect_retention_pct": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Minimum retention percentage from prior stage."
        },
        "description": {
          "type": "string"
        }
      },
      "oneOf": [
        {
          "required": ["sql", "expect_min_count"],
          "not": { "required": ["from_stage"] }
        },
        {
          "required": ["from_stage", "join", "expect_retention_pct"],
          "not": { "required": ["sql"] }
        }
      ]
    },
    "alert": {
      "type": "object",
      "required": ["on", "threshold_pct", "notify"],
      "additionalProperties": false,
      "properties": {
        "on": {
          "type": "string",
          "enum": ["retention_drop", "count_below_min", "stage_empty"]
        },
        "threshold_pct": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "notify": {
          "type": "string",
          "enum": ["slack", "email", "pagerduty"]
        },
        "channel": {
          "type": "string",
          "description": "Notification channel override."
        }
      }
    }
  }
}
```

---

## JSON Schema: CohortManifest

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://trustline.io/schemas/v1/cohort.schema.json",
  "title": "CohortManifest",
  "type": "object",
  "required": ["apiVersion", "kind", "metadata", "spec"],
  "additionalProperties": false,
  "properties": {
    "apiVersion": {
      "type": "string",
      "const": "trustline.io/v1"
    },
    "kind": {
      "type": "string",
      "const": "CohortManifest"
    },
    "metadata": {
      "$ref": "#/$defs/metadata"
    },
    "spec": {
      "type": "object",
      "required": [
        "observation_window",
        "outcome_window",
        "label",
        "sources",
        "expected_positive_rate",
        "frozen_at"
      ],
      "additionalProperties": false,
      "properties": {
        "observation_window": {
          "$ref": "#/$defs/dateWindow"
        },
        "outcome_window": {
          "$ref": "#/$defs/dateWindow"
        },
        "label": {
          "type": "object",
          "required": ["definition"],
          "additionalProperties": false,
          "properties": {
            "definition": {
              "type": "string",
              "description": "Human-readable label definition."
            },
            "sql": {
              "type": "string",
              "description": "SQL expression for label generation."
            }
          }
        },
        "sources": {
          "type": "object",
          "required": ["training", "scoring"],
          "additionalProperties": false,
          "properties": {
            "training": {
              "type": "string",
              "description": "Training feature table reference."
            },
            "scoring": {
              "type": "string",
              "description": "Scoring feature table reference."
            }
          }
        },
        "expected_positive_rate": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Expected positive label rate."
        },
        "positive_rate_tolerance": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "default": 0.02,
          "description": "Acceptable deviation from expected positive rate."
        },
        "frozen_at": {
          "type": "string",
          "format": "date-time",
          "description": "Timestamp when cohort was frozen. Immutable."
        },
        "model_ref": {
          "type": "string",
          "description": "Reference to model artifact or registry entry."
        },
        "notes": {
          "type": "string"
        }
      }
    }
  },
  "$defs": {
    "metadata": {
      "type": "object",
      "required": ["name", "product", "owner"],
      "additionalProperties": false,
      "properties": {
        "name": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9-]{0,62}$"
        },
        "product": {
          "type": "string",
          "minLength": 1
        },
        "owner": {
          "type": "string",
          "format": "email"
        },
        "labels": {
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        }
      }
    },
    "dateWindow": {
      "type": "object",
      "required": ["start", "end"],
      "additionalProperties": false,
      "properties": {
        "start": {
          "type": "string",
          "format": "date"
        },
        "end": {
          "type": "string",
          "format": "date"
        }
      }
    }
  }
}
```

---

## JSON Schema: SourceSwapAnnotation (v0.2 preview)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://trustline.io/schemas/v1/source_swap.schema.json",
  "title": "SourceSwapAnnotation",
  "type": "object",
  "required": ["apiVersion", "kind", "metadata", "spec"],
  "properties": {
    "apiVersion": { "type": "string", "const": "trustline.io/v1" },
    "kind": { "type": "string", "const": "SourceSwapAnnotation" },
    "metadata": { "$ref": "funnel.schema.json#/$defs/metadata" },
    "spec": {
      "type": "object",
      "required": ["table", "migration"],
      "properties": {
        "table": { "type": "string" },
        "migration": {
          "type": "object",
          "required": ["from_source", "to_source", "cutover_date"],
          "properties": {
            "from_source": { "type": "string" },
            "to_source": { "type": "string" },
            "cutover_date": { "type": "string", "format": "date" },
            "semantic_changes": {
              "type": "array",
              "items": { "type": "string" }
            }
          }
        },
        "volume_threshold_pct": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "default": 10,
          "description": "Alert when volume deviates by this percentage."
        }
      }
    }
  }
}
```

---

## ACME Stream Examples

### Example 1: Training positives funnel

Identity funnel for ACME Stream propensity model training population.

```yaml
apiVersion: trustline.io/v1
kind: FunnelContract
metadata:
  name: training_positives
  product: acme_propensity_v2
  owner: platform-team@acme-stream.example
  labels:
    team: data-platform
    env: production
spec:
  stages:
    - name: source_donors
      description: "Donors with at least one gift in observation window"
      sql: "SELECT donor_id, email, gift_amount FROM {{ ref('donor_gifts') }} WHERE gift_date >= '2025-01-01'"
      expect_min_count: 2000

    - name: app_identity_match
      description: "Donors matched to app user accounts via email"
      from_stage: source_donors
      join:
        table: "{{ ref('app_users') }}"
        on: email
        type: left
      expect_retention_pct: 40

    - name: behavioral_features
      description: "Matched users with sufficient watch history for feature engineering"
      from_stage: app_identity_match
      join:
        table: "{{ ref('watch_events') }}"
        on: user_id
        type: inner
      expect_retention_pct: 25

  alerts:
    - on: retention_drop
      threshold_pct: 5
      notify: slack
      channel: "#data-trust-alerts"
```

**ACME context:** This funnel captures the observed collapse from 2,000 donors → 800 app matches (40%) → 250 with watch features (31% of matched, 12.5% of source). The contract encodes the minimum acceptable retention at each stage.

### Example 2: Propensity training cohort (Q2)

Frozen cohort manifest for ACME Stream propensity model.

```yaml
apiVersion: trustline.io/v1
kind: CohortManifest
metadata:
  name: propensity_training_cohort_q2
  product: acme_propensity_v2
  owner: ml-team@acme-stream.example
  labels:
    team: ml-engineering
    quarter: q2-2025
spec:
  observation_window:
    start: "2025-01-01"
    end: "2025-03-31"
  outcome_window:
    start: "2025-04-01"
    end: "2025-04-30"
  label:
    definition: "User subscribed to ACME Stream premium within 30 days of observation window end"
    sql: |
      CASE
        WHEN subscription_date BETWEEN '2025-04-01' AND '2025-04-30'
        THEN 1
        ELSE 0
      END
  sources:
    training: "{{ ref('features_training') }}"
    scoring: "{{ ref('features_scoring') }}"
  expected_positive_rate: 0.12
  positive_rate_tolerance: 0.02
  frozen_at: "2025-05-01T00:00:00Z"
  model_ref: "acme_propensity_v2_logreg_20250501"
  notes: |
    Cohort frozen after Q2 model review. Positive rate of 12% validated
    against holdout set (AUC 0.78). Do not modify windows without ML team approval.
```

**ACME context:** When the departing ML engineer left, this manifest did not exist in git. The replacement engineer had to reconstruct label definition and positive rate from a Notion doc. This contract makes the cohort executable and auditable.

### Example 3: NewPlayer source swap

Source migration annotation for ACME Stream event pipeline.

```yaml
apiVersion: trustline.io/v1
kind: SourceSwapAnnotation
metadata:
  name: legacy_to_newplayer_swap
  product: acme_propensity_v2
  owner: platform-team@acme-stream.example
  labels:
    team: data-platform
    impact: high
spec:
  table: "{{ ref('user_events_silver') }}"
  migration:
    from_source: LegacyPlayer
    to_source: NewPlayer
    cutover_date: "2025-03-15"
    semantic_changes:
      - "NewPlayer emits play_start instead of play_event"
      - "NewPlayer includes pause/resume events not present in LegacyPlayer"
      - "Session boundary logic changed from 30min to 15min idle timeout"
  volume_threshold_pct: 10
```

**ACME context:** The migration from `LegacyPlayer` to `NewPlayer` changed event semantics and caused backfill churn in silver tables. Watch feature counts shifted, causing score distribution changes that stakeholders noticed before the data team did.

### Example 4: CRM delivery coverage (v0.3 preview)

```yaml
apiVersion: trustline.io/v1
kind: DeliveryLineageContract
metadata:
  name: propensity_crm_delivery
  product: acme_propensity_v2
  owner: platform-team@acme-stream.example
spec:
  lineage:
    - stage: train
      artifact: "acme_propensity_v2_logreg_20250501"
    - stage: score
      table: "{{ ref('propensity_scores_staging') }}"
    - stage: sync_queue
      table: "{{ ref('crm_push_queue') }}"
    - stage: crm_mirror
      table: "{{ ref('crm_contacts_mirror') }}"
      field: propensity_score
  coverage:
    expect_sync_pct: 95
    description: "At least 95% of scored users must appear in CRM mirror"
```

**ACME context:** ACME Stream had 300K rows in the push queue but only 80K contacts in the CRM mirror. The queue was mistaken for authoritative sync state. This contract (v0.3) makes the coverage gap machine-checkable.

---

## `ref()` Syntax

Contracts use dbt-compatible `ref()` syntax for table references:

```yaml
sql: "SELECT * FROM {{ ref('donor_gifts') }}"
```

At compile time, Trustline resolves `ref()` to fully qualified table names using the active profile:

| Profile config | `ref('donor_gifts')` resolves to |
|----------------|----------------------------------|
| `database: ANALYTICS, schema: CURATED` | `ANALYTICS.CURATED.donor_gifts` |
| DuckDB local | `main.donor_gifts` |

In v0.1, resolution is manual via `profiles.yml`. In v0.2, the dbt macro provides automatic resolution from `manifest.json`.

---

## Schema Evolution

### Versioning policy

| Change type | Action |
|-------------|--------|
| Add optional field | Minor schema update; no `apiVersion` bump |
| Add required field | `apiVersion` bump (e.g., `trustline.io/v2`) |
| Remove field | `apiVersion` bump + deprecation notice |
| Change field type | `apiVersion` bump + migration guide |

### RFC process

Breaking schema changes require:

1. GitHub Issue with `RFC` label
2. 7-day comment period
3. Updated JSON Schema in `schemas/`
4. Migration guide in `docs/`
5. Semver tag on release

---

## Validation Usage

> **v0.1 (planned):** `trustline validate` is not implemented in `0.0.1`. The commands below describe the target CLI.

### CLI

```bash
# Validate all contracts in a directory
trustline validate --contracts ./examples/acme_stream/contracts/
```

Additional flags planned for v0.1: `--file` (single contract), `--strict` (warnings as errors).

### CI (GitHub Actions)

```yaml
- run: trustline validate --contracts ./contracts/ --strict
```

### Expected output (v0.1)

```
Validating 1 contracts...

  training_positives.yaml       FunnelContract      PASS

All contracts valid.
```

---

## Related Documents

- [index.md](index.md) — Product overview
- [architecture.md](architecture.md) — How contracts compile to SQL
- [mvp-scope.md](mvp-scope.md) — Which contract kinds ship in v0.1
