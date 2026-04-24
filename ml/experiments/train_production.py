"""
train_production.py

Trains and serializes the final XGBoost production model.

Run this AFTER xgboost_runner.py has completed validation.
Uses the same params and feature pipeline from walk-forward — no changes.

Usage:
    python -m ml.experiments.train_production
"""

import json
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from config.paths import (
    MODELING_DATASET_FILE,
    WALKFORWARD_RESULTS_DIR,
    FEATURE_STABILITY_FILE
)


def load_data():
    df = pd.read_csv(MODELING_DATASET_FILE)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)

    target_col   = "target_252d"
    feature_cols = [
        c for c in df.columns
        if c not in ["date", "symbol", target_col]
        and df[c].dtype != object
    ]
    return df, feature_cols, target_col


def load_stable_features():
    stability_df = pd.read_csv(FEATURE_STABILITY_FILE)
    return stability_df[
        stability_df["frequency"] > 0.6
    ]["feature"].tolist()


def main():
    print("============================")
    print("Production Model Training")
    print("============================")

    # ── 1. Load data ──
    df, feature_cols, target_col = load_data()
    print(f"Dataset rows  : {len(df)}")

    # ── 2. Prepare X, y — same cleaning as walk-forward ──
    X = df[feature_cols].copy()
    y = df[target_col].copy()

    X = X.replace([np.inf, -np.inf], np.nan)
    y = y.replace([np.inf, -np.inf], np.nan).dropna()
    X = X.loc[y.index]

    medians = X.median()
    X       = X.fillna(medians)

    # ── 3. Same stability filter as walk-forward ──
    stable_features = load_stable_features()
    stable_features = sorted(stable_features)
    available       = [f for f in stable_features if f in X.columns]
    X_final         = X[available].values.astype(np.float32)

    print(f"Training rows : {len(X_final)}")
    print(f"Features      : {len(available)}")
    print(f"Feature list  : {available}")

    # ── 4. Train — same params as walk-forward, no early stopping ──
    #    n_estimators=300 — conservative fixed count since no val split.
    #    All other params identical to validated walk-forward config.
    model = XGBRegressor(
        n_estimators=300,
        max_depth=3,
        learning_rate=0.03,
        subsample=0.7,
        colsample_bytree=0.7,
        reg_alpha=0.1,
        reg_lambda=1.0,
        min_child_weight=5,
        random_state=42,
    )

    print("\nTraining...")
    model.fit(X_final, y.values, verbose=False)
    print("Done.")

    # ── 5. Serialize ──
    WALKFORWARD_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    model_path = WALKFORWARD_RESULTS_DIR / "xgboost_production.pkl"
    joblib.dump(model, model_path)

    meta_path = WALKFORWARD_RESULTS_DIR / "xgboost_production_meta.json"
    with open(meta_path, "w") as f:
        json.dump({
            "features":     available,
            "medians":      medians[available].to_dict(),
            "n_estimators": 300,
            "params": {
                "max_depth":        3,
                "learning_rate":    0.03,
                "subsample":        0.7,
                "colsample_bytree": 0.7,
                "reg_alpha":        0.1,
                "reg_lambda":       1.0,
                "min_child_weight": 5
            }
        }, f, indent=2)

    print(f"\n Model saved : {model_path}")
    print(f" Meta saved  : {meta_path}")


if __name__ == "__main__":
    main()