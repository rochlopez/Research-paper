
import csv
from pathlib import Path

# Project folders
base = Path(__file__).resolve().parent.parent
data = base / "data"
data.mkdir(exist_ok=True)

source = "https://www.apoilfed.com/index.php/welcome/opd"

# 1. APOILFED area expansion
area_rows = [
    ["Eluru", "Pedavegi", 4178, 4600.007, 913.448, 5513.455],
    ["Eluru", "Lingapalem", 1822, 2174.474, 747.682, 2922.156],
    ["Kakinada", "Yeleswaram", 871, 680.350, 216.313, 896.663],
    ["Kakinada", "Prathipadu", 327, 339.228, 142.650, 481.878],
    ["Kakinada", "Kirlampudi", 220, 151.412, 97.940, 249.352],
    ["TOTAL", "", 7418, 7945.471, 2118.033, 10063.504]
]

with open(data / "ap_oilfed_area_expansion.csv", "w",
          newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "district", "mandal", "farmers",
        "fruit_bearing_area_ha", "non_fruit_bearing_area_ha",
        "total_area_ha", "reporting_year",
        "coverage", "source"
    ])

    for row in area_rows:
        writer.writerow(row + [
            "Unknown", "Five APOILFED mandals", source
        ])

# 2. APOILFED monthly FFB procurement
monthly_data = [
    ["2020-21", "November", 2708.580],
    ["2020-21", "December", 2056.000],
    ["2020-21", "January", 1023.230],
    ["2020-21", "February", 1000.100],
    ["2020-21", "March", 1307.390],
    ["2020-21", "April", 2035.210],
    ["2020-21", "May", 2568.680],
    ["2020-21", "June", 9258.970],
    ["2020-21", "July", 9459.135],
    ["2020-21", "August", 10277.565],
    ["2020-21", "September", 13054.840],
    ["2020-21", "October", 11479.670],
    ["2021-22", "November", 9760.487],
    ["2021-22", "December", 5331.130],
    ["2021-22", "January", 3101.660],
    ["2021-22", "February", 2385.649],
    ["2021-22", "March", 4911.205],
    ["2021-22", "April", 8278.584],
    ["2021-22", "May", 11905.113],
    ["2021-22", "June", 11592.420],
    ["2021-22", "July", 12989.778],
    ["2021-22", "August", ""],
    ["2021-22", "September", ""],
    ["2021-22", "October", ""]
]

with open(data / "ap_oilfed_ffb_procurement.csv", "w",
          newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "oil_year", "month", "ffb_procured_mt",
        "annual_total_mt", "geographical_coverage",
        "source", "notes"
    ])

    totals = {"2020-21": 66229.370, "2021-22": 70256.026}

    for year, month, quantity in monthly_data:
        writer.writerow([
            year, month, quantity, totals[year],
            "APOILFED procurement; exact coverage unknown",
            source,
            "Blank means not reported" if quantity == "" else ""
        ])

print("APOILFED supplementary datasets created!")
print("1. ap_oilfed_area_expansion.csv")
print("2. ap_oilfed_ffb_procurement.csv")
