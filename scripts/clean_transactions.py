"""
clean_transactions.py
----------------------
Step 5 – Investor Transactions Data Cleaning
Cleans data/raw/08_investor_transactions.csv and saves to
data/processed/clean_transactions.csv.

Cleaning steps:
  1. Parse 'transaction_date' to datetime
  2. Standardise 'transaction_type' casing  (SIP / sip / Sip  →  SIP)
  3. Drop rows with unrecognised transaction types
  4. Validate amount_inr > 0  — report and drop invalid rows
  5. Validate kyc_status is in allowed set — report and drop invalid rows
  6. Save cleaned data

Run from project root:
    python scripts/clean_transactions.py
"""

import pandas as pd
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent.parent
RAW_FILE  = BASE_DIR / "data" / "raw"       / "08_investor_transactions.csv"
OUT_FILE  = BASE_DIR / "data" / "processed" / "clean_transactions.csv"

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Canonical values (uppercase for transaction_type to match source reality)
VALID_TYPES = {"SIP", "Lumpsum", "Redemption"}
VALID_KYC   = {"Verified", "Pending"}

# ── 1. Load ──────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  Bluestock MF Capstone — Investor Transactions Cleaner")
print(f"{'='*60}")
print(f"\n[1/6] Loading raw file: {RAW_FILE.relative_to(BASE_DIR)}")

df = pd.read_csv(RAW_FILE, low_memory=False)
original_shape = df.shape
print(f"      Original shape : {original_shape[0]:,} rows × {original_shape[1]} columns")

# ── 2. Parse transaction_date ────────────────────────────────────────────────
print("\n[2/6] Parsing 'transaction_date' column to datetime …")
df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")

unparsed = df["transaction_date"].isna().sum()
if unparsed:
    print(f"      ⚠  {unparsed:,} unparseable dates dropped.")
    df = df.dropna(subset=["transaction_date"])
else:
    print("      ✓  All dates parsed successfully.")

# ── 3. Standardise transaction_type ─────────────────────────────────────────
print("\n[3/6] Standardising 'transaction_type' …")
# Strip whitespace, then apply title-case mapping; re-map "Sip" → "SIP"
df["transaction_type"] = (
    df["transaction_type"]
    .str.strip()
    .str.title()
    .replace({"Sip": "SIP"})          # title() turns SIP → Sip; fix it back
)

invalid_type_mask = ~df["transaction_type"].isin(VALID_TYPES)
invalid_types     = df.loc[invalid_type_mask, "transaction_type"].unique()

if invalid_types.size:
    print(f"      ⚠  Unrecognised types found ({len(df[invalid_type_mask]):,} rows): {invalid_types}")
    df = df[~invalid_type_mask]
else:
    print(f"      ✓  All types valid: {sorted(df['transaction_type'].unique())}")

# ── 4. Validate amount_inr > 0 ───────────────────────────────────────────────
print("\n[4/6] Validating amount_inr > 0 …")
df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")

invalid_amt_mask  = ~(df["amount_inr"] > 0)   # catches NaN, 0, negatives
invalid_amt_count = invalid_amt_mask.sum()

if invalid_amt_count:
    print(f"      ⚠  {invalid_amt_count:,} rows with invalid amount dropped.")
    print(df[invalid_amt_mask][["investor_id", "transaction_date", "amount_inr"]].head(10).to_string(index=False))
    df = df[~invalid_amt_mask]
else:
    print(f"      ✓  All amounts are positive (min = ₹{df['amount_inr'].min():,.0f}).")

# ── 5. Validate kyc_status ───────────────────────────────────────────────────
print("\n[5/6] Validating 'kyc_status' …")
print(f"      KYC values found : {df['kyc_status'].unique().tolist()}")

invalid_kyc_mask  = ~df["kyc_status"].isin(VALID_KYC)
invalid_kyc_count = invalid_kyc_mask.sum()

if invalid_kyc_count:
    print(f"      ⚠  {invalid_kyc_count:,} rows with unrecognised KYC status dropped.")
    df = df[~invalid_kyc_mask]
else:
    print(f"      ✓  All KYC statuses are valid: {sorted(VALID_KYC)}")

# ── 6. Save ──────────────────────────────────────────────────────────────────
print("\n[6/6] Saving cleaned file …")
df = df.sort_values(["investor_id", "transaction_date"]).reset_index(drop=True)
df.to_csv(OUT_FILE, index=False)

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  Cleaning Summary")
print(f"{'='*60}")
print(f"  Original shape      : {original_shape[0]:,} rows × {original_shape[1]} columns")
print(f"  Cleaned shape       : {len(df):,} rows × {df.shape[1]} columns")
print(f"  Rows removed        : {original_shape[0] - len(df):,}")
print(f"  Unique investors    : {df['investor_id'].nunique():,}")
print(f"  Unique funds        : {df['amfi_code'].nunique():,}")
print(f"  Date range          : {df['transaction_date'].min().date()}  →  {df['transaction_date'].max().date()}")
print(f"  Transaction types   : {sorted(df['transaction_type'].unique())}")
print(f"  KYC distribution    :")
for status, cnt in df["kyc_status"].value_counts().items():
    print(f"      {status:<10} {cnt:,}")
print(f"  Output saved to     : {OUT_FILE.relative_to(BASE_DIR)}")
print(f"\n  ✅  clean_transactions.csv written successfully!\n")
