# 📊 Bluestock Mutual Fund Capstone

## Project Description

The **Bluestock Mutual Fund Capstone** is an end-to-end data analytics and visualization project focused on analyzing Indian mutual fund performance. This project encompasses the complete data lifecycle — from raw data ingestion and SQL-based processing to exploratory data analysis, insight generation, and an interactive dashboard.

The goal is to provide investors and analysts with actionable insights into mutual fund NAV trends, risk-return profiles, fund category comparisons, and portfolio performance metrics — built using industry-standard tools and best practices.

---

## 🎯 Objectives

- Collect and store mutual fund data (NAV, AUM, returns) from public sources
- Clean, transform, and load data using SQL and Python pipelines
- Perform exploratory data analysis (EDA) with statistical summaries and visualizations
- Build an interactive dashboard for fund performance monitoring
- Generate a comprehensive project report with findings and recommendations

---

## 📁 Folder Structure

```
bluestock_mf_capstone/
│
├── data/
│   ├── raw/            # Original, unmodified source data files
│   ├── processed/      # 10 cleaned CSVs (01–10, committed to repo)
│   └── db/             # bluestock_mf.db — SQLite star schema (committed)
│
├── notebooks/          # Jupyter Notebooks for EDA and performance analytics
│   └── 01_data_ingestion.ipynb
│
├── scripts/            # Python ETL scripts
│   ├── run_pipeline.py         ← Master Day 2 runner
│   ├── clean_nav.py            ← NAV history cleaner
│   ├── clean_transactions.py   ← Investor transactions cleaner
│   ├── clean_performance.py    ← Scheme performance cleaner
│   ├── copy_remaining.py       ← Copy remaining CSVs to processed/
│   └── load_database.py        ← Load all cleaned CSVs into SQLite
│
├── sql/
│   ├── schema.sql      # Star schema: CREATE TABLE + FK + 8 indexes + 3 views
│   └── queries.sql     # 13 analytical SQL queries
│
├── reports/
│   └── charts/         # 12 EDA + performance charts (PNG)
│
├── data_dictionary.md  # Column-level documentation for all 11 DB tables
├── .gitignore
└── README.md
```

---

## 🛠️ Tech Stack

| Layer           | Tools / Technologies                        |
|-----------------|---------------------------------------------|
| Language        | Python 3.x                                  |
| Database        | SQLite (star schema via schema.sql)         |
| Data Layer      | Pandas, NumPy, SQLAlchemy                   |
| Visualisation   | Matplotlib, Seaborn, Plotly                 |
| Notebooks       | Jupyter Notebook / JupyterLab               |
| Dashboard       | Streamlit / Power BI                        |
| Version Control | Git & GitHub                                |

---

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/prabhjotkaurarora27/bluestock_mf_capstone.git
   cd bluestock_mf_capstone
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS/Linux
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the full Day 2 pipeline** (clean + load DB in one command)
   ```bash
   python scripts/run_pipeline.py
   ```

5. **Or run individual steps**
   ```bash
   python scripts/clean_nav.py
   python scripts/clean_transactions.py
   python scripts/clean_performance.py
   python scripts/load_database.py
   ```

6. **Verify environment**
   ```bash
   python scripts/test_environment.py   # 9 passed | 0 failed
   ```

---

## 📦 Day 2 Deliverables — Data Cleaning & SQLite DB

### ✅ 10 Cleaned CSVs (`data/processed/`)

| File | Rows | Cleaning Applied |
|------|------|-----------------|
| `01_fund_master.csv` | 40 | Fund dimension — validated & typed |
| `02_nav_history.csv` | 64,320 | Dates parsed, sorted by amfi_code+date, ffill for weekends/holidays, NAV > 0 validated |
| `03_aum_by_fund_house.csv` | 90 | Date normalised |
| `04_monthly_sip_inflows.csv` | 48 | Date normalised |
| `05_category_inflows.csv` | 144 | Date normalised |
| `06_industry_folio_count.csv` | 21 | Date normalised |
| `07_scheme_performance.csv` | 40 | All metrics forced numeric, expense_ratio clipped [0.1–2.5%], Sharpe anomalies flagged |
| `08_investor_transactions.csv` | 32,778 | transaction_type standardised (SIP/Lumpsum/Redemption), amount_inr > 0, KYC enum validated |
| `09_portfolio_holdings.csv` | 322 | Dates normalised |
| `10_benchmark_indices.csv` | 8,050 | Dates normalised |

### ✅ SQLite Database (`data/db/bluestock_mf.db`)

- **Size:** ~12.9 MB — committed to repository
- **Total rows:** 107,461 across 11 tables
- **Dimensions:** `dim_fund` (40 rows), `dim_date` (1,608 rows)
- **Facts:** `fact_nav` (64,320), `fact_transactions` (32,778), `fact_performance` (40), `fact_aum` (90), `fact_sip_inflows` (48), `fact_category_inflows` (144), `fact_folio_count` (21), `fact_portfolio_holdings` (322), `fact_benchmark_indices` (8,050)
- **Views:** `vw_monthly_nav`, `vw_performance_leaderboard`, `vw_tx_monthly_summary`
- **Indexes:** 8 covering common join/filter patterns
- **Schema:** `sql/schema.sql` — FK constraints, CHECK constraints (NAV > 0, amount_inr > 0, KYC enum, transaction_type enum)

### ✅ SQL Files (`sql/`)

| File | Contents |
|------|----------|
| `schema.sql` | 11 CREATE TABLE statements + FK constraints + 8 indexes + 3 views |
| `queries.sql` | 13 analytical queries: Top 5 AUM, avg NAV/month, SIP YoY growth, transactions by state, expense_ratio < 1%, top 3yr performers, SIP vs Lumpsum split, top Sharpe ratio, monthly SIP trend, gender breakdown, city-tier analysis, benchmark comparison, top portfolio holdings |

### ✅ Documentation

- **`data_dictionary.md`** — Column-level docs for all 11 tables: data types, business definitions, value ranges, source references

---

## 📊 Day 3 & 4 — EDA + Performance Analytics

- **`03_eda_analysis.ipynb`** — 15 charts: NAV trends, AUM growth, SIP trend, category heatmap, demographics, geo distribution, correlation matrix, sector allocation
- **`04_performance_analytics.ipynb`** — Sharpe ratio, Alpha, Beta, CAGR, Max Drawdown, Fund Scorecard (Top 15)
- All charts exported to `reports/charts/`

---

## 📌 Status

| Day | Task                                         | Status       |
|-----|----------------------------------------------|--------------|
| 1   | Project structure, Git init, data ingestion  | ✅ Complete  |
| 2   | Data cleaning + SQLite DB loaded             | ✅ Complete  |
| 3   | Exploratory Data Analysis (EDA) — 15 charts  | ✅ Complete  |
| 4   | Performance Analytics (Sharpe, Alpha, Beta)  | ✅ Complete  |
| 5   | Dashboard development                        | 🔜 Upcoming |
| 6   | Final report & presentation                  | 🔜 Upcoming |

---

## 👤 Author

**Prabhjot Kaur**  
Capstone Project — Bluestock Fintech  
© 2026
