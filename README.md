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

## ⚙️ Setup Instructions

### Step 1 — Create the Virtual Environment
```bash
python3 -m venv venv
```

### Step 2 — Activate the Virtual Environment
```bash
# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```
> You should see `(venv)` prefix in your terminal after activation.

### Step 3 — Install All Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Verify the Environment
```bash
python scripts/test_environment.py
```
Expected output: **9 passed | 0 failed** with all package versions listed.

### Dependencies (requirements.txt)

| Package      | Version | Purpose                          |
|--------------|---------|----------------------------------|
| pandas       | 2.3.3   | Data manipulation & analysis     |
| numpy        | 2.0.2   | Numerical computing              |
| matplotlib   | 3.9.4   | Static data visualization        |
| seaborn      | 0.13.2  | Statistical data visualization   |
| plotly       | 6.7.0   | Interactive charts & dashboards  |
| sqlalchemy   | 2.0.50  | Database ORM & SQL toolkit       |
| requests     | 2.32.5  | HTTP requests for data fetching  |
| scipy        | 1.13.1  | Scientific computing & stats     |
| jupyter      | 1.1.1   | Interactive notebook environment |

---

## 📌 Status

| Step | Task                                  | Status        |
|------|---------------------------------------|---------------|
| 1    | Project structure & Git init          | ✅ Complete   |
| 2    | Python environment & dependencies     | ✅ Complete   |
| 3    | Data collection & ingestion           | 🔜 Upcoming  |
| 4    | SQL schema & data processing          | 🔜 Upcoming  |
| 5    | Exploratory Data Analysis (EDA)       | 🔜 Upcoming  |
| 6    | Dashboard development                 | 🔜 Upcoming  |
| 7    | Final report                          | 🔜 Upcoming  |

---

## 👤 Author

**Prabhjot Kaur**  
Capstone Project — Bluestock Fintech  
© 2026
