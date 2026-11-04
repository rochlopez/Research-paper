
import pandas as pd
from pathlib import Path

# Project folders
project_dir = Path(__file__).resolve().parent.parent
data_dir = project_dir / "data"
results_dir = project_dir / "results"

results_dir.mkdir(exist_ok=True)

# Read both historical datasets
ffb_file = data_dir / "ap_oil_palm_historical_6_years.csv"
cpo_file = data_dir / "ap_oil_palm_area_cpo_2015_2021.csv"

ffb = pd.read_csv(ffb_file)
cpo = pd.read_csv(cpo_file)

# Keep only the required columns
ffb = ffb[
    ["year", "total_area_ha", "bearing_area_ha",
     "ffb_production_tonnes"]
].rename(columns={
    "total_area_ha": "area_from_ffb_source_ha"
})

cpo = cpo[
    ["year", "total_area_ha", "cpo_production_tonnes"]
].rename(columns={
    "total_area_ha": "area_from_cpo_source_ha"
})

# Combine records by year
master = pd.merge(ffb, cpo, on="year", how="outer")

# Calculate CPO per total hectare only when area exists
master["cpo_tonnes_per_total_ha"] = (
    master["cpo_production_tonnes"] /
    master["area_from_cpo_source_ha"]
)

# Calculate FFB yield only with bearing-area data
master["ffb_yield_tonnes_per_bearing_ha"] = (
    master["ffb_production_tonnes"] /
    master["bearing_area_ha"]
)

# Sort by year
master = master.sort_values("year")

# Save output
output_file = results_dir / "ap_oil_palm_master_dataset.csv"
master.to_csv(output_file, index=False)

print("\nMASTER DATASET CREATED")
print("-" * 50)

print(master.to_string(index=False))

print("\nMissing values:")
print(master.isnull().sum())

print("\nSaved to:")
print(output_file)
