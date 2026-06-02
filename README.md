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
│   ├── processed/      # Cleaned and transformed data ready for analysis
│   └── db/             # SQLite or other local database files
│
├── notebooks/          # Jupyter Notebooks for EDA and analysis
│
├── scripts/            # Python scripts for ETL, data processing, and automation
│
├── sql/                # SQL scripts for schema creation, queries, and transformations
│
├── dashboard/          # Dashboard application files (Streamlit / Power BI / Tableau)
│
├── reports/            # Final reports, charts, and exported outputs
│
├── .gitignore          # Git ignore rules for Python, Jupyter, and VS Code
└── README.md           # Project documentation (this file)
```

---

## 🛠️ Tech Stack

| Layer        | Tools / Technologies                        |
|--------------|---------------------------------------------|
| Language     | Python 3.x                                  |
| Database     | SQLite / PostgreSQL                         |
| Analysis     | Pandas, NumPy, Matplotlib, Seaborn          |
| Notebooks    | Jupyter Notebook / JupyterLab               |
| Dashboard    | Streamlit / Power BI                        |
| Version Control | Git & GitHub                             |

---

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
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

4. **Run notebooks**
   ```bash
   jupyter notebook notebooks/
   ```

---

## 📌 Status

🚧 **In Progress** — Project structure initialized. Data collection and analysis pipeline coming soon.

---

## 👤 Author

**Prabhjot Kaur**  
Capstone Project — Bluestock Fintech  
© 2026
