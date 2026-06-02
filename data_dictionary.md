# Bluestock MF Capstone — Data Dictionary

> **Database:** `data/db/bluestock_mf.db` (SQLite, 12.07 MB)  
> **Total rows:** 107,461 across 11 tables + 3 views  
> **Coverage:** 40 mutual fund schemes · 10 AMCs · Jan 2022 – May 2026

---

## Schema Map

```
          ┌─────────────┐
          │  dim_fund   │◄─────────────────────────────────┐
          │  (40 rows)  │                                  │
          └──────┬──────┘                                  │
                 │ amfi_code (FK)                          │
        ┌────────┼─────────────────┬──────────────┐        │
        ▼        ▼                 ▼              ▼        │
  fact_nav  fact_transactions  fact_performance  fact_portfolio_holdings
  (64,320)    (32,778)            (40)               (322)

  dim_date   fact_aum   fact_sip_inflows   fact_category_inflows
  (1,608)     (90)          (48)                 (144)

  fact_folio_count   fact_benchmark_indices
      (21)                  (8,050)
```

---

## Dimension Tables

### `dim_fund`
**Source:** `data/processed/01_fund_master.csv`  
**Grain:** One row per mutual fund scheme  
**Rows:** 40 &nbsp;|&nbsp; **Fund Houses:** 10 &nbsp;|&nbsp; **Plans:** Regular (32), Direct (8)

| Column | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `amfi_code` | INTEGER (PK) | No | Unique AMFI scheme identifier | `119551` |
| `fund_house` | TEXT | No | AMC / fund house name | `SBI Mutual Fund` |
| `scheme_name` | TEXT | No | Full official SEBI scheme name | `SBI Bluechip Fund - Regular Plan - Growth` |
| `category` | TEXT | Yes | Broad asset class | `Equity`, `Debt` |
| `sub_category` | TEXT | Yes | SEBI sub-classification | `Large Cap`, `Mid Cap`, `Liquid` |
| `plan` | TEXT | Yes | Plan type | `Regular`, `Direct` |
| `launch_date` | DATE | Yes | Scheme inception date | `2006-02-14` |
| `benchmark` | TEXT | Yes | Benchmark index name | `Nifty 100 TRI` |
| `expense_ratio_pct` | REAL | Yes | Annual TER charged to investors (%) | `1.54` |
| `exit_load_pct` | REAL | Yes | Exit load on early redemption (%) | `1.0` |
| `min_sip_amount` | INTEGER | Yes | Minimum SIP instalment (₹) | `500` |
| `min_lumpsum_amount` | INTEGER | Yes | Minimum lump-sum investment (₹) | `5000` |
| `fund_manager` | TEXT | Yes | Lead fund manager name | `R. Srinivasan` |
| `risk_category` | TEXT | Yes | SEBI risk label | `Low`, `Moderate`, `Moderately High`, `High`, `Very High` |
| `sebi_category_code` | TEXT | Yes | SEBI standardised category code | `EQ-LC` |

---

### `dim_date`
**Source:** Generated programmatically in `scripts/load_database.py`  
**Grain:** One row per calendar day  
**Rows:** 1,608 &nbsp;|&nbsp; **Range:** 2022-01-03 → 2026-05-29 &nbsp;|&nbsp; Weekdays: 1,150 · Weekends: 458

| Column | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `date_id` | INTEGER (PK) | No | Surrogate key in YYYYMMDD format | `20240101` |
| `date` | DATE | No | Calendar date (unique) | `2024-01-01` |
| `year` | INTEGER | No | Calendar year | `2024` |
| `month` | INTEGER | No | Month number (1–12) | `1` |
| `quarter` | INTEGER | No | Quarter number (1–4) | `1` |
| `month_name` | TEXT | No | Full month name | `January` |
| `day_of_week` | INTEGER | No | 0 = Monday … 6 = Sunday (Python convention) | `0` |
| `is_weekday` | INTEGER | No | 1 = Mon–Fri, 0 = Sat–Sun | `1` |

---

## Fact Tables

### `fact_nav`
**Source:** `data/processed/clean_nav.csv`  
**Grain:** One row per (fund, calendar day)  
**Rows:** 64,320 &nbsp;|&nbsp; **Range:** 2022-01-03 → 2026-05-29  
**Note:** Weekends and market holidays are forward-filled from the last known NAV.

| Column | Type | Nullable | Description | Range / Example |
|---|---|---|---|---|
| `id` | INTEGER (PK) | No | Auto-increment surrogate key | — |
| `amfi_code` | INTEGER (FK) | No | Links to `dim_fund` | `119551` |
| `date` | DATE | No | Calendar date | `2024-01-15` |
| `nav` | REAL | No | Net Asset Value in ₹ (must be > 0) | 26.14 – 4,268.55 |
| `daily_return_pct` | REAL | Yes | `(nav_t / nav_{t-1} − 1) × 100`; NULL for first day per fund | avg `0.045%` |

---

### `fact_transactions`
**Source:** `data/processed/clean_transactions.csv`  
**Grain:** One row per investor transaction  
**Rows:** 32,778 &nbsp;|&nbsp; **Investors:** 5,000 &nbsp;|&nbsp; **Funds:** 40 &nbsp;|&nbsp; **Range:** 2024-01-01 → 2025-05-30

| Column | Type | Nullable | Description | Values / Range |
|---|---|---|---|---|
| `tx_id` | INTEGER (PK) | No | Auto-increment transaction ID | — |
| `investor_id` | TEXT | No | Unique investor identifier | `INV000001` – `INV005000` |
| `amfi_code` | INTEGER (FK) | No | Links to `dim_fund` | — |
| `transaction_date` | DATE | No | Date of transaction | 2024-01-01 → 2025-05-30 |
| `transaction_type` | TEXT | No | Type of transaction | `SIP` (60.2%), `Lumpsum` (24.7%), `Redemption` (15.2%) |
| `amount_inr` | REAL | No | Transaction amount in ₹ (must be > 0) | ₹400 – ₹5,97,498 |
| `state` | TEXT | Yes | Investor's state | `Maharashtra`, `Delhi`, … |
| `city` | TEXT | Yes | Investor's city | `Mumbai`, `Hyderabad`, … |
| `city_tier` | TEXT | Yes | AMFI city classification | `T30` (Top 30 cities), `B30` (Beyond Top 30) |
| `age_group` | TEXT | Yes | Investor age bracket | `18-25`, `26-35`, `36-45`, `46-55`, `56+` |
| `gender` | TEXT | Yes | Investor gender | `Male`, `Female` |
| `annual_income_lakh` | REAL | Yes | Self-reported annual income (₹ lakh) | — |
| `payment_mode` | TEXT | Yes | Payment channel | `UPI`, `Mandate`, `Cheque`, `NEFT` |
| `kyc_status` | TEXT | Yes | KYC verification status | `Verified` (92%), `Pending` (8%) |

---

### `fact_performance`
**Source:** `data/processed/clean_performance.csv`  
**Grain:** One row per fund scheme (point-in-time snapshot)  
**Rows:** 40

| Column | Type | Nullable | Description | Range |
|---|---|---|---|---|
| `amfi_code` | INTEGER (PK/FK) | No | Links to `dim_fund` | — |
| `return_1yr_pct` | REAL | Yes | 1-year trailing return (%) | 4.26 – 24.93 |
| `return_3yr_pct` | REAL | Yes | 3-year CAGR (%) | 5.14 – 23.39 |
| `return_5yr_pct` | REAL | Yes | 5-year CAGR (%) | — |
| `benchmark_3yr_pct` | REAL | Yes | Benchmark 3-year CAGR for comparison | — |
| `alpha` | REAL | Yes | Excess return above benchmark (Jensen's α) | 0.51 – 1.98 |
| `beta` | REAL | Yes | Market sensitivity (1.0 = moves with market) | 0.22 – 1.04 |
| `sharpe_ratio` | REAL | Yes | Risk-adjusted return (higher = better) | 0.80 – 7.68* |
| `sortino_ratio` | REAL | Yes | Downside-risk-adjusted return | — |
| `std_dev_ann_pct` | REAL | Yes | Annualised standard deviation of returns (%) | — |
| `max_drawdown_pct` | REAL | Yes | Worst peak-to-trough loss (always negative) | −33.5 – −2.23 |
| `aum_crore` | INTEGER | Yes | Fund AUM at snapshot date (₹ crore) | — |
| `expense_ratio_pct` | REAL | Yes | Total Expense Ratio (%) | 0.55 – 1.64 |
| `morningstar_rating` | INTEGER | Yes | Morningstar star rating (1–5) | 3 (×7), 4 (×16), 5 (×17) |
| `risk_grade` | TEXT | Yes | Qualitative risk label | `Low`, `Moderate`, `Moderately High`, `High`, `Very High` |

> \* Sharpe ratios above 3.0 belong to Liquid/Debt funds — not data errors.

---

### `fact_aum`
**Source:** `data/processed/03_aum_by_fund_house.csv`  
**Grain:** One row per (fund house, month-end date)  
**Rows:** 90 &nbsp;|&nbsp; **Latest total AUM:** ₹62.74 lakh crore (Dec 2025)

| Column | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `id` | INTEGER (PK) | No | Auto-increment key | — |
| `date` | DATE | No | Month-end snapshot date | `2025-12-31` |
| `fund_house` | TEXT | No | AMC name | `SBI Mutual Fund` |
| `aum_lakh_crore` | REAL | Yes | AUM in ₹ lakh crore (headline figure) | `12.5` |
| `aum_crore` | INTEGER | Yes | AUM in ₹ crore (detailed figure) | `1250000` |
| `num_schemes` | INTEGER | Yes | Number of active schemes | `186` |

---

### `fact_sip_inflows`
**Source:** `data/processed/04_monthly_sip_inflows.csv`  
**Grain:** One row per month (industry-wide)  
**Rows:** 48 &nbsp;|&nbsp; **Range:** Jan 2022 – Dec 2025 &nbsp;|&nbsp; Monthly SIP: ₹11,438 – ₹31,002 crore

| Column | Type | Nullable | Description | Range |
|---|---|---|---|---|
| `id` | INTEGER (PK) | No | Auto-increment key | — |
| `month` | DATE | No | First day of month (YYYY-MM-01) | 2022-01-01 → 2025-12-01 |
| `sip_inflow_crore` | INTEGER | Yes | Gross SIP inflow for the month (₹ crore) | 11,438 – 31,002 |
| `active_sip_accounts_crore` | REAL | Yes | Total active SIP accounts (in crore) | — |
| `new_sip_accounts_lakh` | REAL | Yes | New SIP accounts registered in month (lakh) | — |
| `sip_aum_lakh_crore` | REAL | Yes | SIP portfolio AUM (₹ lakh crore) | — |
| `yoy_growth_pct` | REAL | Yes | Year-on-year growth vs same month prior year | — |

---

### `fact_category_inflows`
**Source:** `data/processed/05_category_inflows.csv`  
**Grain:** One row per (month, fund category)  
**Rows:** 144 &nbsp;|&nbsp; **Categories:** 12 &nbsp;|&nbsp; **Range:** Apr 2024 – Mar 2025

| Column | Type | Nullable | Description | Values |
|---|---|---|---|---|
| `id` | INTEGER (PK) | No | Auto-increment key | — |
| `month` | DATE | No | First day of month | 2024-04-01 → 2025-03-01 |
| `category` | TEXT | No | Fund category | `Large Cap`, `Mid Cap`, `Small Cap`, `Flexi Cap`, `ELSS`, `Hybrid`, `Liquid`, `Gilt`, `Short Duration`, `Index/ETF`, `Value/Contra`, `Sectoral/Thematic` |
| `net_inflow_crore` | REAL | Yes | Net inflow into category (₹ crore); negative = net outflow | — |

---

### `fact_folio_count`
**Source:** `data/processed/06_industry_folio_count.csv`  
**Grain:** One row per month (industry-wide)  
**Rows:** 21 &nbsp;|&nbsp; **Range:** Jan 2022 – Dec 2025 &nbsp;|&nbsp; Peak folios: 26.12 crore

| Column | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `id` | INTEGER (PK) | No | Auto-increment key | — |
| `month` | DATE | No | First day of month | `2025-12-01` |
| `total_folios_crore` | REAL | Yes | All folios across all fund types (crore) | `26.12` |
| `equity_folios_crore` | REAL | Yes | Equity fund folios (crore) | — |
| `debt_folios_crore` | REAL | Yes | Debt fund folios (crore) | — |
| `hybrid_folios_crore` | REAL | Yes | Hybrid fund folios (crore) | — |
| `others_folios_crore` | REAL | Yes | Other category folios (crore) | — |

---

### `fact_portfolio_holdings`
**Source:** `data/processed/09_portfolio_holdings.csv`  
**Grain:** One row per (fund, stock, snapshot date)  
**Rows:** 322 &nbsp;|&nbsp; **Funds:** 34 &nbsp;|&nbsp; **Stocks:** 30 &nbsp;|&nbsp; **Sectors:** 14

| Column | Type | Nullable | Description | Values |
|---|---|---|---|---|
| `id` | INTEGER (PK) | No | Auto-increment key | — |
| `amfi_code` | INTEGER (FK) | No | Links to `dim_fund` | — |
| `stock_symbol` | TEXT | No | NSE/BSE ticker symbol | `RELIANCE`, `INFY` |
| `stock_name` | TEXT | Yes | Full company name | `Reliance Industries Ltd` |
| `sector` | TEXT | Yes | GICS-style sector | `Banking`, `IT`, `Pharma`, `FMCG`, `Automobile`, `Energy`, `Infrastructure`, `NBFC`, `Consumer Goods`, `Cement`, `Telecom`, `Utilities`, `Paints`, `Diversified` |
| `weight_pct` | REAL | Yes | Stock's weight in fund portfolio (%) | ≥ 0 |
| `market_value_cr` | REAL | Yes | Market value of holding (₹ crore) | — |
| `current_price_inr` | REAL | Yes | Stock price at snapshot date (₹) | — |
| `portfolio_date` | DATE | No | Date of portfolio snapshot | — |

---

### `fact_benchmark_indices`
**Source:** `data/processed/10_benchmark_indices.csv`  
**Grain:** One row per (index, trading day)  
**Rows:** 8,050 &nbsp;|&nbsp; **Indices:** 7 &nbsp;|&nbsp; **Range:** 2022-01-03 → 2026-05-29

| Column | Type | Nullable | Description | Values |
|---|---|---|---|---|
| `id` | INTEGER (PK) | No | Auto-increment key | — |
| `date` | DATE | No | Trading date | 2022-01-03 → 2026-05-29 |
| `index_name` | TEXT | No | Benchmark index identifier | `NIFTY50`, `NIFTY100`, `NIFTY500`, `NIFTY_MIDCAP150`, `BSE_SMALLCAP`, `CRISIL_GILT`, `CRISIL_LIQUID` |
| `close_value` | REAL | No | Closing index value | — |

---

## Views

| View | Description |
|---|---|
| `vw_monthly_nav` | Monthly NAV summary per fund: avg, high, low, month-end date |
| `vw_performance_leaderboard` | All 40 funds ranked by 3yr return, joined with fund details |
| `vw_tx_monthly_summary` | Transaction count, total value, and average by type and month |

---

## Key Business Definitions

| Term | Definition |
|---|---|
| **NAV** | Net Asset Value — price of one unit of a mutual fund, published daily by AMFI |
| **CAGR** | Compound Annual Growth Rate — standardised multi-year return measure |
| **SIP** | Systematic Investment Plan — fixed periodic investment (usually monthly) |
| **Lumpsum** | One-time bulk investment |
| **Redemption** | Withdrawal / exit from a fund |
| **T30 / B30** | SEBI's city classification: Top 30 cities vs Beyond Top 30 (indicates urban vs semi-urban investors) |
| **Alpha (α)** | Return generated above the benchmark; positive = fund manager added value |
| **Beta (β)** | Correlation with market movement; β < 1 = less volatile than market |
| **Sharpe Ratio** | (Return − Risk-free rate) / Std Dev; measures return per unit of total risk |
| **Sortino Ratio** | Like Sharpe but only penalises downside volatility |
| **Max Drawdown** | Largest percentage fall from a peak to subsequent trough; always negative |
| **Expense Ratio** | Annual % of AUM deducted as fund management fees (TER) |
| **Folio** | A mutual fund account — one investor can hold multiple folios across funds |
| **AUM** | Assets Under Management — total market value of all investor assets in a fund |
| **AMFI** | Association of Mutual Funds in India — regulatory/data body |
| **SEBI** | Securities and Exchange Board of India — capital markets regulator |

---

*Generated: 2026-06-03 · Database version: bluestock_mf.db · Pipeline: Steps 1–8 complete*
