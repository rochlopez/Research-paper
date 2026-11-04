# Module 3: Oil Palm Production and Yield Forecasting for Andhra Pradesh

## 1. Introduction
This module analyses available historical oil-palm statistics for Andhra Pradesh, India. It examines Fresh Fruit Bunch (FFB) production, Crude Palm Oil (CPO) production, and FFB yield, using simple forecasting baselines because the available annual time series are small.

This is Module 3 of a wider project:
- Module 1: Satellite imagery and CNN-based oil-palm identification.
- Module 2: Vegetation-index analysis over time.
- Module 3: Production, CPO, and yield analysis and forecasting.

Module 3 uses statistical production data. It does not claim that satellite predictions from Modules 1 or 2 directly validate or cause the production forecasts.

## 2. Objectives
1. Analyse historical FFB and CPO production.
2. Preserve the different area definitions and data sources.
3. Calculate FFB yield only when production and bearing area match in year and coverage.
4. Compare Linear Regression with a Naïve forecasting baseline.
5. Document limitations and produce next-period estimates.

## 3. Study Area
The study area is Andhra Pradesh, India. State-level observations are supplemented by separate APOILFED information for selected mandals and procurement operations. The APOILFED five-mandal area table is not a statewide total.

## 4. Data Sources

### 4.1 Historical FFB data
File: `data/ap_oil_palm_historical_6_years.csv`

The project records these FFB observations from Government of India's *Agricultural Statistics at a Glance*, Table 2.26:

| Year | FFB production (tonnes) |
|---|---:|
| 2018–19 | 1,379,215 |
| 2019–20 | 1,277,760 |
| 2020–21 | 1,471,521 |
| 2021–22 | 1,722,457 |
| 2022–23 | 1,848,209 |
| 2023–24 | 1,897,147 |

Some area and yield fields in the source CSV are missing.

### 4.2 Historical area and CPO data
File: `data/ap_oil_palm_area_cpo_2015_2021.csv`

Transcribed from a research-paper screenshot supplied for the project:

| Year | Total area (ha) | CPO production (tonnes) |
|---|---:|---:|
| 2015–16 | 149,510 | 193,562 |
| 2016–17 | 156,625 | 190,999 |
| 2017–18 | 162,692 | 234,696 |
| 2018–19 | 169,197 | 232,938 |
| 2019–20 | 172,543 | 208,359 |
| 2020–21 | 179,489 | 240,016 |

The 2020–21 value was marked as a second advance estimate in the supplied source. These area figures are total area, not confirmed bearing area.

### 4.3 APOILFED supplementary data
Official source: [APOILFED – Oil Palm Division](https://www.apoilfed.com/index.php/welcome/opd)

Files:
- `data/ap_oilfed_area_expansion.csv`
- `data/ap_oilfed_ffb_procurement.csv`

The area-expansion table reports five mandals:

| District | Mandal | Farmers | Bearing area (ha) | Non-bearing area (ha) | Total area (ha) |
|---|---|---:|---:|---:|---:|
| Eluru | Pedavegi | 4,178 | 4,600.007 | 913.448 | 5,513.455 |
| Eluru | Lingapalem | 1,822 | 2,174.474 | 747.682 | 2,922.156 |
| Kakinada | Yeleswaram | 871 | 680.350 | 216.313 | 896.663 |
| Kakinada | Prathipadu | 327 | 339.228 | 142.650 | 481.878 |
| Kakinada | Kirlampudi | 220 | 151.412 | 97.940 | 249.352 |
| **Total** | | **7,418** | **7,945.471** | **2,118.033** | **10,063.504** |

The reporting year is not stated in the available evidence. This table covers five listed mandals only; its coverage may not match the procurement coverage.

APOILFED reports:
- 2020–21 FFB procured: **66,229.370 MT**.
- 2021–22 FFB procured: **70,256.026 MT**.

These are procurement quantities, not assumed statewide FFB production. The exact procurement geography is unconfirmed. Blank monthly values in 2021–22 are retained as missing, not zero.

### 4.4 Official productivity reference
File: `data/ap_oil_palm_official_yield_references.csv`

The project records a Government of Andhra Pradesh *Socio-Economic Survey 2023–24* reference for 2022–23:
- Average bearing-plantation productivity: **19.81 tonnes/ha**.
- FFB production: **18.95 lakh MT**.
- CPO production: **3.31 lakh MT**.
- Area covered: **5.68 lakh acres**.

The reported area is described as area covered, not confirmed bearing area. The 19.81 tonnes/ha figure is retained as an official reported productivity reference, not recalculated using that area.

## 5. Data Preparation
The project created `results/ap_oil_palm_master_dataset.csv` by joining the historical FFB and area/CPO datasets by year while retaining separate area-source columns.

The master dataset includes year, FFB production, CPO production, bearing area, separate area-source values, CPO per total hectare, and FFB yield per bearing hectare.

For 2019–20, total area differs between sources:
- FFB source: 172,000 ha.
- CPO source: 172,543 ha.
- Difference: 543 ha (approximately 0.32%).

APOILFED data and the official productivity reference remain separate because their reporting periods, coverage, or definitions are not sufficiently aligned with the statewide series.

## 6. Exploratory Data Analysis

### 6.1 FFB production
From 2018–19 to 2023–24, recorded FFB production increased from 1,379,215 to 1,897,147 tonnes, an overall increase of approximately **37.55%**.

Recorded year-on-year changes:
- 2019–20: −7.36%.
- 2020–21: +15.16%.
- 2021–22: +17.05%.
- 2022–23: +7.30%.
- 2023–24: +2.65%.

These are historical changes, not guaranteed future growth.

### 6.2 CPO production
The CPO dataset contains six observations from 2015–16 to 2020–21. The latest recorded value is 240,016 tonnes in 2020–21. No later CPO observation is present in the current project dataset.

### 6.3 Area definitions
Total planted area includes bearing and non-bearing plantations. FFB yield must use bearing area, not total area.

## 7. FFB Production Forecasting
Two baselines were compared:
1. **Linear Regression:** fits a straight-line trend and extrapolates one period forward.
2. **Naïve:** uses the last observed value as the next-period estimate.

The recorded Linear Regression next-period estimate is **2,054,579.13 tonnes**, following the 2023–24 observation. This is the next period after 2023–24, not a forecast for the current calendar year.

### Step 08 backtest comparison
The final two observations were used as test observations.

| Metric | Linear Regression | Naïve |
|---|---:|---:|
| MAE (tonnes) | 68,544.95 | 87,345.00 |
| RMSE (tonnes) | 69,430.56 | 95,416.18 |

For this two-observation backtest, Linear Regression had lower MAE and RMSE than Naïve forecasting.

## 8. CPO Production Forecasting
The recorded Linear Regression next-period estimate is **245,020.87 tonnes**, following the latest CPO observation in 2020–21. This next period is different from the FFB forecast period.

### Step 08 backtest comparison

| Metric | Linear Regression | Naïve |
|---|---:|---:|
| MAE (tonnes) | 25,795.65 | 28,118.00 |
| RMSE (tonnes) | 32,246.73 | 28,339.84 |

For CPO, Linear Regression had lower MAE, while Naïve forecasting had lower RMSE. Therefore, Linear Regression should not be described as the best method for both CPO metrics.

## 9. FFB Yield Analysis
The formula is:

**FFB yield (tonnes/hectare) = FFB production (tonnes) ÷ fruit-bearing area (hectares).**

The existing yield-check script found six FFB production observations but only one year with bearing area:

| Year | Bearing area (ha) | FFB production (tonnes) | Calculated yield (tonnes/ha) |
|---|---:|---:|---:|
| 2018–19 | Missing | 1,379,215 | Missing |
| 2019–20 | 141,000 | 1,277,760 | 9.06 |
| 2020–21 | Missing | 1,471,521 | Missing |
| 2021–22 | Missing | 1,722,457 | Missing |
| 2022–23 | Missing | 1,848,209 | Missing |
| 2023–24 | Missing | 1,897,147 | Missing |

A discrepancy exists in the starter data: a 2019–20 yield figure of 19.81 had previously appeared, whereas 1,277,760 ÷ 141,000 gives approximately **9.06 tonnes/ha**. The discrepancy must be checked against the original source and definitions; neither value should be silently substituted for the other.

The separate 19.81 tonnes/ha government-reported productivity reference is for 2022–23 and is not combined with the 2019–20 calculated value to create a continuous yield series.

Only one matching annual bearing-area observation is available. A statistically meaningful annual yield forecasting model is therefore not supported.

## 10. Model Evaluation
Step 08 used the final two observations as test observations. This is a very small evaluation sample.

The visualization script from Step 11 also printed these backtest metrics:

| Target | Step 11 MAE | Step 11 RMSE |
|---|---:|---:|
| FFB | 42,893.65 | 56,454.83 |
| CPO | 37,408.75 | 38,200.52 |

These differ from the Step 08 comparison values. The difference has not yet been reconciled and may reflect different evaluation implementations or data handling. For transparency, Step 08 is presented as the primary model comparison because it explicitly compares Linear Regression and Naïve forecasting. Step 11 metrics are shown separately and must not be mixed with Step 08 results.

- **MAE (Mean Absolute Error):** average absolute difference between actual and predicted values. Lower is better.
- **RMSE (Root Mean Squared Error):** square root of average squared prediction errors; larger errors receive more weight. Lower is better.

With six annual observations and only two test observations, results are preliminary and do not establish strong predictive reliability.

## 11. Results and Discussion
1. FFB production increased overall between 2018–19 and 2023–24, with a decline in 2019–20.
2. The FFB Linear Regression next-period estimate is 2,054,579.13 tonnes.
3. The CPO Linear Regression next-period estimate is 245,020.87 tonnes, based on data ending in 2020–21.
4. In Step 08, Linear Regression performed better than Naïve on both FFB metrics. For CPO, Linear Regression had lower MAE, while Naïve had lower RMSE.
5. Available bearing-area data are insufficient for a reliable yield trend or yield forecast.
6. APOILFED area and procurement figures provide supplementary context but are not treated as statewide totals.
7. The official 2022–23 productivity reference remains separate from the 2019–20 calculated yield.

## 12. Limitations
- Only six annual observations are available for each production target.
- The backtest contains only two test observations.
- The CPO series ends in 2020–21, earlier than the FFB series.
- Annual statewide bearing-area data are largely missing.
- The APOILFED area table's reporting year is unknown and covers five mandals only.
- Exact geographical coverage of APOILFED procurement is unconfirmed.
- The two 2019–20 total-area source values differ slightly.
- The 2019–20 yield discrepancy (19.81 in the starter data versus 9.06 calculated from recorded production and bearing area) remains unresolved.
- Step 08 and Step 11 backtest metrics differ and require code-level reconciliation.
- Linear trend extrapolation is sensitive to a small sample.
- Production trends alone do not establish deforestation, soil degradation, supply shortage, or future import requirements.

## 13. Conclusion
Module 3 establishes a documented workflow for analysing Andhra Pradesh FFB and CPO production and producing simple next-period forecasting baselines. The recorded FFB and CPO Linear Regression estimates are 2,054,579.13 tonnes and 245,020.87 tonnes, respectively, but refer to different next periods.

The comparisons are preliminary because the time series are short. FFB yield forecasting is not statistically supported by the available matching bearing-area data. APOILFED information and the official productivity reference add context but remain separate where period, coverage, or definitions are uncertain.

The most important future improvement is to obtain consistent annual statewide bearing-area, FFB production, and CPO production observations with clearly documented definitions and reporting periods.

## 14. References
1. Government of India, *Agricultural Statistics at a Glance*, Table 2.26, as recorded in the project dataset.
2. Research-paper screenshot supplied for the project: historical total-area and CPO production values for 2015–16 to 2020–21.
3. Andhra Pradesh Oil Federation (APOILFED), Oil Palm Division: [https://www.apoilfed.com/index.php/welcome/opd](https://www.apoilfed.com/index.php/welcome/opd).
4. Government of Andhra Pradesh, *Socio-Economic Survey 2023–24*, Oil Palm section, page 82, as recorded in the project reference dataset.

## Reproducibility and expected outputs
Existing scripts and outputs are retained. Relevant scripts include:
- `script/01_check_historical_data.py`
- `script/02_analyze_production_trend.py`
- `script/03_check_yield_data.py`
- `script/04_prepare_master_dataset.py`
- `script/05_data_quality_audit.py`
- `script/06_visualize_production.py`
- `script/07_production_forecasting.py`
- `script/08_compare_forecasting_models.py`
- `script/09_create_apoilfed_datasets.py`
- `script/10_create_official_yield_references.py`
- `script/11_final_forecasting_visualizations.py`

Expected chart files in `results/`:
- `ffb_production_trend.png`
- `cpo_production_trend.png`
- `ffb_forecast.png`
- `cpo_forecast.png`
- `ffb_actual_vs_predicted.png`
- `cpo_actual_vs_predicted.png`

Before submission, confirm that each listed file exists locally. This report describes the recorded project state at the time of preparation.
