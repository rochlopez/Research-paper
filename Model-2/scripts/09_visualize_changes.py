
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "results" / "change_summary_by_tile.csv"
OUTPUT_DIR = BASE_DIR / "results"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)
df.columns = df.columns.str.strip()

required = {
    "tile", "index", "months", "mean_change",
    "median_change", "negative_months", "positive_months"
}
missing = required - set(df.columns)

if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

# Chart 1: Mean change by index and tile
pivot = df.pivot(
    index="tile",
    columns="index",
    values="mean_change"
)

ax = pivot.plot(kind="bar", figsize=(10, 6))
ax.axhline(0, linewidth=1)
ax.set_title("Mean Vegetation Index Change: 2026 vs 2024")
ax.set_xlabel("Tile")
ax.set_ylabel("Mean change (2026 minus 2024)")
ax.legend(title="Index")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "mean_change_by_tile.png", dpi=200)
plt.close()

# Chart 2: Negative versus positive months
long_df = df.melt(
    id_vars=["tile", "index"],
    value_vars=["negative_months", "positive_months"],
    var_name="direction",
    value_name="month_count"
)

long_df["direction"] = long_df["direction"].map({
    "negative_months": "Negative",
    "positive_months": "Positive"
})

long_df["group"] = (
    "Tile " + long_df["tile"].astype(str)
    + " - " + long_df["index"].astype(str)
)

pivot_counts = long_df.pivot(
    index="group",
    columns="direction",
    values="month_count"
)

ax = pivot_counts.plot(kind="bar", figsize=(12, 7))
ax.set_title("Number of Comparable Months by Change Direction")
ax.set_xlabel("Tile and index")
ax.set_ylabel("Number of months")
plt.xticks(rotation=60, ha="right")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "change_direction_by_tile.png", dpi=200)
plt.close()

# Save a readable copy of the summary
df.to_csv(OUTPUT_DIR / "change_summary_by_tile_final.csv", index=False)

print("Visualization complete.")
print("Created:")
print(OUTPUT_DIR / "mean_change_by_tile.png")
print(OUTPUT_DIR / "change_direction_by_tile.png")
print(OUTPUT_DIR / "change_summary_by_tile_final.csv")
