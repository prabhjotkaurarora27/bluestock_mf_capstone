"""
Generates Performance_Analytics.ipynb at the repo root.
Run from: bluestock_mf_capstone/
"""
import json, textwrap
from pathlib import Path

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": [text]}

def code(src):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [src],
    }

cells = []

# ── Title ────────────────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
# Day 4 — Performance Analytics
**Bluestock Mutual Fund Capstone**  
Covers: Daily Returns · CAGR · Sharpe · Sortino · Alpha/Beta · Max Drawdown · Scorecard · Benchmark Chart""")))

# ── Setup ─────────────────────────────────────────────────────────────────────
cells.append(md("## 0. Setup & Imports"))
cells.append(code(textwrap.dedent("""\
import warnings; warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy.stats import linregress
from pathlib import Path
import os

sns.set_theme(style="whitegrid", palette="muted")
pd.set_option("display.max_rows", 50)
pd.set_option("display.float_format", "{:.4f}".format)

# ── Paths (relative to repo root) ────────────────────────────────────
PROCESSED = Path("data/processed")
REPORTS   = Path("reports")
CHARTS    = Path("reports/charts")
CHARTS.mkdir(parents=True, exist_ok=True)
(REPORTS).mkdir(parents=True, exist_ok=True)

RF_ANNUAL    = 0.065          # RBI repo rate proxy
RF_DAILY     = RF_ANNUAL / 252
TRADING_DAYS = 252

print("Libraries loaded.")
print(f"PROCESSED: {PROCESSED.resolve()}")
print(f"REPORTS:   {REPORTS.resolve()}")""")))

# ── Task 1 ─────────────────────────────────────────────────────────────────
cells.append(md("## Task 1 — Daily Returns\n`daily_return = nav / nav.shift(1) - 1` per fund. Validate distribution."))
cells.append(code(textwrap.dedent("""\
# Load NAV history
nav = pd.read_csv(PROCESSED / "02_nav_history.csv", parse_dates=["date"])
nav = nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)

# Load fund master for names
funds = pd.read_csv(PROCESSED / "01_fund_master.csv")
funds["amfi_code"] = pd.to_numeric(funds["amfi_code"], errors="coerce").astype("Int64").astype(str)
nav["amfi_code"]   = pd.to_numeric(nav["amfi_code"],   errors="coerce").astype("Int64").astype(str)

print(f"NAV rows: {len(nav):,}  |  Funds: {nav['amfi_code'].nunique()}")
nav.head(3)""")))

cells.append(code(textwrap.dedent("""\
# Compute daily returns per fund
nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()
nav = nav.dropna(subset=["daily_return"])

print("Daily Return Statistics (all funds combined):")
stats = nav["daily_return"].describe()
for k, v in stats.items():
    print(f"  {k:8s}: {v*100:.4f}%")

# Distribution plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(nav["daily_return"] * 100, bins=150, color="#4F81BD",
        edgecolor="white", linewidth=0.2, alpha=0.85)
ax.axvline(0, color="red", linewidth=1.5, linestyle="--", label="Zero return")
ax.set_xlabel("Daily Return (%)")
ax.set_ylabel("Frequency")
ax.set_title("Distribution of Daily Returns — All 40 Funds")
ax.legend()
plt.tight_layout()
plt.show()
print("Histogram rendered.")""")))

# ── Task 2 ─────────────────────────────────────────────────────────────────
cells.append(md("## Task 2 — CAGR Table (1yr / 3yr / 5yr)\n`CAGR = (NAV_end / NAV_start)^(1/n) - 1`"))
cells.append(code(textwrap.dedent("""\
def cagr(series, years):
    s = series.dropna()
    n_days = years * TRADING_DAYS
    if len(s) < n_days:
        return np.nan
    return (s.iloc[-1] / s.iloc[-int(n_days)]) ** (1 / years) - 1

cagr_rows = []
for code, grp in nav.groupby("amfi_code"):
    s = grp.set_index("date")["nav"].sort_index()
    cagr_rows.append({
        "amfi_code":  code,
        "cagr_1yr":   cagr(s, 1),
        "cagr_3yr":   cagr(s, 3),
        "cagr_5yr":   cagr(s, 5),
    })

cagr_df = (pd.DataFrame(cagr_rows)
           .merge(funds[["amfi_code","scheme_name","category","expense_ratio_pct"]],
                  on="amfi_code", how="left")
           .sort_values("cagr_3yr", ascending=False)
           .reset_index(drop=True))

print(f"CAGR computed for {len(cagr_df)} funds")
print(f"3yr NaN count: {cagr_df['cagr_3yr'].isna().sum()}")
print()
display(cagr_df[["amfi_code","scheme_name","cagr_1yr","cagr_3yr","cagr_5yr"]].round(4))""")))

# ── Task 3 ─────────────────────────────────────────────────────────────────
cells.append(md("## Task 3 — Sharpe Ratio\n`Sharpe = (mean(Rp) - Rf) / std(Rp) × √252`   |   Rf = 6.5% / 252"))
cells.append(code(textwrap.dedent("""\
sharpe_rows = []
for code, grp in nav.groupby("amfi_code"):
    r = grp["daily_return"].dropna()
    excess = r - RF_DAILY
    std    = r.std()
    sharpe_rows.append({
        "amfi_code":    code,
        "sharpe_ratio": (excess.mean() / std * np.sqrt(TRADING_DAYS)) if std > 0 else np.nan
    })

sharpe_df = (pd.DataFrame(sharpe_rows)
             .merge(funds[["amfi_code","scheme_name"]], on="amfi_code", how="left")
             .sort_values("sharpe_ratio", ascending=False)
             .reset_index(drop=True))

print("Top 15 Funds by Sharpe Ratio:")
display(sharpe_df[["amfi_code","scheme_name","sharpe_ratio"]].head(15).round(4))""")))

# ── Task 4 ─────────────────────────────────────────────────────────────────
cells.append(md("## Task 4 — Sortino Ratio\nSame as Sharpe but denominator = std of **negative** return days only."))
cells.append(code(textwrap.dedent("""\
sortino_rows = []
for code, grp in nav.groupby("amfi_code"):
    r      = grp["daily_return"].dropna()
    excess = r - RF_DAILY
    down   = excess[excess < 0]
    dstd   = down.std()
    sortino_rows.append({
        "amfi_code":     code,
        "sortino_ratio": (excess.mean() / dstd * np.sqrt(TRADING_DAYS)) if dstd > 0 else np.nan
    })

sortino_df = pd.DataFrame(sortino_rows)

# Merge into one metrics table
metrics = (sharpe_df[["amfi_code","scheme_name","sharpe_ratio"]]
           .merge(sortino_df, on="amfi_code", how="left"))

print("Sharpe vs Sortino (top 10):")
display(metrics.head(10).round(4))""")))

# ── Task 5 ─────────────────────────────────────────────────────────────────
cells.append(md("## Task 5 — Alpha & Beta (OLS vs Nifty 100)\n`scipy.stats.linregress`  |  Alpha annualised = intercept × 252"))
cells.append(code(textwrap.dedent("""\
bench = pd.read_csv(PROCESSED / "10_benchmark_indices.csv", parse_dates=["date"])
bench = bench.sort_values("date")

# Nifty 100 daily returns
nifty100 = (bench[bench["index_name"] == "NIFTY100"]
            .set_index("date")["close_value"]
            .pct_change().dropna())

print(f"Nifty100 return rows: {len(nifty100)}")
print(f"Date range: {nifty100.index.min().date()} → {nifty100.index.max().date()}")""")))

cells.append(code(textwrap.dedent("""\
ab_rows = []
for code, grp in nav.groupby("amfi_code"):
    fund_ret = grp.set_index("date")["daily_return"].dropna()
    common   = fund_ret.index.intersection(nifty100.index)
    if len(common) < 60:
        ab_rows.append({"amfi_code": code, "alpha": np.nan, "beta": np.nan, "r_squared": np.nan})
        continue
    y = fund_ret.loc[common].values
    x = nifty100.loc[common].values
    slope, intercept, r, p, se = linregress(x, y)
    ab_rows.append({
        "amfi_code": code,
        "alpha":     intercept * TRADING_DAYS * 100,   # annualised %
        "beta":      round(slope, 4),
        "r_squared": round(r**2, 4),
    })

alpha_beta = (pd.DataFrame(ab_rows)
              .merge(funds[["amfi_code","scheme_name","category"]], on="amfi_code", how="left")
              .sort_values("alpha", ascending=False)
              .reset_index(drop=True))

# Save
alpha_beta[["amfi_code","scheme_name","category","alpha","beta","r_squared"]].to_csv(
    REPORTS / "alpha_beta.csv", index=False)
print(f"Saved reports/alpha_beta.csv  ({len(alpha_beta)} rows)")

print("\\nTop 10 Funds by Alpha:")
display(alpha_beta[["scheme_name","alpha","beta","r_squared"]].head(10).round(4))""")))

# ── Task 6 ─────────────────────────────────────────────────────────────────
cells.append(md("## Task 6 — Maximum Drawdown\n`drawdown = nav / running_max - 1`  |  Find worst trough and its peak."))
cells.append(code(textwrap.dedent("""\
dd_rows = []
for code, grp in nav.groupby("amfi_code"):
    g = grp.set_index("date")["nav"].sort_index()
    running_max  = g.cummax()
    drawdown     = g / running_max - 1
    max_dd       = drawdown.min()
    trough_date  = drawdown.idxmin()
    # peak = last time running_max was updated before trough
    peak_date    = running_max.loc[:trough_date].idxmax()
    dd_rows.append({
        "amfi_code":    code,
        "max_drawdown": max_dd,
        "peak_date":    str(peak_date)[:10],
        "trough_date":  str(trough_date)[:10],
    })

dd_df = pd.DataFrame(dd_rows)

print("5 Worst Drawdowns:")
worst = (dd_df.merge(funds[["amfi_code","scheme_name"]], on="amfi_code", how="left")
             .sort_values("max_drawdown")
             .head(5))
display(worst[["scheme_name","max_drawdown","peak_date","trough_date"]].round(4))""")))

# ── Task 7 ─────────────────────────────────────────────────────────────────
cells.append(md("## Task 7 — Fund Scorecard (0–100 Composite)\n`30% CAGR3yr + 25% Sharpe + 20% Alpha + 15% Expense(inv) + 10% MaxDD(inv)`"))
cells.append(code(textwrap.dedent("""\
# Build master metrics table
sc = (cagr_df[["amfi_code","scheme_name","category","expense_ratio_pct","cagr_3yr"]]
      .merge(sharpe_df[["amfi_code","sharpe_ratio"]], on="amfi_code", how="left")
      .merge(sortino_df, on="amfi_code", how="left")
      .merge(alpha_beta[["amfi_code","alpha","beta","r_squared"]], on="amfi_code", how="left")
      .merge(dd_df[["amfi_code","max_drawdown","peak_date","trough_date"]], on="amfi_code", how="left"))

n = len(sc)

def pct_rank(col, ascending=False):
    \"\"\"Percentile rank 0-100; ascending=False means higher value → higher score.\"\"\"
    r = sc[col].rank(ascending=ascending, na_option="bottom")
    return (r - 1) / (n - 1) * 100

sc["score_cagr3"]  = pct_rank("cagr_3yr",         ascending=False)
sc["score_sharpe"] = pct_rank("sharpe_ratio",      ascending=False)
sc["score_alpha"]  = pct_rank("alpha",             ascending=False)
sc["score_exp"]    = pct_rank("expense_ratio_pct", ascending=True)   # lower = better
sc["score_dd"]     = pct_rank("max_drawdown",      ascending=False)  # less negative = better

sc["composite_score"] = (
    0.30 * sc["score_cagr3"]  +
    0.25 * sc["score_sharpe"] +
    0.20 * sc["score_alpha"]  +
    0.15 * sc["score_exp"]    +
    0.10 * sc["score_dd"]
)

sc = sc.sort_values("composite_score", ascending=False).reset_index(drop=True)
sc["rank"] = sc.index + 1

# Save
out_cols = ["rank","amfi_code","scheme_name","category","cagr_3yr","sharpe_ratio",
            "sortino_ratio","alpha","beta","expense_ratio_pct","max_drawdown",
            "peak_date","trough_date","composite_score"]
sc[out_cols].to_csv(REPORTS / "fund_scorecard.csv", index=False)
print(f"Saved reports/fund_scorecard.csv  ({len(sc)} rows)")
print()
print("Full Scorecard (all 40 funds):")
display(sc[["rank","scheme_name","category","cagr_3yr","sharpe_ratio",
            "alpha","expense_ratio_pct","max_drawdown","composite_score"]].round(3))""")))

# ── Task 8 ─────────────────────────────────────────────────────────────────
cells.append(md("## Task 8 — Benchmark Comparison Chart\nTop 5 funds vs Nifty 50 & Nifty 100, last 3 years, normalised to 100."))
cells.append(code(textwrap.dedent("""\
# Top 5 funds by composite score
top5 = sc.head(5)
top5_codes = [str(c) for c in top5["amfi_code"].tolist()]
top5_names = {
    str(r["amfi_code"]): str(r["scheme_name"]) if pd.notna(r["scheme_name"]) else str(r["amfi_code"])
    for _, r in top5.iterrows()
}

# Ensure date is datetime in nav
nav["date"] = pd.to_datetime(nav["date"])
bench["date"] = pd.to_datetime(bench["date"])

# 3-year cutoff
latest = nav["date"].max()
cutoff = latest - pd.DateOffset(years=3)

# Wide NAV matrix for top 5
nav_top5 = (nav.assign(amfi_code=nav["amfi_code"].astype(str))
            [lambda d: d["amfi_code"].isin(top5_codes)]
            .query("date >= @cutoff")
            .pivot(index="date", columns="amfi_code", values="nav"))

# Benchmark series
bench_pivot = (bench.query("date >= @cutoff")
               .pivot(index="date", columns="index_name", values="close_value"))

print(f"NAV top5 shape: {nav_top5.shape}")
print(f"Bench pivot shape: {bench_pivot.shape}")

# Normalise to 100 at first valid row
def normalise(df):
    first_valid = df.apply(lambda c: c.first_valid_index())
    result = df.copy()
    for col in df.columns:
        fv = first_valid[col]
        if fv is not None and df.loc[fv, col] != 0:
            result[col] = df[col] / df.loc[fv, col] * 100
    return result

nav_norm   = normalise(nav_top5)
bench_norm = normalise(bench_pivot[["NIFTY50","NIFTY100"]])

# Tracking error per fund vs Nifty 100
nifty100_ret = bench_pivot["NIFTY100"].pct_change().dropna()
te_info = {}
for code in top5_codes:
    if code not in nav_top5.columns:
        continue
    f_ret  = nav_top5[code].pct_change().dropna()
    common = f_ret.index.intersection(nifty100_ret.index)
    if len(common) > 30:
        diff = f_ret.loc[common] - nifty100_ret.loc[common]
        te   = diff.std() * np.sqrt(TRADING_DAYS) * 100
        te_info[code] = te

print(f"Tracking errors computed: {len(te_info)}")
for code, te in te_info.items():
    name = top5_names.get(str(code), str(code))
    print(f"  {name[:40]}: {float(te):.2f}%")""")))

cells.append(code(textwrap.dedent("""\
COLORS_FUND  = ["#E74C3C","#3498DB","#2ECC71","#F39C12","#9B59B6"]
COLORS_BENCH = {"NIFTY50":"#2C3E50","NIFTY100":"#7F8C8D"}

fig, ax = plt.subplots(figsize=(14, 7))

# Benchmark lines
for idx in ["NIFTY50","NIFTY100"]:
    if idx in bench_norm.columns:
        ax.plot(bench_norm.index, bench_norm[idx],
                color=COLORS_BENCH[idx], linewidth=2,
                linestyle="--" if idx=="NIFTY50" else "-.",
                label=idx, alpha=0.85)

# Fund lines
for i, code in enumerate(top5_codes):
    if code not in nav_norm.columns:
        continue
    name = top5_names.get(str(code), str(code))[:28]
    ax.plot(nav_norm.index, nav_norm[code],
            color=COLORS_FUND[i], linewidth=1.8, label=name)

# Tracking error annotation box
te_text = "Tracking Error vs NIFTY100:\\n"
for i, code in enumerate(top5_codes):
    if code in te_info:
        nm = top5_names.get(str(code), str(code))[:22]
        te_text += f"  {nm}: {float(te_info[code]):.2f}%\\n"
ax.text(0.01, 0.97, te_text.strip(),
        transform=ax.transAxes, fontsize=7.5,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow",
                  edgecolor="grey", alpha=0.85))

ax.axhline(100, color="grey", linewidth=0.7, linestyle=":")
ax.set_ylabel("Normalised Price (100 = start)")
ax.set_title("Top 5 Funds vs Nifty 50 & Nifty 100 — 3 Year Performance", fontsize=13)
ax.legend(loc="upper left", fontsize=8, ncol=2)
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %Y"))
plt.xticks(rotation=30)
plt.tight_layout()

out_path = CHARTS / "benchmark_comparison.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight")
plt.show()
print(f"Saved {out_path}  ({os.path.getsize(out_path)/1024:.1f} KB)")""")))

# ── Final Summary ─────────────────────────────────────────────────────────────
cells.append(md("## Final Summary — Top 10 Funds"))
cells.append(code(textwrap.dedent("""\
# Tracking error for all funds (top 5 computed above)
te_series = pd.Series(te_info, name="tracking_error_pct").rename_axis("amfi_code").reset_index()

summary = (sc[["rank","amfi_code","scheme_name","composite_score","sharpe_ratio",
               "alpha","cagr_3yr","max_drawdown"]]
           .head(10)
           .merge(te_series, on="amfi_code", how="left"))

print("="*80)
print("TOP 10 FUNDS — BLUESTOCK PERFORMANCE SCORECARD")
print("="*80)
display(summary.set_index("rank").round(3))

print()
print("Output files:")
for f in [REPORTS/"fund_scorecard.csv", REPORTS/"alpha_beta.csv",
          CHARTS/"benchmark_comparison.png"]:
    size = os.path.getsize(f)/1024 if f.exists() else 0
    status = "OK" if f.exists() else "MISSING"
    print(f"  [{status}] {str(f):<50} {size:.1f} KB")""")))

# ── Assemble notebook ──────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.9.0"},
    },
    "cells": cells,
}

out = Path("Performance_Analytics.ipynb")
with open(out, "w") as f:
    json.dump(nb, f, indent=1)

print(f"Notebook written: {out.resolve()}")
print(f"Total cells: {len(cells)}")
