"""
clean_nav.py
------------------
Step 4 – NAV History Data Cleaning
Cleans data/raw/02_nav_history.csv and saves to data/processed/clean_nav.csv.

Cleaning steps:
  1. Parse 'date' column to datetime
  2. Sort by amfi_code then date
  3. Forward-fill NAV for weekends / market holidays (reindex to daily freq per fund)
  4. Remove duplicate rows on (amfi_code, date)
  5. Validate nav > 0  — report and drop invalid rows
  6. Save cleaned data to data/processed/clean_nav.csv

Run from project root:
    python scripts/clean_nav.py
"""

import pandas as pd
from pathlib import Path

# ── Paths (resolved relative to this script, works from any cwd) ────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
RAW_FILE   = BASE_DIR / "data" / "raw"       / "02_nav_history.csv"
OUT_FILE   = BASE_DIR / "data" / "processed" / "clean_nav.csv"

# Ensure output directory exists
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ── 1. Load ──────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  Bluestock MF Capstone — NAV History Cleaner")
print(f"{'='*60}")
print(f"\n[1/6] Loading raw file: {RAW_FILE.relative_to(BASE_DIR)}")

df = pd.read_csv(RAW_FILE, low_memory=False)
original_shape = df.shape
print(f"      Original shape : {original_shape[0]:,} rows × {original_shape[1]} columns")

# ── 2. Parse date column ─────────────────────────────────────────────────────
print("\n[2/6] Parsing 'date' column to datetime …")
df["date"] = pd.to_datetime(df["date"], errors="coerce")

unparsed = df["date"].isna().sum()
if unparsed:
    print(f"      ⚠  {unparsed:,} rows had unparseable dates — they will be dropped.")
    df = df.dropna(subset=["date"])
else:
    print("      ✓  All dates parsed successfully.")

# ── 3. Sort by amfi_code then date ──────────────────────────────────────────
print("\n[3/6] Sorting by amfi_code → date …")
df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

# ── 4. Remove duplicate rows on (amfi_code, date) ───────────────────────────
print("\n[4/6] Removing duplicates on (amfi_code, date) …")
before_dedup = len(df)
df = df.drop_duplicates(subset=["amfi_code", "date"])
dropped_dups = before_dedup - len(df)
print(f"      Duplicates removed : {dropped_dups:,}")

# ── 5. Forward-fill missing NAV (weekends / market holidays) ─────────────────
print("\n[5/6] Reindexing each fund to daily frequency and forward-filling …")

def ffill_fund(group: pd.DataFrame) -> pd.DataFrame:
    """Reindex a single fund's series to calendar-daily and forward-fill NAV."""
    group = group.set_index("date")
    full_range = pd.date_range(start=group.index.min(), end=group.index.max(), freq="D")
    group = group.reindex(full_range)
    # Restore amfi_code after reindex (NaN for new rows)
    group["amfi_code"] = group["amfi_code"].ffill()
    # Forward-fill NAV only (do not back-fill)
    group["nav"] = group["nav"].ffill()
    group.index.name = "date"
    return group.reset_index()

filled_parts = []
for code, grp in df.groupby("amfi_code", sort=False):
    filled_parts.append(ffill_fund(grp))

df_filled = pd.concat(filled_parts, ignore_index=True)

# Flatten any accidental MultiIndex (safety net)
if isinstance(df_filled.index, pd.MultiIndex):
    df_filled = df_filled.reset_index(drop=True)

rows_added = len(df_filled) - len(df)
print(f"      Calendar rows added by ffill : {rows_added:,}")

df = df_filled

# ── 6. Validate nav > 0 ──────────────────────────────────────────────────────
print("\n[6/6] Validating nav > 0 …")
# Coerce nav to numeric (catches stray strings)
df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

invalid_mask = ~(df["nav"] > 0)          # catches NaN, 0, negatives
invalid_count = invalid_mask.sum()
print(f"      Invalid nav rows found : {invalid_count:,}")

if invalid_count:
    print("      Sample invalid rows:")
    print(df[invalid_mask][["amfi_code", "date", "nav"]].head(10).to_string(index=False))
    df = df[~invalid_mask].reset_index(drop=True)

# ── 7. Final sort & save ─────────────────────────────────────────────────────
df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

df.to_csv(OUT_FILE, index=False)

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  Cleaning Summary")
print(f"{'='*60}")
print(f"  Original shape  : {original_shape[0]:,} rows × {original_shape[1]} columns")
print(f"  Cleaned shape   : {len(df):,} rows × {df.shape[1]} columns")
print(f"  Funds covered   : {df['amfi_code'].nunique()}")
print(f"  Date range      : {df['date'].min().date()}  →  {df['date'].max().date()}")
print(f"  Output saved to : {OUT_FILE.relative_to(BASE_DIR)}")
print(f"\n  ✅  clean_nav.csv written successfully!\n")
