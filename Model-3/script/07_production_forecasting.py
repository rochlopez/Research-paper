
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Project paths
project_dir = Path(__file__).resolve().parent.parent
data_file = project_dir / "results" / "ap_oil_palm_master_dataset.csv"
results_dir = project_dir / "results"

df = pd.read_csv(data_file)

def forecast_production(data, target, name):
    # Select available observations
    series = data[["year", target]].dropna().copy()
    series = series.reset_index(drop=True)

    print(f"\n{name} FORECAST")
    print("=" * 45)

    if len(series) < 4:
        print("Not enough historical observations.")
        return None

    # Sequential time index
    X = np.arange(len(series)).reshape(-1, 1)
    y = series[target].values

    # Compare models using the last two observations
    predictions = []
    actuals = []

    for test_index in range(len(series) - 2, len(series)):
        model = LinearRegression()
        model.fit(X[:test_index], y[:test_index])

        predicted = model.predict(X[test_index:test_index + 1])[0]

        predictions.append(predicted)
        actuals.append(y[test_index])

    # Evaluation
    mae = mean_absolute_error(actuals, predictions)
    rmse = np.sqrt(mean_squared_error(actuals, predictions))

    print("Observations:", len(series))
    print("Backtest MAE:", round(mae, 2))
    print("Backtest RMSE:", round(rmse, 2))

    # Fit final linear trend using all observations
    final_model = LinearRegression()
    final_model.fit(X, y)

    next_index = np.array([[len(series)]])
    forecast = final_model.predict(next_index)[0]

    # Naive forecast
    naive_forecast = y[-1]

    print("Last recorded year:", series["year"].iloc[-1])
    print("Last recorded production:", round(y[-1], 2))
    print("Linear trend next-period estimate:", round(forecast, 2))
    print("Naive next-period estimate:", round(naive_forecast, 2))

    return {
        "target": name,
        "last_recorded_year": series["year"].iloc[-1],
        "observations": len(series),
        "backtest_mae": mae,
        "backtest_rmse": rmse,
        "linear_estimate": forecast,
        "naive_estimate": naive_forecast
    }

results = []

# FFB forecasting
ffb_result = forecast_production(
    df, "ffb_production_tonnes", "FFB"
)

if ffb_result:
    results.append(ffb_result)

# CPO forecasting
cpo_result = forecast_production(
    df, "cpo_production_tonnes", "CPO"
)

if cpo_result:
    results.append(cpo_result)

# Save results
if results:
    output = pd.DataFrame(results)
    output_file = results_dir / "production_forecast_baselines.csv"
    output.to_csv(output_file, index=False)

    print("\nResults saved to:")
    print(output_file)

print("\nFORECASTING BASELINE COMPLETED")
