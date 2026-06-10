# 📊 Bluestock Mutual Fund Analytics Platform

> End-to-end data analytics platform for Indian mutual fund intelligence — ETL pipeline, star-schema database, EDA, performance analytics, and interactive 7-page Streamlit dashboard.

---

## Project Overview

The **Bluestock MF Analytics Platform** covers the complete data lifecycle for 40 SEBI-registered mutual fund schemes across 10 AMCs — from raw data ingestion and SQL-based star-schema modelling to exploratory analysis, financial performance metrics, and an interactive web dashboard.

**Data scope:** 4.5 years of daily NAV (Jan 2022 – May 2026) · 32,778 investor transactions · 107,461 DB rows across 11 tables

---

## Project Structure

```
bluestock_mf_capstone/
│
├── dashboard/                      # ★ Day 5 — Interactive Streamlit Dashboard
│   ├── app.py                      #   Entry-point shim (delegates to root dashboard)
│   └── README.md                   #   Day 5 folder docs & run instructions
│
├── data/
│   ├── raw/                        # Original source files (not committed)
│   ├── processed/                  # 13 cleaned CSVs — committed to repo
│   │   ├── 01_fund_master.csv          (40 schemes)
│   │   ├── 02_nav_history.csv          (64,320 daily NAV records)
│   │   ├── 03_aum_by_fund_house.csv    (quarterly AUM by AMC)
│   │   ├── 04_monthly_sip_inflows.csv  (monthly SIP stats)
│   │   ├── 05_category_inflows.csv     (category-wise net inflows)
│   │   ├── 06_industry_folio_count.csv (folio count by category)
│   │   ├── 07_scheme_performance.csv   (1yr/3yr/5yr returns)
│   │   ├── 08_investor_transactions.csv(32,778 investor records)
│   │   ├── 09_portfolio_holdings.csv   (sector holdings)
│   │   ├── 10_benchmark_indices.csv    (NIFTY 50/100 daily)
│   │   ├── clean_nav.csv               (filtered NAV for dashboard)
│   │   ├── clean_performance.csv       (cleaned performance metrics)
│   │   └── clean_transactions.csv      (cleaned transactions)
│   └── db/
│       └── bluestock_mf.db             (SQLite star schema, ~12.9 MB)
│
├── notebooks/
│   └── 01_data_ingestion.ipynb     # Data ingestion walkthrough
│
├── scripts/
│   ├── data_ingestion.py           # Raw data loader
│   ├── live_nav_fetch.py           # Live NAV fetcher (AMFI API)
│   ├── clean_nav.py                # NAV history cleaner
│   ├── clean_transactions.py       # Investor transactions cleaner
│   ├── clean_performance.py        # Scheme performance cleaner
│   ├── copy_remaining.py           # Copy CSVs to processed/
│   ├── load_database.py            # Load all CSVs into SQLite
│   ├── run_pipeline.py             # Master runner (all Day 2 steps)
│   ├── performance_analytics.py    # Sharpe, Alpha, Beta, CAGR, Drawdown
│   ├── build_notebook.py           # Programmatic notebook builder
│   └── test_environment.py         # Dependency validation (9 checks)
│
├── sql/
│   ├── schema.sql                  # 11 tables + FK + 8 indexes + 3 views
│   └── queries.sql                 # 13 analytical SQL queries
│
├── reports/
│   ├── fund_scorecard.csv          # Bluestock composite score for 40 funds
│   ├── alpha_beta.csv              # Alpha & Beta vs NIFTY 100
│   └── charts/                    # 15 exported PNG charts
│       ├── 01_nav_trends.png
│       ├── 02_aum_growth.png
│       ├── 03_sip_inflow_trend.png
│       ├── 04_category_heatmap.png
│       ├── 05_06_07_demographics.png
│       ├── 08_09_geo_distribution.png
│       ├── 10_folio_growth.png
│       ├── 11_correlation_matrix.png
│       ├── 12_sector_allocation.png
│       ├── 13_14_15_performance.png
│       ├── benchmark_comparison.png
│       └── fund_scorecard_top15.png
│
├── streamlit_dashboard.py          # Day 5: 7-page interactive dashboard (1,300+ lines)
├── data_dictionary.md              # Column-level docs for all 11 DB tables
├── requirements.txt                # All Python dependencies (pinned)
├── .gitignore
└── README.md
```

---

##  Tech Stack

| Layer | Tools |
|-------|-------|
| **Language** | Python 3.9+ |
| **Database** | SQLite (star schema via `schema.sql`) |
| **Data Processing** | Pandas, NumPy, SQLAlchemy |
| **Visualisation** | Plotly, Matplotlib, Seaborn |
| **Dashboard** | Streamlit 1.50 |
| **Financial Math** | SciPy (Markowitz optimisation, Monte Carlo) |
| **Notebooks** | Jupyter Notebook / JupyterLab |
| **Version Control** | Git & GitHub |

---

##  Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/prabhjotkaurarora27/bluestock_mf_capstone.git
cd bluestock_mf_capstone
```

### 2. Create & activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate          # macOS / Linux
venv\Scripts\activate             # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the interactive dashboard 
```bash
python3 -m streamlit run streamlit_dashboard.py
# Opens at → http://localhost:8501
```

### 5. Run the full ETL pipeline (Day 2)
```bash
python scripts/run_pipeline.py
# Cleans all CSVs → loads bluestock_mf.db
```

### 6. Verify environment
```bash
python scripts/test_environment.py
# Expected: 9 passed | 0 failed
```

---

##  Day 5 — Interactive Dashboard

A 7-page Streamlit web app with Plotly charts, cross-page slicers, fund comparison, drill-through, CSV/Excel exports, Monte Carlo simulation, and Markowitz portfolio optimisation.

**Run:** `python3 -m streamlit run streamlit_dashboard.py` → http://localhost:8501

### Pages

| # | Page | Charts & Features |
|---|------|-------------------|
| 🏠 | **Dashboard Home** | Hero card · 5 KPI stats · page guide · methodology & glossary · FAQ · tech stack |
| 🏭 | **Industry Overview** | SIP AUM dual-axis trend · AMC grouped bar · folio stacked area · YoY badges · CSV/Excel export |
| 📊 | **Fund Performance** | Risk-return scatter (bubble=AUM, colour=Sharpe) · scorecard table · NAV vs NIFTY 100 · fund comparison tool · drill-through with mini NAV chart |
| 👥 | **Investor Analytics** | State-wise bar · transaction type donut · SIP by age group · monthly volume trend · T30/B30 donut · state drill-through |
| 📈 | **SIP & Market Trends** | SIP vs NIFTY 50 dual-axis · category heatmap · FY25 top categories · YoY growth rate · SIP account growth |
| 🎲 | **Monte Carlo Simulation** | 10,000-path 5-year NAV projection · confidence bands (5th–95th pct) · final value histogram · probability of target CAGR |
| 🎯 | **Portfolio Optimization** | Markowitz efficient frontier · 3,000 random portfolios · max Sharpe ★ · min volatility ● · custom weight sliders |

### Key Features
- **Dynamic slicers** — Fund House, Category, Plan filters applied per page
- **Fund comparison tool** — Select 2 funds → side-by-side metrics with green/red delta highlights + indexed NAV chart
- **Drill-through** — Click any fund → 6-month NAV mini-chart + full performance & fund info breakdown
- **CSV & Excel exports** — Download buttons with unique keys on every data table
- **Readable charts** — All axes, legends, tooltips use `#FFFFFF`/`#e0e8f0` on dark navy `#0f1923` background
- **Branding** — Bluestock blue `#2196F3` · accent green `#4CAF50` · orange `#FF9800` · off-white `#F5F0E8`

---

## Database Schema — Star Schema (`bluestock_mf.db`)

**Size:** ~12.9 MB · **Rows:** 107,461 · **Tables:** 11 · **Views:** 3 · **Indexes:** 8

| Table | Type | Rows | Description |
|-------|------|------|-------------|
| `dim_fund` | Dimension | 40 | Fund master — AMC, category, benchmark, manager |
| `dim_date` | Dimension | 1,608 | Date dimension — year, quarter, month, week |
| `fact_nav` | Fact | 64,320 | Daily NAV per fund |
| `fact_transactions` | Fact | 32,778 | Investor transactions (SIP/Lumpsum/Redemption) |
| `fact_performance` | Fact | 40 | Scheme performance (1/3/5yr CAGR, Sharpe, Alpha) |
| `fact_aum` | Fact | 90 | Quarterly AUM by fund house |
| `fact_sip_inflows` | Fact | 48 | Monthly SIP inflow & account stats |
| `fact_category_inflows` | Fact | 144 | Category-wise net inflows |
| `fact_folio_count` | Fact | 21 | Monthly folio count by category |
| `fact_portfolio_holdings` | Fact | 322 | Sector holdings per fund |
| `fact_benchmark_indices` | Fact | 8,050 | Daily NIFTY 50 / NIFTY 100 close values |

---

##  Day 4 — Performance Analytics

Computed via `scripts/performance_analytics.py` and exported to `reports/`:

| Metric | Formula | Output |
|--------|---------|--------|
| **CAGR (3yr)** | `(End NAV / Start NAV)^(1/3) − 1` | `fund_scorecard.csv` |
| **Sharpe Ratio** | `(Rp − Rf) / σp` · Rf = 6% p.a. | `fund_scorecard.csv` |
| **Alpha (Jensen's)** | `Rp − [Rf + β(Rm − Rf)]` vs NIFTY 100 | `alpha_beta.csv` |
| **Beta** | `Cov(Rp, Rm) / Var(Rm)` | `alpha_beta.csv` |
| **Max Drawdown** | `(Trough − Peak) / Peak` | `fund_scorecard.csv` |
| **Bluestock Score** | `40%·CAGR + 30%·Sharpe + 20%·Alpha + 10%·(1−MaxDD)` | `fund_scorecard.csv` |

---

##  Day 3 — Exploratory Data Analysis (15 charts)

All charts exported to `reports/charts/`:

| Chart | Insight |
|-------|---------|
| NAV Trends | 4.5-year price history for top 5 funds |
| AUM Growth | Quarterly AUM by fund house (2022–2025) |
| SIP Inflow Trend | Monthly SIP inflows with YoY growth |
| Category Heatmap | Net inflows by category and month |
| Demographics | Age group, gender, KYC status breakdown |
| Geographic Distribution | T30 vs B30 transaction volumes |
| Folio Growth | Equity/Debt/Hybrid folio count trend |
| Correlation Matrix | Return correlations across 40 funds |
| Sector Allocation | Top sectors by portfolio weight |
| Performance Charts | CAGR vs Sharpe scatter, top/bottom 5 funds |
| Benchmark Comparison | Fund NAV vs NIFTY 100 (indexed to 100) |
| Fund Scorecard | Top 15 funds by Bluestock composite score |

---

##  Dependencies (`requirements.txt`)

```
jupyter==1.1.1
matplotlib==3.9.4
numpy==2.0.2
openpyxl==3.1.5
pandas==2.3.3
plotly==6.7.0
requests==2.32.5
scipy==1.13.1
seaborn==0.13.2
SQLAlchemy==2.0.50
streamlit==1.50.0
```

---

##  Project Status

| Day | Deliverable | Status |
|-----|-------------|--------|
| **Day 1** | Project setup, Git init, data ingestion pipeline | ✅ Complete |
| **Day 2** | Data cleaning (13 CSVs) + SQLite star-schema DB loaded | ✅ Complete |
| **Day 3** | Exploratory Data Analysis — 15 charts exported | ✅ Complete |
| **Day 4** | Performance Analytics — Sharpe, Alpha, Beta, CAGR, Scorecard | ✅ Complete |
| **Day 5** | Interactive Dashboard — 7 pages (Streamlit + Plotly) | ✅ Complete |
| **Day 6** | Final report & presentation | 🔜 Upcoming |

---

## 
 Author

**Prabhjot Kaur**
Bluestock Fintech · Data Analytics Internship · © 2026

🔗 [GitHub Repository](https://github.com/prabhjotkaurarora27/bluestock_mf_capstone)
