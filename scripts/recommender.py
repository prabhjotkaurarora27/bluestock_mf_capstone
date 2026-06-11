"""
Bluestock MF Fund Recommender System — Day 6
Content-based filtering: risk_appetite -> top N funds

Usage:
    from scripts.recommender import recommend_funds
    df = recommend_funds("Low")      # "Low" | "Moderate" | "High"

Run standalone:
    python scripts/recommender.py
"""

import os
import pandas as pd
from typing import Literal

BASE = "/Users/prabhjotkaur/Desktop/bluestock_mf_capstone"
PROC = os.path.join(BASE, "data", "processed")
RPT  = os.path.join(BASE, "reports")


def _load_merged() -> pd.DataFrame:
    """Merge scorecard + fund_master + clean_performance."""
    sc   = pd.read_csv(os.path.join(RPT,  "fund_scorecard.csv"))
    fm   = pd.read_csv(os.path.join(PROC, "01_fund_master.csv"))
    perf = pd.read_csv(os.path.join(PROC, "clean_performance.csv"))
    merged = (
        sc[["amfi_code", "sharpe_ratio", "alpha", "composite_score", "max_drawdown"]]
        .merge(fm[["amfi_code", "scheme_name", "fund_house", "category",
                   "sub_category", "expense_ratio_pct", "risk_category"]],
               on="amfi_code", how="left")
        .merge(perf[["amfi_code", "std_dev_ann_pct", "aum_crore",
                     "return_1yr_pct", "return_3yr_pct"]].drop_duplicates("amfi_code"),
               on="amfi_code", how="left")
    )
    return merged.dropna(subset=["std_dev_ann_pct", "sharpe_ratio"])


def recommend_funds(
    risk_appetite: Literal["Low", "Moderate", "High"],
    top_n: int = 3
) -> pd.DataFrame:
    """
    Recommend top mutual funds based on investor risk appetite.

    Filtering logic (percentile-derived, not hardcoded):
        Low      -> std_dev <= p33 AND sharpe > 0.5
        Moderate -> p33 < std_dev <= p67 AND sharpe > 0.8
        High     -> std_dev > p67 AND sharpe > 0.8

    Args:
        risk_appetite: "Low" | "Moderate" | "High"
        top_n:         Number of recommendations (default 3)

    Returns:
        DataFrame ranked 1..top_n with scheme details.

    Raises:
        ValueError: If risk_appetite is not valid.

    Example:
        >>> df = recommend_funds("Moderate", top_n=5)
        >>> print(df[["scheme_name", "sharpe_ratio"]].to_string())
    """
    valid = {"Low", "Moderate", "High"}
    if risk_appetite not in valid:
        raise ValueError(
            f"Invalid risk_appetite='{risk_appetite}'. Choose from: {sorted(valid)}"
        )

    merged = _load_merged()
    p33 = merged["std_dev_ann_pct"].quantile(0.33)
    p67 = merged["std_dev_ann_pct"].quantile(0.67)

    # Primary filter
    if risk_appetite == "Low":
        mask = (merged["std_dev_ann_pct"] <= p33) & (merged["sharpe_ratio"] > 0.5)
    elif risk_appetite == "Moderate":
        mask = ((merged["std_dev_ann_pct"] > p33) &
                (merged["std_dev_ann_pct"] <= p67) &
                (merged["sharpe_ratio"] > 0.8))
    else:
        mask = (merged["std_dev_ann_pct"] > p67) & (merged["sharpe_ratio"] > 0.8)

    filtered = merged[mask].copy()

    # Fallback: relax Sharpe gate if fewer than top_n results
    if len(filtered) < top_n:
        if risk_appetite == "Low":
            filtered = merged[merged["std_dev_ann_pct"] <= p33].copy()
        elif risk_appetite == "Moderate":
            filtered = merged[(merged["std_dev_ann_pct"] > p33) &
                              (merged["std_dev_ann_pct"] <= p67)].copy()
        else:
            filtered = merged[merged["std_dev_ann_pct"] > p67].copy()

    cols = ["scheme_name", "fund_house", "category", "sub_category",
            "sharpe_ratio", "std_dev_ann_pct", "composite_score",
            "return_1yr_pct", "return_3yr_pct", "expense_ratio_pct"]
    result = (filtered
              .sort_values(["composite_score", "sharpe_ratio"], ascending=False)
              .head(top_n)[cols]
              .reset_index(drop=True))
    result.index = range(1, len(result) + 1)
    return result


def fund_distribution_summary() -> pd.DataFrame:
    """Show fund count per risk tier."""
    merged = _load_merged()
    p33 = merged["std_dev_ann_pct"].quantile(0.33)
    p67 = merged["std_dev_ann_pct"].quantile(0.67)
    rows = []
    for label, lo, hi in [("Low Risk", 0, p33),
                           ("Moderate Risk", p33, p67),
                           ("High Risk", p67, 999)]:
        n = ((merged["std_dev_ann_pct"] > lo) & (merged["std_dev_ann_pct"] <= hi)).sum()
        rows.append({"Risk Tier": label,
                     "Std Dev Range": f"{lo:.1f}%–{hi:.1f}%",
                     "Fund Count": n,
                     "% of Universe": f"{n/len(merged)*100:.0f}%"})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("=" * 65)
    print("  Bluestock MF Fund Recommender — All Risk Tiers")
    print("=" * 65)
    print("\nFund Universe Distribution:")
    print(fund_distribution_summary().to_string(index=False))
    for level in ("Low", "Moderate", "High"):
        print(f"\n{'─'*65}\n  {level.upper()} RISK — Top 3\n{'─'*65}")
        df = recommend_funds(level)
        print(df[["scheme_name", "sharpe_ratio", "std_dev_ann_pct",
                  "return_3yr_pct", "expense_ratio_pct"]].to_string())
    print()
