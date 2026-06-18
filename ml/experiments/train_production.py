"""
train_xgboost_final.py

Final training + serialization for the selected XGBoost V1 model.

Usage:
    python -m ml.experiments.train_production
"""

import json
import warnings

import numpy as np
import pandas as pd
import xgboost as xgb
from xgboost import XGBRegressor
import joblib

from config.paths import (
    MODELING_DATASET_FILE,
    FEATURE_STABILITY_FILE,
    XGBOOST_BEST_PARAMS_FILE,
    XGBOOST_TUNED_SUMMARY_FILE,
    XGBOOST_BACKTEST_SUMMARY_FILE,
    XGBOOST_FINAL_MODEL_DIR,
    XGBOOST_FINAL_DOCS_DIR,
    XGBOOST_FINAL_FIGURES_DIR,
    XGB_MODEL,
    XGB_MODEL_PKL,
    XGB_MODEL_META,
    XGB_FEATURE_COLUMNS,
    XGB_FEATURE_MEDIANS,
    XGB_FINAL_PARAMS,
)

warnings.filterwarnings("ignore")


# =====================================================
# Final Training Settings
# =====================================================
TARGET_COL = "target_252d"

SELECTED_TUNING_VERSION = "V1"
STABILITY_THRESHOLD = 0.6
VALIDATION_FRACTION = 0.15
EARLY_STOPPING_ROUNDS = 30


# =====================================================
# Helpers
# =====================================================
def ensure_output_dirs():
    XGBOOST_FINAL_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    XGBOOST_FINAL_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    XGBOOST_FINAL_FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(obj, file, indent=2)


# =====================================================
# Load Dataset
# =====================================================
def load_data():
    if not MODELING_DATASET_FILE.exists():
        raise FileNotFoundError(f"Missing modeling dataset: {MODELING_DATASET_FILE}")

    df = pd.read_csv(MODELING_DATASET_FILE)

    if "date" not in df.columns:
        raise ValueError("Modeling dataset must contain a 'date' column.")

    if "symbol" not in df.columns:
        raise ValueError("Modeling dataset must contain a 'symbol' column.")

    if TARGET_COL not in df.columns:
        raise ValueError(f"Modeling dataset must contain target column: {TARGET_COL}")

    df["date"] = pd.to_datetime(df["date"])

    # Critical for time-series training and internal validation split
    df = df.sort_values(["date", "symbol"]).reset_index(drop=True)

    feature_cols = [
        col for col in df.columns
        if col not in ["date", "symbol", TARGET_COL]
        and pd.api.types.is_numeric_dtype(df[col])
    ]

    if not feature_cols:
        raise ValueError("No numeric feature columns found.")

    return df, feature_cols


# =====================================================
# Final Feature Selection
# =====================================================
def load_final_features(feature_cols):
    if not FEATURE_STABILITY_FILE.exists():
        raise FileNotFoundError(f"Missing feature stability file: {FEATURE_STABILITY_FILE}")

    stability_df = pd.read_csv(FEATURE_STABILITY_FILE)

    required_cols = {"feature", "frequency"}
    missing_cols = required_cols - set(stability_df.columns)

    if missing_cols:
        raise ValueError(
            f"Feature stability file is missing columns: {missing_cols}"
        )

    final_features = stability_df.loc[
        stability_df["frequency"] > STABILITY_THRESHOLD,
        "feature",
    ].tolist()

    final_features = [
        feature for feature in final_features
        if feature in feature_cols
    ]

    final_features = sorted(final_features)

    if not final_features:
        raise ValueError(
            "No final features found. Check feature stability threshold "
            f"or feature_stability.csv. Threshold = {STABILITY_THRESHOLD}"
        )

    return final_features


# =====================================================
# Prepare Training Data
# =====================================================
def prepare_training_data(df, final_features):
    X = df[final_features].copy()
    y = df[TARGET_COL].copy()

    X = X.replace([np.inf, -np.inf], np.nan)
    y = y.replace([np.inf, -np.inf], np.nan)

    valid_mask = y.notna()

    X = X.loc[valid_mask].reset_index(drop=True)
    y = y.loc[valid_mask].reset_index(drop=True)

    dates = df.loc[valid_mask, "date"].reset_index(drop=True)
    symbols = df.loc[valid_mask, "symbol"].reset_index(drop=True)

    # Medians are part of production preprocessing
    medians = X.median()
    X = X.fillna(medians)

    X_np = X.values.astype(np.float32)
    y_np = y.values.astype(np.float32)

    return X_np, y_np, dates, symbols, medians


# =====================================================
# Estimate Best Number of Trees
# =====================================================
def find_best_n_estimators(X, y, best_params):
    """
    Uses the last 15% of the time-ordered training data as validation
    to estimate the best number of boosting rounds.

    The final model is later retrained on all data using this number.
    """

    n_rows = len(X)

    if n_rows < 100:
        print("Dataset too small for internal validation. Using original n_estimators.")
        return int(best_params["n_estimators"])

    split_idx = int(n_rows * (1 - VALIDATION_FRACTION))

    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]

    temp_params = {
        **best_params,
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
        return int(best_params["n_estimators"])

    return int(best_iteration) + 1


# =====================================================
# Final Model Training
# =====================================================
def train_final_model(X, y, best_params, best_n_estimators):
    final_params = {
        **best_params,
        "n_estimators": int(best_n_estimators),
    }

    # Final full-data model should not use early stopping
    final_params.pop("early_stopping_rounds", None)

    model = XGBRegressor(**final_params)
    model.fit(X, y, verbose=False)

    return model, final_params


# =====================================================
# Save Artifacts
# =====================================================
def save_artifacts(
    model,
    final_features,
    medians,
    final_params,
    dates,
    symbols,
    validation_summary,
    backtest_summary,
):
    # 1. Save model
    model.save_model(str(XGB_MODEL))

    # 2. Save model in joblib/pickle format for Python app usage
    joblib.dump(model, XGB_MODEL_PKL)

    # 3. Save feature columns
    save_json(final_features, XGB_FEATURE_COLUMNS)

    # 4. Save medians
    medians.to_json(XGB_FEATURE_MEDIANS, indent=2)

    # 5. Save final params
    save_json(final_params, XGB_FINAL_PARAMS)

    # 6. Save metadata
    metadata = {
        "model_name": "xgboost_v1_final",
        "model_type": "XGBRegressor",
        "selected_tuning_version": SELECTED_TUNING_VERSION,
        "target": TARGET_COL,

        "feature_selection": {
            "source_file": str(FEATURE_STABILITY_FILE),
            "rule": f"frequency > {STABILITY_THRESHOLD}",
            "n_features": int(len(final_features)),
            "features_file": XGB_FEATURE_COLUMNS.name,
            "medians_file": XGB_FEATURE_MEDIANS.name,
        },

        "training_data": {
            "source_file": str(MODELING_DATASET_FILE),
            "n_training_rows": int(len(dates)),
            "n_symbols": int(symbols.nunique()),
            "training_start_date": str(pd.to_datetime(dates).min().date()),
            "training_end_date": str(pd.to_datetime(dates).max().date()),
            "date_ordering": "date, symbol",
        },

        "training_strategy": {
            "internal_validation_fraction": VALIDATION_FRACTION,
            "early_stopping_rounds_for_iteration_selection": EARLY_STOPPING_ROUNDS,
            "final_model_training": "Retrained on all available rows after selecting n_estimators",
        },

        "final_params": final_params,

        "validation_results": {
            "source_file": str(XGBOOST_TUNED_SUMMARY_FILE),
            **validation_summary,
        },

        "backtest_results": {
            "source_file": str(XGBOOST_BACKTEST_SUMMARY_FILE),
            **backtest_summary,
        },

    "artifact_files": {
        "model_json": str(XGB_MODEL),
        "model_pickle": str(XGB_MODEL_PKL),
        "metadata": str(XGB_MODEL_META),
        "feature_columns": str(XGB_FEATURE_COLUMNS),
        "feature_medians": str(XGB_FEATURE_MEDIANS),
        "final_params": str(XGB_FINAL_PARAMS),
    },

        "library_versions": {
            "xgboost": xgb.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
    }

    save_json(metadata, XGB_MODEL_META)

    return {
        "model_json": XGB_MODEL,
        "model_pickle": XGB_MODEL_PKL,
        "metadata": XGB_MODEL_META,
        "feature_columns": XGB_FEATURE_COLUMNS,
        "feature_medians": XGB_FEATURE_MEDIANS,
        "final_params": XGB_FINAL_PARAMS,
    }


# =====================================================
# Main
# =====================================================
def main():
    ensure_output_dirs()

    print("Loading final selected XGBoost V1 parameters...")
    best_params = load_json(XGBOOST_BEST_PARAMS_FILE)

    print("Loading validation summary...")
    validation_summary = load_json(XGBOOST_TUNED_SUMMARY_FILE)

    print("Loading backtest summary...")
    backtest_summary = load_json(XGBOOST_BACKTEST_SUMMARY_FILE)

    print("\nLoading modeling dataset...")
    df, feature_cols = load_data()

    print(f"Dataset rows: {len(df):,}")
    print(f"Numeric features before final selection: {len(feature_cols)}")

    print("\nLoading final stable feature set...")
    final_features = load_final_features(feature_cols)

    print(f"Final selected features: {len(final_features)}")
    for feature in final_features:
        print(f"  - {feature}")

    print("\nPreparing final training matrix...")
    X, y, dates, symbols, medians = prepare_training_data(
        df=df,
        final_features=final_features,
    )

    print(f"Training rows after target filtering: {len(y):,}")
    print(f"Training date range: {dates.min().date()} -> {dates.max().date()}")

    print("\nSelecting final n_estimators using internal validation...")
    best_n_estimators = find_best_n_estimators(
        X=X,
        y=y,
        best_params=best_params,
    )

    print(f"Original n_estimators from V1: {best_params['n_estimators']}")
    print(f"Final selected n_estimators: {best_n_estimators}")

    print("\nTraining final XGBoost model on all available data...")
    final_model, final_params = train_final_model(
        X=X,
        y=y,
        best_params=best_params,
        best_n_estimators=best_n_estimators,
    )

    print("\nSaving production artifacts...")
    artifact_paths = save_artifacts(
        model=final_model,
        final_features=final_features,
        medians=medians,
        final_params=final_params,
        dates=dates,
        symbols=symbols,
        validation_summary=validation_summary,
        backtest_summary=backtest_summary,
    )

    print("\n====================================")
    print("Final XGBoost production model saved")
    print("====================================")

    for name, path in artifact_paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()