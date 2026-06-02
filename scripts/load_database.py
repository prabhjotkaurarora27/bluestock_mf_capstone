"""
load_database.py
-----------------
Step 8 – Load All Processed CSVs Into SQLite
Applies sql/schema.sql and bulk-loads every processed CSV into
data/db/bluestock_mf.db.

Special handling:
  • dim_date  : built programmatically from the NAV date range
  • fact_nav  : daily_return_pct computed via pct_change per fund
  • fact_performance : extra CSV columns not in schema are dropped before insert
  • All tables loaded with if_exists="append" so schema constraints are honoured

Run from project root:
    python scripts/load_database.py
"""

import sqlite3
import pandas as pd
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
DB_PATH    = BASE_DIR / "data" / "db"  / "bluestock_mf.db"
SCHEMA_SQL = BASE_DIR / "sql"          / "schema.sql"
PROC_DIR   = BASE_DIR / "data"         / "processed"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Helper: SQLAlchemy-free bulk insert via pandas + sqlite3 ─────────────────
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def load_table(df: pd.DataFrame, table: str, conn: sqlite3.Connection) -> int:
    """Append df to table; return rows inserted."""
    df.to_sql(table, conn, if_exists="append", index=False)
    return len(df)

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  Bluestock MF Capstone — Database Loader")
print(f"{'='*60}")

# ── 1. Apply schema (fresh DB each run) ──────────────────────────────────────
print(f"\n[1/12] Applying schema from {SCHEMA_SQL.relative_to(BASE_DIR)} …")
if DB_PATH.exists():
    DB_PATH.unlink()                   # start clean on every run
    print("       Existing DB removed — starting fresh.")

conn = get_conn()
schema_sql = SCHEMA_SQL.read_text()

# Execute each statement individually (split on ";\n" to avoid splitting
# inside string literals or comments; strip blank/comment-only blocks)
statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
for stmt in statements:
    # Skip pure-comment blocks
    non_comment = "\n".join(
        line for line in stmt.splitlines()
        if not line.strip().startswith("--")
    ).strip()
    if non_comment:
        conn.execute(stmt)

conn.commit()
print("       ✅  Schema applied successfully.")

# ── 2. dim_fund ──────────────────────────────────────────────────────────────
print("\n[2/12] Loading dim_fund …")
df_fund = pd.read_csv(PROC_DIR / "01_fund_master.csv")
df_fund["amfi_code"] = df_fund["amfi_code"].astype(int)
n = load_table(df_fund, "dim_fund", conn)
conn.commit()
print(f"       ✅  dim_fund          : {n:,} rows")

# ── 3. dim_date (built programmatically) ─────────────────────────────────────
print("\n[3/12] Building & loading dim_date …")
nav_raw = pd.read_csv(PROC_DIR / "clean_nav.csv", usecols=["date"], parse_dates=["date"])
min_date = nav_raw["date"].min()
max_date = nav_raw["date"].max()

date_range = pd.date_range(start=min_date, end=max_date, freq="D")
dim_date = pd.DataFrame({
    "date_id"    : date_range.strftime("%Y%m%d").astype(int),
    "date"       : date_range.strftime("%Y-%m-%d"),
    "year"       : date_range.year,
    "month"      : date_range.month,
    "quarter"    : date_range.quarter,
    "month_name" : date_range.strftime("%B"),
    "day_of_week": date_range.dayofweek,   # 0=Mon … 6=Sun
    "is_weekday" : (date_range.dayofweek < 5).astype(int),
})
n = load_table(dim_date, "dim_date", conn)
conn.commit()
print(f"       ✅  dim_date          : {n:,} rows  "
      f"({min_date.date()} → {max_date.date()})")

# ── 4. fact_nav (with computed daily_return_pct) ──────────────────────────────
print("\n[4/12] Loading fact_nav (computing daily_return_pct) …")
df_nav = pd.read_csv(PROC_DIR / "clean_nav.csv", parse_dates=["date"])
df_nav["amfi_code"] = df_nav["amfi_code"].astype(int)
df_nav = df_nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)

# Compute daily return % per fund (first day per fund → NaN)
df_nav["daily_return_pct"] = (
    df_nav.groupby("amfi_code")["nav"]
    .pct_change()
    .mul(100)
    .round(6)
)

# Select only columns that exist in the schema (drop auto-increment id)
df_nav_load = df_nav[["amfi_code", "date", "nav", "daily_return_pct"]].copy()
df_nav_load["date"] = df_nav_load["date"].dt.strftime("%Y-%m-%d")

n = load_table(df_nav_load, "fact_nav", conn)
conn.commit()
print(f"       ✅  fact_nav          : {n:,} rows")

# ── 5. fact_transactions ──────────────────────────────────────────────────────
print("\n[5/12] Loading fact_transactions …")
df_tx = pd.read_csv(PROC_DIR / "clean_transactions.csv", parse_dates=["transaction_date"])
df_tx["transaction_date"] = df_tx["transaction_date"].dt.strftime("%Y-%m-%d")
df_tx["amfi_code"] = df_tx["amfi_code"].astype(int)
# tx_id is AUTOINCREMENT in schema — do not pass it
n = load_table(df_tx, "fact_transactions", conn)
conn.commit()
print(f"       ✅  fact_transactions : {n:,} rows")

# ── 6. fact_performance ───────────────────────────────────────────────────────
print("\n[6/12] Loading fact_performance …")
df_perf = pd.read_csv(PROC_DIR / "clean_performance.csv")
df_perf["amfi_code"] = df_perf["amfi_code"].astype(int)

# CSV has extra columns not in the schema table — keep only schema columns
PERF_COLS = [
    "amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio",
    "std_dev_ann_pct", "max_drawdown_pct", "aum_crore", "expense_ratio_pct",
    "morningstar_rating", "risk_grade",
]
df_perf = df_perf[[c for c in PERF_COLS if c in df_perf.columns]]
n = load_table(df_perf, "fact_performance", conn)
conn.commit()
print(f"       ✅  fact_performance  : {n:,} rows")

# ── 7. fact_aum ───────────────────────────────────────────────────────────────
print("\n[7/12] Loading fact_aum …")
df_aum = pd.read_csv(PROC_DIR / "03_aum_by_fund_house.csv", parse_dates=["date"])
df_aum["date"] = df_aum["date"].dt.strftime("%Y-%m-%d")
n = load_table(df_aum, "fact_aum", conn)
conn.commit()
print(f"       ✅  fact_aum          : {n:,} rows")

# ── 8. fact_sip_inflows ───────────────────────────────────────────────────────
print("\n[8/12] Loading fact_sip_inflows …")
df_sip = pd.read_csv(PROC_DIR / "04_monthly_sip_inflows.csv", parse_dates=["month"])
df_sip["month"] = df_sip["month"].dt.strftime("%Y-%m-%d")
n = load_table(df_sip, "fact_sip_inflows", conn)
conn.commit()
print(f"       ✅  fact_sip_inflows  : {n:,} rows")

# ── 9. fact_category_inflows ──────────────────────────────────────────────────
print("\n[9/12] Loading fact_category_inflows …")
df_cat = pd.read_csv(PROC_DIR / "05_category_inflows.csv", parse_dates=["month"])
df_cat["month"] = df_cat["month"].dt.strftime("%Y-%m-%d")
n = load_table(df_cat, "fact_category_inflows", conn)
conn.commit()
print(f"       ✅  fact_category_inflows : {n:,} rows")

# ── 10. fact_folio_count ──────────────────────────────────────────────────────
print("\n[10/12] Loading fact_folio_count …")
df_folio = pd.read_csv(PROC_DIR / "06_industry_folio_count.csv", parse_dates=["month"])
df_folio["month"] = df_folio["month"].dt.strftime("%Y-%m-%d")
n = load_table(df_folio, "fact_folio_count", conn)
conn.commit()
print(f"       ✅  fact_folio_count  : {n:,} rows")

# ── 11. fact_portfolio_holdings ───────────────────────────────────────────────
print("\n[11/12] Loading fact_portfolio_holdings …")
df_ph = pd.read_csv(PROC_DIR / "09_portfolio_holdings.csv", parse_dates=["portfolio_date"])
df_ph["portfolio_date"] = df_ph["portfolio_date"].dt.strftime("%Y-%m-%d")
df_ph["amfi_code"] = df_ph["amfi_code"].astype(int)
n = load_table(df_ph, "fact_portfolio_holdings", conn)
conn.commit()
print(f"       ✅  fact_portfolio_holdings : {n:,} rows")

# ── 12. fact_benchmark_indices ────────────────────────────────────────────────
print("\n[12/12] Loading fact_benchmark_indices …")
df_bench = pd.read_csv(PROC_DIR / "10_benchmark_indices.csv", parse_dates=["date"])
df_bench["date"] = df_bench["date"].dt.strftime("%Y-%m-%d")
n = load_table(df_bench, "fact_benchmark_indices", conn)
conn.commit()
print(f"       ✅  fact_benchmark_indices : {n:,} rows")

# ── Verification ──────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  Database Verification — Row Counts")
print(f"{'='*60}")

tables_to_check = [
    "dim_fund", "dim_date",
    "fact_nav", "fact_transactions", "fact_performance",
    "fact_aum", "fact_sip_inflows", "fact_category_inflows",
    "fact_folio_count", "fact_portfolio_holdings", "fact_benchmark_indices",
]

total_rows = 0
for tbl in tables_to_check:
    count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    total_rows += count
    print(f"  {tbl:<35} {count:>8,} rows")

# Spot-check a view
view_rows = conn.execute("SELECT COUNT(*) FROM vw_performance_leaderboard").fetchone()[0]
print(f"\n  vw_performance_leaderboard (view)       {view_rows:>8,} rows")

db_size_mb = DB_PATH.stat().st_size / (1024 * 1024)

print(f"\n{'='*60}")
print(f"  Total rows loaded : {total_rows:,}")
print(f"  DB file size      : {db_size_mb:.2f} MB")
print(f"  Location          : {DB_PATH.relative_to(BASE_DIR)}")
print(f"\n  🎉  bluestock_mf.db is ready!\n")

conn.close()
