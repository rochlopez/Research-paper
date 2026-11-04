
import pandas as pd
from pathlib import Path

# Locate the Model-3 folder automatically
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "ap_oil_palm_historical_6_years.csv"

print("MODEL 3: HISTORICAL DATA CHECK")
print("-" * 40)

if not DATA_FILE.exists():
    print("ERROR: CSV file not found.")
    print("Expected location:", DATA_FILE)
else:
    df = pd.read_csv(DATA_FILE)

    print("\n1. Dataset shape:")
    print(df.shape)

    print("\n2. Column names:")
    print(df.columns.tolist())

    print("\n3. Historical records:")
    print(df.to_string(index=False))

    print("\n4. Missing values per column:")
    print(df.isnull().sum())

    print("\n5. Data types:")
    print(df.dtypes)

    print("\n6. Production summary:")
    if "ffb_production_tonnes" in df.columns:
        print(df["ffb_production_tonnes"].describe())

    print("\nCheck complete.")
