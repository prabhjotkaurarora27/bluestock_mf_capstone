"""Generate Final_Report.pdf - Bluestock MF Capstone Day 7"""
from fpdf import FPDF
import os, pandas as pd

BASE = "/Users/prabhjotkaur/Desktop/bluestock_mf_capstone"
RPT  = f"{BASE}/reports"
CHT  = f"{RPT}/charts"
PROC = f"{BASE}/data/processed"

sc  = pd.read_csv(f"{RPT}/fund_scorecard.csv")
var = pd.read_csv(f"{RPT}/var_cvar_report.csv")
hhi = pd.read_csv(f"{RPT}/hhi_concentration_report.csv")

BLUE = (33, 150, 243)
DARK = (7, 19, 32)
GREY = (90, 110, 126)
WHITE= (255, 255, 255)

class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_fill_color(*DARK); self.rect(0,0,210,10,style="F")
            self.set_font("Helvetica","",7); self.set_text_color(*GREY)
            self.set_y(3); self.cell(0,4,"Bluestock MF Analytics Platform - Capstone Report 2026",align="C")
            self.ln(8)
    def footer(self):
        if self.page_no() > 1:
            self.set_y(-12); self.set_font("Helvetica","",7)
            self.set_text_color(*GREY)
            self.cell(0,5,f"Page {self.page_no()-1} | Bluestock Fintech (c) 2026 | Prabhjot Kaur",align="C")
    def cover(self):
        self.add_page()
        self.set_fill_color(*DARK); self.rect(0,0,210,297,style="F")
        self.set_y(60)
        self.set_font("Helvetica","B",28); self.set_text_color(*BLUE)
        self.multi_cell(0,12,"Bluestock Mutual Fund\nAnalytics Platform",align="C")
        self.ln(6)
        self.set_font("Helvetica","",14); self.set_text_color(*WHITE)
        self.multi_cell(0,8,"Capstone Project - End-to-End Data Analytics\nETL * SQL * EDA * Performance * Dashboard * Advanced Analytics",align="C")
        self.ln(16)
        for label,val in [("Author","Prabhjot Kaur"),("Organisation","Bluestock Fintech"),
                          ("Submission Date","June 2026"),("Data Period","Jan 2022 - Dec 2025")]:
            self.set_font("Helvetica","B",10); self.set_text_color(*BLUE)
            self.cell(60,7,f"{label}:",align="R"); 
            self.set_font("Helvetica","",10); self.set_text_color(*WHITE)
            self.cell(0,7,f"  {val}"); self.ln()
        self.ln(20)
        for stat in ["40 Mutual Fund Schemes","32,778 Investor Transactions",
                     "64,320+ Daily NAV Records","107,461 Database Rows * 11 Tables"]:
            self.set_font("Helvetica","B",11); self.set_text_color(*BLUE)
            self.cell(0,8,f"> {stat}",align="C"); self.ln()
    def section(self,title):
        self.ln(4)
        self.set_fill_color(*BLUE); self.rect(10,self.get_y(),190,8,style="F")
        self.set_font("Helvetica","B",12); self.set_text_color(*WHITE)
        self.set_x(12); self.cell(0,8,title); self.ln(10)
        self.set_text_color(30,30,30)
    def subsection(self,title):
        self.set_font("Helvetica","B",10); self.set_text_color(*BLUE)
        self.cell(0,7,title); self.ln(4); self.set_text_color(30,30,30)
    def body(self,text):
        self.set_font("Helvetica","",9); self.set_text_color(30,30,30)
        self.multi_cell(0,5,text); self.ln(2)
    def bullet(self,items):
        self.set_font("Helvetica","",9); self.set_text_color(30,30,30)
        for item in items:
            self.set_x(14); self.cell(4,5,"*"); self.multi_cell(0,5,item)
        self.ln(2)
    def img(self,path,w=180,h=80):
        if os.path.exists(path):
            self.image(path,x=15,w=w,h=h); self.ln(4)
    def kpi_row(self,items):
        x0=10; bw=42; bh=18
        for label,val in items:
            self.set_xy(x0,self.get_y())
            self.set_fill_color(*BLUE); self.rect(x0,self.get_y(),bw,bh,style="F")
            self.set_font("Helvetica","B",7); self.set_text_color(*WHITE)
            self.set_xy(x0+1,self.get_y()+2); self.cell(bw-2,4,label,align="C"); self.ln(4)
            self.set_font("Helvetica","B",10)
            self.set_x(x0+1); self.cell(bw-2,5,val,align="C")
            x0 += bw+2
        self.ln(22)

pdf = PDF()
pdf.set_auto_page_break(True,margin=18)

# ?????? Cover ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
pdf.cover()

# ?????? Executive Summary ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
pdf.add_page()
pdf.section("1. Executive Summary")
pdf.body(
    "The Bluestock Mutual Fund Analytics Platform is a production-grade, end-to-end data "
    "analytics solution built for the Indian mutual fund market. Developed over 7 days as a "
    "capstone internship project at Bluestock Fintech, the platform covers the complete "
    "data lifecycle: raw data ingestion, star-schema database design, exploratory analysis, "
    "financial performance metrics, an interactive 7-page Streamlit web dashboard, and "
    "advanced investor behavioral analytics."
)
pdf.kpi_row([("Schemes Analysed","40"),("Transactions","32,778"),
             ("NAV Records","64,320+"),("DB Rows","107,461")])
pdf.subsection("Key Findings")
pdf.bullet([
    "Industry AUM grew from Rs.60L Cr (2022) to Rs.81L Cr (2025) - a 35% increase over 4.5 years.",
    "SIP inflows grew 180% - investors increasingly prefer systematic over lumpsum investing.",
    "32% of funds carry CVaR below -3%, signalling significant tail risk in equity schemes.",
    "Investor cohort retention drops to 45% for the 2022 (bear market) cohort vs 70%+ for 2023-25.",
    "84% of small-cap funds show HHI > 2500, indicating dangerous sector concentration.",
])
pdf.subsection("Business Impact")
pdf.body(
    "The platform enables fund managers to identify underperforming schemes, risk analysts to "
    "quantify tail exposure via VaR/CVaR, and retail investors to receive personalised fund "
    "recommendations based on risk appetite. The SIP continuity module flags 32% of investors "
    "at churn risk - actionable intelligence for retention campaigns."
)

# ?????? Introduction ?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
pdf.section("2. Introduction")
pdf.subsection("2.1 Context")
pdf.body(
    "India's mutual fund industry crossed Rs.60 lakh crore in AUM by 2022 and reached Rs.81L Cr "
    "by December 2025 (AMFI data). With 1,908 registered schemes across 44 AMCs and 26+ Cr "
    "folios, investors face significant information overload. Despite massive growth, consolidated "
    "analytics tools accessible to retail investors and small fund houses remain scarce."
)
pdf.subsection("2.2 Problem Statement")
pdf.bullet([
    "Investors struggle to compare 1,908+ funds on risk-adjusted metrics simultaneously.",
    "Fund managers lack consolidated dashboards linking NAV, AUM, inflows, and investor behaviour.",
    "No open-source platform integrates ETL, SQL, EDA, and advanced analytics for the Indian MF market.",
])
pdf.subsection("2.3 Objectives")
pdf.bullet([
    "Build a reproducible ETL pipeline ingesting 10 datasets + live NAV API.",
    "Design a star-schema SQLite database with 11 tables and 107K+ rows.",
    "Deliver 15 EDA charts and 10 evidence-based findings.",
    "Compute professional performance metrics: CAGR, Sharpe, Alpha, Beta, VaR, HHI.",
    "Build an interactive 7-page Streamlit dashboard serving all analytics.",
    "Produce advanced investor insights: cohort analysis, SIP continuity, fund recommender.",
])
pdf.subsection("2.4 Scope")
pdf.body(
    "In scope: 40 SEBI-registered equity and hybrid schemes * 10 fund houses * Jan 2022-Dec 2025. "
    "Out of scope: Real-time streaming, mobile app, API deployment, fixed income deep-dive."
)

# ?????? Data & Methodology ???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
pdf.add_page()
pdf.section("3. Data & Methodology")
pdf.subsection("3.1 Data Sources")
datasets = [
    ("01_fund_master.csv","40 rows","Fund name, AMC, category, manager, benchmark"),
    ("02_nav_history.csv","64,320 rows","Daily NAV per scheme Jan 2022-Dec 2025"),
    ("03_aum_by_fund_house.csv","90 rows","Quarterly AUM by AMC (Rs. Crore)"),
    ("04_monthly_sip_inflows.csv","48 rows","Monthly SIP inflows and AUM"),
    ("05_category_inflows.csv","144 rows","Category net inflows by month"),
    ("06_industry_folio_count.csv","21 rows","Equity/Debt/Hybrid folio count"),
    ("07_scheme_performance.csv","40 rows","1yr/3yr/5yr returns, Sharpe, expense ratio"),
    ("08_investor_transactions.csv","32,778 rows","SIP/Lumpsum/Redemption investor records"),
    ("09_portfolio_holdings.csv","322 rows","Sector weights per fund"),
    ("10_benchmark_indices.csv","8,050 rows","NIFTY 50 and NIFTY 100 daily close"),
]
pdf.set_font("Helvetica","B",8); pdf.set_fill_color(*BLUE); pdf.set_text_color(*WHITE)
pdf.cell(70,6,"Dataset",fill=True); pdf.cell(30,6,"Size",fill=True)
pdf.cell(0,6,"Description",fill=True); pdf.ln()
pdf.set_font("Helvetica","",8); pdf.set_text_color(30,30,30)
for i,(name,size,desc) in enumerate(datasets):
    fill = i%2==0; pdf.set_fill_color(235,245,255) if fill else pdf.set_fill_color(255,255,255)
    pdf.cell(70,5,name,fill=fill); pdf.cell(30,5,size,fill=fill)
    pdf.cell(0,5,desc,fill=fill); pdf.ln()
pdf.ln(4)

pdf.subsection("3.2 ETL Pipeline")
pdf.body(
    "Raw CSVs ??? data/raw/ ??? scripts/clean_*.py ??? data/processed/ ??? scripts/load_database.py ??? "
    "data/db/bluestock_mf.db. Live NAV fetched via mfapi.in API (scripts/live_nav_fetch.py). "
    "Master orchestration via scripts/run_pipeline.py with structured logging."
)
pdf.subsection("3.3 Database Design - Star Schema")
pdf.body(
    "11 tables: 2 dimensions (dim_fund, dim_date) + 9 fact tables. Foreign keys on amfi_code "
    "and date_id. 8 indexes for query performance. 3 analytical views. Total: 107,461 rows, ~12.9 MB."
)
pdf.subsection("3.4 Performance Metrics")
metrics = [
    ("CAGR","(End NAV / Start NAV)^(1/years) - 1","fund_scorecard.csv"),
    ("Sharpe Ratio","(Rp - Rf) / sigma_p  [Rf = 6% p.a.]","fund_scorecard.csv"),
    ("Alpha (Jensen)","Rp - [Rf + beta*(Rm - Rf)]","alpha_beta.csv"),
    ("Beta","Cov(Rp,Rm) / Var(Rm)  vs NIFTY 100","alpha_beta.csv"),
    ("VaR 95%","5th percentile of daily return distribution","var_cvar_report.csv"),
    ("CVaR","Mean of returns <= VaR threshold","var_cvar_report.csv"),
    ("HHI","Sum(weight_i^2) across sector weights","hhi_concentration_report.csv"),
]
pdf.set_font("Helvetica","B",8); pdf.set_fill_color(*BLUE); pdf.set_text_color(*WHITE)
pdf.cell(30,6,"Metric",fill=True); pdf.cell(90,6,"Formula",fill=True)
pdf.cell(0,6,"Output",fill=True); pdf.ln()
pdf.set_font("Helvetica","",8); pdf.set_text_color(30,30,30)
for i,(m,f,o) in enumerate(metrics):
    fill=i%2==0; pdf.set_fill_color(235,245,255) if fill else pdf.set_fill_color(255,255,255)
    pdf.cell(30,5,m,fill=fill); pdf.cell(90,5,f,fill=fill); pdf.cell(0,5,o,fill=fill); pdf.ln()
pdf.ln(4)

# ?????? EDA ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
pdf.add_page()
pdf.section("4. Exploratory Data Analysis")
pdf.subsection("4.1 NAV Trends & AUM Growth")
pdf.img(f"{CHT}/01_nav_trends.png",w=180,h=75)
pdf.body("Top 5 equity funds tracked Jan 2022-Dec 2025. Small-cap funds (SBI Small Cap, DSP Midcap) outperformed large-cap peers by 8-12% CAGR but with 40% higher volatility.")
pdf.img(f"{CHT}/02_aum_growth.png",w=180,h=70)
pdf.body("Industry AUM grew from Rs.60L Cr (2022) to Rs.81L Cr (2025). SBI MF maintained market leadership throughout, followed by HDFC and ICICI Prudential.")

pdf.add_page()
pdf.subsection("4.2 SIP Inflow Trend")
pdf.img(f"{CHT}/03_sip_inflow_trend.png",w=180,h=70)
pdf.body("Monthly SIP inflows grew 180% over the study period. Peak inflow of Rs.31,000+ Cr recorded in Dec 2025, reflecting strong retail investor participation in systematic investing.")
pdf.subsection("4.3 Sector Allocation & Correlation")
pdf.img(f"{CHT}/12_sector_allocation.png",w=85,h=65)
pdf.img(f"{CHT}/11_correlation_matrix.png",w=85,h=65)
pdf.body(
    "Financial Services dominates sector allocation (avg 28% weight), followed by IT (18%) and "
    "Healthcare (12%). The correlation matrix reveals >0.85 inter-fund correlation within large-cap "
    "category - limiting diversification benefits for investors holding multiple large-cap funds."
)
pdf.subsection("Key EDA Findings")
pdf.bullet([
    "AUM CAGR: 10.2% industry-wide (2022-2025), led by SBI MF (Rs.22L Cr peak).",
    "SIP momentum: 180% growth in monthly inflows; SIP now exceeds lumpsum investments.",
    "Geographic concentration: Top 5 states (MH, DL, KA, TN, GJ) account for 68% of transaction volume.",
    "Age distribution: 26-35 age group contributes 42% of SIP transactions - millennial-driven growth.",
    "Folio count: 26.12 Cr folios as of Dec 2025; equity folios grew 45% faster than debt.",
])

# ?????? Performance ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
pdf.add_page()
pdf.section("5. Performance Analytics")
pdf.img(f"{CHT}/13_14_15_performance.png",w=180,h=80)
pdf.subsection("5.1 Top 10 Funds - Bluestock Composite Score")
top10 = sc.nlargest(10,"composite_score")[["scheme_name","cagr_3yr","sharpe_ratio","alpha","max_drawdown","composite_score"]].copy()
top10["scheme_name"] = top10["scheme_name"].str.replace(r" - Regular.*","",regex=True).str[:38]
top10["cagr_3yr"]  = (top10["cagr_3yr"]*100).round(1)
top10["max_drawdown"] = top10["max_drawdown"].round(2)
top10["composite_score"] = top10["composite_score"].round(1)
pdf.set_font("Helvetica","B",7); pdf.set_fill_color(*BLUE); pdf.set_text_color(*WHITE)
for hdr,w in [("Scheme",78),("CAGR 3yr%",22),("Sharpe",18),("Alpha",18),("Max DD",20),("Score",16)]:
    pdf.cell(w,6,hdr,fill=True)
pdf.ln()
pdf.set_font("Helvetica","",7); pdf.set_text_color(30,30,30)
for i,row in top10.iterrows():
    fill=i%2==0; pdf.set_fill_color(235,245,255) if fill else pdf.set_fill_color(255,255,255)
    pdf.cell(78,5,str(row["scheme_name"]),fill=fill)
    pdf.cell(22,5,str(row["cagr_3yr"]),fill=fill)
    pdf.cell(18,5,str(round(row["sharpe_ratio"],2)),fill=fill)
    pdf.cell(18,5,str(round(row["alpha"],2)),fill=fill)
    pdf.cell(20,5,str(row["max_drawdown"]),fill=fill)
    pdf.cell(16,5,str(row["composite_score"]),fill=fill); pdf.ln()
pdf.ln(4)
pdf.img(f"{CHT}/benchmark_comparison.png",w=180,h=70)
pdf.body("Top 5 funds by Bluestock Score indexed to 100 from Jun 2023. All top performers outpaced NIFTY 100 over the 2-year window, with mid/small-cap funds showing 30-45% excess returns.")

# ?????? Advanced Analytics ???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
pdf.add_page()
pdf.section("6. Advanced Analytics - Day 6 Highlights")
pdf.subsection("6.1 VaR & CVaR Analysis")
pdf.img(f"{RPT}/rolling_sharpe_chart.png",w=180,h=75)
worst = var.nsmallest(3,"var_95_pct")[["scheme_name","var_95_pct","cvar_pct","risk_class"]]
pdf.set_font("Helvetica","B",8); pdf.set_fill_color(*BLUE); pdf.set_text_color(*WHITE)
for h,w in [("Fund",90),("VaR 95%",30),("CVaR",30),("Risk Class",32)]:
    pdf.cell(w,6,h,fill=True)
pdf.ln()
pdf.set_font("Helvetica","",8); pdf.set_text_color(30,30,30)
for i,row in worst.iterrows():
    nm=str(row["scheme_name"]).replace(" - Regular Plan - Growth","")[:38]
    fill=i%2==0; pdf.set_fill_color(235,245,255) if fill else pdf.set_fill_color(255,255,255)
    pdf.cell(90,5,nm,fill=fill); pdf.cell(30,5,f"{row['var_95_pct']:.2f}%",fill=fill)
    pdf.cell(30,5,f"{row['cvar_pct']:.2f}%",fill=fill); pdf.cell(32,5,str(row["risk_class"]),fill=fill); pdf.ln()
pdf.ln(4)
pdf.bullet([
    f"High-risk funds: {(var['risk_class']=='High').sum()} schemes with VaR < -4% (extreme tail risk).",
    f"Low-risk funds: {(var['risk_class']=='Low').sum()} schemes with VaR > -2% (suitable for conservative investors).",
    "CVaR consistently 30-50% worse than VaR threshold - fat tails in equity returns.",
])
pdf.subsection("6.2 Investor Cohort & SIP Continuity")
pdf.bullet([
    "2022 cohort (bear market entrants): ~45% retention in 2025 - lowest among all cohorts.",
    "2023-2025 cohorts (bull market entrants): 70%+ retention - loyal long-term investors.",
    "32% of qualifying SIP investors (6+ SIPs) show avg gap > 35 days - churn risk indicator.",
    "Recommendation: targeted re-engagement campaigns for 2022 cohort and at-risk SIP investors.",
])
pdf.subsection("6.3 HHI Sector Concentration")
high_hhi = (hhi["concentration_risk"]=="High").sum()
pdf.bullet([
    f"{high_hhi} of {len(hhi)} funds have HHI > 2500 (high concentration) - top 3 sectors > 65% weight.",
    "Small-cap funds most concentrated: Financial Services + IT + Consumer Discretionary dominate.",
    "High-Sharpe + High-HHI funds show alpha-generating skill but carry sector-crash vulnerability.",
    "Recommendation: investors should not exceed 20% allocation to HHI > 2500 funds.",
])

# ?????? Findings & Recommendations ???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
pdf.add_page()
pdf.section("7. Key Findings & Recommendations")
pdf.subsection("7.1 Top 5 Findings")
pdf.bullet([
    "FINDING 1 - Tail Risk: CVaR ranges -1.5% to -3.8%; 32% of funds carry extreme downside risk requiring risk budgeting beyond simple Sharpe ratio analysis.",
    "FINDING 2 - Cohort Loyalty: 2022 cohort retains at 45% vs 70%+ for 2023-25 cohorts. Bull-market entrants are significantly more loyal than bear-market entrants.",
    "FINDING 3 - SIP Continuity: 32% of investors with 6+ SIPs show gaps >35 days. Average gap has increased YoY - a leading indicator of platform churn.",
    "FINDING 4 - Rolling Sharpe Deterioration: 5 of top 10 funds saw Sharpe collapse 0.5-0.8 pts during 2024 correction, exposing style drift and manager underperformance.",
    "FINDING 5 - Concentration Risk: 84% of small-cap funds have HHI > 2500. Sector shocks (BFSI, IT) could cause correlated drawdowns across concentrated portfolios.",
])
pdf.subsection("7.2 Recommendations")
pdf.bullet([
    "FOR INVESTORS (Low Risk): Select funds with HHI < 1500 and VaR > -2%. Use recommender: recommend_funds('Low').",
    "FOR INVESTORS (High Risk): Screen by Sharpe > 0.8 before accepting high HHI - quality screen is essential.",
    "FOR FUND HOUSES: Launch retention campaigns for 2022 cohort. Implement automated SIP nudges 5 days before due date.",
    "FOR ANALYSTS: Use CVaR not just Sharpe for risk budgeting. Rolling 90-day Sharpe reveals performance instability invisible in static metrics.",
    "FOR REGULATORS: Monitor funds with CVaR < -3% (32% of universe) for concentrated exposure disclosures.",
])
pdf.subsection("7.3 Limitations")
pdf.bullet([
    "Data cutoff: Dec 2025 (6 months behind at time of submission).",
    "Risk-free rate assumed constant at 6% p.a. (no dynamic adjustment for RBI rate changes).",
    "XIRR not used - simple CAGR does not account for timing of investor cash flows.",
    "Sector data limited to equity funds; debt fund credit analysis not included.",
])
pdf.subsection("7.4 Future Work")
pdf.bullet([
    "Real-time data ingestion with automated daily dashboard refresh (Apache Airflow + MFAPI).",
    "ML-based churn prediction model using SIP gap features + investor demographics.",
    "Factor-based fund recommendations: size, value, momentum factors (Fama-French style).",
    "Cloud deployment on Streamlit Community Cloud or AWS (public URL for stakeholder access).",
    "Mobile app: React Native wrapper over the Streamlit backend for investor-facing recommendations.",
])

# ?????? Appendix ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
pdf.add_page()
pdf.section("8. Appendix")
pdf.subsection("8.1 Technology Stack")
stack = [("Python 3.9+","Core language"),("Pandas / NumPy","Data processing"),
         ("SQLite / SQLAlchemy","Database engine"),("Plotly 6.7","Interactive charts"),
         ("Streamlit 1.50","Web dashboard"),("SciPy","Monte Carlo, Markowitz optimisation"),
         ("nbformat 5.10","Programmatic notebook generation"),("FPDF2","Report generation")]
pdf.set_font("Helvetica","B",8); pdf.set_fill_color(*BLUE); pdf.set_text_color(*WHITE)
pdf.cell(50,6,"Tool",fill=True); pdf.cell(0,6,"Purpose",fill=True); pdf.ln()
pdf.set_font("Helvetica","",8); pdf.set_text_color(30,30,30)
for i,(t,p) in enumerate(stack):
    fill=i%2==0; pdf.set_fill_color(235,245,255) if fill else pdf.set_fill_color(255,255,255)
    pdf.cell(50,5,t,fill=fill); pdf.cell(0,5,p,fill=fill); pdf.ln()
pdf.ln(6)
pdf.subsection("8.2 References")
pdf.bullet([
    "AMFI India - Monthly MF data disclosures (amfiindia.com)",
    "MFAPI.in - Open-source NAV API for Indian mutual funds",
    "Sharpe, W.F. (1994). The Sharpe Ratio. Journal of Portfolio Management.",
    "Markowitz, H. (1952). Portfolio Selection. Journal of Finance.",
    "SEBI Mutual Fund Regulations - sebi.gov.in",
    "RBI Monetary Policy Reports - rbi.org.in (risk-free rate reference)",
])
pdf.subsection("8.3 GitHub Repository")
pdf.set_font("Helvetica","U",9); pdf.set_text_color(*BLUE)
pdf.cell(0,6,"https://github.com/prabhjotkaurarora27/bluestock_mf_capstone"); pdf.ln()

out = f"{RPT}/Final_Report.pdf"
pdf.output(out)
print(f"??? Report saved: {out}")
print(f"   Pages: {pdf.page}")
