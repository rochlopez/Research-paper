
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

root = Path(__file__).resolve().parent
X = np.load(root / "prepared_data" / "X_patches.npy")
df = pd.read_csv(root / "results" / "patch_clusters.csv")

# Display RGB using bands B4, B3, B2 (indices 3, 2, 1)
ids = []
for cluster in sorted(df["cluster"].unique()):
    ids.extend(df.index[df["cluster"] == cluster][:3])

fig, axes = plt.subplots(len(ids), 1, figsize=(5, 3 * len(ids)))
if len(ids) == 1:
    axes = [axes]

for ax, i in zip(axes, ids):
    rgb = np.stack([X[i, 3], X[i, 2], X[i, 1]], axis=-1)
    rgb = np.clip(rgb * 2.5, 0, 1)
    ax.imshow(rgb)
    ax.set_title(f"Patch {i} — Cluster {df.loc[i, 'cluster']}")
    ax.axis("off")

plt.tight_layout()
out = root / "results" / "cluster_examples.png"
plt.savefig(out, dpi=150)
plt.close()
print("Saved:", out)
