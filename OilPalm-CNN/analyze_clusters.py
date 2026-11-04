
import numpy as np
import pandas as pd
from pathlib import Path

root = Path(__file__).resolve().parent
X = np.load(root / "prepared_data" / "X_patches.npy")
df = pd.read_csv(root / "results" / "patch_clusters.csv")

# Band order: B1,B2,B3,B4,B5,B6,B7,B8,B8A,B9,B11,B12,NDVI,NDMI,EVI
names = ["B1","B2","B3","B4","B5","B6","B7","B8",
         "B8A","B9","B11","B12","NDVI","NDMI","EVI"]

rows = []
for cluster in sorted(df["cluster"].unique()):
    patches = X[df["cluster"].to_numpy() == cluster]
    row = {"cluster": cluster, "patch_count": len(patches)}
    for i, name in enumerate(names):
        row[name + "_mean"] = float(patches[:, i].mean())
    rows.append(row)

summary = pd.DataFrame(rows)
out = root / "results" / "cluster_summary.csv"
summary.to_csv(out, index=False)

print(summary.round(3).to_string(index=False))
print("\nSaved:", out)
