
import pandas as pd
from pathlib import Path

for name in ["oil_palm_mandal_data.csv", "india_oil_palm_area.csv"]:
    path = Path(name)

    print(f"\n--- {name} ---")

    if path.exists():
        df = pd.read_csv(path)
        print("Columns:", list(df.columns))
        print(df.head(3).to_string(index=False))
    else:
        print("File not found")
