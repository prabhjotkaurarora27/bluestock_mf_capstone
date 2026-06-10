# 📊 Day 5 — Interactive Streamlit Dashboard

This folder is the **Day 5** deliverable for the Bluestock MF Analytics Capstone.

## Files

| File | Description |
|------|-------------|
| `app.py` | Entry-point shim — delegates to `../streamlit_dashboard.py` |
| `../streamlit_dashboard.py` | **Main dashboard** — 1,300+ lines, 7 interactive pages |

## How to Run

From the **project root** (`bluestock_mf_capstone/`):

```bash
# Primary command (recommended)
streamlit run streamlit_dashboard.py

# Alternative — run via this folder
streamlit run dashboard/app.py
```

Both commands open the app at → **http://localhost:8501**

## Dashboard Pages

| # | Page | Key Features |
|---|------|-------------|
| 🏠 | **Dashboard Home** | Hero card · 5 KPI stats · methodology · glossary · FAQ |
| 🏭 | **Industry Overview** | SIP AUM dual-axis · AMC grouped bar · folio stacked area |
| 📊 | **Fund Performance** | Risk-return scatter · scorecard table · NAV vs NIFTY 100 · fund comparison |
| 👥 | **Investor Analytics** | State bar · transaction donut · SIP by age · T30/B30 split |
| 📈 | **SIP & Market Trends** | SIP vs NIFTY dual-axis · category heatmap · YoY growth |
| 🎲 | **Monte Carlo Simulation** | 10,000-path NAV projection · 5th/50th/95th percentile bands |
| 🎯 | **Portfolio Optimization** | Markowitz efficient frontier · max Sharpe · min volatility |

## Tech Stack

- **Streamlit 1.50** — web framework
- **Plotly 6.7** — interactive charts
- **Pandas / NumPy** — data processing
- **SciPy** — Monte Carlo & Markowitz optimisation

---

*Bluestock Fintech · Data Analytics Internship · Prabhjot Kaur · © 2026*
