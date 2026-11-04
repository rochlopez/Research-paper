
import pandas as pd
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
file_path = project_dir / "data" / "ap_oil_palm_historical_6_years.csv"

df = pd.read_csv(file_path)

required = ["year", "bearing_area_ha", "ffb_production_tonnes"]
missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

df["calculated_yield_tonnes_per_ha"] = (
    df["ffb_production_tonnes"] / df["bearing_area_ha"]
)

df.loc[
    df["bearing_area_ha"].isna()
    | (df["bearing_area_ha"] <= 0),
    "calculated_yield_tonnes_per_ha"
] = float("nan")

print("\nYIELD DATA CHECK")
print(df[
    [
        "year",
        "bearing_area_ha",
        "ffb_production_tonnes",
        "calculated_yield_tonnes_per_ha"
    ]
].to_string(index=False))

print("\nYears with verified bearing area:", 
      df["bearing_area_ha"].notna().sum())
print("Yield calculation check complete.")
