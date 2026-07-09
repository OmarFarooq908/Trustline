#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_PATH="${ROOT}/examples/acme_stream/demo.duckdb"
SEED_SQL="${ROOT}/examples/acme_stream/sql/seed_data.sql"

rm -f "${DB_PATH}"
uv run python - <<PY
import duckdb
from pathlib import Path

db = Path("${DB_PATH}")
seed = Path("${SEED_SQL}")
con = duckdb.connect(str(db))
con.execute(seed.read_text(encoding="utf-8"))
con.execute("CHECKPOINT")
con.close()
size = db.stat().st_size
if size > 500 * 1024:
    raise SystemExit(f"demo.duckdb is too large: {size} bytes (limit 500KB)")
print(f"Wrote {db} ({size} bytes)")
PY
