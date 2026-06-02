-- =============================================================
-- queries.sql
-- Bluestock MF Capstone — Analytical SQL Query Library
-- Database : data/db/bluestock_mf.db
-- Run      : sqlite3 data/db/bluestock_mf.db < sql/queries.sql
-- =============================================================

-- ─────────────────────────────────────────────────────────────
-- Q1 : Top 5 fund houses by LATEST AUM (most recent month)
-- ─────────────────────────────────────────────────────────────
-- NOTE: SUM over all dates would double-count history;
--       filter to the single latest date for a true snapshot.
SELECT
    fund_house,
    ROUND(SUM(aum_crore) / 1e5, 2)  AS aum_lakh_crore,
    SUM(aum_crore)                   AS aum_crore,
    SUM(num_schemes)                 AS total_schemes
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
GROUP BY fund_house
ORDER BY aum_crore DESC
LIMIT 5;

-- ─────────────────────────────────────────────────────────────
-- Q2 : Average NAV per month per fund (with scheme name)
-- ─────────────────────────────────────────────────────────────
SELECT
    n.amfi_code,
    f.scheme_name,
    strftime('%Y-%m', n.date)    AS month,
    ROUND(MIN(n.nav), 4)         AS month_open_nav,
    ROUND(AVG(n.nav), 4)         AS avg_nav,
    ROUND(MAX(n.nav), 4)         AS month_high_nav
FROM fact_nav n
JOIN dim_fund f USING (amfi_code)
GROUP BY n.amfi_code, month
ORDER BY n.amfi_code, month;

-- ─────────────────────────────────────────────────────────────
-- Q3 : SIP inflow year-over-year growth
-- ─────────────────────────────────────────────────────────────
-- Table is fact_sip_inflows (not fact_sip_industry)
SELECT
    strftime('%Y', month)                  AS year,
    ROUND(SUM(sip_inflow_crore), 2)        AS total_sip_crore,
    ROUND(AVG(active_sip_accounts_crore), 4) AS avg_active_accounts_crore,
    ROUND(AVG(yoy_growth_pct), 2)          AS avg_yoy_growth_pct
FROM fact_sip_inflows
GROUP BY year
ORDER BY year;

-- ─────────────────────────────────────────────────────────────
-- Q4 : Total transactions by state (amount + count)
-- ─────────────────────────────────────────────────────────────
SELECT
    state,
    COUNT(*)                                  AS tx_count,
    ROUND(SUM(amount_inr) / 1e7, 2)          AS total_crore,
    ROUND(AVG(amount_inr), 0)                AS avg_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_crore DESC;

-- ─────────────────────────────────────────────────────────────
-- Q5 : Funds with expense ratio < 1% (Direct plans)
-- ─────────────────────────────────────────────────────────────
-- Uses fact_performance which has confirmed non-NULL expense_ratio_pct
-- dim_fund.expense_ratio_pct can be NULL for some rows
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.plan,
    p.expense_ratio_pct,
    p.return_3yr_pct
FROM fact_performance p
JOIN dim_fund f USING (amfi_code)
WHERE p.expense_ratio_pct < 1.0
ORDER BY p.expense_ratio_pct ASC;

-- ─────────────────────────────────────────────────────────────
-- Q6 : Top 10 best-performing funds by 3-year return
-- ─────────────────────────────────────────────────────────────
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    f.plan,
    p.return_1yr_pct,
    p.return_3yr_pct,
    p.return_5yr_pct,
    p.morningstar_rating,
    p.risk_grade
FROM fact_performance p
JOIN dim_fund f USING (amfi_code)
ORDER BY p.return_3yr_pct DESC
LIMIT 10;

-- ─────────────────────────────────────────────────────────────
-- Q7 : SIP vs Lumpsum vs Redemption split
-- ─────────────────────────────────────────────────────────────
SELECT
    transaction_type,
    COUNT(*)                             AS num_transactions,
    ROUND(SUM(amount_inr) / 1e7, 2)     AS total_crore,
    ROUND(AVG(amount_inr), 0)           AS avg_amount_inr,
    ROUND(100.0 * COUNT(*) /
          SUM(COUNT(*)) OVER (), 2)      AS pct_of_transactions
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_crore DESC;

-- ─────────────────────────────────────────────────────────────
-- Q8 : Top 5 funds by Sharpe ratio (risk-adjusted return)
-- ─────────────────────────────────────────────────────────────
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    p.sharpe_ratio,
    p.sortino_ratio,
    p.return_3yr_pct,
    p.max_drawdown_pct
FROM fact_performance p
JOIN dim_fund f USING (amfi_code)
ORDER BY p.sharpe_ratio DESC
LIMIT 5;

-- ─────────────────────────────────────────────────────────────
-- Q9 : Monthly SIP trend with 3-month rolling average
-- ─────────────────────────────────────────────────────────────
-- Table is fact_sip_inflows (not fact_sip_industry)
SELECT
    month,
    sip_inflow_crore,
    ROUND(
        AVG(sip_inflow_crore) OVER (
            ORDER BY month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2
    )  AS rolling_3m_avg_crore,
    yoy_growth_pct
FROM fact_sip_inflows
ORDER BY month;

-- ─────────────────────────────────────────────────────────────
-- Q10 : Gender-wise average investment amount (SIP only)
-- ─────────────────────────────────────────────────────────────
-- transaction_type = 'SIP' (uppercase) — that is the canonical value
SELECT
    gender,
    COUNT(*)                          AS num_transactions,
    COUNT(DISTINCT investor_id)       AS unique_investors,
    ROUND(AVG(amount_inr), 2)        AS avg_sip_amount_inr,
    ROUND(SUM(amount_inr) / 1e7, 2)  AS total_crore
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY gender
ORDER BY avg_sip_amount_inr DESC;

-- ─────────────────────────────────────────────────────────────
-- Q11 : City-tier breakdown — investor activity (T30 vs B30)
-- ─────────────────────────────────────────────────────────────
SELECT
    city_tier,
    COUNT(DISTINCT investor_id)       AS unique_investors,
    COUNT(*)                          AS total_transactions,
    ROUND(SUM(amount_inr) / 1e7, 2)  AS total_crore,
    ROUND(AVG(amount_inr), 0)        AS avg_ticket_size_inr
FROM fact_transactions
GROUP BY city_tier
ORDER BY total_crore DESC;

-- ─────────────────────────────────────────────────────────────
-- Q12 : Fund NAV vs Benchmark — 3-year return comparison
-- ─────────────────────────────────────────────────────────────
SELECT
    f.scheme_name,
    f.category,
    p.return_3yr_pct                        AS fund_3yr_pct,
    p.benchmark_3yr_pct                     AS benchmark_3yr_pct,
    ROUND(p.return_3yr_pct
          - p.benchmark_3yr_pct, 2)         AS excess_return_pct,
    p.alpha,
    CASE
        WHEN p.return_3yr_pct > p.benchmark_3yr_pct THEN 'Outperformer'
        ELSE 'Underperformer'
    END                                     AS vs_benchmark
FROM fact_performance p
JOIN dim_fund f USING (amfi_code)
ORDER BY excess_return_pct DESC;

-- ─────────────────────────────────────────────────────────────
-- Q13 : Top 10 stock holdings by total portfolio weight
-- ─────────────────────────────────────────────────────────────
SELECT
    h.stock_symbol,
    h.stock_name,
    h.sector,
    COUNT(DISTINCT h.amfi_code)            AS num_funds_holding,
    ROUND(SUM(h.weight_pct), 2)            AS total_weight_pct,
    ROUND(SUM(h.market_value_cr), 2)       AS total_market_value_cr
FROM fact_portfolio_holdings h
GROUP BY h.stock_symbol, h.stock_name, h.sector
ORDER BY total_market_value_cr DESC
LIMIT 10;
