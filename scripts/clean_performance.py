"""
clean_performance.py
---------------------
Step 6 – Scheme Performance Data Cleaning
Cleans data/raw/07_scheme_performance.csv and saves to
data/processed/clean_performance.csv.

Cleaning steps:
  1. Force all metric columns to numeric (coerce bad values → NaN)
  2. Report & flag suspicious Sharpe ratios (> 3); keep but annotate
  3. Validate expense_ratio_pct in realistic range [0.1, 2.5]
     → report out-of-range rows; clip to bounds rather than drop
  4. Validate morningstar_rating in [1, 5] — report & drop invalids
  5. Normalise 'category'  (e.g. "Index" → "Index/ETF")
  6. Standardise casing of 'plan' and 'risk_grade'
  7. Save cleaned data

Run from project root:
    python scripts/clean_performance.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw"       / "07_scheme_performance.csv"
OUT_FILE = BASE_DIR / "data" / "processed" / "clean_performance.csv"

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ── Column groups ────────────────────────────────────────────────────────────
RETURN_COLS = [
    "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "benchmark_3yr_pct", "sharpe_ratio", "sortino_ratio",
    "alpha", "beta", "std_dev_ann_pct", "max_drawdown_pct",
    "aum_crore", "expense_ratio_pct",
]

# ── 1. Load ──────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  Bluestock MF Capstone — Scheme Performance Cleaner")
print(f"{'='*60}")
print(f"\n[1/7] Loading raw file: {RAW_FILE.relative_to(BASE_DIR)}")

df = pd.read_csv(RAW_FILE, low_memory=False)
original_shape = df.shape
print(f"      Original shape : {original_shape[0]:,} rows × {original_shape[1]} columns")

# ── 2. Force numeric on all metric columns ───────────────────────────────────
print("\n[2/7] Coercing metric columns to numeric …")
coerce_issues = {}
for col in RETURN_COLS:
    if col not in df.columns:
        print(f"      ⚠  Column '{col}' not found — skipping.")
        continue
    before_nulls = df[col].isna().sum()
    df[col] = pd.to_numeric(df[col], errors="coerce")
    after_nulls  = df[col].isna().sum()
    new_nulls    = after_nulls - before_nulls
    if new_nulls > 0:
        coerce_issues[col] = new_nulls
        print(f"      ⚠  '{col}' : {new_nulls} non-numeric value(s) → NaN")

if not coerce_issues:
    print("      ✓  All metric columns already numeric — no coercion needed.")

# ── 3. Sharpe ratio check ────────────────────────────────────────────────────
print("\n[3/7] Checking Sharpe ratio …")
SHARPE_WARN_THRESHOLD = 3.0
neg_sharpe  = df[df["sharpe_ratio"] < 0]
high_sharpe = df[df["sharpe_ratio"] > SHARPE_WARN_THRESHOLD]

if len(neg_sharpe):
    print(f"      ⚠  {len(neg_sharpe)} fund(s) with NEGATIVE Sharpe ratio (kept — may be valid):")
    print(neg_sharpe[["scheme_name", "sharpe_ratio"]].to_string(index=False))
else:
    print("      ✓  No negative Sharpe ratios.")

if len(high_sharpe):
    print(f"      ℹ  {len(high_sharpe)} fund(s) with Sharpe > {SHARPE_WARN_THRESHOLD} "
          f"(likely Liquid / Debt funds — kept as-is):")
    print(high_sharpe[["scheme_name", "category", "sharpe_ratio"]].to_string(index=False))
else:
    print(f"      ✓  No Sharpe ratios above {SHARPE_WARN_THRESHOLD}.")

# ── 4. Expense ratio validation ──────────────────────────────────────────────
EXPENSE_MIN, EXPENSE_MAX = 0.1, 2.5
print(f"\n[4/7] Validating expense_ratio_pct in [{EXPENSE_MIN}, {EXPENSE_MAX}] …")

out_of_range_mask = ~df["expense_ratio_pct"].between(EXPENSE_MIN, EXPENSE_MAX)
out_of_range      = df[out_of_range_mask]

if len(out_of_range):
    print(f"      ⚠  {len(out_of_range)} row(s) outside [{EXPENSE_MIN}, {EXPENSE_MAX}] — clipping to bounds:")
    print(out_of_range[["scheme_name", "expense_ratio_pct"]].to_string(index=False))
    df["expense_ratio_pct"] = df["expense_ratio_pct"].clip(lower=EXPENSE_MIN, upper=EXPENSE_MAX)
else:
    er_min = df["expense_ratio_pct"].min()
    er_max = df["expense_ratio_pct"].max()
    print(f"      ✓  All expense ratios in range  (actual range: {er_min:.2f}% – {er_max:.2f}%)")

# ── 5. Morningstar rating validation ─────────────────────────────────────────
print("\n[5/7] Validating morningstar_rating in [1, 5] …")
df["morningstar_rating"] = pd.to_numeric(df["morningstar_rating"], errors="coerce")
invalid_rating_mask = ~df["morningstar_rating"].between(1, 5)
invalid_rating_count = invalid_rating_mask.sum()

if invalid_rating_count:
    print(f"      ⚠  {invalid_rating_count} invalid rating(s) found — dropping rows:")
    print(df[invalid_rating_mask][["scheme_name", "morningstar_rating"]].to_string(index=False))
    df = df[~invalid_rating_mask].reset_index(drop=True)
else:
    print(f"      ✓  All ratings valid. Distribution: "
          f"{df['morningstar_rating'].value_counts().sort_index().to_dict()}")

# ── 6. Normalise 'category' ──────────────────────────────────────────────────
print("\n[6/7] Normalising 'category' values …")
CATEGORY_MAP = {
    "Index":    "Index/ETF",   # merge standalone "Index" into "Index/ETF"
}
before_cats = df["category"].value_counts().to_dict()
df["category"] = df["category"].str.strip().replace(CATEGORY_MAP)
after_cats  = df["category"].value_counts().to_dict()

merged = {k: v for k, v in CATEGORY_MAP.items() if k in before_cats}
if merged:
    print(f"      ✓  Merged categories: {merged}")
else:
    print("      ✓  No category normalisation needed.")
print(f"      Final categories: {sorted(df['category'].unique())}")

# ── 7. Standardise casing of plan & risk_grade ───────────────────────────────
print("\n[7/7] Standardising casing for 'plan' and 'risk_grade' …")
df["plan"]       = df["plan"].str.strip().str.title()
df["risk_grade"] = df["risk_grade"].str.strip().str.title()
print(f"      plan       values : {sorted(df['plan'].unique())}")
print(f"      risk_grade values : {sorted(df['risk_grade'].unique())}")

# ── Save ─────────────────────────────────────────────────────────────────────
df = df.sort_values("amfi_code").reset_index(drop=True)
df.to_csv(OUT_FILE, index=False)

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  Cleaning Summary")
print(f"{'='*60}")
print(f"  Original shape   : {original_shape[0]:,} rows × {original_shape[1]} columns")
print(f"  Cleaned shape    : {len(df):,} rows × {df.shape[1]} columns")
print(f"  Rows removed     : {original_shape[0] - len(df):,}")
print(f"\n  Return metrics summary (cleaned):")

metric_display = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
                  "sharpe_ratio", "alpha", "beta", "expense_ratio_pct"]
summary = df[metric_display].agg(["min", "mean", "max"]).round(3)
print(summary.to_string())

print(f"\n  Output saved to  : {OUT_FILE.relative_to(BASE_DIR)}")
print(f"\n  ✅  clean_performance.csv written successfully!\n")
