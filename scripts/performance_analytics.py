"""
Performance Analytics — Day 4
Generates: fund_scorecard.csv, alpha_beta.csv, cagr_metrics.csv,
           benchmark_comparison.png, daily_returns_dist.png, sharpe_ranking.png
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import linregress
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
CHARTS    = ROOT / "reports" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

RF_ANNUAL = 0.065          # RBI repo-rate proxy
RF_DAILY  = RF_ANNUAL / 252
TRADING_DAYS = 252

# ── Load Data ─────────────────────────────────────────────────────────────────
print("Loading data …")
nav   = pd.read_csv(PROCESSED / "clean_nav.csv",   parse_dates=["date"])
funds = pd.read_csv(PROCESSED / "01_fund_master.csv")
bench = pd.read_csv(PROCESSED / "10_benchmark_indices.csv", parse_dates=["date"])

nav["amfi_code"]   = nav["amfi_code"].astype(str).str.strip()
funds["amfi_code"] = funds["amfi_code"].astype(str).str.strip()
bench = bench.sort_values("date")

# Wide NAV matrix  (dates × funds)
nav_wide = (
    nav.sort_values("date")
       .pivot(index="date", columns="amfi_code", values="nav")
)
print(f"  NAV wide: {nav_wide.shape[0]} days × {nav_wide.shape[1]} funds")

# ── 1. Daily Returns ──────────────────────────────────────────────────────────
print("Computing daily returns …")
ret_wide = nav_wide.pct_change()   # NAV_t / NAV_t-1  − 1

# Sanity check
desc = ret_wide.stack().describe()
print(f"  Return stats — mean={desc['mean']*100:.4f}% "
      f"std={desc['std']*100:.4f}% "
      f"min={desc['min']*100:.2f}% max={desc['max']*100:.2f}%")

# Plot: daily-return distribution
fig, ax = plt.subplots(figsize=(10, 5))
all_rets = ret_wide.stack().dropna()
ax.hist(all_rets * 100, bins=120, color="#4F81BD", edgecolor="white", linewidth=0.3)
ax.axvline(0, color="red", linewidth=1.2, linestyle="--", label="Zero")
ax.set_xlabel("Daily Return (%)")
ax.set_ylabel("Frequency")
ax.set_title("Distribution of Daily Returns — All 40 Funds")
ax.legend()
plt.tight_layout()
fig.savefig(CHARTS / "daily_returns_dist.png", dpi=150)
plt.close(fig)
print("  Saved: daily_returns_dist.png")

# ── 2. CAGR  (1yr / 3yr / 5yr) ───────────────────────────────────────────────
print("Computing CAGR …")

def cagr(series, years):
    s = series.dropna()
    if len(s) < 2:
        return np.nan
    return (s.iloc[-1] / s.iloc[0]) ** (1 / years) - 1

cagr_rows = []
for code in nav_wide.columns:
    s = nav_wide[code].dropna()
    row = {"amfi_code": code,
           "cagr_1yr_pct": cagr(s.iloc[-252:],  1) * 100 if len(s) >= 252  else np.nan,
           "cagr_3yr_pct": cagr(s.iloc[-756:],  3) * 100 if len(s) >= 756  else np.nan,
           "cagr_5yr_pct": cagr(s.iloc[-1260:], 5) * 100 if len(s) >= 1260 else np.nan}
    cagr_rows.append(row)

cagr_df = pd.DataFrame(cagr_rows)
cagr_df = cagr_df.merge(funds[["amfi_code","scheme_name","fund_house","category"]], on="amfi_code", how="left")
cagr_df = cagr_df.sort_values("cagr_3yr_pct", ascending=False)
print(f"  CAGR computed for {len(cagr_df)} funds")

# ── 3. Sharpe Ratio ───────────────────────────────────────────────────────────
print("Computing Sharpe ratio …")

def sharpe(daily_rets):
    er = daily_rets - RF_DAILY
    std = er.std()
    return (er.mean() / std * np.sqrt(TRADING_DAYS)) if std > 0 else np.nan

sharpe_rows = []
for code in ret_wide.columns:
    r = ret_wide[code].dropna()
    sharpe_rows.append({"amfi_code": code, "sharpe_ratio": sharpe(r)})

sharpe_df = pd.DataFrame(sharpe_rows)

# Plot: Sharpe ranking (top 20)
merged_sh = sharpe_df.merge(funds[["amfi_code","scheme_name"]], on="amfi_code")
top20 = merged_sh.nlargest(20, "sharpe_ratio")
fig, ax = plt.subplots(figsize=(12, 7))
colors = ["#2ECC71" if v > 1 else "#3498DB" for v in top20["sharpe_ratio"]]
bars = ax.barh(top20["scheme_name"].str[:35], top20["sharpe_ratio"], color=colors)
ax.axvline(1, color="red", linestyle="--", linewidth=1, label="Sharpe = 1")
ax.set_xlabel("Sharpe Ratio")
ax.set_title("Top 20 Funds — Sharpe Ratio (Rf = 6.5%)")
ax.legend()
plt.tight_layout()
fig.savefig(CHARTS / "sharpe_ratio_ranking.png", dpi=150)
plt.close(fig)
print("  Saved: sharpe_ratio_ranking.png")

# ── 4. Sortino Ratio ──────────────────────────────────────────────────────────
print("Computing Sortino ratio …")

def sortino(daily_rets):
    er = daily_rets - RF_DAILY
    down = er[er < 0]
    dstd = down.std()
    return (er.mean() / dstd * np.sqrt(TRADING_DAYS)) if dstd > 0 else np.nan

sortino_rows = []
for code in ret_wide.columns:
    r = ret_wide[code].dropna()
    sortino_rows.append({"amfi_code": code, "sortino_ratio": sortino(r)})

sortino_df = pd.DataFrame(sortino_rows)

# ── 5. Alpha & Beta (OLS vs NIFTY100) ────────────────────────────────────────
print("Computing Alpha & Beta …")

# Prepare benchmark returns
bench_100 = (bench[bench["index_name"] == "NIFTY100"]
             .set_index("date")["close_value"]
             .sort_index()
             .pct_change()
             .dropna())

ab_rows = []
for code in ret_wide.columns:
    fund_r = ret_wide[code].dropna()
    common  = fund_r.index.intersection(bench_100.index)
    if len(common) < 60:
        ab_rows.append({"amfi_code": code, "alpha": np.nan, "beta": np.nan, "r_squared": np.nan})
        continue
    y = fund_r.loc[common].values
    x = bench_100.loc[common].values
    slope, intercept, r, p, se = linregress(x, y)
    ab_rows.append({
        "amfi_code": code,
        "alpha":     intercept * TRADING_DAYS * 100,   # annualised %
        "beta":      slope,
        "r_squared": r ** 2
    })

alpha_beta_df = pd.DataFrame(ab_rows)
alpha_beta_df = alpha_beta_df.merge(funds[["amfi_code","scheme_name","fund_house","category"]], on="amfi_code", how="left")
alpha_beta_df = alpha_beta_df.sort_values("alpha", ascending=False)
print(f"  Alpha/Beta computed for {len(alpha_beta_df)} funds")

# ── 6. Maximum Drawdown ───────────────────────────────────────────────────────
print("Computing Maximum Drawdown …")

def max_drawdown(nav_series):
    s = nav_series.dropna()
    if len(s) < 2:
        return np.nan, None, None
    roll_max = s.expanding().max()
    dd = (s / roll_max) - 1
    worst_idx = dd.idxmin()
    peak_idx  = roll_max.loc[:worst_idx].idxmax()
    return dd.min() * 100, peak_idx, worst_idx

dd_rows = []
for code in nav_wide.columns:
    val, peak, trough = max_drawdown(nav_wide[code])
    dd_rows.append({
        "amfi_code":        code,
        "max_drawdown_pct": val,
        "drawdown_peak":    str(peak)[:10] if peak else None,
        "drawdown_trough":  str(trough)[:10] if trough else None
    })

dd_df = pd.DataFrame(dd_rows)

# ── 7. Composite Fund Scorecard ───────────────────────────────────────────────
print("Building Fund Scorecard …")

scorecard = funds[["amfi_code","scheme_name","fund_house","category","expense_ratio_pct"]].copy()
scorecard = (scorecard
    .merge(cagr_df[["amfi_code","cagr_1yr_pct","cagr_3yr_pct","cagr_5yr_pct"]], on="amfi_code", how="left")
    .merge(sharpe_df,  on="amfi_code", how="left")
    .merge(sortino_df, on="amfi_code", how="left")
    .merge(alpha_beta_df[["amfi_code","alpha","beta","r_squared"]], on="amfi_code", how="left")
    .merge(dd_df[["amfi_code","max_drawdown_pct","drawdown_peak","drawdown_trough"]], on="amfi_code", how="left")
)

# Rank components (higher rank = better, 1 = best)
n = len(scorecard)
scorecard["rank_cagr3"]    = scorecard["cagr_3yr_pct"].rank(ascending=False)
scorecard["rank_sharpe"]   = scorecard["sharpe_ratio"].rank(ascending=False)
scorecard["rank_alpha"]    = scorecard["alpha"].rank(ascending=False)
scorecard["rank_exp_inv"]  = scorecard["expense_ratio_pct"].rank(ascending=True)   # lower = better
scorecard["rank_dd_inv"]   = scorecard["max_drawdown_pct"].rank(ascending=False)   # less negative = better

# Convert ranks to 0–100 scores
def rank_to_score(rank_col):
    return (1 - (rank_col - 1) / (n - 1)) * 100

scorecard["score_cagr3"]   = rank_to_score(scorecard["rank_cagr3"])
scorecard["score_sharpe"]  = rank_to_score(scorecard["rank_sharpe"])
scorecard["score_alpha"]   = rank_to_score(scorecard["rank_alpha"])
scorecard["score_exp"]     = rank_to_score(scorecard["rank_exp_inv"])
scorecard["score_dd"]      = rank_to_score(scorecard["rank_dd_inv"])

# Composite: 30% cagr3 + 25% sharpe + 20% alpha + 15% expense(inv) + 10% drawdown(inv)
scorecard["bluestock_score"] = (
      0.30 * scorecard["score_cagr3"]
    + 0.25 * scorecard["score_sharpe"]
    + 0.20 * scorecard["score_alpha"]
    + 0.15 * scorecard["score_exp"]
    + 0.10 * scorecard["score_dd"]
)

scorecard = scorecard.sort_values("bluestock_score", ascending=False).reset_index(drop=True)
scorecard["rank"] = scorecard.index + 1

print(f"  Scorecard built: {len(scorecard)} funds")
print("\nTop 10 Funds:")
cols_show = ["rank","scheme_name","bluestock_score","cagr_3yr_pct","sharpe_ratio","alpha"]
print(scorecard[cols_show].head(10).to_string(index=False))

# Scorecard chart
top15 = scorecard.head(15)
fig, ax = plt.subplots(figsize=(13, 8))
cmap = plt.cm.RdYlGn
norm_scores = (top15["bluestock_score"] - top15["bluestock_score"].min()) / \
              (top15["bluestock_score"].max() - top15["bluestock_score"].min() + 1e-9)
bar_colors  = [cmap(v) for v in norm_scores]
bars = ax.barh(
    top15["scheme_name"].str[:40].iloc[::-1],
    top15["bluestock_score"].iloc[::-1],
    color=bar_colors[::-1], edgecolor="white", linewidth=0.5
)
for bar, score in zip(bars, top15["bluestock_score"].iloc[::-1]):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
            f"{score:.1f}", va="center", fontsize=9)
ax.set_xlabel("Bluestock Score (0–100)")
ax.set_title("Top 15 Funds — Bluestock Composite Scorecard\n"
             "30% CAGR(3yr) + 25% Sharpe + 20% Alpha + 15% Expense(inv) + 10% MaxDD(inv)",
             fontsize=11)
ax.set_xlim(0, 115)
plt.tight_layout()
fig.savefig(CHARTS / "fund_scorecard_top15.png", dpi=150)
plt.close(fig)
print("  Saved: fund_scorecard_top15.png")

# ── 8. Benchmark Comparison Chart ────────────────────────────────────────────
print("Creating benchmark comparison chart …")

# Top 5 funds by bluestock_score
top5_codes = scorecard.head(5)["amfi_code"].tolist()
top5_names = scorecard.head(5).set_index("amfi_code")["scheme_name"].to_dict()

# 3-year window
cutoff = nav_wide.index.max() - pd.DateOffset(years=3)
nav_3y = nav_wide.loc[nav_wide.index >= cutoff]
bench_wide = bench.pivot(index="date", columns="index_name", values="close_value")
bench_3y   = bench_wide.loc[bench_wide.index >= cutoff]

fig, ax = plt.subplots(figsize=(14, 7))
colors_fund = plt.cm.tab10.colors

# Benchmark lines
for idx_name, ls, lw in [("NIFTY50","--",2), ("NIFTY100","-.",2)]:
    if idx_name in bench_3y.columns:
        s = bench_3y[idx_name].dropna()
        norm = (s / s.iloc[0] - 1) * 100
        ax.plot(norm.index, norm.values, linestyle=ls, linewidth=lw,
                color="black", label=idx_name, alpha=0.8)

# Fund lines
tracking_rows = []
for i, code in enumerate(top5_codes):
    if code not in nav_3y.columns:
        continue
    s = nav_3y[code].dropna()
    norm = (s / s.iloc[0] - 1) * 100
    label = top5_names.get(code, code)[:30]
    ax.plot(norm.index, norm.values, linewidth=1.8,
            color=colors_fund[i], label=label)

    # Tracking error vs NIFTY100
    if "NIFTY100" in bench_3y.columns:
        b_ret  = bench_3y["NIFTY100"].pct_change().dropna()
        f_ret  = nav_3y[code].pct_change().dropna()
        common = f_ret.index.intersection(b_ret.index)
        if len(common) > 30:
            diff = f_ret.loc[common] - b_ret.loc[common]
            te   = diff.std() * np.sqrt(TRADING_DAYS) * 100
            tracking_rows.append({"amfi_code": code, "scheme_name": label, "tracking_error_pct": te})

ax.axhline(0, color="grey", linewidth=0.8, linestyle=":")
ax.set_ylabel("Cumulative Return (%)")
ax.set_title("Top 5 Funds vs Nifty 50 & Nifty 100 — 3-Year Performance")
ax.legend(loc="upper left", fontsize=8)
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %Y"))
plt.xticks(rotation=30)
plt.tight_layout()
fig.savefig(CHARTS / "benchmark_comparison.png", dpi=150)
plt.close(fig)
print("  Saved: benchmark_comparison.png")

if tracking_rows:
    te_df = pd.DataFrame(tracking_rows)
    print("\nTracking Error vs NIFTY100:")
    print(te_df.to_string(index=False))

# ── Save CSVs ─────────────────────────────────────────────────────────────────
print("\nSaving CSV deliverables …")

# fund_scorecard.csv
out_cols = ["rank","amfi_code","scheme_name","fund_house","category",
            "cagr_1yr_pct","cagr_3yr_pct","cagr_5yr_pct",
            "sharpe_ratio","sortino_ratio","alpha","beta","r_squared",
            "max_drawdown_pct","drawdown_peak","drawdown_trough",
            "expense_ratio_pct","bluestock_score"]
scorecard[out_cols].to_csv(PROCESSED / "fund_scorecard.csv", index=False)
print(f"  fund_scorecard.csv — {len(scorecard)} rows")

# alpha_beta.csv
alpha_beta_df[["amfi_code","scheme_name","fund_house","category",
               "alpha","beta","r_squared"]].to_csv(PROCESSED / "alpha_beta.csv", index=False)
print(f"  alpha_beta.csv    — {len(alpha_beta_df)} rows")

# cagr_metrics.csv
cagr_df[["amfi_code","scheme_name","fund_house","category",
          "cagr_1yr_pct","cagr_3yr_pct","cagr_5yr_pct"]].to_csv(PROCESSED / "cagr_metrics.csv", index=False)
print(f"  cagr_metrics.csv  — {len(cagr_df)} rows")

# ── Final Summary ─────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("DAY 4 PERFORMANCE ANALYTICS — COMPLETE")
print("="*70)

from pathlib import Path as P
import os
for f in ["fund_scorecard.csv","alpha_beta.csv","cagr_metrics.csv"]:
    p = PROCESSED / f
    print(f"  [CSV]   {f:<35} {os.path.getsize(p)/1024:.1f} KB")
for f in ["daily_returns_dist.png","sharpe_ratio_ranking.png",
          "fund_scorecard_top15.png","benchmark_comparison.png"]:
    p = CHARTS / f
    if p.exists():
        print(f"  [PNG]   {f:<35} {os.path.getsize(p)/1024:.1f} KB")
print("="*70)
