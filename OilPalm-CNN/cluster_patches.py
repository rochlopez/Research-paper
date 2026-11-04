
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

root = Path(__file__).resolve().parent
X = np.load(root / "prepared_data" / "X_patches.npy")

# Summarize each patch using its mean and standard deviation per band
features = np.concatenate([
    X.mean(axis=(2, 3)),
    X.std(axis=(2, 3))
], axis=1)

features = StandardScaler().fit_transform(features)

model = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters = model.fit_predict(features)

result = pd.DataFrame({
    "patch_id": np.arange(len(X)),
    "cluster": clusters
})

out = root / "results"
out.mkdir(exist_ok=True)
result.to_csv(out / "patch_clusters.csv", index=False)

print("Patches grouped:", len(result))
print("\nPatches per cluster:")
print(result["cluster"].value_counts().sort_index())
print("\nSaved to results/patch_clusters.csv")
