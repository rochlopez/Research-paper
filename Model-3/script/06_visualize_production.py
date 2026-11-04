
import pandas as pd
import matplotlib

# Save charts without opening separate windows
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pathlib import Path

print("MODEL 3 - PRODUCTION VISUALIZATION STARTED", flush=True)

# Locate folders
project_dir = Path(__file__).resolve().parent.parent
data_file = project_dir / "results" / "ap_oil_palm_master_dataset.csv"
results_dir = project_dir / "results"

# Check input file
if not data_file.exists():
    print("ERROR: Master dataset not found!")
    print("Expected:", data_file)
    raise SystemExit(1)

df = pd.read_csv(data_file)

print("Dataset loaded successfully.")
print("Records:", len(df))

# -----------------------------
# 1. FFB PRODUCTION CHART
# -----------------------------

ffb = df.dropna(subset=["ffb_production_tonnes"]).copy()

if len(ffb) > 0:
    plt.figure(figsize=(10, 5))
    plt.plot(
        ffb["year"],
        ffb["ffb_production_tonnes"],
        marker="o"
    )

    plt.title("Andhra Pradesh Oil Palm FFB Production")
    plt.xlabel("Year")
    plt.ylabel("FFB Production (tonnes)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    ffb_path = results_dir / "ffb_production_trend.png"
    plt.savefig(ffb_path, dpi=150)
    plt.close()

    print("FFB chart saved:", ffb_path)
else:
    print("No FFB production records available.")

# -----------------------------
# 2. CPO PRODUCTION CHART
# -----------------------------

cpo = df.dropna(subset=["cpo_production_tonnes"]).copy()

if len(cpo) > 0:
    plt.figure(figsize=(10, 5))
    plt.plot(
        cpo["year"],
        cpo["cpo_production_tonnes"],
        marker="o"
    )

    plt.title("Andhra Pradesh Crude Palm Oil Production")
    plt.xlabel("Year")
    plt.ylabel("CPO Production (tonnes)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    cpo_path = results_dir / "cpo_production_trend.png"
    plt.savefig(cpo_path, dpi=150)
    plt.close()

    print("CPO chart saved:", cpo_path)
else:
    print("No CPO production records available.")

print("\nVISUALIZATION COMPLETED SUCCESSFULLY!")
