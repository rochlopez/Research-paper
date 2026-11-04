
from pathlib import Path
import pandas as pd

ROOT = Path(
    r"C:\Users\Roch Lopez\Downloads\code\research paper"
)

RESULTS = ROOT / "forest_loss" / "results"

# Table 1: Annual forest/tree-cover loss
loss_file = RESULTS / "annual_tree_cover_loss.csv"
loss_df = pd.read_csv(loss_file)

loss_df["year"] = pd.to_numeric(
    loss_df["year"], errors="coerce"
).astype("Int64")

# Table 2: 2024 vegetation summary
vegetation_file = RESULTS / "vegetation_baseline_2024.csv"
vegetation_df = pd.read_csv(vegetation_file)

# Power BI imports pandas DataFrames.
# These names will appear in the Navigator window.
df_loss = loss_df
df_vegetation = vegetation_df
