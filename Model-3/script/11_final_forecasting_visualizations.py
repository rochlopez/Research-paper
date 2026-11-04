
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

base = Path(__file__).resolve().parent.parent
data = base / "data"
results = base / "results"
results.mkdir(exist_ok=True)


def analyze(file, target, name):
    df = pd.read_csv(data / file)
    df = df[["year", target]].dropna()

    x = np.arange(len(df)).reshape(-1, 1)
    y = df[target].values

    # Forecast next period
    model = LinearRegression()
    model.fit(x, y)
    forecast = model.predict([[len(df)]])[0]

    # Historical trend and next-period forecast
    plt.figure(figsize=(9, 5))
    plt.plot(df["year"], y, marker="o", label="Actual production")
    plt.scatter(len(df), forecast, color="red",
                label="Next-period forecast")
    plt.plot(
        np.arange(len(df) + 1),
        model.predict(np.arange(len(df) + 1).reshape(-1, 1)),
        linestyle="--", label="Linear trend"
    )
    plt.xticks(
        list(range(len(df) + 1)),
        list(df["year"]) + ["Next period"],
        rotation=30
    )
    plt.title(name + " Production Forecast")
    plt.ylabel("Production (tonnes)")
    plt.xlabel("Year")
    plt.legend()
    plt.tight_layout()
    plt.savefig(results / (name.lower() + "_forecast.png"))
    plt.close()

    # Backtest: last two observations
    train_x, test_x = x[:-2], x[-2:]
    train_y, test_y = y[:-2], y[-2:]

    test_model = LinearRegression()
    test_model.fit(train_x, train_y)
    predictions = test_model.predict(test_x)

    naive = y[-3:-1]

    mae = mean_absolute_error(test_y, predictions)
    rmse = np.sqrt(mean_squared_error(test_y, predictions))

    plt.figure(figsize=(8, 5))
    positions = np.arange(2)
    width = 0.25

    plt.bar(positions - width, test_y, width, label="Actual")
    plt.bar(positions, predictions, width, label="Linear Regression")
    plt.bar(positions + width, naive, width, label="Naive")

    plt.xticks(positions, df["year"].iloc[-2:])
    plt.title(name + " Actual vs Predicted")
    plt.ylabel("Production (tonnes)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(results / (name.lower() + "_actual_vs_predicted.png"))
    plt.close()

    print("\n", name, "FORECAST")
    print("Last recorded year:", df["year"].iloc[-1])
    print("Next-period estimate:", round(forecast, 2))
    print("Backtest MAE:", round(mae, 2))
    print("Backtest RMSE:", round(rmse, 2))


analyze(
    "ap_oil_palm_historical_6_years.csv",
    "ffb_production_tonnes",
    "FFB"
)

analyze(
    "ap_oil_palm_area_cpo_2015_2021.csv",
    "cpo_production_tonnes",
    "CPO"
)

print("\nAll forecasting visualizations saved!")
