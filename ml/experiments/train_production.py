"""
train_xgboost_final.py

Final training + serialization for selected XGBoost V1 model.

Usage:
    python -m ml.experiments.train_xgboost_final
"""

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from config.paths import (
    MODELING_DATASET_FILE,
    WALKFORWARD_BASELINE_DIR,
    FEATURE_STABILITY_FILE,
)

warnings.filterwarnings("ignore")


ARTIFACT_DIR = WALKFORWARD_BASELINE_DIR / "xgboost_final_artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


# Selected final model: V1
BEST_PARAMS = {
    "n_estimators": 308,
    "max_depth": 5,
    "learning_rate": 0.03362895774231974,
    "subsample": 0.7383038258652408,
    "colsample_bytree": 0.5773203111238806,
    "min_child_weight": 15,
    "gamma": 0.87742101992794,
    "reg_alpha": 0.1799281490630024,
    "reg_lambda": 8.502851087916396,
    "objective": "reg:squarederror",
    "eval_metric": "rmse",
    "tree_method": "hist",
    "random_state": 42,
    "n_jobs": -1,
}

EARLY_STOPPING_ROUNDS = 30
VALIDATION_FRACTION = 0.15
STABILITY_THRESHOLD = 0.6


def load_data():
    df = pd.read_csv(MODELING_DATASET_FILE)

    df["date"] = pd.to_datetime(df["date"])

    # Important: keep time ordering
    df = df.sort_values(["date", "symbol"]).reset_index(drop=True)

    target_col = "target_252d"

    feature_cols = [
        c for c in df.columns
        if c not in ["date", "symbol", target_col]
        and df[c].dtype != object
    ]

    return df, feature_cols, target_col


def load_final_features(feature_cols):
    stability_df = pd.read_csv(FEATURE_STABILITY_FILE)

    if "feature" not in stability_df.columns or "frequency" not in stability_df.columns:
        raise ValueError("FEATURE_STABILITY_FILE must contain columns: feature, frequency")

    final_features = stability_df[
        stability_df["frequency"] > STABILITY_THRESHOLD
    ]["feature"].tolist()

    final_features = [f for f in final_features if f in feature_cols]
    final_features = sorted(final_features)

    if len(final_features) == 0:
        raise ValueError("No final features found. Check feature stability file.")

    return final_features


def prepare_final_training_data(df, final_features, target_col):
    X = df[final_features].copy()
    y = df[target_col].copy()

    X = X.replace([np.inf, -np.inf], np.nan)
    y = y.replace([np.inf, -np.inf], np.nan)

    valid_target = y.notna()

    X = X.loc[valid_target]
    y = y.loc[valid_target]

    dates = df.loc[valid_target, "date"].copy()

    # Medians calculated from final training data
    medians = X.median()
    X = X.fillna(medians)

    X_np = X.values.astype(np.float32)
    y_np = y.values.astype(np.float32)

    return X_np, y_np, dates, medians


def find_best_iteration(X, y):
    """
    Use the last 15% of the time-ordered training data as validation
    to estimate the best number of boosting rounds.
    """

    n = len(X)
    split = int(n * (1 - VALIDATION_FRACTION))

    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    temp_params = {
        **BEST_PARAMS,
        "early_stopping_rounds": EARLY_STOPPING_ROUNDS,
    }

    model = XGBRegressor(**temp_params)

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    best_iteration = getattr(model, "best_iteration", None)

    if best_iteration is None:
        best_n_estimators = BEST_PARAMS["n_estimators"]
    else:
        best_n_estimators = int(best_iteration) + 1

    return best_n_estimators


def train_final_model_on_all_data(X, y, best_n_estimators):
    """
    Final model is retrained on all available data using the selected
    number of estimators.

    This avoids losing the last 15% of data in the final production model.
    """

    final_params = {
        **BEST_PARAMS,
        "n_estimators": best_n_estimators,
    }

    # No early stopping in the final full-data training
    final_params.pop("early_stopping_rounds", None)

    model = XGBRegressor(**final_params)
    model.fit(X, y, verbose=False)

    return model, final_params


def save_artifacts(
    model,
    final_features,
    medians,
    final_params,
    df,
    dates,
    target_col,
):
    model_path = ARTIFACT_DIR / "xgboost_model.json"
    features_path = ARTIFACT_DIR / "feature_columns.json"
    medians_path = ARTIFACT_DIR / "feature_medians.json"
    params_path = ARTIFACT_DIR / "xgboost_final_params.json"
    metadata_path = ARTIFACT_DIR / "model_metadata.json"

    model.save_model(model_path)

    with open(features_path, "w", encoding="utf-8") as f:
        json.dump(final_features, f, indent=2)

    medians.to_json(medians_path, indent=2)

    with open(params_path, "w", encoding="utf-8") as f:
        json.dump(final_params, f, indent=2)

    metadata = {
        "model_name": "xgboost_v1_final",
        "model_type": "XGBRegressor",
        "target": target_col,
        "selected_tuning_version": "V1",
        "feature_selection_rule": f"FEATURE_STABILITY_FILE frequency > {STABILITY_THRESHOLD}",
        "n_features": int(len(final_features)),
        "n_training_rows": int(len(dates)),
        "training_start_date": str(pd.to_datetime(dates).min().date()),
        "training_end_date": str(pd.to_datetime(dates).max().date()),
        "initial_best_params": BEST_PARAMS,
        "final_training_params": final_params,
        "validation_results": {
            "v1_avg_ic": 0.181379,
            "v1_avg_spearman_ic": 0.154177,
            "v1_spearman_icir": 1.175202,
            "v1_negative_spearman_folds": "1/15",
        },
        "backtest_results": {
            "rebalance_mode": "FOLD_START",
            "n_rebalances": 15,
            "avg_top_return": 0.238645,
            "avg_bottom_return": -0.014310,
            "avg_benchmark_return": 0.092130,
            "avg_active_return": 0.146515,
            "avg_long_short_spread": 0.252955,
            "avg_top_return_after_cost": 0.237880,
            "avg_active_after_cost": 0.145750,
            "avg_long_short_after_cost": 0.251387,
            "top_beats_benchmark_rate": 0.733333,
            "top_beats_bottom_rate": 0.733333,
            "positive_long_short_rate": 0.733333,
            "active_after_cost_sharpe_like": 0.709312,
            "long_short_after_cost_sharpe_like": 0.871446,
        },
        "artifact_files": {
            "model": model_path.name,
            "features": features_path.name,
            "medians": medians_path.name,
            "params": params_path.name,
            "metadata": metadata_path.name,
        },
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return {
        "model": model_path,
        "features": features_path,
        "medians": medians_path,
        "params": params_path,
        "metadata": metadata_path,
    }


def main():
    print("Loading data...")
    df, feature_cols, target_col = load_data()

    print(f"Dataset rows: {len(df)}")
    print(f"Numeric features before final selection: {len(feature_cols)}")

    final_features = load_final_features(feature_cols)

    print(f"Final selected features: {len(final_features)}")
    for f in final_features:
        print(f"  - {f}")

    X, y, dates, medians = prepare_final_training_data(
        df=df,
        final_features=final_features,
        target_col=target_col,
    )

    print("\nFinding best iteration using internal validation...")
    best_n_estimators = find_best_iteration(X, y)

    print(f"Original n_estimators: {BEST_PARAMS['n_estimators']}")
    print(f"Selected final n_estimators: {best_n_estimators}")

    print("\nTraining final model on all available data...")
    final_model, final_params = train_final_model_on_all_data(
        X=X,
        y=y,
        best_n_estimators=best_n_estimators,
    )

    print("\nSaving artifacts...")
    paths = save_artifacts(
        model=final_model,
        final_features=final_features,
        medians=medians,
        final_params=final_params,
        df=df,
        dates=dates,
        target_col=target_col,
    )

    print("\n============================")
    print("Final model serialization done")
    print("============================")
    for name, path in paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()