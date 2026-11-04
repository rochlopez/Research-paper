# Oil Palm Satellite CNN Project

## 1. Project overview

This project combines CNN-based oil-palm location prediction
with satellite vegetation-index comparisons.

Study area: selected tiles in Andhra Pradesh, India.
Model 1: CNN classification of likely oil-palm locations.
Model 2: monthly comparison of NDVI, NDMI and EVI.
Comparison period: corresponding months in 2024 and 2026.

## 2. Model 1 outputs

The trained CNN and tile prediction/probability rasters are
stored in OilPalm-CNN/results.

Predictions are model outputs, not independently verified
plantation boundaries.

## 3. Year-comparison data quality

Total comparison rows: 120

Status counts:
- COMPARABLE: 96
- INSUFFICIENT_VALID_PIXELS: 24

Missing change values: 24

## 4. Mean vegetation-index changes

Change is calculated as the 2026 index minus the 2024 index.
Negative values mean the index was lower in 2026.

| Tile | Index | Months | Mean change | Median change | Negative months | Positive months |
|---:|---|---:|---:|---:|---:|---:|
| 1 | EVI | 5 | -0.0134 | -0.0012 | 3 | 2 |
| 1 | NDMI | 5 | -0.0248 | -0.0176 | 3 | 2 |
| 1 | NDVI | 5 | -0.0452 | -0.0223 | 3 | 2 |
| 2 | EVI | 8 | -0.0290 | -0.0375 | 6 | 2 |
| 2 | NDMI | 8 | -0.0247 | -0.0137 | 6 | 2 |
| 2 | NDVI | 8 | -0.0334 | -0.0295 | 6 | 2 |
| 3 | EVI | 10 | -0.0292 | -0.0219 | 7 | 3 |
| 3 | NDMI | 10 | -0.0193 | -0.0118 | 6 | 4 |
| 3 | NDVI | 10 | -0.0338 | -0.0424 | 7 | 3 |
| 4 | EVI | 9 | 0.0123 | 0.0174 | 3 | 6 |
| 4 | NDMI | 9 | 0.0146 | 0.0178 | 2 | 7 |
| 4 | NDVI | 9 | 0.0025 | -0.0154 | 6 | 3 |

## 5. Monthly data

Rows in monthly statistics table: 264

Monthly observations vary in availability and quality.
Interpret comparisons only where valid observations are sufficient.

## 6. Interpretation and limitations

- Negative index changes are signals for further investigation,
  not proof of unhealthy vegetation or deforestation.
- Changes can reflect seasonality, rainfall, image quality,
  cloud masking or actual land-cover changes.
- CNN predictions require independent reference data for reliable
  accuracy assessment.
- This project does not independently establish oil-palm yield,
  production, disease or confirmed plantation decline.
- Tile summaries cover different numbers of comparable months.

## 7. Reproducibility

Retain the original imagery, model weights, scripts and CSV outputs.
Run the scripts in their intended order and verify input paths.
Record software versions and any changes to scripts.

## 8. Main conclusion

The current analysis identifies differences in vegetation-index
changes across the four study tiles. These results are preliminary
and should be interpreted alongside data quality and independent
validation before making claims about plantation condition.
