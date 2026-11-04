
import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "results" / "comparison_2024_vs_2026.csv"
OUTPUT_FILE = BASE_DIR / "results" / "change_summary_by_tile.csv"

# Load comparison data
df = pd.read_csv(INPUT_FILE)

print("Input columns:")
print(df.columns.tolist())

# Clean column names
df.columns = df.columns.str.strip()

# Keep only comparable rows
if "status" in df.columns:
    df = df[df["status"].astype(str).str.lower() == "comparable"].copy()

# Ensure change values are numeric
df["change_2026_minus_2024"] = pd.to_numeric(
    df["change_2026_minus_2024"], errors="coerce"
)
df = df.dropna(subset=["change_2026_minus_2024"])

# Summarize each tile and index
summary = (
    df.groupby(["tile", "index"])["change_2026_minus_2024"]
    .agg(
        months="count",
        mean_change="mean",
        median_change="median",
        negative_months=lambda x: int((x < 0).sum()),
        positive_months=lambda x: int((x > 0).sum()),
        unchanged_months=lambda x: int((x == 0).sum()),
    )
    .reset_index()
)

# Round change values for readability
summary["mean_change"] = summary["mean_change"].round(4)
summary["median_change"] = summary["median_change"].round(4)

# Sort rows consistently
summary = summary.sort_values(["tile", "index"])

# Save summary
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
summary.to_csv(OUTPUT_FILE, index=False)

print("\nSummary by tile and index:")
print(summary.to_string(index=False))

print(f"\nSaved summary to:\n{OUTPUT_FILE}")
