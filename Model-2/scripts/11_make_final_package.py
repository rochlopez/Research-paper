
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
PROJECT = BASE.parent
RESULTS = BASE / "results"
OUTPUT = RESULTS / "FINAL_PROJECT_REPORT.md"

comparison_file = RESULTS / "comparison_2024_vs_2026.csv"
summary_file = RESULTS / "change_summary_by_tile.csv"
monthly_file = RESULTS / "monthly_oil_palm_statistics.csv"

lines = [
    "# Oil Palm Satellite CNN Project",
    "",
    "## 1. Project overview",
    "",
    "This project combines CNN-based oil-palm location prediction",
    "with satellite vegetation-index comparisons.",
    "",
    "Study area: selected tiles in Andhra Pradesh, India.",
    "Model 1: CNN classification of likely oil-palm locations.",
    "Model 2: monthly comparison of NDVI, NDMI and EVI.",
    "Comparison period: corresponding months in 2024 and 2026.",
    "",
    "## 2. Model 1 outputs",
    "",
    "The trained CNN and tile prediction/probability rasters are",
    "stored in OilPalm-CNN/results.",
    "",
    "Predictions are model outputs, not independently verified",
    "plantation boundaries.",
    "",
]

if comparison_file.exists():
    df = pd.read_csv(comparison_file)
    df.columns = df.columns.str.strip()

    lines += [
        "## 3. Year-comparison data quality",
        "",
        f"Total comparison rows: {len(df)}",
        "",
    ]

    if "comparison_status" in df.columns:
        counts = df["comparison_status"].value_counts(dropna=False)
        lines += ["Status counts:"]
        for name, count in counts.items():
            lines.append(f"- {name}: {count}")

    if "change_2026_minus_2024" in df.columns:
        lines += [
            "",
            "Missing change values: "
            + str(df["change_2026_minus_2024"].isna().sum()),
            "",
        ]

if summary_file.exists():
    summary = pd.read_csv(summary_file)
    lines += [
        "## 4. Mean vegetation-index changes",
        "",
        "Change is calculated as the 2026 index minus the 2024 index.",
        "Negative values mean the index was lower in 2026.",
        "",
        "| Tile | Index | Months | Mean change | Median change | Negative months | Positive months |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]

    for _, r in summary.iterrows():
        lines.append(
            f"| {int(r['tile'])} | {r['index']} | "
            f"{int(r['months'])} | {r['mean_change']:.4f} | "
            f"{r['median_change']:.4f} | "
            f"{int(r['negative_months'])} | "
            f"{int(r['positive_months'])} |"
        )

if monthly_file.exists():
    monthly = pd.read_csv(monthly_file)
    lines += [
        "",
        "## 5. Monthly data",
        "",
        f"Rows in monthly statistics table: {len(monthly)}",
        "",
        "Monthly observations vary in availability and quality.",
        "Interpret comparisons only where valid observations are sufficient.",
    ]

lines += [
    "",
    "## 6. Interpretation and limitations",
    "",
    "- Negative index changes are signals for further investigation,",
    "  not proof of unhealthy vegetation or deforestation.",
    "- Changes can reflect seasonality, rainfall, image quality,",
    "  cloud masking or actual land-cover changes.",
    "- CNN predictions require independent reference data for reliable",
    "  accuracy assessment.",
    "- This project does not independently establish oil-palm yield,",
    "  production, disease or confirmed plantation decline.",
    "- Tile summaries cover different numbers of comparable months.",
    "",
    "## 7. Reproducibility",
    "",
    "Retain the original imagery, model weights, scripts and CSV outputs.",
    "Run the scripts in their intended order and verify input paths.",
    "Record software versions and any changes to scripts.",
    "",
    "## 8. Main conclusion",
    "",
    "The current analysis identifies differences in vegetation-index",
    "changes across the four study tiles. These results are preliminary",
    "and should be interpreted alongside data quality and independent",
    "validation before making claims about plantation condition.",
    "",
]

OUTPUT.write_text("\n".join(lines), encoding="utf-8")

print("Final report created:")
print(OUTPUT)
print("\nExisting results were read; source data and model weights were not changed.")
