
import pandas as pd
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
file_path = project_dir / "results" / "ap_oil_palm_master_dataset.csv"

df = pd.read_csv(file_path)

print("\nMODEL 3 - DATA QUALITY AUDIT")
print("=" * 50)

# Check overlapping area values
print("\n1. AREA COMPARISON")

area_check = df.dropna(
    subset=["area_from_ffb_source_ha", "area_from_cpo_source_ha"]
).copy()

area_check["area_difference_ha"] = (
    area_check["area_from_ffb_source_ha"]
    - area_check["area_from_cpo_source_ha"]
)

print(area_check[
    ["year", "area_from_ffb_source_ha",
     "area_from_cpo_source_ha", "area_difference_ha"]
].to_string(index=False))

# Check production availability
print("\n2. PRODUCTION DATA AVAILABILITY")

print("FFB records:", df["ffb_production_tonnes"].count())
print("CPO records:", df["cpo_production_tonnes"].count())

# Check missing values
print("\n3. MISSING DATA")

print(df.isnull().sum())

# Check years
print("\n4. YEAR COVERAGE")
print(df["year"].tolist())

print("\nAudit complete. No original data was changed.")
