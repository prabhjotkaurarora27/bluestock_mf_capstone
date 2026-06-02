"""
copy_remaining.py
------------------
Step 7 – Copy Uncleaned CSVs to Processed
Copies the 7 files that need no heavy cleaning directly from
data/raw/ to data/processed/ (overwriting if already present).

Run from project root:
    python scripts/copy_remaining.py
"""

import shutil
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent.parent
RAW_DIR   = BASE_DIR / "data" / "raw"
PROC_DIR  = BASE_DIR / "data" / "processed"

PROC_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    "01_fund_master.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]

# ── Copy ─────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  Bluestock MF Capstone — Copy Remaining CSVs")
print(f"{'='*60}\n")

copied, skipped = [], []

for fname in FILES:
    src  = RAW_DIR  / fname
    dest = PROC_DIR / fname

    if not src.exists():
        print(f"  ⚠  MISSING  {fname}  (not found in data/raw/ — skipped)")
        skipped.append(fname)
        continue

    shutil.copy2(src, dest)          # copy2 preserves metadata timestamps
    size_kb = dest.stat().st_size / 1024
    print(f"  ✅  Copied   {fname:<40}  ({size_kb:6.1f} KB)")
    copied.append(fname)

# ── Verify processed/ state ──────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  Processed Directory — Current State")
print(f"{'='*60}")

all_processed = sorted(PROC_DIR.glob("*.csv"))
total_size_kb  = sum(f.stat().st_size for f in all_processed) / 1024

for f in all_processed:
    print(f"  {f.name:<45}  {f.stat().st_size / 1024:7.1f} KB")

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  Summary")
print(f"{'='*60}")
print(f"  Files copied     : {len(copied)}")
print(f"  Files skipped    : {len(skipped)}")
print(f"  Total CSVs in processed/ : {len(all_processed)}")
print(f"  Total size              : {total_size_kb:.1f} KB  ({total_size_kb/1024:.2f} MB)")
print(f"\n  ✅  Done!\n")
