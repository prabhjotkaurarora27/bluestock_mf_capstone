"""
data_ingestion.py
------------------
Step 3 - Data Ingestion Pipeline
Loads all CSV files from data/raw/ and profiles each dataset.
"""

import os
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

csv_files = sorted(RAW_DIR.glob("*.csv"))

print(f"\nFound {len(csv_files)} CSV file(s) in data/raw/\n")
print("=" * 65)

for csv_path in csv_files:
    print(f"\nFile: {csv_path.name}")
    print("-" * 65)

    df = pd.read_csv(csv_path, low_memory=False)

    # Shape
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")

    # Column names and data types
    print("\nColumns & Data Types:")
    for col, dtype in df.dtypes.items():
        print(f"  {col:<40} {dtype}")

    # First 3 rows
    print("\nFirst 3 Rows:")
    print(df.head(3).to_string(index=True))

    # Missing value counts
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        print("\nMissing Values: None")
    else:
        print("\nMissing Values:")
        for col, count in missing.items():
            print(f"  {col:<40} {count}")

    print("=" * 65)

print("\nAll files loaded successfully.\n")
