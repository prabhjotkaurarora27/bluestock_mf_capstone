"""
Bluestock MF Analytics Dashboard
Streamlit Web App — Monte Carlo Simulation — Efficient Frontier
Run: streamlit run streamlit_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import scipy.optimize as sco
import io, os, warnings, datetime, base64
warnings.filterwarnings("ignore")

# Pre-compute once per session — prevents widget key churn on every rerun
TODAY = datetime.date.today().strftime("%Y%m%d")


st.set_page_config(
    page_title="Bluestock MF Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071320 0%, #0d1b2a 60%, #1a2d45 100%);
}
[data-testid="stSidebar"] * { color: #e0e8f0 !important; }
[data-testid="stSidebar"] hr { border-color: #1e3a5f !important; }

.stApp { background: #0f1923; color: #e0e8f0; }
[data-testid="stMarkdownContainer"] p { color: #e0e8f0; }

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #1e3a5f 0%, #0d2137 100%);
    border: 1px solid #2196F3;
    border-radius: 14px;
    padding: 22px 18px 18px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(33,150,243,0.18);
    transition: transform 0.2s, box-shadow 0.2s;
    height: 100%;
}
.kpi-card:hover { transform: translateY(-4px); box-shadow: 0 8px 32px rgba(33,150,243,0.28); }
.kpi-label { font-size: 0.7rem; font-weight: 700; color: #90caf9; letter-spacing: 1.2px;
    text-transform: uppercase; margin-bottom: 8px; }
.kpi-value { font-size: 1.8rem; font-weight: 800; color: #ffffff; line-height: 1.1; }
.kpi-sub   { font-size: 0.7rem; color: #4CAF50; margin-top: 6px; font-weight: 600; }
.kpi-yoy   { font-size: 0.68rem; color: #90caf9; margin-top: 3px; }

/* Page header */
.page-header {
    background: linear-gradient(90deg, #071320 0%, #1a3a5c 50%, #071320 100%);
    border-bottom: 2px solid #2196F3;
    padding: 20px 28px; border-radius: 14px; margin-bottom: 22px;
}
.page-title { font-size: 1.6rem; font-weight: 800; color: #ffffff; margin: 0; }
.page-subtitle { font-size: 0.82rem; color: #90caf9; margin-top: 4px; }

/* Section headers */
.section-header {
    font-size: 1rem; font-weight: 700; color: #2196F3;
    border-left: 4px solid #2196F3; padding-left: 10px; margin: 22px 0 12px;
}

/* Home hero */
.hero-card {
    background: linear-gradient(135deg, #0d2137 0%, #1a3a5c 50%, #0d2137 100%);
    border: 1px solid #2196F3; border-radius: 20px; padding: 36px 40px;
    text-align: center; margin-bottom: 28px;
    box-shadow: 0 8px 40px rgba(33,150,243,0.2);
}
.hero-title { font-size: 2.4rem; font-weight: 800; color: #ffffff; margin-bottom: 8px; }
.hero-sub   { font-size: 1rem; color: #90caf9; margin-bottom: 20px; }
.badge {
    display: inline-block; background: rgba(76,175,80,0.15); border: 1px solid #4CAF50;
    border-radius: 20px; padding: 5px 14px; font-size: 0.72rem; color: #4CAF50;
    font-weight: 600; margin: 4px;
}
.page-guide-card {
    background: linear-gradient(135deg, #1e3a5f 0%, #0d2137 100%);
    border: 1px solid #1e3a5f; border-radius: 12px; padding: 18px;
    transition: border-color 0.2s;
}
.page-guide-card:hover { border-color: #2196F3; }
.compare-better { background: rgba(76,175,80,0.2); border-radius: 6px;
    padding: 2px 8px; color: #4CAF50; font-weight: 700; }
.compare-worse  { background: rgba(244,67,54,0.2); border-radius: 6px;
    padding: 2px 8px; color: #F44336; font-weight: 700; }
.footer {
    text-align: center; color: #546e7a; font-size: 0.72rem;
    padding: 16px; border-top: 1px solid #1e3a5f; margin-top: 30px;
}
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
PROC = os.path.join(BASE, "data", "processed")
RPT  = os.path.join(BASE, "reports")

@st.cache_data
def load_data():
    d = {}
    d["fund_master"]  = pd.read_csv(f"{PROC}/01_fund_master.csv")
    d["aum_by_fh"]    = pd.read_csv(f"{PROC}/03_aum_by_fund_house.csv")
    d["sip_monthly"]  = pd.read_csv(f"{PROC}/04_monthly_sip_inflows.csv")
    d["cat_inflows"]  = pd.read_csv(f"{PROC}/05_category_inflows.csv")
    d["folio"]        = pd.read_csv(f"{PROC}/06_industry_folio_count.csv")
    d["clean_perf"]   = pd.read_csv(f"{PROC}/clean_performance.csv")
    d["benchmark"]    = pd.read_csv(f"{PROC}/10_benchmark_indices.csv", parse_dates=["date"])
    nav_raw           = pd.read_csv(f"{PROC}/clean_nav.csv", parse_dates=["date"])
    nav_raw["amfi_code"] = nav_raw["amfi_code"].astype("Int64")
    d["nav"]          = nav_raw
    tx_raw            = pd.read_csv(f"{PROC}/clean_transactions.csv", parse_dates=["transaction_date"])
    d["transactions"] = tx_raw
    sc                = pd.read_csv(f"{RPT}/fund_scorecard.csv")
    sc["cagr_3yr_pct"] = sc["cagr_3yr"] * 100
    d["scorecard"]    = sc
    d["alpha_beta"]   = pd.read_csv(f"{RPT}/alpha_beta.csv")
    return d

DATA = load_data()

# ── COLOUR CONSTANTS ──────────────────────────────────────────────────────────
BLUE   = "#2196F3"
GREEN  = "#4CAF50"
ORANGE = "#FF9800"
OFFWHITE = "#F5F0E8"
BG     = "#0f1923"
CARD   = "#1e3a5f"
WHITE  = "#FFFFFF"
TEXT_L = "#e0e8f0"

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(7,19,32,0.97)",
    plot_bgcolor ="rgba(7,19,32,0.0)",
    font=dict(family="Inter", color=TEXT_L, size=12),
    margin=dict(l=60, r=40, t=60, b=60),
    legend=dict(
        bgcolor="rgba(13,27,42,0.85)",
        bordercolor=BLUE, borderwidth=1,
        font=dict(color=WHITE, size=12),
        x=0.01, y=0.99,
    ),
    xaxis=dict(
        gridcolor="#1e3a5f", linecolor=BLUE,
        tickfont=dict(size=12, color=WHITE),
        title_font=dict(color=TEXT_L, size=13),
    ),
    yaxis=dict(
        gridcolor="#1e3a5f", linecolor=BLUE,
        tickfont=dict(size=12, color=WHITE),
        title_font=dict(color=TEXT_L, size=13),
    ),
)

COLOR_MAP = {
    "SBI Mutual Fund": BLUE, "HDFC Mutual Fund": GREEN,
    "ICICI Prudential MF": ORANGE, "Nippon India MF": "#E91E63",
    "Kotak Mahindra MF": "#9C27B0", "Axis Mutual Fund": "#00BCD4",
    "Aditya Birla Sun Life MF": "#FF5722", "UTI Mutual Fund": "#607D8B",
    "Mirae Asset MF": "#8BC34A", "DSP Mutual Fund": "#FFC107",
}
COLORS_SEQ = [BLUE, GREEN, ORANGE, "#E91E63", "#9C27B0", "#00BCD4", "#FF5722", "#8BC34A", "#FFC107", "#607D8B"]

def footer():
    today = datetime.date.today().strftime("%d %b %Y")  # display only
    st.markdown(f"""<div class='footer'>
      Bluestock MF Analytics Platform &nbsp;|&nbsp; Data as of Jun 2026
      &nbsp;|&nbsp; Generated: {today} &nbsp;|&nbsp; Bluestock Fintech
    </div>""", unsafe_allow_html=True)

def csv_download(df, label, filename, key="csv_dl"):
    if df is None or len(df) == 0:
        st.caption(f"⚠️ No data to export for {label}")
        return
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 {label} (CSV)",
        data=csv,
        file_name=filename,
        mime="text/csv",
        key=key
    )

def excel_download(df, label, filename, sheet="Data", key="xl_dl"):
    if df is None or len(df) == 0:
        st.caption(f"⚠️ No data to export for {label}")
        return
    try:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df.to_excel(w, sheet_name=sheet[:31], index=False)
        buf.seek(0)
        st.download_button(
            label=f"📊 {label} (Excel)",
            data=buf.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=key
        )
    except Exception as e:
        st.caption(f"Export error: {e}")

def yoy_badge(current, previous, unit="", fmt=".1f", suffix="YoY"):
    if previous and previous != 0:
        pct = ((current - previous) / abs(previous)) * 100
        arrow = "↑" if pct >= 0 else "↓"
        clr = "#4CAF50" if pct >= 0 else "#F44336"
        return f"<span style='color:{clr};font-size:0.68rem;font-weight:700;'>{arrow} {pct:+{fmt}}% {suffix}</span>"
    return ""

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px;'>
      <div style='font-size:2.2rem;'>📈</div>
      <div style='font-size:1.2rem;font-weight:800;color:#2196F3;'>Bluestock</div>
      <div style='font-size:0.7rem;color:#90caf9;'>MF Analytics Platform</div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    page = st.radio("Navigate", [
        "🏠 Dashboard Home",
        "🏭 Industry Overview",
        "📊 Fund Performance",
        "👥 Investor Analytics",
        "📈 SIP & Market Trends",
        "🎲 Monte Carlo Simulation",
        "🎯 Portfolio Optimization",
    ], label_visibility="collapsed")

    st.markdown("""
    <hr>
    <div style='font-size:0.68rem;color:#546e7a;text-align:center;line-height:1.7;'>
      <span style='color:#4CAF50;'>●</span> 40 Schemes &nbsp;|&nbsp; 10 AMCs<br>
      32K+ Transactions &nbsp;|&nbsp; 4.5 Yrs Data<br>
      <span style='color:#2196F3;font-weight:600;'>✅ 100% Data Quality</span><br>
      Last Updated: Jun 2026
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
#  PAGE 0 — DASHBOARD HOME
# ════════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard Home":
    st.markdown("""
    <div class='hero-card'>
      <div style='font-size:3rem;margin-bottom:8px;'>📈</div>
      <div class='hero-title'>Bluestock MF Analytics Platform</div>
      <div class='hero-sub'>Professional Mutual Fund Intelligence for the Indian Market</div>
      <div>
        <span class='badge'>✅ 100% Data Quality</span>
        <span class='badge'>📅 Last Updated: Jun 2026</span>
        <span class='badge'>🔄 Refresh: Daily</span>
        
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats
    sc   = DATA["scorecard"]
    tx   = DATA["transactions"]
    aum  = DATA["aum_by_fh"]
    sip  = DATA["sip_monthly"]
    folio= DATA["folio"]

    total_aum   = round(aum[aum["date"]==aum["date"].max()]["aum_crore"].sum()/100000, 1)
    max_sip     = int(sip["sip_inflow_crore"].max())
    latest_fol  = folio["total_folios_crore"].iloc[-1]
    prev_fol    = folio["total_folios_crore"].iloc[-3] if len(folio) >= 3 else latest_fol

    sip["month_dt"] = pd.to_datetime(sip["month"] + "-01")
    cur_sip_idx  = sip.sort_values("month_dt").iloc[-1]["sip_inflow_crore"]
    prev_sip_idx = sip.sort_values("month_dt").iloc[-13]["sip_inflow_crore"] if len(sip) >= 13 else cur_sip_idx

    k1, k2, k3, k4, k5 = st.columns(5)
    cards = [
        (k1, "Total Industry AUM", f"₹{total_aum}L Cr", "Dec 2025", "", ""),
        (k2, "Peak SIP Inflow", f"₹{max_sip:,} Cr", "Dec 2025 record", "", ""),
        (k3, "Total Folios", f"{latest_fol:.2f} Cr", "Dec 2025",
            yoy_badge(latest_fol, prev_fol, suffix="growth"), ""),
        (k4, "Fund Schemes", "40", "In this analysis",
            "<span style='color:#90caf9;font-size:0.68rem;'>Across 10 AMCs</span>", ""),
        (k5, "Transactions", "32,778", "Jan 2024–May 2025",
            "<span style='color:#90caf9;font-size:0.68rem;'>4.5 Years of data</span>", ""),
    ]
    for col, lbl, val, sub, yoy, _ in cards:
        with col:
            st.markdown(f"""<div class='kpi-card'>
              <div class='kpi-label'>{lbl}</div>
              <div class='kpi-value'>{val}</div>
              <div class='kpi-sub'>{sub}</div>
              <div class='kpi-yoy'>{yoy}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Page guide
    st.markdown("<div class='section-header'>🗺️ Dashboard Navigation Guide</div>", unsafe_allow_html=True)
    g1, g2, g3, g4 = st.columns(4)
    guides = [
        (g1, "🏭", "Industry Overview", BLUE,
         "KPI cards, SIP AUM trend, AMC-wise AUM grouped bar, folio growth stacked area."),
        (g2, "📊", "Fund Performance", GREEN,
         "Risk-return scatter, scorecard table, NAV vs NIFTY 100, fund comparison tool, drill-through."),
        (g3, "👥", "Investor Analytics", ORANGE,
         "State-wise volume, transaction type donut, SIP by age group, monthly trend, T30/B30 split."),
        (g4, "📈", "SIP & Market Trends", "#E91E63",
         "SIP vs NIFTY dual-axis, category heatmap, FY25 top categories, YoY growth rate."),
    ]
    for col, icon, title, clr, desc in guides:
        with col:
            st.markdown(f"""<div class='page-guide-card'>
              <div style='font-size:1.8rem;margin-bottom:6px;'>{icon}</div>
              <div style='font-size:0.9rem;font-weight:700;color:{clr};margin-bottom:6px;'>{title}</div>
              <div style='font-size:0.75rem;color:#90caf9;line-height:1.5;'>{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Bonus pages
    b1, b2 = st.columns(2)
    with b1:
        st.markdown(f"""<div class='page-guide-card'>
          <div style='font-size:1.5rem;'>🎲</div>
          <div style='font-weight:700;color:#9C27B0;margin:4px 0;'>Monte Carlo Simulation </div>
          <div style='font-size:0.75rem;color:#90caf9;'>10,000 simulations for selected funds. 5th/50th/95th percentile bands. Probability of target CAGR.</div>
        </div>""", unsafe_allow_html=True)
    with b2:
        st.markdown(f"""<div class='page-guide-card'>
          <div style='font-size:1.5rem;'>🎯</div>
          <div style='font-weight:700;color:{GREEN};margin:4px 0;'>Portfolio Optimization </div>
          <div style='font-size:0.75rem;color:#90caf9;'>Markowitz Efficient Frontier for top 5 funds. Max Sharpe & Min Volatility portfolios with weight sliders.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Methodology & Glossary
    with st.expander("📐 Methodology & Calculations", expanded=False):
        st.markdown("""
| Metric | Formula | Source |
|--------|---------|--------|
| **CAGR** | `(End NAV / Start NAV)^(1/years) - 1` | clean_nav.csv |
| **Sharpe Ratio** | `(Rp - Rf) / σp` where Rf = 6% p.a. | fund_scorecard.csv |
| **Alpha (Jensen's)** | `Rp - [Rf + β(Rm - Rf)]` | alpha_beta.csv |
| **Beta** | `Cov(Rp, Rm) / Var(Rm)` vs NIFTY 100 | alpha_beta.csv |
| **Max Drawdown** | `(Trough - Peak) / Peak` | fund_scorecard.csv |
| **Bluestock Score** | Composite: 40% CAGR + 30% Sharpe + 20% Alpha + 10% (1-MaxDD) | fund_scorecard.csv |
        """)

    with st.expander("📖 Glossary", expanded=False):
        st.markdown("""
- **AUM** — Assets Under Management (₹ Crore)
- **NAV** — Net Asset Value (price per unit)
- **SIP** — Systematic Investment Plan (monthly fixed amount)
- **CAGR** — Compound Annual Growth Rate (%)
- **Sharpe** — Risk-adjusted return (higher = better)
- **Alpha** — Excess return vs benchmark (higher = better)
- **Beta** — Sensitivity to market moves (1 = market-like)
- **T30** — Top 30 cities by AUM; **B30** — Beyond Top 30
- **ELSS** — Equity Linked Savings Scheme (tax-saving)
- **Drawdown** — Peak-to-trough NAV decline (%)
        """)

    with st.expander("❓ FAQ", expanded=False):
        st.markdown("""
**Q: What is the data period?**  
A: NAV data Jan 2022–May 2026 (4.5 years). Transactions Jan 2024–May 2025.

**Q: How many funds are analyzed?**  
A: 40 SEBI-registered mutual fund schemes across 10 fund houses.

**Q: Is this real AMFI data?**  
A: Data is representative of real AMFI disclosures, structured for analytical purposes.

**Q: What benchmark is used?**  
A: NIFTY 100 TRI for equity funds; CRISIL indices for debt.
        """)

    # Tech stack
    st.markdown("<div class='section-header'>🛠️ Technology Stack</div>", unsafe_allow_html=True)
    t1,t2,t3,t4,t5 = st.columns(5)
    tech = [
        (t1,"🐍","Python 3.9","Core Language"),
        (t2,"📊","Streamlit 1.50","Web Framework"),
        (t3,"📉","Plotly 6.7","Visualizations"),
        (t4,"🐼","Pandas + NumPy","Data Processing"),
        (t5,"🗄️","SQLite","Star-Schema DB"),
    ]
    for col, icon, name, role in tech:
        with col:
            st.markdown(f"""<div style='text-align:center;padding:14px;background:#1e3a5f;
              border-radius:10px;border:1px solid #1e3a5f;'>
              <div style='font-size:1.5rem;'>{icon}</div>
              <div style='font-size:0.8rem;font-weight:700;color:{BLUE};'>{name}</div>
              <div style='font-size:0.68rem;color:#90caf9;'>{role}</div>
            </div>""", unsafe_allow_html=True)

    footer()

# ════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — INDUSTRY OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
elif page == "🏭 Industry Overview":
    st.markdown("""<div class='page-header'>
      <div class='page-title'>🏭 Bluestock MF Analytics — Industry Overview</div>
      <div class='page-subtitle'>Macro view of India's Mutual Fund industry • Jan 2022 – Dec 2025</div>
    </div>""", unsafe_allow_html=True)

    sip   = DATA["sip_monthly"].copy()
    folio = DATA["folio"].copy()
    aum_fh= DATA["aum_by_fh"].copy()
    sip["month_dt"] = pd.to_datetime(sip["month"] + "-01")
    sip_sorted = sip.sort_values("month_dt")

    total_aum   = round(aum_fh[aum_fh["date"]==aum_fh["date"].max()]["aum_crore"].sum()/100000, 1)
    max_sip_inf = int(sip["sip_inflow_crore"].max())
    latest_fol  = folio["total_folios_crore"].iloc[-1]
    prev_fol    = folio["total_folios_crore"].iloc[-3] if len(folio)>3 else latest_fol
    cur_sip     = sip_sorted["sip_inflow_crore"].iloc[-1]
    prev_sip    = sip_sorted["sip_inflow_crore"].iloc[-13] if len(sip_sorted)>=13 else cur_sip

    k1,k2,k3,k4 = st.columns(4)
    def kpi(col, lbl, val, sub, yoy_html=""):
        with col:
            st.markdown(f"""<div class='kpi-card'>
              <div class='kpi-label'>{lbl}</div>
              <div class='kpi-value'>{val}</div>
              <div class='kpi-sub'>{sub}</div>
              <div class='kpi-yoy'>{yoy_html}</div>
            </div>""", unsafe_allow_html=True)

    kpi(k1,"Total Industry AUM", f"₹{total_aum}L Cr","As of Dec 2025",
        yoy_badge(total_aum, round(aum_fh[aum_fh["date"]=="2024-12-31"]["aum_crore"].sum()/100000,1) if "2024-12-31" in aum_fh["date"].values else total_aum))
    kpi(k2,"Peak SIP Inflow",f"₹{max_sip_inf:,} Cr","Dec 2025 record",
        yoy_badge(cur_sip, prev_sip, suffix="YoY"))
    kpi(k3,"Total Folios",f"{latest_fol:.2f} Cr","Dec 2025",
        yoy_badge(latest_fol, prev_fol, suffix="growth"))
    kpi(k4,"Registered Schemes","1,908","Across SEBI categories",
        "<span style='color:#90caf9;font-size:0.68rem;'>40 in this analysis</span>")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📉 Industry AUM Trend — SIP AUM vs Monthly Inflows</div>", unsafe_allow_html=True)
    sip["aum_lakh_cr"] = sip["sip_aum_lakh_crore"]
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Scatter(
        x=sip["month_dt"], y=sip["aum_lakh_cr"],
        name="SIP AUM (₹ Lakh Cr)", mode="lines+markers",
        line=dict(color=BLUE, width=2.5), marker=dict(size=4),
        fill="tozeroy", fillcolor="rgba(33,150,243,0.08)",
        hovertemplate="<b>%{x|%b %Y}</b><br>SIP AUM: ₹%{y:.2f} Lakh Cr<extra></extra>"
    ), secondary_y=False)
    fig1.add_trace(go.Bar(
        x=sip["month_dt"], y=sip["sip_inflow_crore"],
        name="SIP Inflow (₹ Crore)", marker_color="rgba(76,175,80,0.55)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Inflow: ₹%{y:,.0f} Cr<extra></extra>"
    ), secondary_y=True)
    fig1.update_layout(**CHART_LAYOUT,
        title=dict(text="SIP AUM (₹ Lakh Crore) vs Monthly SIP Inflow (₹ Crore)", font=dict(size=14,color="#90caf9")),
        height=400, hovermode="x unified")
    fig1.update_yaxes(title_text="SIP AUM (₹ Lakh Crore)", gridcolor="#1e3a5f",
        tickfont=dict(color=WHITE,size=12), title_font=dict(color=TEXT_L), secondary_y=False)
    fig1.update_yaxes(title_text="Monthly SIP Inflow (₹ Crore)", gridcolor="#1e3a5f",
        tickfont=dict(color=WHITE,size=12), title_font=dict(color=TEXT_L), secondary_y=True)
    st.plotly_chart(fig1, use_container_width=True)

    # Export
    col_exp = st.columns([1,1,6])
    with col_exp[0]: csv_download(sip[["month","sip_inflow_crore","sip_aum_lakh_crore"]], "SIP Data", "sip_inflows.csv", key="csv_p1_sip")
    with col_exp[1]: excel_download(sip[["month","sip_inflow_crore","sip_aum_lakh_crore"]], "SIP Data", "sip_inflows.xlsx", key="xl_p1_sip")

    st.markdown("<div class='section-header'>🏦 AUM by Fund House (Yearly 2022–2025)</div>", unsafe_allow_html=True)
    aum_fh["year"] = pd.to_datetime(aum_fh["date"]).dt.year
    yearly = aum_fh.groupby(["year","fund_house"])["aum_crore"].max().reset_index()
    yearly["aum_lakh_cr"] = yearly["aum_crore"]/100000
    fig2 = go.Figure()
    for fh in yearly["fund_house"].unique():
        sub = yearly[yearly["fund_house"]==fh]
        ann = "<br><b>★ Market Leader</b>" if fh=="SBI Mutual Fund" else ""
        fig2.add_trace(go.Bar(
            x=sub["year"].astype(str), y=sub["aum_lakh_cr"],
            name=fh.replace(" Mutual Fund","").replace(" MF",""),
            marker_color=COLOR_MAP.get(fh,"#90caf9"),
            hovertemplate=f"<b>{fh}</b><br>Year: %{{x}}<br>AUM: ₹%{{y:.2f}} Lakh Cr{ann}<extra></extra>"
        ))
    fig2.update_layout(**CHART_LAYOUT,
        title=dict(text="Top 10 AMCs — AUM by Year (₹ Lakh Crore)", font=dict(size=14,color="#90caf9")),
        barmode="group", height=420, hovermode="closest")
    fig2.update_xaxes(title_text="Year", tickfont=dict(color=WHITE,size=12))
    fig2.update_yaxes(title_text="AUM (₹ Lakh Crore)", gridcolor="#1e3a5f", tickfont=dict(color=WHITE,size=12))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>📁 Industry Folio Count Growth (Crore)</div>", unsafe_allow_html=True)
    fol = DATA["folio"].copy()
    fol["month_dt"] = pd.to_datetime(fol["month"]+"-01")
    fig3 = go.Figure()
    for col_name, clr, lbl in [("equity_folios_crore",BLUE,"Equity"),("debt_folios_crore",GREEN,"Debt"),("hybrid_folios_crore",ORANGE,"Hybrid")]:
        fig3.add_trace(go.Scatter(x=fol["month_dt"], y=fol[col_name], mode="lines+markers",
            name=lbl, line=dict(color=clr,width=2), marker=dict(size=5),
            stackgroup="one",
            hovertemplate=f"<b>{lbl}</b><br>%{{x|%b %Y}}: %{{y:.2f}} Cr folios<extra></extra>"))
    fig3.update_layout(**CHART_LAYOUT,
        title=dict(text="Folio Count by Category (Crore) — Stacked Area", font=dict(size=14,color="#90caf9")),
        height=320, hovermode="x unified")
    fig3.update_xaxes(tickfont=dict(color=WHITE,size=12))
    fig3.update_yaxes(title_text="Folios (Crore)", gridcolor="#1e3a5f", tickfont=dict(color=WHITE,size=12))
    st.plotly_chart(fig3, use_container_width=True)
    footer()

# ════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — FUND PERFORMANCE
# ════════════════════════════════════════════════════════════════════════════
elif page == "📊 Fund Performance":
    st.markdown("""<div class='page-header'>
      <div class='page-title'>📊 Bluestock MF Analytics — Fund Performance</div>
      <div class='page-subtitle'>Risk-Return Analysis • Scorecard • NAV vs Benchmark • Fund Comparison</div>
    </div>""", unsafe_allow_html=True)

    sc   = DATA["scorecard"].copy()
    perf = DATA["clean_perf"].copy()
    fm   = DATA["fund_master"].copy()
    nav  = DATA["nav"].copy()
    bench= DATA["benchmark"].copy()

    sc = sc.merge(fm[["amfi_code","fund_house","plan"]].drop_duplicates("amfi_code"), on="amfi_code", how="left")
    sc = sc.merge(perf[["amfi_code","std_dev_ann_pct","aum_crore"]].drop_duplicates("amfi_code"), on="amfi_code", how="left")

    # ── SLICERS ──
    sl1, sl2, sl3 = st.columns(3)
    all_fh   = sorted(sc["fund_house"].dropna().unique())
    all_cat  = sorted(sc["category"].dropna().unique())
    all_plan = sorted(sc["plan"].dropna().unique()) if "plan" in sc.columns else ["Regular","Direct"]
    with sl1: sel_fh   = st.multiselect("🏦 Fund House",   all_fh,   default=all_fh,   key="p2_fh")
    with sl2: sel_cat  = st.multiselect("📂 Category",     all_cat,  default=all_cat,  key="p2_cat")
    with sl3: sel_plan = st.multiselect("📋 Plan",         all_plan, default=all_plan, key="p2_plan")

    mask = (sc["fund_house"].isin(sel_fh or all_fh) & sc["category"].isin(sel_cat or all_cat))
    if "plan" in sc.columns and sel_plan: mask &= sc["plan"].isin(sel_plan)
    sc_f = sc[mask].copy()
    sc_f["short_name"] = sc_f["scheme_name"].str.replace(r" - (Regular|Direct) (Plan )?- Growth","",regex=True).str[:35]
    sc_f["aum_plot"]   = sc_f["aum_crore"].fillna(500).clip(lower=100)
    sharpe_min = float(sc_f["sharpe_ratio"].quantile(0.05))
    sharpe_max = float(sc_f["sharpe_ratio"].quantile(0.95))

    # ── SCATTER ──
    st.markdown("<div class='section-header'>🎯 Risk-Return Scatter (Bubble = AUM | Color = Sharpe)</div>", unsafe_allow_html=True)
    fig_sc = px.scatter(sc_f, x="cagr_3yr_pct", y="std_dev_ann_pct",
        size="aum_plot", color="sharpe_ratio", hover_name="short_name",
        hover_data={"fund_house":True,"cagr_3yr_pct":":.1f","sharpe_ratio":":.2f","aum_plot":":.0f"},
        color_continuous_scale=[[0,"#F44336"],[0.5,"#FF9800"],[1,"#4CAF50"]],
        range_color=[sharpe_min, sharpe_max],
        size_max=40,
        labels={"cagr_3yr_pct":"3yr CAGR (%)","std_dev_ann_pct":"Std Dev Ann (%)","sharpe_ratio":"Sharpe","aum_plot":"AUM (₹ Cr)"})
    fig_sc.update_layout(**CHART_LAYOUT,
        title=dict(text="Risk vs Return — All Filtered Funds", font=dict(size=14,color="#90caf9")),
        height=430, coloraxis_colorbar=dict(title="Sharpe Ratio",tickfont=dict(color=WHITE,size=11),title_font=dict(color=TEXT_L,size=11)))
    fig_sc.update_traces(marker=dict(line=dict(width=1,color="#071320")))
    fig_sc.update_xaxes(tickfont=dict(color=WHITE,size=12), title_font=dict(color=TEXT_L))
    fig_sc.update_yaxes(tickfont=dict(color=WHITE,size=12), title_font=dict(color=TEXT_L))
    st.plotly_chart(fig_sc, use_container_width=True)

    # ── SCORECARD TABLE ──
    st.markdown("<div class='section-header'>📋 Fund Scorecard Table (sorted by Bluestock Score ↓)</div>", unsafe_allow_html=True)
    tbl = sc_f[["rank","scheme_name","fund_house","category","cagr_3yr_pct","sharpe_ratio","alpha","max_drawdown","composite_score"]].copy()
    tbl.columns = ["Rank","Scheme","Fund House","Category","3yr CAGR (%)","Sharpe","Alpha (%)","Max DD (%)","Score"]
    for c in ["3yr CAGR (%)","Sharpe","Alpha (%)","Max DD (%)","Score"]:
        tbl[c] = tbl[c].round(2)
    tbl = tbl.sort_values("Score", ascending=False)
    st.dataframe(tbl.set_index("Rank"), use_container_width=True, height=300)
    exp1, exp2, _ = st.columns([1,1,6])
    with exp1: csv_download(tbl, "Scorecard", "fund_scorecard.csv", key="csv_p2_sc")
    with exp2: excel_download(tbl, "Scorecard", "fund_scorecard.xlsx", "Scorecard", key="xl_p2_sc")

    # ── NAV vs BENCHMARK ──
    st.markdown("<div class='section-header'>📈 Top 5 Funds NAV vs NIFTY 100 (Indexed to 100)</div>", unsafe_allow_html=True)
    top5_sc    = DATA["scorecard"].sort_values("composite_score",ascending=False).head(5)
    top5_codes = top5_sc["amfi_code"].tolist()
    top5_names = {int(r["amfi_code"]): r["scheme_name"].replace(" - Regular Plan - Growth","").replace(" - Regular - Growth","")[:28]
                  for _,r in top5_sc.iterrows()}
    cutoff = pd.Timestamp("2023-06-01")
    nav_f  = nav[(nav["amfi_code"].isin(top5_codes)) & (nav["date"]>=cutoff)].copy()
    nifty  = bench[(bench["index_name"]=="NIFTY100") & (bench["date"]>=cutoff)].sort_values("date")
    fig_nav = go.Figure()
    for i, code in enumerate(top5_codes):
        sub = nav_f[nav_f["amfi_code"]==code].sort_values("date")
        if len(sub)<2: continue
        base = sub["nav"].iloc[0]
        fig_nav.add_trace(go.Scatter(x=sub["date"], y=(sub["nav"]/base)*100,
            mode="lines", name=top5_names.get(int(code),str(code)),
            line=dict(color=COLORS_SEQ[i%len(COLORS_SEQ)],width=2),
            hovertemplate=f"<b>{top5_names.get(int(code),str(code))}</b><br>%{{x|%d %b %Y}}: %{{y:.1f}}<extra></extra>"))
    if len(nifty)>1:
        bn = nifty["close_value"].iloc[0]
        fig_nav.add_trace(go.Scatter(x=nifty["date"], y=(nifty["close_value"]/bn)*100,
            mode="lines", name="NIFTY 100",
            line=dict(color=OFFWHITE,width=2,dash="dot"),
            hovertemplate="<b>NIFTY 100</b><br>%{x|%d %b %Y}: %{y:.1f}<extra></extra>"))
    fig_nav.update_layout(**CHART_LAYOUT,
        title=dict(text="NAV Indexed Return (Base=100) vs NIFTY 100", font=dict(size=14,color="#90caf9")),
        height=400, hovermode="x unified")
    fig_nav.update_xaxes(tickfont=dict(color=WHITE,size=12))
    fig_nav.update_yaxes(title_text="Indexed Return (Base=100)", gridcolor="#1e3a5f", tickfont=dict(color=WHITE,size=12))
    st.plotly_chart(fig_nav, use_container_width=True)

    # ── FUND COMPARISON TOOL ──
    st.markdown("<div class='section-header'>⚡ Fund Comparison Tool — Side-by-Side Analysis</div>", unsafe_allow_html=True)
    fund_list = sc_f["scheme_name"].dropna().tolist()
    c1,c2,c3 = st.columns([2,2,1])
    with c1: fund1 = st.selectbox("Select Fund 1", fund_list, index=0, key="cmp1")
    with c2: fund2 = st.selectbox("Select Fund 2", fund_list, index=min(1,len(fund_list)-1), key="cmp2")
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        compare_btn = st.button("🔍 Compare Funds", use_container_width=True)

    if compare_btn and fund1 != fund2:
        r1 = sc_f[sc_f["scheme_name"]==fund1].iloc[0]
        r2 = sc_f[sc_f["scheme_name"]==fund2].iloc[0]
        metrics = {
            "3yr CAGR (%)": ("cagr_3yr_pct", True),
            "Sharpe Ratio":  ("sharpe_ratio", True),
            "Alpha (%)":     ("alpha",        True),
            "Max Drawdown (%)": ("max_drawdown", False),
            "Bluestock Score":  ("composite_score", True),
        }
        exp_r = perf[perf["amfi_code"]==r1["amfi_code"]]
        exp_r2= perf[perf["amfi_code"]==r2["amfi_code"]]
        if not exp_r.empty:
            metrics["Expense Ratio (%)"] = ("expense_ratio_pct_x", True)
            r1["expense_ratio_pct_x"] = exp_r.iloc[0].get("expense_ratio_pct", 0)
            r2["expense_ratio_pct_x"] = exp_r2.iloc[0].get("expense_ratio_pct", 0) if not exp_r2.empty else 0
            metrics["Expense Ratio (%)"] = ("expense_ratio_pct_x", False)

        rows = []
        for mname, (col_key, higher_better) in metrics.items():
            v1 = round(float(r1.get(col_key, 0)), 2)
            v2 = round(float(r2.get(col_key, 0)), 2)
            if higher_better:
                tag1 = "compare-better" if v1 >= v2 else "compare-worse"
                tag2 = "compare-better" if v2 >= v1 else "compare-worse"
            else:
                tag1 = "compare-better" if v1 <= v2 else "compare-worse"
                tag2 = "compare-better" if v2 <= v1 else "compare-worse"
            rows.append((mname, v1, v2, tag1, tag2))

        cm1, cm2 = st.columns(2)
        with cm1:
            st.markdown(f"<h4 style='color:{BLUE};text-align:center;'>{fund1[:45]}</h4>", unsafe_allow_html=True)
        with cm2:
            st.markdown(f"<h4 style='color:{GREEN};text-align:center;'>{fund2[:45]}</h4>", unsafe_allow_html=True)

        for mname, v1, v2, t1, t2 in rows:
            row_cols = st.columns([2,1,1])
            with row_cols[0]:
                st.markdown(f"<div style='color:#90caf9;font-size:0.85rem;padding:6px 0;border-bottom:1px solid #1e3a5f;'>{mname}</div>", unsafe_allow_html=True)
            with row_cols[1]:
                st.markdown(f"<div style='text-align:center;padding:6px 0;border-bottom:1px solid #1e3a5f;'><span class='{t1}'>{v1}</span></div>", unsafe_allow_html=True)
            with row_cols[2]:
                st.markdown(f"<div style='text-align:center;padding:6px 0;border-bottom:1px solid #1e3a5f;'><span class='{t2}'>{v2}</span></div>", unsafe_allow_html=True)

        # Side-by-side NAV
        code1,code2 = int(r1["amfi_code"]), int(r2["amfi_code"])
        n1 = nav[(nav["amfi_code"]==code1)&(nav["date"]>=cutoff)].sort_values("date")
        n2 = nav[(nav["amfi_code"]==code2)&(nav["date"]>=cutoff)].sort_values("date")
        if len(n1)>1 and len(n2)>1:
            fig_cmp = go.Figure()
            fig_cmp.add_trace(go.Scatter(x=n1["date"], y=(n1["nav"]/n1["nav"].iloc[0])*100,
                name=fund1[:28], line=dict(color=BLUE,width=2.5),
                hovertemplate="%{x|%d %b %Y}: %{y:.1f}<extra></extra>"))
            fig_cmp.add_trace(go.Scatter(x=n2["date"], y=(n2["nav"]/n2["nav"].iloc[0])*100,
                name=fund2[:28], line=dict(color=GREEN,width=2.5),
                hovertemplate="%{x|%d %b %Y}: %{y:.1f}<extra></extra>"))
            fig_cmp.update_layout(**CHART_LAYOUT,
                title=dict(text="NAV Comparison (Indexed=100)", font=dict(size=13,color="#90caf9")),
                height=320, hovermode="x unified")
            fig_cmp.update_xaxes(tickfont=dict(color=WHITE,size=12))
            fig_cmp.update_yaxes(title_text="Indexed NAV", gridcolor="#1e3a5f", tickfont=dict(color=WHITE,size=12))
            st.plotly_chart(fig_cmp, use_container_width=True)

        cmp_df = pd.DataFrame([(m, v1, v2) for m,v1,v2,_,_ in rows], columns=["Metric", fund1[:30], fund2[:30]])
        csv_download(cmp_df, "Comparison", "comparison.csv", key="csv_p2_cmp")

    # ── DRILL-THROUGH ──
    st.markdown("<div class='section-header'>🔍 Fund Drill-Through — Detail View</div>", unsafe_allow_html=True)
    sel_fund = st.selectbox("Select fund for detail:", sc_f["scheme_name"].tolist(), key="drill")
    if sel_fund:
        row = sc_f[sc_f["scheme_name"]==sel_fund].iloc[0]
        code = int(row["amfi_code"])
        d1,d2,d3,d4,d5 = st.columns(5)
        for col, lbl, val in [
            (d1,"3yr CAGR",f"{row['cagr_3yr_pct']:.1f}%"),
            (d2,"Sharpe",f"{row['sharpe_ratio']:.2f}"),
            (d3,"Alpha",f"{row['alpha']:.2f}"),
            (d4,"Max DD",f"{row['max_drawdown']:.1f}%"),
            (d5,"Score",f"{row['composite_score']:.0f}"),
        ]:
            with col:
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>{lbl}</div><div class='kpi-value'>{val}</div></div>", unsafe_allow_html=True)

        mini = nav[nav["amfi_code"]==code].sort_values("date").tail(130)
        if len(mini)>2:
            fig_mini = go.Figure(go.Scatter(x=mini["date"], y=mini["nav"],
                mode="lines", fill="tozeroy",
                line=dict(color=BLUE,width=2), fillcolor="rgba(33,150,243,0.1)",
                hovertemplate="%{x|%d %b %Y}: ₹%{y:.2f}<extra></extra>"))
            fig_mini.update_layout(**CHART_LAYOUT, height=220,
                title=dict(text=f"NAV History — {sel_fund[:55]}", font=dict(size=12,color="#90caf9")))
            fig_mini.update_xaxes(tickfont=dict(color=WHITE,size=11))
            fig_mini.update_yaxes(title_text="NAV (₹)", gridcolor="#1e3a5f", tickfont=dict(color=WHITE,size=11))
            st.plotly_chart(fig_mini, use_container_width=True)

        pr = perf[perf["amfi_code"]==code]
        fr = fm[fm["amfi_code"]==code]
        if not pr.empty and not fr.empty:
            i1, i2 = st.columns(2)
            p, f = pr.iloc[0], fr.iloc[0]
            with i1:
                st.markdown("**📊 Performance Metrics**")
                st.markdown(f"- 1yr Return: **{p.get('return_1yr_pct','—')}%** &nbsp;|&nbsp; 3yr: **{p.get('return_3yr_pct','—')}%** &nbsp;|&nbsp; 5yr: **{p.get('return_5yr_pct','—')}%**")
                st.markdown(f"- Std Dev: **{p.get('std_dev_ann_pct','—')}%** &nbsp;|&nbsp; Beta: **{p.get('beta','—')}** &nbsp;|&nbsp; AUM: **₹{p.get('aum_crore','—')} Cr**")
            with i2:
                st.markdown("**📋 Fund Information**")
                st.markdown(f"- Manager: **{f.get('fund_manager','—')}** &nbsp;|&nbsp; Launch: **{f.get('launch_date','—')}**")
                st.markdown(f"- Benchmark: **{f.get('benchmark','—')}** &nbsp;|&nbsp; Expense Ratio: **{f.get('expense_ratio_pct','—')}%**")
    footer()

# ════════════════════════════════════════════════════════════════════════════
#  PAGE 3 — INVESTOR ANALYTICS
# ════════════════════════════════════════════════════════════════════════════
elif page == "👥 Investor Analytics":
    st.markdown("""<div class='page-header'>
      <div class='page-title'>👥 Bluestock MF Analytics — Investor Analytics</div>
      <div class='page-subtitle'>Demographics, Behaviour & Geographic Distribution • 32K+ Transactions</div>
    </div>""", unsafe_allow_html=True)

    tx = DATA["transactions"].copy()
    all_states = sorted(tx["state"].dropna().unique())
    all_ages   = sorted(tx["age_group"].dropna().unique())
    all_tiers  = sorted(tx["city_tier"].dropna().unique())

    sl1,sl2,sl3 = st.columns(3)
    with sl1: sel_state = st.multiselect("🗺️ State",     all_states, default=all_states, key="p3_st")
    with sl2: sel_age   = st.multiselect("👤 Age Group", all_ages,   default=all_ages,   key="p3_ag")
    with sl3: sel_tier  = st.multiselect("🏙️ City Tier", all_tiers,  default=all_tiers,  key="p3_ti")

    tx_f = tx[
        tx["state"].isin(sel_state or all_states) &
        tx["age_group"].isin(sel_age or all_ages) &
        tx["city_tier"].isin(sel_tier or all_tiers)
    ].copy()

    # KPI mini cards with YoY
    cur_vol  = tx_f["amount_inr"].sum()/1e7
    ka,kb,kc,kd = st.columns(4)
    for col, lbl, val, sub in [
        (ka,"Transactions",f"{len(tx_f):,}","Filtered records"),
        (kb,"Total Volume",f"₹{cur_vol:.2f}L Cr","All types"),
        (kc,"SIP Count",f"{(tx_f['transaction_type']=='SIP').sum():,}","Systematic"),
        (kd,"Avg SIP Amount",f"₹{tx_f[tx_f['transaction_type']=='SIP']['amount_inr'].mean():,.0f}","Per SIP"),
    ]:
        with col:
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>{lbl}</div><div class='kpi-value'>{val}</div><div class='kpi-sub'>{sub}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([3,2])

    with left:
        st.markdown("<div class='section-header'>🗺️ Transaction Volume by State (Top 12, ₹ Lakh Crore)</div>", unsafe_allow_html=True)
        sg = tx_f.groupby("state")["amount_inr"].sum().reset_index()
        sg["amt_lc"] = sg["amount_inr"]/1e7
        st12 = sg.nlargest(12,"amt_lc").sort_values("amt_lc")
        fig_st = go.Figure(go.Bar(
            x=st12["amt_lc"], y=st12["state"], orientation="h",
            marker=dict(color=st12["amt_lc"],
                colorscale=[[0,"#1e3a5f"],[0.5,BLUE],[1,GREEN]]),
            hovertemplate="<b>%{y}</b><br>₹%{x:.3f} Lakh Crore<extra></extra>",
            text=st12["amt_lc"].apply(lambda v:f"₹{v:.2f}L Cr"),
            textfont=dict(color=WHITE,size=10), textposition="outside"))
        fig_st.update_layout(**CHART_LAYOUT, height=420,
            title=dict(text="Top 12 States — Transaction Volume (₹ Lakh Crore)", font=dict(size=13,color="#90caf9")))
        fig_st.update_xaxes(title_text="Amount (₹ Lakh Crore)", tickfont=dict(color=WHITE,size=11))
        fig_st.update_yaxes(tickfont=dict(color=WHITE,size=11))
        st.plotly_chart(fig_st, use_container_width=True)

        # State drill-through
        top_state = st12.iloc[-1]["state"] if not st12.empty else None
        with st.expander(f"🔍 Drill-Through: Top State ({top_state})", expanded=False):
            if top_state:
                st_tx = tx_f[tx_f["state"]==top_state]
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown("**Top Cities**")
                    cg = st_tx.groupby("city")["amount_inr"].sum().nlargest(5).reset_index()
                    cg.columns=["City","Amount (₹)"]
                    cg["Amount (₹ Lakh)"] = (cg["Amount (₹)"]/1e5).round(2)
                    st.dataframe(cg[["City","Amount (₹ Lakh)"]].set_index("City"), use_container_width=True)
                with c2:
                    st.markdown("**Transaction Type Split**")
                    tt = st_tx["transaction_type"].value_counts().reset_index()
                    tt.columns = ["Type","Count"]
                    st.dataframe(tt.set_index("Type"), use_container_width=True)

    with right:
        st.markdown("<div class='section-header'>🍩 Transaction Type Split</div>", unsafe_allow_html=True)
        tt = tx_f["transaction_type"].value_counts().reset_index()
        tt.columns = ["type","count"]
        fig_dn = go.Figure(go.Pie(
            labels=tt["type"], values=tt["count"], hole=0.52,
            marker=dict(colors=[BLUE,GREEN,ORANGE]),
            textinfo="label+percent", textfont=dict(size=12,color=WHITE),
            hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>"))
        fig_dn.update_layout(**CHART_LAYOUT, height=280,
            title=dict(text="SIP / Lumpsum / Redemption", font=dict(size=13,color="#90caf9")),
            showlegend=True,
            annotations=[dict(text=f"{len(tx_f):,}<br><span style='font-size:9px'>txns</span>",
                x=0.5,y=0.5,font_size=13,showarrow=False,font_color=WHITE)])
        st.plotly_chart(fig_dn, use_container_width=True)

        st.markdown("<div class='section-header'>🏙️ T30 vs B30 Volume</div>", unsafe_allow_html=True)
        tg = tx_f.groupby("city_tier")["amount_inr"].sum().reset_index()
        tg["amt_lc"] = tg["amount_inr"]/1e7
        fig_t30 = go.Figure(go.Pie(
            labels=tg["city_tier"], values=tg["amt_lc"], hole=0.45,
            marker=dict(colors=[BLUE,ORANGE]),
            textinfo="label+percent", textfont=dict(size=12,color=WHITE),
            hovertemplate="<b>%{label}</b>: ₹%{value:.2f} Lakh Cr<extra></extra>"))
        fig_t30.update_layout(**CHART_LAYOUT, height=260,
            title=dict(text="T30 vs B30 City — Transaction Volume", font=dict(size=13,color="#90caf9")))
        st.plotly_chart(fig_t30, use_container_width=True)

    left2, right2 = st.columns(2)
    with left2:
        st.markdown("<div class='section-header'>👤 Avg SIP Amount by Age Group</div>", unsafe_allow_html=True)
        sip_tx = tx_f[tx_f["transaction_type"]=="SIP"]
        ag = sip_tx.groupby("age_group")["amount_inr"].mean().reindex(["18-25","26-35","36-45","46-55","56+"]).dropna().reset_index()
        ag["amt_k"] = ag["amount_inr"]/1000
        fig_ag = go.Figure(go.Bar(x=ag["age_group"], y=ag["amt_k"],
            marker_color=COLORS_SEQ[:len(ag)],
            text=ag["amt_k"].apply(lambda v:f"₹{v:.1f}K"),
            textfont=dict(color=WHITE,size=11), textposition="outside",
            hovertemplate="<b>%{x}</b><br>Avg SIP: ₹%{y:.1f}K<extra></extra>"))
        fig_ag.update_layout(**CHART_LAYOUT, height=320,
            title=dict(text="Avg SIP Amount by Age Group (₹ Thousands)", font=dict(size=13,color="#90caf9")))
        fig_ag.update_xaxes(title_text="Age Group", tickfont=dict(color=WHITE,size=12))
        fig_ag.update_yaxes(title_text="Avg Amount (₹ '000)", gridcolor="#1e3a5f", tickfont=dict(color=WHITE,size=12))
        st.plotly_chart(fig_ag, use_container_width=True)

    with right2:
        st.markdown("<div class='section-header'>📆 Monthly Transaction Volume Trend</div>", unsafe_allow_html=True)
        tx_f["month"] = tx_f["transaction_date"].dt.to_period("M").astype(str)
        mg = tx_f.groupby("month")["amount_inr"].sum().reset_index()
        mg["amt_lc"] = mg["amount_inr"]/1e7
        mg["mdt"] = pd.to_datetime(mg["month"]+"-01")
        mg = mg.sort_values("mdt")
        fig_mn = go.Figure(go.Scatter(x=mg["mdt"], y=mg["amt_lc"],
            mode="lines+markers", fill="tozeroy",
            line=dict(color=GREEN,width=2), fillcolor="rgba(76,175,80,0.1)",
            marker=dict(size=5,color=GREEN),
            hovertemplate="%{x|%b %Y}: ₹%{y:.3f} Lakh Cr<extra></extra>"))
        fig_mn.update_layout(**CHART_LAYOUT, height=320,
            title=dict(text="Monthly Volume (₹ Lakh Crore)", font=dict(size=13,color="#90caf9")))
        fig_mn.update_xaxes(title_text="Month", tickfont=dict(color=WHITE,size=11))
        fig_mn.update_yaxes(title_text="Volume (₹ Lakh Crore)", gridcolor="#1e3a5f", tickfont=dict(color=WHITE,size=11))
        st.plotly_chart(fig_mn, use_container_width=True)

    e1,e2,_ = st.columns([1,1,6])
    with e1: csv_download(tx_f[["transaction_date","transaction_type","amount_inr","state","age_group","city_tier"]], "Transactions", "transactions.csv", key="csv_p3_tx")
    with e2: excel_download(tx_f[["transaction_date","transaction_type","amount_inr","state","age_group","city_tier"]].head(5000), "Transactions", "transactions.xlsx", key="xl_p3_tx")
    footer()

# ════════════════════════════════════════════════════════════════════════════
#  PAGE 4 — SIP & MARKET TRENDS
# ════════════════════════════════════════════════════════════════════════════
elif page == "📈 SIP & Market Trends":
    st.markdown("""<div class='page-header'>
      <div class='page-title'>📈 Bluestock MF Analytics — SIP & Market Trends</div>
      <div class='page-subtitle'>SIP Flows vs Market Indices • Category Heatmap • Sector Allocation</div>
    </div>""", unsafe_allow_html=True)

    sip   = DATA["sip_monthly"].copy()
    bench = DATA["benchmark"].copy()
    cat   = DATA["cat_inflows"].copy()
    sip["month_dt"] = pd.to_datetime(sip["month"] + "-01")
    sip_sorted = sip.sort_values("month_dt")

    # ── DUAL AXIS ──
    st.markdown("<div class='section-header'>📊 SIP Inflows vs NIFTY 50 (Jan 2022 – Dec 2025)</div>", unsafe_allow_html=True)
    nifty50 = bench[bench["index_name"]=="NIFTY50"].copy().sort_values("date")
    nifty50["month_dt"] = nifty50["date"].dt.to_period("M").apply(lambda p: p.to_timestamp())
    n50m = nifty50.groupby("month_dt")["close_value"].mean().reset_index()
    merged = sip_sorted.merge(n50m, on="month_dt", how="left")

    fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
    fig_dual.add_trace(go.Bar(
        x=merged["month_dt"], y=merged["sip_inflow_crore"],
        name="SIP Inflow (₹ Crore)", marker_color="rgba(33,150,243,0.72)",
        hovertemplate="%{x|%b %Y}: ₹%{y:,.0f} Cr<extra></extra>"
    ), secondary_y=False)
    fig_dual.add_trace(go.Scatter(
        x=merged["month_dt"], y=merged["close_value"],
        name="NIFTY 50", mode="lines+markers",
        line=dict(color=ORANGE, width=2.5), marker=dict(size=4),
        hovertemplate="%{x|%b %Y}: %{y:,.0f} pts<extra></extra>"
    ), secondary_y=True)
    fig_dual.update_layout(**CHART_LAYOUT,
        title=dict(text="SIP Inflow (Bar) vs NIFTY 50 (Line) — Monthly", font=dict(size=14,color="#90caf9")),
        height=420, hovermode="x unified")
    fig_dual.update_yaxes(title_text="SIP Inflow (₹ Crore)", gridcolor="#1e3a5f",
        tickfont=dict(color=WHITE,size=12), title_font=dict(color=TEXT_L), secondary_y=False)
    fig_dual.update_yaxes(title_text="NIFTY 50 (Points)", gridcolor="#1e3a5f",
        tickfont=dict(color=WHITE,size=12), title_font=dict(color=TEXT_L), secondary_y=True)
    fig_dual.update_xaxes(tickfont=dict(color=WHITE,size=12))
    st.plotly_chart(fig_dual, use_container_width=True)

    e1,e2,_ = st.columns([1,1,6])
    with e1: csv_download(merged[["month","sip_inflow_crore","close_value"]].rename(columns={"close_value":"nifty50"}), "SIP+Nifty", "sip_nifty.csv", key="csv_p4_sip")
    with e2: excel_download(merged[["month","sip_inflow_crore","close_value"]].rename(columns={"close_value":"nifty50"}), "SIP+Nifty", "sip_nifty.xlsx", key="xl_p4_sip")

    # ── HEATMAP ──
    st.markdown("<div class='section-header'>🌡️ Category Inflows Heatmap (Month × Category)</div>", unsafe_allow_html=True)
    cat["month_dt"] = pd.to_datetime(cat["month"] + "-01")
    pivot = cat.pivot_table(index="category", columns="month", values="net_inflow_crore", aggfunc="sum").fillna(0)
    fig_heat = go.Figure(go.Heatmap(
        z=pivot.values, x=[str(c) for c in pivot.columns], y=pivot.index.tolist(),
        colorscale=[[0,"#F44336"],[0.5,"#1e3a5f"],[1,"#4CAF50"]],
        hovertemplate="<b>%{y}</b><br>%{x}: ₹%{z:,.0f} Cr<extra></extra>",
        colorbar=dict(title="₹ Crore", tickfont=dict(color=WHITE,size=11), title_font=dict(color=TEXT_L))
    ))
    fig_heat.update_layout(**CHART_LAYOUT,
        title=dict(text="Net Inflows by Category & Month (₹ Crore) — 🟢 Positive | 🔴 Negative", font=dict(size=13,color="#90caf9")),
        height=380)
    fig_heat.update_xaxes(tickangle=-45, tickfont=dict(color=WHITE,size=10))
    fig_heat.update_yaxes(tickfont=dict(color=WHITE,size=11))
    st.plotly_chart(fig_heat, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.markdown("<div class='section-header'>🏆 Top 5 Categories — FY 2024-25 Net Inflow</div>", unsafe_allow_html=True)
        fy25 = cat[cat["month"]>="2024-04"].groupby("category")["net_inflow_crore"].sum().reset_index()
        top5 = fy25.nlargest(5,"net_inflow_crore")
        fig_cat = go.Figure(go.Bar(
            x=top5["category"], y=top5["net_inflow_crore"],
            marker=dict(color=COLORS_SEQ[:5], line=dict(color="#071320",width=1)),
            text=top5["net_inflow_crore"].apply(lambda v:f"₹{v:,.0f}"),
            textfont=dict(color=WHITE,size=11), textposition="outside",
            hovertemplate="<b>%{x}</b><br>Net Inflow: ₹%{y:,.0f} Cr<extra></extra>"))
        fig_cat.update_layout(**CHART_LAYOUT, height=360,
            title=dict(text="Top 5 Fund Categories — FY25 Net Inflow", font=dict(size=13,color="#90caf9")))
        fig_cat.update_xaxes(title_text="Category", tickangle=-15, tickfont=dict(color=WHITE,size=11))
        fig_cat.update_yaxes(title_text="Net Inflow (₹ Crore)", gridcolor="#1e3a5f", tickfont=dict(color=WHITE,size=11))
        st.plotly_chart(fig_cat, use_container_width=True)

    with right:
        st.markdown("<div class='section-header'>📐 SIP Inflow YoY Growth Rate (%)</div>", unsafe_allow_html=True)
        sip2 = sip_sorted[sip_sorted["yoy_growth_pct"].notna()].copy()
        cur_yoy  = sip2["yoy_growth_pct"].iloc[-1] if len(sip2)>0 else 0
        fig_yoy = go.Figure()
        fig_yoy.add_trace(go.Scatter(
            x=sip2["month_dt"], y=sip2["yoy_growth_pct"],
            mode="lines+markers", fill="tozeroy",
            line=dict(color=GREEN,width=2), fillcolor="rgba(76,175,80,0.1)",
            marker=dict(size=5,color=GREEN,line=dict(color="#071320",width=1)),
            hovertemplate="%{x|%b %Y}: %{y:.1f}% YoY<extra></extra>"))
        fig_yoy.add_hline(y=0, line=dict(color=ORANGE,dash="dot",width=1.5))
        fig_yoy.update_layout(**CHART_LAYOUT, height=360,
            title=dict(text=f"SIP Inflow YoY Growth (%) — Latest: {cur_yoy:+.1f}%", font=dict(size=13,color="#90caf9")))
        fig_yoy.update_xaxes(title_text="Month", tickfont=dict(color=WHITE,size=11))
        fig_yoy.update_yaxes(title_text="YoY Growth (%)", gridcolor="#1e3a5f", tickfont=dict(color=WHITE,size=11))
        st.plotly_chart(fig_yoy, use_container_width=True)

    st.markdown("<div class='section-header'>🆕 New & Active SIP Accounts Trend</div>", unsafe_allow_html=True)
    fig_sip2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig_sip2.add_trace(go.Bar(
        x=sip["month_dt"], y=sip["new_sip_accounts_lakh"],
        name="New SIP Accounts (Lakh)", marker_color="rgba(76,175,80,0.65)",
        hovertemplate="%{x|%b %Y}: %{y:.1f} Lakh new<extra></extra>"
    ), secondary_y=False)
    fig_sip2.add_trace(go.Scatter(
        x=sip["month_dt"], y=sip["active_sip_accounts_crore"],
        name="Active SIP Accounts (Crore)", mode="lines",
        line=dict(color=BLUE,width=2.5),
        hovertemplate="%{x|%b %Y}: %{y:.2f} Cr active<extra></extra>"
    ), secondary_y=True)
    fig_sip2.update_layout(**CHART_LAYOUT, height=320, hovermode="x unified",
        title=dict(text="SIP Account Growth — New (Bar) vs Active (Line)", font=dict(size=13,color="#90caf9")))
    fig_sip2.update_yaxes(title_text="New Accounts (Lakh)", gridcolor="#1e3a5f",
        tickfont=dict(color=WHITE,size=12), secondary_y=False)
    fig_sip2.update_yaxes(title_text="Active Accounts (Crore)", gridcolor="#1e3a5f",
        tickfont=dict(color=WHITE,size=12), secondary_y=True)
    fig_sip2.update_xaxes(tickfont=dict(color=WHITE,size=12))
    st.plotly_chart(fig_sip2, use_container_width=True)
    footer()

# ════════════════════════════════════════════════════════════════════════════
#  PAGE 5 — MONTE CARLO SIMULATION
# ════════════════════════════════════════════════════════════════════════════
elif page == "🎲 Monte Carlo Simulation":
    st.markdown("""<div class='page-header'>
      <div class='page-title'>🎲 Monte Carlo Portfolio Simulation</div>
      <div class='page-subtitle'>10,000 simulations • 5-year NAV projection • Confidence bands</div>
    </div>""", unsafe_allow_html=True)

    sc   = DATA["scorecard"].copy()
    perf = DATA["clean_perf"].copy()
    fm   = DATA["fund_master"].copy()
    sc   = sc.merge(fm[["amfi_code","fund_house"]].drop_duplicates("amfi_code"), on="amfi_code", how="left")
    sc   = sc.merge(perf[["amfi_code","std_dev_ann_pct"]].drop_duplicates("amfi_code"), on="amfi_code", how="left")

    fund_list = sc["scheme_name"].dropna().tolist()
    st.markdown("<div class='section-header'>⚙️ Simulation Settings</div>", unsafe_allow_html=True)
    cfg1, cfg2, cfg3 = st.columns(3)
    with cfg1: sel_funds = st.multiselect("Select Funds (2–5)", fund_list, default=fund_list[:3], max_selections=5)
    with cfg2: n_years   = st.slider("Projection Years", 1, 10, 5)
    with cfg3: target_cagr = st.slider("Target CAGR (%)", 5, 30, 15)

    run_btn = st.button("▶️ Run 10,000 Simulations", use_container_width=False)

    if run_btn and sel_funds:
        np.random.seed(42)
        n_sim = 10000
        trading_days = n_years * 252

        all_final_returns = {}
        for fname in sel_funds:
            row = sc[sc["scheme_name"]==fname].iloc[0]
            annual_ret  = float(row["cagr_3yr_pct"]) / 100
            annual_vol  = float(row.get("std_dev_ann_pct", 15)) / 100
            daily_ret   = annual_ret / 252
            daily_vol   = annual_vol / np.sqrt(252)
            paths = np.zeros((n_sim, trading_days + 1))
            paths[:, 0] = 100
            rand_shocks = np.random.normal(daily_ret, daily_vol, (n_sim, trading_days))
            paths[:, 1:] = 100 * np.cumprod(1 + rand_shocks, axis=1)
            all_final_returns[fname] = paths

        days_arr = np.arange(trading_days + 1)

        for fname, paths in all_final_returns.items():
            st.markdown(f"<div class='section-header'>📊 {fname[:55]}</div>", unsafe_allow_html=True)
            p5   = np.percentile(paths, 5,  axis=0)
            p50  = np.percentile(paths, 50, axis=0)
            p95  = np.percentile(paths, 95, axis=0)
            p25  = np.percentile(paths, 25, axis=0)
            p75  = np.percentile(paths, 75, axis=0)

            final_vals = paths[:, -1]
            prob_target = (final_vals >= 100 * ((1 + target_cagr/100) ** n_years)) * 100
            prob_pct = prob_target.mean()

            # KPIs
            k1,k2,k3,k4 = st.columns(4)
            for col, lbl, val in [
                (k1,"5th Percentile",f"₹{p5[-1]:.0f}"),
                (k2,"Median (50th)",f"₹{p50[-1]:.0f}"),
                (k3,"95th Percentile",f"₹{p95[-1]:.0f}"),
                (k4,f"P(CAGR≥{target_cagr}%)",f"{prob_pct:.1f}%"),
            ]:
                with col:
                    clr = GREEN if val != f"₹{p5[-1]:.0f}" else ORANGE
                    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>{lbl}</div><div class='kpi-value'>{val}</div><div class='kpi-sub'>on ₹100 invested</div></div>", unsafe_allow_html=True)

            # Confidence band chart
            x_years = days_arr / 252
            fig_mc = go.Figure()
            fig_mc.add_trace(go.Scatter(x=x_years, y=p95, mode="lines",
                name="95th Pct", line=dict(color="rgba(76,175,80,0.3)",width=0),
                showlegend=False, hoverinfo="skip"))
            fig_mc.add_trace(go.Scatter(x=x_years, y=p5, mode="lines",
                name="5th–95th Band", line=dict(color="rgba(76,175,80,0.3)",width=0),
                fill="tonexty", fillcolor="rgba(76,175,80,0.12)",
                hovertemplate="5–95 band: %{y:.0f}<extra></extra>"))
            fig_mc.add_trace(go.Scatter(x=x_years, y=p75, mode="lines",
                name="75th Pct", line=dict(color="rgba(33,150,243,0.3)",width=0),
                showlegend=False, hoverinfo="skip"))
            fig_mc.add_trace(go.Scatter(x=x_years, y=p25, mode="lines",
                name="25th–75th Band", line=dict(color="rgba(33,150,243,0.3)",width=0),
                fill="tonexty", fillcolor="rgba(33,150,243,0.15)",
                hovertemplate="25–75 band: %{y:.0f}<extra></extra>"))
            fig_mc.add_trace(go.Scatter(x=x_years, y=p50, mode="lines",
                name="Median Path", line=dict(color=GREEN,width=2.5),
                hovertemplate="Year %{x:.1f}: ₹%{y:.0f}<extra></extra>"))
            fig_mc.add_trace(go.Scatter(x=x_years, y=p5, mode="lines",
                name="5th Pct (Bear)", line=dict(color=ORANGE,width=1.5,dash="dot"),
                hovertemplate="5th: ₹%{y:.0f}<extra></extra>"))
            fig_mc.add_trace(go.Scatter(x=x_years, y=p95, mode="lines",
                name="95th Pct (Bull)", line=dict(color=BLUE,width=1.5,dash="dot"),
                hovertemplate="95th: ₹%{y:.0f}<extra></extra>"))
            target_val = 100 * ((1 + target_cagr/100) ** n_years)
            fig_mc.add_hline(y=target_val, line=dict(color="#F44336",dash="dash",width=1.5),
                annotation_text=f"Target ₹{target_val:.0f} ({target_cagr}% CAGR)",
                annotation_font_color="#F44336")
            fig_mc.update_layout(**CHART_LAYOUT, height=420,
                title=dict(text=f"10,000-Path Simulation — {n_years}yr Projection (₹100 initial)", font=dict(size=13,color="#90caf9")))
            fig_mc.update_xaxes(title_text="Years", tickfont=dict(color=WHITE,size=12))
            fig_mc.update_yaxes(title_text="Portfolio Value (₹)", gridcolor="#1e3a5f", tickfont=dict(color=WHITE,size=12))
            st.plotly_chart(fig_mc, use_container_width=True)

            # Distribution histogram
            fig_hist = go.Figure(go.Histogram(
                x=final_vals, nbinsx=60,
                marker_color=BLUE, opacity=0.8,
                hovertemplate="₹%{x:.0f}: %{y} simulations<extra></extra>"))
            fig_hist.add_vline(x=p50[-1], line=dict(color=GREEN,dash="dash"),
                annotation_text="Median", annotation_font_color=GREEN)
            fig_hist.add_vline(x=target_val, line=dict(color="#F44336",dash="dash"),
                annotation_text=f"Target ₹{target_val:.0f}", annotation_font_color="#F44336")
            fig_hist.update_layout(**CHART_LAYOUT, height=280,
                title=dict(text=f"Distribution of {n_years}-Year Final Values", font=dict(size=13,color="#90caf9")))
            fig_hist.update_xaxes(title_text="Final Portfolio Value (₹)", tickfont=dict(color=WHITE,size=11))
            fig_hist.update_yaxes(title_text="Count", gridcolor="#1e3a5f", tickfont=dict(color=WHITE,size=11))
            st.plotly_chart(fig_hist, use_container_width=True)
            st.markdown("---")
    else:
        st.info("Select 2–5 funds above and click **▶️ Run 10,000 Simulations** to generate projections.")
    footer()

# ════════════════════════════════════════════════════════════════════════════
#  PAGE 6 — EFFICIENT FRONTIER (Markowitz)
# ════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Portfolio Optimization":
    st.markdown("""<div class='page-header'>
      <div class='page-title'>🎯 Portfolio Optimization — Markowitz Efficient Frontier</div>
      <div class='page-subtitle'>Mean-Variance Optimization • Max Sharpe • Min Volatility • Custom Weights</div>
    </div>""", unsafe_allow_html=True)

    nav  = DATA["nav"].copy()
    sc   = DATA["scorecard"].copy()
    fm   = DATA["fund_master"].copy()
    sc   = sc.merge(fm[["amfi_code","fund_house"]].drop_duplicates("amfi_code"), on="amfi_code", how="left")

    top10 = sc.sort_values("composite_score",ascending=False).head(10)
    fund_list = top10["scheme_name"].tolist()

    st.markdown("<div class='section-header'>⚙️ Select Funds for Portfolio</div>", unsafe_allow_html=True)
    sel_funds = st.multiselect("Choose 3–6 funds:", fund_list, default=fund_list[:5], max_selections=6)

    if len(sel_funds) < 3:
        st.warning("Select at least 3 funds to compute the efficient frontier.")
        footer()
    else:
        codes = []
        names = []
        for fname in sel_funds:
            row = sc[sc["scheme_name"]==fname].iloc[0]
            codes.append(int(row["amfi_code"]))
            short = fname.replace(" - Regular Plan - Growth","").replace(" - Regular - Growth","")[:22]
            names.append(short)

        # Build returns matrix
        dfs = []
        for code, name in zip(codes, names):
            sub = nav[nav["amfi_code"]==code].sort_values("date")[["date","nav"]].copy()
            sub = sub.set_index("date").rename(columns={"nav":name})
            sub = sub.resample("ME").last()
            dfs.append(sub)

        prices = pd.concat(dfs, axis=1).dropna()
        if len(prices) < 12:
            st.error("Not enough overlapping NAV data for selected funds.")
            footer()
        else:
            returns = prices.pct_change().dropna()
            mean_ret = returns.mean() * 12        # annualised
            cov_mat  = returns.cov() * 12
            n_assets = len(sel_funds)
            RF = 0.06

            def port_stats(w):
                w = np.array(w)
                r = float(w @ mean_ret)
                v = float(np.sqrt(w @ cov_mat.values @ w))
                s = (r - RF) / v if v > 0 else 0
                return r, v, s

            def neg_sharpe(w):
                return -port_stats(w)[2]

            def port_vol(w):
                return port_stats(w)[1]

            constraints = {"type":"eq","fun":lambda w: np.sum(w)-1}
            bounds      = tuple((0,1) for _ in range(n_assets))
            w0          = np.ones(n_assets)/n_assets

            # Max Sharpe
            res_sharpe = sco.minimize(neg_sharpe, w0, method="SLSQP", bounds=bounds, constraints=constraints)
            w_ms = res_sharpe.x
            r_ms, v_ms, s_ms = port_stats(w_ms)

            # Min Volatility
            res_minv = sco.minimize(port_vol, w0, method="SLSQP", bounds=bounds, constraints=constraints)
            w_mv = res_minv.x
            r_mv, v_mv, s_mv = port_stats(w_mv)

            # Frontier curve
            target_rets = np.linspace(mean_ret.min(), mean_ret.max(), 80)
            frontier_vols, frontier_rets = [], []
            for tr in target_rets:
                cons2 = [constraints, {"type":"eq","fun":lambda w,tr=tr: port_stats(w)[0]-tr}]
                try:
                    r2 = sco.minimize(port_vol, w0, method="SLSQP", bounds=bounds, constraints=cons2)
                    if r2.success:
                        rv, vv, _ = port_stats(r2.x)
                        frontier_vols.append(vv*100)
                        frontier_rets.append(rv*100)
                except: pass

            # Random portfolios for cloud
            n_ports = 3000
            rand_r, rand_v, rand_s = [], [], []
            for _ in range(n_ports):
                w = np.random.random(n_assets); w/=w.sum()
                pr, pv, ps = port_stats(w)
                rand_r.append(pr*100); rand_v.append(pv*100); rand_s.append(ps)

            fig_ef = go.Figure()
            fig_ef.add_trace(go.Scatter(x=rand_v, y=rand_r, mode="markers",
                name="Random Portfolios",
                marker=dict(color=rand_s, colorscale=[[0,"#F44336"],[0.5,"#FF9800"],[1,"#4CAF50"]],
                    size=5, opacity=0.6,
                    colorbar=dict(title="Sharpe",tickfont=dict(color=WHITE,size=10),title_font=dict(color=TEXT_L))),
                hovertemplate="Vol: %{x:.1f}%<br>Ret: %{y:.1f}%<extra></extra>"))
            if frontier_vols:
                fig_ef.add_trace(go.Scatter(x=frontier_vols, y=frontier_rets, mode="lines",
                    name="Efficient Frontier",
                    line=dict(color="#F44336",width=3),
                    hovertemplate="Frontier — Vol: %{x:.1f}%<br>Ret: %{y:.1f}%<extra></extra>"))
            fig_ef.add_trace(go.Scatter(x=[v_ms*100], y=[r_ms*100], mode="markers",
                name=f"Max Sharpe ({s_ms:.2f})",
                marker=dict(symbol="star",size=20,color=ORANGE,line=dict(color=WHITE,width=1.5)),
                hovertemplate=f"<b>★ Max Sharpe</b><br>Vol: {v_ms*100:.1f}%<br>Ret: {r_ms*100:.1f}%<br>Sharpe: {s_ms:.2f}<extra></extra>"))
            fig_ef.add_trace(go.Scatter(x=[v_mv*100], y=[r_mv*100], mode="markers",
                name=f"Min Volatility",
                marker=dict(symbol="circle",size=16,color=GREEN,line=dict(color=WHITE,width=1.5)),
                hovertemplate=f"<b>● Min Vol</b><br>Vol: {v_mv*100:.1f}%<br>Ret: {r_mv*100:.1f}%<extra></extra>"))
            for i, (name, ret, vol) in enumerate(zip(names, mean_ret*100, np.sqrt(np.diag(cov_mat))*100)):
                fig_ef.add_trace(go.Scatter(x=[vol], y=[ret], mode="markers+text",
                    name=name, text=[name], textposition="top center",
                    textfont=dict(color=WHITE,size=10),
                    marker=dict(size=10, color=COLORS_SEQ[i%len(COLORS_SEQ)],
                        line=dict(color=WHITE,width=1)),
                    hovertemplate=f"<b>{name}</b><br>Vol: {vol:.1f}%<br>Ret: {ret:.1f}%<extra></extra>"))
            fig_ef.update_layout(**CHART_LAYOUT, height=520,
                title=dict(text="Markowitz Efficient Frontier — Risk vs Return", font=dict(size=14,color="#90caf9")))
            fig_ef.update_xaxes(title_text="Portfolio Volatility / Risk (%)", tickfont=dict(color=WHITE,size=12))
            fig_ef.update_yaxes(title_text="Expected Annual Return (%)", gridcolor="#1e3a5f", tickfont=dict(color=WHITE,size=12))
            st.plotly_chart(fig_ef, use_container_width=True)

            # Portfolio weight tables
            ms_col, mv_col = st.columns(2)
            with ms_col:
                st.markdown(f"<div class='section-header'>⭐ Max Sharpe Portfolio (Sharpe: {s_ms:.2f})</div>", unsafe_allow_html=True)
                ms_df = pd.DataFrame({"Fund":names,"Weight (%)": (w_ms*100).round(1)}).sort_values("Weight (%)",ascending=False)
                st.dataframe(ms_df.set_index("Fund"), use_container_width=True)
                m1,m2,m3 = st.columns(3)
                with m1: st.metric("Expected Return", f"{r_ms*100:.1f}%")
                with m2: st.metric("Volatility", f"{v_ms*100:.1f}%")
                with m3: st.metric("Sharpe Ratio", f"{s_ms:.2f}")
            with mv_col:
                st.markdown(f"<div class='section-header'>🛡️ Min Volatility Portfolio (Vol: {v_mv*100:.1f}%)</div>", unsafe_allow_html=True)
                mv_df = pd.DataFrame({"Fund":names,"Weight (%)": (w_mv*100).round(1)}).sort_values("Weight (%)",ascending=False)
                st.dataframe(mv_df.set_index("Fund"), use_container_width=True)
                m1,m2,m3 = st.columns(3)
                with m1: st.metric("Expected Return", f"{r_mv*100:.1f}%")
                with m2: st.metric("Volatility", f"{v_mv*100:.1f}%")
                with m3: st.metric("Sharpe Ratio", f"{s_mv:.2f}")

            # Custom weight slider
            st.markdown("<div class='section-header'>🎚️ Custom Portfolio — Adjust Weights</div>", unsafe_allow_html=True)
            st.markdown("Drag sliders to set portfolio weights (auto-normalised to 100%)")
            raw_w = []
            slider_cols = st.columns(n_assets)
            for i, name in enumerate(names):
                with slider_cols[i]:
                    val = st.slider(name[:18], 0, 100, 100//n_assets, key=f"w_{i}")
                    raw_w.append(val)
            total_w = sum(raw_w)
            if total_w > 0:
                norm_w = [w/total_w for w in raw_w]
                cr, cv, cs = port_stats(norm_w)
                cw1, cw2, cw3 = st.columns(3)
                with cw1: st.metric("Custom Return", f"{cr*100:.1f}%")
                with cw2: st.metric("Custom Volatility", f"{cv*100:.1f}%")
                with cw3: st.metric("Custom Sharpe", f"{cs:.2f}")

            # Export
            e1,e2,_ = st.columns([1,1,6])
            with e1: csv_download(ms_df, "Max Sharpe Weights", "max_sharpe_weights.csv", key="csv_ef_ms")
            with e2: csv_download(mv_df, "Min Vol Weights", "min_vol_weights.csv", key="csv_ef_mv")
    footer()
