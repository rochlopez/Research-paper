
import pandas as pd
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
file_path = project_dir / "data" / "ap_oil_palm_historical_6_years.csv"

df = pd.read_csv(file_path)

df["production_change_tonnes"] = (
    df["ffb_production_tonnes"].diff()
)

df["production_change_percent"] = (
    df["ffb_production_tonnes"].pct_change() * 100
)

print("\nANDHRA PRADESH OIL-PALM PRODUCTION TREND")
print("=" * 50)

print(
    df[
        [
            "year",
            "ffb_production_tonnes",
            "production_change_tonnes",
            "production_change_percent",
        ]
    ].round(2).to_string(index=False)
)

print("\nOverall production change:")
first = df["ffb_production_tonnes"].iloc[0]
last = df["ffb_production_tonnes"].iloc[-1]

change_percent = (last - first) / first * 100

print(f"{change_percent:.2f}% from {df['year'].iloc[0]} "
      f"to {df['year'].iloc[-1]}")
