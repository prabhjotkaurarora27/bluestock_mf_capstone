"""
etl_pipeline.py
---------------
Bluestock MF Capstone — Day 1 ETL Pipeline (D1 Deliverable)
============================================================
Master orchestration script that runs the full end-to-end pipeline:
  Stage 1 : Data ingestion   (data_ingestion.py + live_nav_fetch.py)
  Stage 2 : NAV cleaning     (clean_nav.py)
  Stage 3 : Txn cleaning     (clean_transactions.py)
  Stage 4 : Perf cleaning    (clean_performance.py)
  Stage 5 : Copy remaining   (copy_remaining.py)
  Stage 6 : SQLite DB load   (load_database.py)
  Stage 7 : Metrics compute  (compute_metrics.py)

Usage (run from project root):
    python scripts/etl_pipeline.py
    python scripts/etl_pipeline.py --skip-metrics   # skip Stage 7
    python scripts/etl_pipeline.py --skip-db        # skip Stage 6+

Error handling:
    - Each stage runs in a try/except; failures are logged and counted.
    - Non-zero exit code returned if any stage fails.
    - All paths built with pathlib.Path — no hard-coded strings.
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path

# ── Project root (two levels up from this script) ────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── CLI flags ─────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Bluestock MF ETL Pipeline")
parser.add_argument("--skip-db",      action="store_true", help="Skip DB load stage")
parser.add_argument("--skip-metrics", action="store_true", help="Skip metrics compute stage")
args = parser.parse_args()

# ── Pipeline stages ───────────────────────────────────────────────────────────
STAGES = [
    ("Stage 1/7 — Data Ingestion",          "scripts/data_ingestion.py",    True),
    ("Stage 2/7 — Clean NAV History",        "scripts/clean_nav.py",         True),
    ("Stage 3/7 — Clean Investor Txns",      "scripts/clean_transactions.py", True),
    ("Stage 4/7 — Clean Scheme Perf",        "scripts/clean_performance.py", True),
    ("Stage 5/7 — Copy Remaining CSVs",      "scripts/copy_remaining.py",    True),
    ("Stage 6/7 — Load SQLite Database",     "scripts/load_database.py",     not args.skip_db),
    ("Stage 7/7 — Compute Metrics",          "scripts/compute_metrics.py",   not args.skip_metrics),
]

# ── Banner ────────────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print("   Bluestock MF Capstone — ETL Pipeline  (etl_pipeline.py)")
print(f"{'='*65}\n")

start_total = time.time()
errors: list[str] = []

for label, script, enabled in STAGES:
    print(f"\n{'─'*65}")
    print(f"  ▶  {label}")
    print(f"{'─'*65}")

    if not enabled:
        print("  ⏭  Skipped (--skip flag active)")
        continue

    script_path = BASE_DIR / script
    if not script_path.exists():
        print(f"  ⚠  Script not found: {script_path} — skipping")
        errors.append(script)
        continue

    t0 = time.time()
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(BASE_DIR),
        )
        elapsed = time.time() - t0
        if result.returncode != 0:
            errors.append(script)
            print(f"  ❌  {label} FAILED  (exit {result.returncode}, {elapsed:.1f}s)")
        else:
            print(f"  ✅  Done in {elapsed:.1f}s")
    except Exception as exc:
        errors.append(script)
        print(f"  ❌  {label} raised exception: {exc}")

# ── Summary ───────────────────────────────────────────────────────────────────
total_elapsed = time.time() - start_total
print(f"\n{'='*65}")
if errors:
    print(f"  ⚠  Pipeline finished with {len(errors)} error(s):")
    for e in errors:
        print(f"      • {e}")
    print(f"{'='*65}\n")
    sys.exit(1)
else:
    print(f"  🎉  All stages completed successfully in {total_elapsed:.1f}s")
    print()
    print("  Deliverables produced:")
    print("    data/processed/          ← 10 cleaned CSVs (01–10_*.csv)")
    print("    data/db/bluestock_mf.db  ← SQLite star schema (107K+ rows)")
    print("    sql/schema.sql           ← CREATE TABLE + FK + indexes + views")
    print("    sql/queries.sql          ← 13 analytical SQL queries")
    print("    data_dictionary.md       ← column-level documentation")
    print("    reports/fund_scorecard.csv ← composite performance scorecard")
    print(f"{'='*65}\n")
