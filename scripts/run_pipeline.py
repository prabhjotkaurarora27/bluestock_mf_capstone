"""
run_pipeline.py
---------------
Day 2 Master Pipeline Runner
Executes all cleaning scripts + database loader in order.

Run from project root:
    python scripts/run_pipeline.py
"""

import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STEPS = [
    ("Step 1/4 — Clean NAV History",          "scripts/clean_nav.py"),
    ("Step 2/4 — Clean Investor Transactions", "scripts/clean_transactions.py"),
    ("Step 3/4 — Clean Scheme Performance",   "scripts/clean_performance.py"),
    ("Step 4/4 — Copy remaining CSVs",         "scripts/copy_remaining.py"),
    ("Step 5/5 — Load SQLite Database",        "scripts/load_database.py"),
]

print(f"\n{'='*60}")
print("  Bluestock MF Capstone — Day 2 Full Pipeline")
print(f"{'='*60}\n")

start_total = time.time()
errors = []

for label, script in STEPS:
    print(f"\n{'─'*60}")
    print(f"  ▶  {label}")
    print(f"{'─'*60}")
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, str(BASE_DIR / script)],
        cwd=str(BASE_DIR),
    )
    elapsed = time.time() - t0
    if result.returncode != 0:
        errors.append(script)
        print(f"  ❌  {label} FAILED (exit code {result.returncode})")
    else:
        print(f"  ✅  Done in {elapsed:.1f}s")

total_elapsed = time.time() - start_total
print(f"\n{'='*60}")
if errors:
    print(f"  ⚠  Pipeline finished with {len(errors)} error(s):")
    for e in errors:
        print(f"      • {e}")
else:
    print(f"  🎉  All steps completed successfully in {total_elapsed:.1f}s")
    print()
    print("  Deliverables:")
    print("    data/processed/   ← 10 cleaned CSVs (01–10)")
    print("    data/db/bluestock_mf.db  ← SQLite star schema")
    print("    sql/schema.sql    ← CREATE TABLE + FK + indexes + views")
    print("    sql/queries.sql   ← 13 analytical SQL queries")
    print("    data_dictionary.md ← column-level documentation")
print(f"{'='*60}\n")
