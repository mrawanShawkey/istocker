"""
xgboost_tuner.py

Optuna-based hyperparameter tuning for XGBoostModel.
Tunes on 5 representative folds, validates winner on all 20.

Usage:
    python -m ml.experiments.xgboost_tuner
"""

import numpy as np
import pandas as pd
import json
import optuna
from scipy.stats import spearmanr

from ml.training.walk_forward_split import WalkForwardSplit
from ml.feature_selection.feature_cache import load_features
from ml.models.xgboost_model import XGBoostModel

from config.paths import (
    MODELING_DATASET_FILE,
    WALKFORWARD_RESULTS_DIR,
    FEATURE_STABILITY_FILE
)

# ─────────────────────────────────────────────
# Representative folds — cover different regimes
#   F1  (strong positive IC ~0.45)
#   F6  (moderate positive ~0.34)
#   F9  (moderate positive ~0.25)
#   F12 (strong positive ~0.42)
#   F13 (negative IC ~-0.10)  ← stress fold
# ─────────────────────────────────────────────
TUNE_FOLDS = [0, 5, 8, 11, 12]   # 0-indexed


def load_data():
    df = pd.read_csv(MODELING_DATASET_FILE)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
    target_col = "target_252d"
    feature_cols = [
        c for c in df.columns
        if c not in ["date", "symbol", target_col]
        and df[c].dtype != object
    ]
    return df, feature_cols, target_col


def load_stable_features():
    try:
        stability_df = pd.read_csv(FEATURE_STABILITY_FILE)
        return stability_df[stability_df["frequency"] > 0.6]["feature"].tolist()
    except Exception:
        return None


def prepare_fold(df, feature_cols, target_col, train_idx, test_idx,
                fold_key, stable_features):
    train_df = df.loc[train_idx]
    test_df  = df.loc[test_idx]

    X_train = train_df[feature_cols].copy()
    y_train = train_df[target_col]
    X_test  = test_df[feature_cols].copy()
    y_test  = test_df[target_col]

    # Clean
    X_train = X_train.replace([np.inf, -np.inf], np.nan)
    X_test  = X_test.replace([np.inf, -np.inf], np.nan)
    medians = X_train.median()
    X_train = X_train.fillna(medians)
    X_test  = X_test.fillna(medians)

    y_train = y_train.replace([np.inf, -np.inf], np.nan).dropna()
    X_train = X_train.loc[y_train.index]
    y_test  = y_test.replace([np.inf, -np.inf], np.nan).dropna()
    X_test  = X_test.loc[y_test.index]

    # Feature selection (cached)
    cached = load_features(fold_key)
    selected = list(cached) if cached is not None else list(feature_cols)

    # Stability filter
    if stable_features:
        selected = [f for f in selected if f in stable_features]

    selected = sorted(selected)

    X_tr = X_train[selected].values.astype(np.float32)
    X_te = X_test[selected].values.astype(np.float32)
    return X_tr, y_train.values, X_te, y_test.values


def evaluate_params(params, df, feature_cols, target_col,
                    folds, fold_indices, stable_features):
    """Run params on the given fold indices, return avg IC."""
    ics = []
    for fold_id in fold_indices:
        train_idx, test_idx = folds[fold_id]
        fold_key = fold_id + 1

        X_tr, y_tr, X_te, y_te = prepare_fold(
            df, feature_cols, target_col,
            train_idx, test_idx, fold_key, stable_features
        )

        model = XGBoostModel(params=params)
        model.fit(X_tr, y_tr)
        preds = model.predict(X_te)

        mask = np.isfinite(y_te) & np.isfinite(preds)
        if mask.sum() < 5:
            ics.append(0.0)
            continue

        ic = np.corrcoef(preds[mask], y_te[mask])[0, 1]
        ics.append(ic if np.isfinite(ic) else 0.0)

    return float(np.mean(ics))


def objective(trial, df, feature_cols, target_col,
            folds, stable_features):

    params = {
        "n_estimators":       500,          # early stopping handles actual count
        "max_depth":          trial.suggest_int("max_depth", 2, 5),
        "learning_rate":      trial.suggest_float("learning_rate", 0.01, 0.10, log=True),
        "subsample":          trial.suggest_float("subsample", 0.5, 0.9),
        "colsample_bytree":   trial.suggest_float("colsample_bytree", 0.5, 0.9),
        "reg_alpha":          trial.suggest_float("reg_alpha", 0.01, 5.0, log=True),
        "reg_lambda":         trial.suggest_float("reg_lambda", 0.1, 5.0, log=True),
        "min_child_weight":   trial.suggest_int("min_child_weight", 3, 15),
        "random_state":       42,
        "eval_metric":        "rmse",
        "early_stopping_rounds": 30,
    }

    avg_ic = evaluate_params(
        params, df, feature_cols, target_col,
        folds, TUNE_FOLDS, stable_features
    )

    return avg_ic


def run_full_validation(best_params, df, feature_cols, target_col,
                        folds, stable_features):
    """Run all 20 folds with the best params."""
    all_fold_ids = list(range(len(folds)))
    results = []

    print("\n=== Full 20-fold validation with best params ===")
    for fold_id in all_fold_ids:
        train_idx, test_idx = folds[fold_id]
        fold_key = fold_id + 1

        X_tr, y_tr, X_te, y_te = prepare_fold(
            df, feature_cols, target_col,
            train_idx, test_idx, fold_key, stable_features
        )

        model = XGBoostModel(params=best_params)
        model.fit(X_tr, y_tr)
        preds = model.predict(X_te)

        mask = np.isfinite(y_te) & np.isfinite(preds)
        ic = np.corrcoef(preds[mask], y_te[mask])[0, 1] if mask.sum() >= 5 else np.nan
        sp_ic = spearmanr(preds[mask], y_te[mask]).correlation if mask.sum() >= 5 else np.nan

        print(f"Fold {fold_key:2d} | IC: {ic:.4f} | Spearman IC: {sp_ic:.4f}")
        results.append({
            "fold": fold_key,
            "ic": ic,
            "spearman_ic": sp_ic,
            "n_preds": int(mask.sum())
        })

    results_df = pd.DataFrame(results)
    avg_ic  = results_df["ic"].mean()
    ic_std  = results_df["ic"].std()
    icir    = avg_ic / ic_std if ic_std > 0 else 0
    avg_sic = results_df["spearman_ic"].mean()
    neg_folds = (results_df["ic"] < 0).sum()

    print(f"\n{'='*40}")
    print(f"Avg IC:          {avg_ic:.4f}")
    print(f"Avg Spearman IC: {avg_sic:.4f}")
    print(f"ICIR:            {icir:.4f}")
    print(f"Negative folds:  {neg_folds}/20")
    print(f"{'='*40}")

    return results_df, avg_ic, icir


def main():
    print("Loading data...")
    df, feature_cols, target_col = load_data()
    stable_features = load_stable_features()

    splitter = WalkForwardSplit()
    folds, fold_info = splitter.split(df)
    folds = list(folds)

    print(f"Total folds: {len(folds)}")
    print(f"Tuning on folds: {[f+1 for f in TUNE_FOLDS]}")

    # Silence Optuna's per-trial logs — only show progress
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=42),
        pruner=optuna.pruners.MedianPruner(n_warmup_steps=10)
    )

    print("\nStarting Optuna search (50 trials)...")
    study.optimize(
        lambda trial: objective(
            trial, df, feature_cols, target_col, folds, stable_features
        ),
        n_trials=50,
        show_progress_bar=True
    )

    print(f"\nBest trial IC (on 5 folds): {study.best_value:.4f}")
    print("Best params:")
    for k, v in study.best_params.items():
        print(f"  {k}: {v}")

    # Add fixed params back
    best_params = {
        **study.best_params,
        "n_estimators": 500,
        "random_state": 42,
        "eval_metric": "rmse",
        "early_stopping_rounds": 30,
    }

    # Full validation
    results_df, avg_ic, icir = run_full_validation(
        best_params, df, feature_cols, target_col, folds, stable_features
    )

    # Save
    out_path = WALKFORWARD_RESULTS_DIR / "xgboost_tuned_results.csv"
    results_df.to_csv(out_path, index=False)

    params_path = WALKFORWARD_RESULTS_DIR / "xgboost_best_params.json"
    with open(params_path, "w") as f:
        json.dump(best_params, f, indent=2)

    print(f"\nResults saved to: {out_path}")
    print(f"Best params saved to: {params_path}")


if __name__ == "__main__":
    main()