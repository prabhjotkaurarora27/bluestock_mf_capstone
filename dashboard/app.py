"""
Bluestock MF Analytics Dashboard — Day 5
=========================================
Entry point located in dashboard/ folder.

The full 7-page dashboard lives at the project root:
    streamlit_dashboard.py  (1,300+ lines)

Run from the project root:
    streamlit run streamlit_dashboard.py
    # Opens → http://localhost:8501

Or run via this file (also from the project root):
    streamlit run dashboard/app.py
    # Opens → http://localhost:8501
"""

import sys
import os

# Add project root to path so all relative data paths resolve correctly
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Execute the main dashboard module
exec(open(os.path.join(ROOT, "streamlit_dashboard.py")).read())
