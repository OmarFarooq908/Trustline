#!/usr/bin/env bash
# Reject legacy planning doc filenames at docs/ root.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

LEGACY_DOC_BASENAMES=(
  "GO_TO_MARKET.md"
  "RISKS_AND_MITIGATIONS.md"
  "PRODUCT_PLAN.md"
  "MVP_SCOPE.md"
  "DECISIONS.md"
)

failed=0

for base in "${LEGACY_DOC_BASENAMES[@]}"; do
  if find docs -maxdepth 1 -name "$base" 2>/dev/null | grep -q .; then
    echo "ERROR: unexpected doc at docs/$base (remove or relocate)"
    failed=1
  fi
done

if [[ "$failed" -ne 0 ]]; then
  exit 1
fi

echo "Documentation check passed."
