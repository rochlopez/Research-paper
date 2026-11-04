
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
data = root / "data"
out = root / "results"
out.mkdir(exist_ok=True)

files = sorted(
    p for p in data.glob("AP_Sentinel2_2024_Tile_*.tif")
    if "AllBands_Test" not in p.name
)

rows = []

for file in files:
    with rasterio.open(file) as src:
        # Bands 13, 14, 15 = NDVI, NDMI, EVI
        indices = src.read([13, 14, 15], masked=True).astype("float32")
        names = ["NDVI", "NDMI", "EVI"]
        row = {"tile": file.name}

        for i, name in enumerate(names):
            values = indices[i].compressed()
            values = values[np.isfinite(values)]
            row[name + "_mean"] = float(values.mean()) if values.size else np.nan

        rows.append(row)

df = pd.DataFrame(rows)
df.to_csv(out / "vegetation_summary.csv", index=False)

ax = df.set_index("tile")[
    ["NDVI_mean", "NDMI_mean", "EVI_mean"]
].plot(kind="bar", figsize=(10, 5))

ax.set_title("Vegetation Indices by Satellite Tile")
ax.set_ylabel("Mean index value")
ax.set_xlabel("Satellite tile")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(out / "vegetation_summary.png", dpi=200)
plt.close()

print(df.to_string(index=False))
print("\nSaved results to:", out)
