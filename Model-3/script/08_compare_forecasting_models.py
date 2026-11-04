
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

project_dir = Path(__file__).resolve().parent.parent
data_file = project_dir / "results" / "ap_oil_palm_master_dataset.csv"
results_dir = project_dir / "results"

df = pd.read_csv(data_file)

def compare_models(target, name):
    data = df[["year", target]].dropna().reset_index(drop=True)

    y = data[target].values
    years = data["year"].values

    actual = []
    linear_predictions = []
    naive_predictions = []

    # Test the final two observations
    for test_index in range(len(data) - 2, len(data)):

        train_y = y[:test_index]
        X_train = np.arange(test_index).reshape(-1, 1)
        X_test = np.array([[test_index]])

        model = LinearRegression()
        model.fit(X_train, train_y)

        linear_predictions.append(model.predict(X_test)[0])

        # Previous year's value
        naive_predictions.append(y[test_index - 1])

        actual.append(y[test_index])

    linear_mae = mean_absolute_error(actual, linear_predictions)
    naive_mae = mean_absolute_error(actual, naive_predictions)

    linear_rmse = np.sqrt(
        mean_squared_error(actual, linear_predictions)
    )
    naive_rmse = np.sqrt(
        mean_squared_error(actual, naive_predictions)
    )

    print(f"\n{name} MODEL COMPARISON")
    print("-" * 45)
    print("Test years:", list(years[-2:]))
    print("Actual values:", actual)
    print("Linear predictions:", np.round(linear_predictions, 2))
    print("Naive predictions:", naive_predictions)

    print("\nLinear MAE:", round(linear_mae, 2))
    print("Naive MAE:", round(naive_mae, 2))
    print("Linear RMSE:", round(linear_rmse, 2))
    print("Naive RMSE:", round(naive_rmse, 2))

    return {
        "target": name,
        "observations": len(data),
        "linear_mae": linear_mae,
        "naive_mae": naive_mae,
        "linear_rmse": linear_rmse,
        "naive_rmse": naive_rmse
    }

results = []

for target, name in [
    ("ffb_production_tonnes", "FFB"),
    ("cpo_production_tonnes", "CPO")
]:
    result = compare_models(target, name)

    if result:
        results.append(result)

output = pd.DataFrame(results)
output_file = results_dir / "model_comparison.csv"
output.to_csv(output_file, index=False)

print("\nComparison saved to:", output_file)
print("\nSTEP 08 COMPLETED")
