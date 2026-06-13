import pickle
from pathlib import Path
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from config.paths import FEATURE_CACHE_DIR , EDA_OUTPUT_DIR
CACHE_DIR = FEATURE_CACHE_DIR
OUTPUT_DIR = EDA_OUTPUT_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def categorize_feature(feature):
    macro = {
        "interest_rate", "gdp", "inflation_rate",
        "exchange_rate", "unemployment_rate", "regime_post_2016"
    }

    momentum_trend = {
        "mom_252", "mom_126", "mom_60", "price_to_ma252",
        "price_to_ma60", "ma_60_slope", "ma_252", "ma_60",
        "mom60_x_vol20"
    }

    volatility = {"vol_60", "atr_14", "realized_vol_20"}
    liquidity = {"volume"}
    seasonality = {"month", "quarter", "q_3"}
    raw_ohlc = {"open", "high", "low", "close"}

    if feature in macro:
        return "Macroeconomic"
    if feature in momentum_trend:
        return "Momentum / Trend"
    if feature in volatility:
        return "Volatility"
    if feature in liquidity:
        return "Liquidity"
    if feature in seasonality:
        return "Seasonality"
    if feature in raw_ohlc:
        return "Raw OHLC"
    return "Other"

def extract_features(obj):
    """
    Handles common pickle shapes:
    - list of feature names
    - dict with selected_features/features/feature_names/X_columns
    - pandas DataFrame
    """
    if isinstance(obj, list):
        return obj

    if isinstance(obj, tuple):
        for item in obj:
            result = extract_features(item)
            if result:
                return result

    if isinstance(obj, dict):
        possible_keys = [
            "selected_features",
            "features",
            "feature_names",
            "X_columns",
            "columns"
        ]

        for key in possible_keys:
            if key in obj:
                value = obj[key]
                if isinstance(value, list):
                    return value
                if hasattr(value, "tolist"):
                    return value.tolist()

        print("Dictionary keys found:", obj.keys())
        return []

    if hasattr(obj, "columns"):
        return list(obj.columns)

    return []

records = []

for pkl_file in sorted(CACHE_DIR.glob("features_fold_*.pkl")):
    fold_num = int(pkl_file.stem.replace("features_fold_", ""))

    with open(pkl_file, "rb") as f:
        obj = pickle.load(f)

    features = extract_features(obj)

    if not features:
        print(f"Could not extract features from {pkl_file}")
        continue

    for feature in features:
        records.append({
            "fold": fold_num,
            "feature": feature,
            "category": categorize_feature(feature)
        })

selection_df = pd.DataFrame(records)

if selection_df.empty:
    raise ValueError("No features were extracted. Inspect one PKL file manually.")

num_folds = selection_df["fold"].nunique()

freq_df = (
    selection_df
    .groupby(["feature", "category"], as_index=False)
    .agg(count=("fold", "nunique"))
)

freq_df["frequency"] = freq_df["count"] / num_folds
freq_df["frequency_percent"] = freq_df["frequency"] * 100
freq_df = freq_df.sort_values("frequency_percent", ascending=False)

freq_df.to_csv(OUTPUT_DIR / "final_features_results.csv", index=False)
selection_df.to_csv(OUTPUT_DIR / "feature_selection_by_fold.csv", index=False)

# Fold-feature matrix
matrix = (
    selection_df
    .assign(selected=1)
    .pivot_table(
        index="feature",
        columns="fold",
        values="selected",
        fill_value=0,
        aggfunc="max"
    )
)

matrix["selection_count"] = matrix.sum(axis=1)
matrix = matrix.sort_values("selection_count", ascending=False)
matrix.to_csv(OUTPUT_DIR / "feature_survival_matrix.csv")

# Chart 1: feature frequency
plot_df = freq_df.sort_values("frequency_percent", ascending=True)

plt.figure(figsize=(11, 8))
plt.barh(plot_df["feature"], plot_df["frequency_percent"])
plt.xlabel("Selection Frequency Across Walk-Forward Folds (%)")
plt.ylabel("Feature")
plt.title("Feature Selection Frequency Across Walk-Forward Folds")
plt.xlim(0, 105)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "figure_feature_selection_frequency.png", dpi=300, bbox_inches="tight")
plt.close()

# Chart 2: category frequency
cat_df = (
    freq_df
    .groupby("category", as_index=False)
    .agg(
        average_frequency_percent=("frequency_percent", "mean"),
        number_of_features=("feature", "count")
    )
    .sort_values("average_frequency_percent", ascending=True)
)

cat_df.to_csv(OUTPUT_DIR / "feature_category_summary.csv", index=False)

plt.figure(figsize=(9, 5))
plt.barh(cat_df["category"], cat_df["average_frequency_percent"])
plt.xlabel("Average Selection Frequency (%)")
plt.ylabel("Feature Category")
plt.title("Average Selection Frequency by Feature Category")
plt.xlim(0, 105)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "figure_feature_category_frequency.png", dpi=300, bbox_inches="tight")
plt.close()

# Top features table
top_df = freq_df.head(12).copy()
top_df["frequency_percent"] = top_df["frequency_percent"].round(1)
top_df.to_csv(OUTPUT_DIR / "top_stable_features.csv", index=False)

print("Done.")
print(f"Folds detected: {num_folds}")
print(f"Outputs saved to: {OUTPUT_DIR}")
print(freq_df.head(15))