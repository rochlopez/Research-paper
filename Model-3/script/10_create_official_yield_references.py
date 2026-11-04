
import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent.parent
output = base / "data" / "ap_oil_palm_official_yield_references.csv"

data = [{
    "survey": "AP Socio-Economic Survey 2023-24",
    "production_year": "2022-23",
    "area_covered_acres": 568000,
    "bearing_area_ha": None,
    "ffb_production_tonnes": 1895000,
    "cpo_production_tonnes": 331000,
    "reported_yield_tonnes_per_ha": 19.81,
    "yield_type": "Government-reported average bearing-plantation productivity",
    "source_page": 82,
    "source_url": "https://s3.ap-south-1.amazonaws.com/apfinance.gov.in/uploads/index-docs/Socio_Economic_Survey_2023-24.pdf",
    "notes": "Area covered is not confirmed bearing area. Do not calculate yield using this area."
}]

df = pd.DataFrame(data)
df.to_csv(output, index=False)

print("Official yield reference dataset created!")
print(df.to_string(index=False))
print("\nSaved to:", output)
