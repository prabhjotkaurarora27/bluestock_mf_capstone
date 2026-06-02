-- =============================================================
-- schema.sql
-- Bluestock MF Capstone — SQLite Star Schema
-- =============================================================
-- Star-schema layout
--   Dimensions : dim_fund, dim_date
--   Facts      : fact_nav, fact_transactions, fact_performance,
--                fact_aum, fact_sip_inflows, fact_category_inflows,
--                fact_folio_count, fact_portfolio_holdings,
--                fact_benchmark_indices
-- =============================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;      -- better concurrent read performance

-- =============================================================
-- DIMENSION TABLES
-- =============================================================

-- dim_fund
-- Source : data/processed/01_fund_master.csv  (40 rows, 15 cols)
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code             INTEGER PRIMARY KEY,   -- e.g. 119551
    fund_house            TEXT    NOT NULL,
    scheme_name           TEXT    NOT NULL,
    category              TEXT,                  -- Large Cap / Mid Cap / ...
    sub_category          TEXT,
    plan                  TEXT,                  -- Regular | Direct
    launch_date           DATE,
    benchmark             TEXT,
    expense_ratio_pct     REAL,
    exit_load_pct         REAL,
    min_sip_amount        INTEGER,
    min_lumpsum_amount    INTEGER,
    fund_manager          TEXT,
    risk_category         TEXT,
    sebi_category_code    TEXT
);

-- dim_date
-- Populated programmatically in load_db.py (one row per calendar day)
CREATE TABLE IF NOT EXISTS dim_date (
    date_id    INTEGER PRIMARY KEY,  -- YYYYMMDD integer key, e.g. 20240101
    date       DATE    NOT NULL UNIQUE,
    year       INTEGER NOT NULL,
    month      INTEGER NOT NULL,     -- 1–12
    quarter    INTEGER NOT NULL,     -- 1–4
    month_name TEXT    NOT NULL,     -- 'January' … 'December'
    day_of_week INTEGER NOT NULL,    -- 0=Monday … 6=Sunday (Python convention)
    is_weekday INTEGER NOT NULL      -- 1 = Mon–Fri, 0 = Sat–Sun
);

-- =============================================================
-- FACT TABLES
-- =============================================================

-- fact_nav
-- Source : data/processed/clean_nav.csv  (64,320 rows after ffill)
-- Grain  : one row per (amfi_code, date)
CREATE TABLE IF NOT EXISTS fact_nav (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code        INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    date             DATE    NOT NULL,
    nav              REAL    NOT NULL CHECK (nav > 0),
    daily_return_pct REAL,           -- computed during load: (nav/prev_nav - 1)*100
    UNIQUE (amfi_code, date)
);

-- fact_transactions
-- Source : data/processed/clean_transactions.csv  (32,778 rows, 13 cols)
-- Grain  : one row per investor transaction
CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id        TEXT    NOT NULL,
    amfi_code          INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    transaction_date   DATE    NOT NULL,
    transaction_type   TEXT    NOT NULL  CHECK (transaction_type IN ('SIP','Lumpsum','Redemption')),
    amount_inr         REAL    NOT NULL  CHECK (amount_inr > 0),
    state              TEXT,
    city               TEXT,
    city_tier          TEXT,            -- T30 | B30
    age_group          TEXT,
    gender             TEXT,
    annual_income_lakh REAL,
    payment_mode       TEXT,
    kyc_status         TEXT             CHECK (kyc_status IN ('Verified','Pending'))
);

-- fact_performance
-- Source : data/processed/clean_performance.csv  (40 rows, 19 cols)
-- Grain  : one row per fund (snapshot — no date dimension needed)
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code          INTEGER PRIMARY KEY REFERENCES dim_fund(amfi_code),
    return_1yr_pct     REAL,
    return_3yr_pct     REAL,
    return_5yr_pct     REAL,
    benchmark_3yr_pct  REAL,
    alpha              REAL,
    beta               REAL,
    sharpe_ratio       REAL,
    sortino_ratio      REAL,
    std_dev_ann_pct    REAL,
    max_drawdown_pct   REAL,
    aum_crore          INTEGER,
    expense_ratio_pct  REAL,
    morningstar_rating INTEGER CHECK (morningstar_rating BETWEEN 1 AND 5),
    risk_grade         TEXT
);

-- fact_aum
-- Source : data/processed/03_aum_by_fund_house.csv  (5 cols)
-- Grain  : one row per (fund_house, date)
CREATE TABLE IF NOT EXISTS fact_aum (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    date             DATE    NOT NULL,
    fund_house       TEXT    NOT NULL,
    aum_lakh_crore   REAL,            -- high-level figure in lakh crore
    aum_crore        INTEGER,         -- detailed figure in crore
    num_schemes      INTEGER,
    UNIQUE (fund_house, date)
);

-- fact_sip_inflows
-- Source : data/processed/04_monthly_sip_inflows.csv  (6 cols)
-- Grain  : one row per month (industry-wide SIP data)
CREATE TABLE IF NOT EXISTS fact_sip_inflows (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    month                     DATE    NOT NULL UNIQUE,   -- first day of month
    sip_inflow_crore          INTEGER,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh     REAL,
    sip_aum_lakh_crore        REAL,
    yoy_growth_pct            REAL
);

-- fact_category_inflows
-- Source : data/processed/05_category_inflows.csv  (3 cols)
-- Grain  : one row per (month, category)
CREATE TABLE IF NOT EXISTS fact_category_inflows (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    month            DATE    NOT NULL,
    category         TEXT    NOT NULL,
    net_inflow_crore REAL,
    UNIQUE (month, category)
);

-- fact_folio_count
-- Source : data/processed/06_industry_folio_count.csv  (6 cols)
-- Grain  : one row per month (industry-wide folio counts)
CREATE TABLE IF NOT EXISTS fact_folio_count (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    month                DATE    NOT NULL UNIQUE,
    total_folios_crore   REAL,
    equity_folios_crore  REAL,
    debt_folios_crore    REAL,
    hybrid_folios_crore  REAL,
    others_folios_crore  REAL
);

-- fact_portfolio_holdings
-- Source : data/processed/09_portfolio_holdings.csv  (8 cols)
-- Grain  : one row per (amfi_code, stock_symbol, portfolio_date)
CREATE TABLE IF NOT EXISTS fact_portfolio_holdings (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    stock_symbol        TEXT    NOT NULL,
    stock_name          TEXT,
    sector              TEXT,
    weight_pct          REAL    CHECK (weight_pct >= 0),
    market_value_cr     REAL,
    current_price_inr   REAL,
    portfolio_date      DATE    NOT NULL,
    UNIQUE (amfi_code, stock_symbol, portfolio_date)
);

-- fact_benchmark_indices
-- Source : data/processed/10_benchmark_indices.csv  (3 cols)
-- Grain  : one row per (date, index_name)
CREATE TABLE IF NOT EXISTS fact_benchmark_indices (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        DATE    NOT NULL,
    index_name  TEXT    NOT NULL,
    close_value REAL    NOT NULL,
    UNIQUE (date, index_name)
);

-- =============================================================
-- INDEXES  (speed up common join / filter patterns)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_nav_amfi_date
    ON fact_nav (amfi_code, date);

CREATE INDEX IF NOT EXISTS idx_nav_date
    ON fact_nav (date);

CREATE INDEX IF NOT EXISTS idx_tx_investor
    ON fact_transactions (investor_id);

CREATE INDEX IF NOT EXISTS idx_tx_amfi_date
    ON fact_transactions (amfi_code, transaction_date);

CREATE INDEX IF NOT EXISTS idx_tx_type
    ON fact_transactions (transaction_type);

CREATE INDEX IF NOT EXISTS idx_aum_date
    ON fact_aum (date);

CREATE INDEX IF NOT EXISTS idx_holdings_amfi
    ON fact_portfolio_holdings (amfi_code, portfolio_date);

CREATE INDEX IF NOT EXISTS idx_benchmark_date
    ON fact_benchmark_indices (date, index_name);

-- =============================================================
-- VIEWS  (handy pre-built queries for notebooks / dashboard)
-- =============================================================

-- Monthly NAV: last NAV of each month per fund
CREATE VIEW IF NOT EXISTS vw_monthly_nav AS
SELECT
    amfi_code,
    strftime('%Y-%m', date)          AS year_month,
    MAX(date)                        AS month_end_date,
    ROUND(AVG(nav), 4)               AS avg_nav,
    MAX(nav)                         AS max_nav,
    MIN(nav)                         AS min_nav
FROM fact_nav
GROUP BY amfi_code, strftime('%Y-%m', date);

-- Fund performance leaderboard
CREATE VIEW IF NOT EXISTS vw_performance_leaderboard AS
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    f.plan,
    p.return_1yr_pct,
    p.return_3yr_pct,
    p.return_5yr_pct,
    p.sharpe_ratio,
    p.alpha,
    p.morningstar_rating,
    p.risk_grade
FROM fact_performance p
JOIN dim_fund f USING (amfi_code)
ORDER BY p.return_3yr_pct DESC;

-- Transaction summary by type and month
CREATE VIEW IF NOT EXISTS vw_tx_monthly_summary AS
SELECT
    strftime('%Y-%m', transaction_date) AS year_month,
    transaction_type,
    COUNT(*)                            AS num_transactions,
    ROUND(SUM(amount_inr) / 1e7, 2)    AS total_crore,
    ROUND(AVG(amount_inr), 0)          AS avg_amount_inr
FROM fact_transactions
GROUP BY year_month, transaction_type
ORDER BY year_month, transaction_type;
