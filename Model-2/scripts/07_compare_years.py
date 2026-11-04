
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "Model-2" / "results" / "monthly_oil_palm_statistics.csv"
OUTPUT = ROOT / "Model-2" / "results" / "comparison_2024_vs_2026.csv"

with open(INPUT, "r", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Index each record by tile, month, and vegetation index.
records = {}
for row in rows:
    key = (int(row["tile"]), int(row["year"]),
           int(row["month"]), row["index"])
    records[key] = row

output_rows = []

for tile in range(1, 5):
    for month in range(1, 11):  # Months available in both years
        for index_name in ("NDVI", "NDMI", "EVI"):
            r2024 = records.get((tile, 2024, month, index_name))
            r2026 = records.get((tile, 2026, month, index_name))

            result = {
                "tile": tile,
                "month": month,
                "index": index_name,
                "mean_2024": "",
                "mean_2026": "",
                "change_2026_minus_2024": "",
                "valid_fraction_2024": "",
                "valid_fraction_2026": "",
                "comparison_status": "",
            }

            if not r2024 or not r2026:
                result["comparison_status"] = "MISSING_RECORD"
                output_rows.append(result)
                continue

            n24 = int(r2024["valid_pixels"] or 0)
            n26 = int(r2026["valid_pixels"] or 0)
            total24 = int(r2024["predicted_oil_palm_pixels"] or 0)
            total26 = int(r2026["predicted_oil_palm_pixels"] or 0)

            frac24 = n24 / total24 if total24 else 0
            frac26 = n26 / total26 if total26 else 0

            result["valid_fraction_2024"] = round(frac24, 4)
            result["valid_fraction_2026"] = round(frac26, 4)

            # Require at least half the predicted area to have valid data
            # in BOTH years before comparing means.
            if (
                r2024["status"] != "OK"
                or r2026["status"] != "OK"
                or frac24 < 0.50
                or frac26 < 0.50
            ):
                result["comparison_status"] = "INSUFFICIENT_VALID_PIXELS"
            else:
                mean24 = float(r2024["mean"])
                mean26 = float(r2026["mean"])

                result["mean_2024"] = mean24
                result["mean_2026"] = mean26
                result["change_2026_minus_2024"] = mean26 - mean24
                result["comparison_status"] = "COMPARABLE"

            output_rows.append(result)

fields = [
    "tile", "month", "index", "mean_2024", "mean_2026",
    "change_2026_minus_2024",
    "valid_fraction_2024", "valid_fraction_2026",
    "comparison_status",
]

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(output_rows)

print("Year comparison complete.")
print("Saved:", OUTPUT)
print("Total comparisons:", len(output_rows))
print("Comparable:", sum(
    r["comparison_status"] == "COMPARABLE" for r in output_rows
))
print("Excluded:", sum(
    r["comparison_status"] != "COMPARABLE" for r in output_rows
))
