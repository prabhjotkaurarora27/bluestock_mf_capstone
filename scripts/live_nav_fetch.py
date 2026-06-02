import requests
import pandas as pd
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# Scheme codes to fetch
schemes = {
    "125497": "HDFC_Top100",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_LargeCap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip",
}

for code, name in schemes.items():
    url = f"https://api.mfapi.in/mf/{code}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Extract NAV history
        nav_records = data["data"]  # list of {date, nav}
        df = pd.DataFrame(nav_records)
        df["amfi_code"] = code
        df["fund_name"] = name
        
        # Save to CSV
        out_file = OUTPUT_PATH / f"live_nav_{code}_{name}.csv"
        df.to_csv(out_file, index=False)
        print(f"✅ Saved {name}: {len(df)} rows → {out_file.name}")
    except Exception as e:
        print(f"❌ Failed for {name} ({code}): {e}")
