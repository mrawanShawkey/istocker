import pandas as pd

files = {
    "XGBoost": "data/ml_data/results/xgboost_results.csv",
    "SARIMAX": "data/ml_data/results/sarimax_results.csv",
    "LSTM":    "data/ml_data/results/lstm_results.csv"
}

all_results = []

for model_name, path in files.items():

    df = pd.read_csv(path)
    df["model"] = model_name

    all_results.append(df)

all_results = pd.concat(all_results, ignore_index=True)

summary = all_results.groupby("model").mean(numeric_only=True)

print("\n============================")
print("MODEL COMPARISON")
print("============================")

print(summary[[
    "rmse",
    "mae",
    "r2",
    "directional_accuracy",
    "information_coefficient",
    "r2_out_of_sample"
]])

summary.to_csv("data/ml_data/results/model_comparison.csv")