"""
compute_metrics.py
------------------
Bluestock MF Capstone — Performance Metrics Computation (D4 Deliverable)
=========================================================================
Wraps performance_analytics.py to produce all quantitative metrics:
  • CAGR (1yr / 3yr / 5yr)  — annualised using 252 trading days
  • Sharpe Ratio             — (Rp - Rf) / sigma_p * sqrt(252), Rf = 6.5%
  • Sortino Ratio            — downside-deviation denominator
  • Alpha & Beta             — OLS regression vs NIFTY 100
  • Maximum Drawdown         — peak-to-trough via expanding window
  • Composite Bluestock Score— weighted rank-based composite

Outputs (written to reports/ and data/processed/):
  reports/fund_scorecard.csv   — full 40-fund scorecard with ranks
  reports/alpha_beta.csv       — alpha, beta, R-squared per fund
  reports/charts/              — benchmark_comparison.png + others

Usage (from project root):
    python scripts/compute_metrics.py

Notes:
  - Uses 252 / n_trading_days for annualisation (not calendar days)
  - Risk-free rate: RBI repo-rate proxy = 6.5% p.a. = 6.5/252 per day
  - All paths use pathlib.Path — no hard-coded strings
"""

from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
TARGET   = BASE_DIR / "scripts" / "performance_analytics.py"

print("=" * 60)
print("  Bluestock MF — compute_metrics.py")
print("  Delegating to: scripts/performance_analytics.py")
print("=" * 60)

if not TARGET.exists():
    print(f"  ❌ performance_analytics.py not found at {TARGET}")
    sys.exit(1)

result = subprocess.run(
    [sys.executable, str(TARGET)],
    cwd=str(BASE_DIR),
)

if result.returncode != 0:
    print("  ❌ compute_metrics failed — see output above")
    sys.exit(result.returncode)

print("\n  ✅ All metrics computed successfully.")
print("  Outputs:")
print("    reports/fund_scorecard.csv")
print("    reports/alpha_beta.csv")
print("    reports/charts/benchmark_comparison.png")
print("    reports/charts/sharpe_ratio_ranking.png")
print("    reports/charts/fund_scorecard_top15.png")
print("    reports/charts/daily_returns_dist.png")
