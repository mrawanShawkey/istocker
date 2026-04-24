"""
walkforward_training.py

Core walk-forward training engine.

What this file does:
-------------------
This module runs a full time-series walk-forward experiment.

Pipeline per fold:
1. Split data into train/test (time-based)
2. Clean data (handle NaN / Inf)
3. Load or compute feature selection (cached per fold)
4. Train model (fresh model per fold → no leakage)
5. Predict on test window
6. Align predictions (important for LSTM)
7. Evaluate using both statistical and financial metrics
8. Store results

Key Design Decisions:
--------------------
- Feature selection is cached per fold → ensures consistency across models
- New model instance per fold → prevents information leakage
- Model-agnostic → supports XGBoost, SARIMAX, LSTM, etc.
- Walk-forward (expanding window) → realistic financial evaluation
"""
"""
walkforward_training.py
"""

import pandas as pd
import numpy as np
import json
import joblib

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from ml.training.walk_forward_split import WalkForwardSplit
from ml.feature_selection.feature_selector import FeatureSelector
from ml.feature_selection.feature_cache import save_features, load_features

from ml.evaluation.metrics import (
    directional_accuracy,
    information_coefficient,
    out_of_sample_r2
)

from config.paths import (
    MODELING_DATASET_FILE,
    WALKFORWARD_RESULTS_DIR
)

from scipy.stats import spearmanr


def sign_hit_rate(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    y_true = y_true[mask]
    y_pred = y_pred[mask]

    if len(y_true) == 0:
        return np.nan

    return np.mean(np.sign(y_true) == np.sign(y_pred))


def spearman_ic(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    y_true = y_true[mask]
    y_pred = y_pred[mask]

    if len(y_true) < 3:
        return np.nan

    return spearmanr(y_pred, y_true).correlation



class WalkForwardTraining:

    def __init__(self, model_factory, model_name):

        self.model_factory = model_factory
        self.model_name    = model_name

        print("Loading dataset...")

        self.df = pd.read_csv(MODELING_DATASET_FILE)
        self.df["date"] = pd.to_datetime(self.df["date"])

        # ---------------------------------------------------------
        # Sort by symbol then date — CRITICAL for LSTM sequences
        # ---------------------------------------------------------
        self.df = self.df.sort_values(
            ["symbol", "date"]
        ).reset_index(drop=True)

        print("Dataset size:", len(self.df))

        self.target_col = "target_252d"

        # ---------------------------------------------------------
        # Feature columns — numeric only, no symbol/date/target
        # ---------------------------------------------------------
        self.feature_cols = [
            c for c in self.df.columns
            if c not in ["date", "symbol", self.target_col]
            and self.df[c].dtype != object
        ]

        print("Total features:", len(self.feature_cols))

        self.splitter = WalkForwardSplit()
        self.results  = []

    def run(self):

        folds, fold_info = self.splitter.split(self.df)

        print("\n============================")
        print("Walk-Forward Validation")
        print("============================")
        print("Total folds:", len(folds))
        print("\nFold boundaries preview:")
        print(fold_info.head())

        for fold_id, (train_idx, test_idx) in enumerate(folds):

            print("\n===================================")
            print(f"Running Fold {fold_id + 1}/{len(folds)}")
            print("===================================")

            model = self.model_factory()

            train_df = self.df.loc[train_idx]
            test_df  = self.df.loc[test_idx]

            X_train = train_df[self.feature_cols].copy()
            y_train = train_df[self.target_col]
            X_test  = test_df[self.feature_cols].copy()
            y_test  = test_df[self.target_col]

            # ---------------------------------------------------------
            # Store symbols BEFORE any transformation
            # ---------------------------------------------------------
            train_symbols = train_df["symbol"].values
            test_symbols  = test_df["symbol"].values

            # ---------------------------------------------------------
            # Clean inf/nan
            # ---------------------------------------------------------
            X_train = X_train.replace([np.inf, -np.inf], np.nan)
            X_test  = X_test.replace([np.inf, -np.inf], np.nan)
            medians = X_train.median()
            X_train = X_train.fillna(medians)
            X_test  = X_test.fillna(medians)

            y_train = y_train.replace([np.inf, -np.inf], np.nan).dropna()
            X_train = X_train.loc[y_train.index]
            train_symbols = train_df.loc[y_train.index, "symbol"].values

            y_test = y_test.replace([np.inf, -np.inf], np.nan).dropna()
            X_test = X_test.loc[y_test.index]
            test_symbols = test_df.loc[y_test.index, "symbol"].values

            # ---------------------------------------------------------
            # Feature selection (cached)
            # ---------------------------------------------------------
            print("selecting features...")
            fold_key       = fold_id + 1
            print("fold keys", fold_key)
            cached_features = load_features(fold_key)

            if cached_features is None:
                print("Running feature selection...")
                selector = FeatureSelector()
                X_train_sel   = selector.fit_transform(X_train, y_train)
                selected_features = list(X_train_sel.columns)
                save_features(fold_key, selected_features)
            else:
                print("Loaded cached features")
                selected_features = list(cached_features)

            # ---------------------------------------------------------
            # Stability filter
            # ---------------------------------------------------------
            from config.paths import FEATURE_STABILITY_FILE as STABILITY_PATH
            try:
                stability_df     = pd.read_csv(STABILITY_PATH)
                stable_features  = stability_df[
                    stability_df["frequency"] > 0.6
                ]["feature"].tolist()
                selected_features = [
                    f for f in selected_features if f in stable_features
                ]
                print("Stable features:", len(selected_features))
            except Exception:
                print("No stability filter applied")

            selected_features = sorted(selected_features)

            X_train_sel = X_train[selected_features].values.astype(np.float32)
            X_test_sel  = X_test[selected_features].values.astype(np.float32)

            print("Selected features:", len(selected_features))

            # ---------------------------------------------------------
            # Train — pass symbols so LSTM can group per stock
            # ---------------------------------------------------------
            is_lstm = hasattr(model, "window")

            if is_lstm:
                model.fit(X_train_sel, y_train.values, symbols=train_symbols)
            else:
                model.fit(X_train_sel, y_train.values)

            # ---------------------------------------------------------
            # Predict — pass symbols for LSTM alignment
            # ---------------------------------------------------------
            if is_lstm:
                preds, pred_indices = model.predict(
                    X_test_sel, symbols=test_symbols
                )
                # Align y_test to predicted indices
                y_test_aligned = y_test.iloc[pred_indices].values
            else:
                preds          = model.predict(X_test_sel)
                y_test_aligned = y_test.values

            # ---------------------------------------------------------
            # Safety check
            # ---------------------------------------------------------
            if len(preds) != len(y_test_aligned):
                raise ValueError(
                    f"Fold {fold_id+1}: prediction length {len(preds)} "
                    f"!= target length {len(y_test_aligned)}"
                )

            # ---------------------------------------------------------
            # Metrics
            # ---------------------------------------------------------
            rmse  = np.sqrt(mean_squared_error(y_test_aligned, preds))
            mae   = mean_absolute_error(y_test_aligned, preds)
            r2    = r2_score(y_test_aligned, preds)
            da    = directional_accuracy(y_test_aligned, preds)
            ic    = information_coefficient(y_test_aligned, preds)
            r2_os = out_of_sample_r2(y_test_aligned, preds, y_train.mean())

            sp_ic = spearman_ic(y_test_aligned, preds)
            sign_hr = sign_hit_rate(y_test_aligned, preds)
            pred_mean = float(np.mean(preds)) if len(preds) else np.nan
            pred_std = float(np.std(preds)) if len(preds) else np.nan
            actual_mean = float(np.mean(y_test_aligned)) if len(y_test_aligned) else np.nan
            actual_std = float(np.std(y_test_aligned)) if len(y_test_aligned) else np.nan

            print("IC:", ic)
            print("Spearman IC:", sp_ic)
            print("Sign Hit Rate:", sign_hr)

            self.results.append({
                "fold": fold_id + 1,
                "rmse": rmse,
                "mae": mae,
                "r2": r2,
                "directional_accuracy": da,
                "information_coefficient": ic,
                "spearman_ic": sp_ic,
                "sign_hit_rate": sign_hr,
                "pred_mean": pred_mean,
                "pred_std": pred_std,
                "actual_mean": actual_mean,
                "actual_std": actual_std,
                "n_preds": len(preds),
                "r2_out_of_sample": r2_os,
                "preds": json.dumps(preds.tolist()),
                "y_true": json.dumps(y_test_aligned.tolist())
            })

        # ---------------------------------------------------------
        # Aggregate
        # ---------------------------------------------------------
        self.results = pd.DataFrame(self.results)

        print("\n============================")
        print("Average Performance")
        print("============================")
        print(self.results.mean(numeric_only=True))

        ic_mean = self.results["information_coefficient"].mean()
        ic_std  = self.results["information_coefficient"].std()
        icir    = 0 if ic_std == 0 else ic_mean / ic_std

        print("\n============================")
        print("Signal Stability")
        print("============================")
        print("ICIR:", icir)

        

        output_path = WALKFORWARD_RESULTS_DIR / f"{self.model_name}_results.csv"
        self.results.to_csv(output_path, index=False)
        print(f"\nResults saved to: {output_path}")