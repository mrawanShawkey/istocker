"""
xgboost_tuner.py

Optuna-based hyperparameter tuning for XGBoostModel.

This version is adapted to your current walk-forward setup:
    - Dataset size: 106,888
    - Total features: 45
    - Total folds: 15
    - Baseline Avg IC: ~0.178
    - Baseline Avg Spearman IC: ~0.150
    - Baseline ICIR: ~1.207

What this script does:
    1. Loads the modeling dataset.
    2. Loads cached fold-specific features.
    3. Applies the same stability filtering logic used in validation.
    4. Tunes XGBoost on representative folds.
    5. Optimizes Spearman IC.
    6. Validates best params on all 15 folds.
    7. Saves tuned fold results and best params.

Usage:
    python -m ml.experiments.xgboost_tuner
"""

import json
import warnings

import numpy as np
import optuna
import pandas as pd
from scipy.stats import spearmanr

from ml.training.walk_forward_split import WalkForwardSplit
from ml.feature_selection.feature_cache import load_features
from ml.models.xgboost_model import XGBoostModel

from config.paths import (
    MODELING_DATASET_FILE,
    WALKFORWARD_BASELINE_DIR,
    FEATURE_STABILITY_FILE,
)

warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────
# Representative folds based on your latest 15-fold results
#
# 0  = Fold 1  | negative Spearman IC
# 1  = Fold 2  | strong positive
# 2  = Fold 3  | strong positive
# 5  = Fold 6  | negative / stress
# 8  = Fold 9  | weak positive
# 11 = Fold 12 | moderate positive
# 14 = Fold 15 | negative / stress
# ─────────────────────────────────────────────
TUNE_FOLDS = [0, 1, 2, 5, 8, 11, 14]


def load_data():
    """
    Load dataset and define numeric feature columns.
    """

    df = pd.read_csv(MODELING_DATASET_FILE)

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)

    target_col = "target_252d"

    feature_cols = [
        c for c in df.columns
        if c not in ["date", "symbol", target_col]
        and df[c].dtype != object
    ]

    print(f"Dataset size: {len(df)}")
    print(f"Total features: {len(feature_cols)}")

    return df, feature_cols, target_col


def load_stable_features():
    """
    Load globally stable features from FEATURE_STABILITY_FILE.

    If the file is missing or invalid, return None.
    """

    try:
        stability_df = pd.read_csv(FEATURE_STABILITY_FILE)

        stable_features = stability_df[
            stability_df["frequency"] > 0.6
        ]["feature"].tolist()

        if len(stable_features) == 0:
            print("Warning: stability file exists but no features passed frequency > 0.6")
            return None

        print(f"Global stable features loaded: {len(stable_features)}")
        return stable_features

    except Exception as e:
        print(f"Warning: could not load stable features: {e}")
        return None


def prepare_fold(
    df,
    feature_cols,
    target_col,
    train_idx,
    test_idx,
    fold_key,
    stable_features,
):
    """
    Prepare one walk-forward fold.

    Important:
        - Medians are calculated from train only.
        - Test is filled using train medians.
        - Cached feature selection is loaded per fold.
        - Stable feature filter is applied after cached feature loading.
    """

    train_df = df.loc[train_idx]
    test_df = df.loc[test_idx]

    X_train = train_df[feature_cols].copy()
    y_train = train_df[target_col].copy()

    X_test = test_df[feature_cols].copy()
    y_test = test_df[target_col].copy()

    # Replace infinity with NaN
    X_train = X_train.replace([np.inf, -np.inf], np.nan)
    X_test = X_test.replace([np.inf, -np.inf], np.nan)

    # Fill missing values using train medians only
    medians = X_train.median()
    X_train = X_train.fillna(medians)
    X_test = X_test.fillna(medians)

    # Clean target
    y_train = y_train.replace([np.inf, -np.inf], np.nan)
    y_test = y_test.replace([np.inf, -np.inf], np.nan)

    # Keep rows with valid target only
    valid_train = y_train.notna()
    valid_test = y_test.notna()

    X_train = X_train.loc[valid_train]
    y_train = y_train.loc[valid_train]

    X_test = X_test.loc[valid_test]
    y_test = y_test.loc[valid_test]

    # Load cached selected features for this fold
    cached = load_features(fold_key)

    if cached is not None:
        selected = list(cached)
    else:
        selected = list(feature_cols)

    # Apply stability filter
    if stable_features:
        selected = [f for f in selected if f in stable_features]

    # Keep only existing numeric columns
    selected = [f for f in selected if f in X_train.columns]

    selected = sorted(selected)

    if len(selected) == 0:
        raise ValueError(f"No selected features found for fold {fold_key}")

    X_tr = X_train[selected].values.astype(np.float32)
    X_te = X_test[selected].values.astype(np.float32)

    y_tr = y_train.values.astype(np.float32)
    y_te = y_test.values.astype(np.float32)

    return X_tr, y_tr, X_te, y_te, selected


def calculate_metrics(y_true, preds):
    """
    Calculate fold-level metrics.

    Main tuning metric:
        - Spearman IC

    Extra monitoring metrics:
        - Pearson IC
        - Sign Hit Rate
        - n_preds
    """

    mask = np.isfinite(y_true) & np.isfinite(preds)

    if mask.sum() < 5:
        return {
            "ic": np.nan,
            "spearman_ic": np.nan,
            "sign_hit_rate": np.nan,
            "n_preds": int(mask.sum()),
        }

    yt = y_true[mask]
    pr = preds[mask]

    ic = np.corrcoef(pr, yt)[0, 1]
    if not np.isfinite(ic):
        ic = np.nan

    spearman_ic = spearmanr(pr, yt).correlation
    if not np.isfinite(spearman_ic):
        spearman_ic = np.nan

    sign_hit_rate = np.mean(np.sign(pr) == np.sign(yt))

    return {
        "ic": float(ic) if np.isfinite(ic) else np.nan,
        "spearman_ic": float(spearman_ic) if np.isfinite(spearman_ic) else np.nan,
        "sign_hit_rate": float(sign_hit_rate),
        "n_preds": int(mask.sum()),
    }


def objective(trial, df, feature_cols, target_col, folds, stable_features):
    """
    Optuna objective.

    The objective returns average Spearman IC across representative folds.

    Pruning is enabled:
        After each representative fold, we report the running average.
        If the trial is clearly weak, Optuna can prune it.
    """

    params = {
        "n_estimators": trial.suggest_int("n_estimators", 150, 900),
        "max_depth": trial.suggest_int("max_depth", 2, 5),
        "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.08, log=True),
        "subsample": trial.suggest_float("subsample", 0.55, 0.95),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.55, 0.95),
        "min_child_weight": trial.suggest_int("min_child_weight", 3, 20),
        "gamma": trial.suggest_float("gamma", 0.0, 2.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.001, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 0.1, 20.0, log=True),

        "objective": "reg:squarederror",
        "eval_metric": "rmse",
        "tree_method": "hist",
        "random_state": 42,
        "n_jobs": -1,
    }

    fold_scores = []

    for step, fold_id in enumerate(TUNE_FOLDS):
        train_idx, test_idx = folds[fold_id]
        fold_key = fold_id + 1

        X_tr, y_tr, X_te, y_te, selected = prepare_fold(
            df=df,
            feature_cols=feature_cols,
            target_col=target_col,
            train_idx=train_idx,
            test_idx=test_idx,
            fold_key=fold_key,
            stable_features=stable_features,
        )

        model = XGBoostModel(params=params)
        model.fit(X_tr, y_tr)

        preds = model.predict(X_te)

        metrics = calculate_metrics(y_te, preds)

        fold_spearman = metrics["spearman_ic"]

        if np.isfinite(fold_spearman):
            fold_scores.append(fold_spearman)
        else:
            fold_scores.append(0.0)

        running_avg = float(np.mean(fold_scores))

        trial.report(running_avg, step=step)

        if trial.should_prune():
            raise optuna.TrialPruned()

    return float(np.mean(fold_scores))


def run_full_validation(best_params, df, feature_cols, target_col, folds, stable_features):
    """
    Validate best params on all 15 walk-forward folds.
    """

    results = []

    print("\n===================================")
    print("Full validation with best params")
    print("===================================")

    for fold_id in range(len(folds)):
        train_idx, test_idx = folds[fold_id]
        fold_key = fold_id + 1

        X_tr, y_tr, X_te, y_te, selected = prepare_fold(
            df=df,
            feature_cols=feature_cols,
            target_col=target_col,
            train_idx=train_idx,
            test_idx=test_idx,
            fold_key=fold_key,
            stable_features=stable_features,
        )

        model = XGBoostModel(params=best_params)
        model.fit(X_tr, y_tr)

        preds = model.predict(X_te)

        metrics = calculate_metrics(y_te, preds)

        print(
            f"Fold {fold_key:2d} | "
            f"Features: {len(selected):2d} | "
            f"IC: {metrics['ic']:.4f} | "
            f"Spearman IC: {metrics['spearman_ic']:.4f} | "
            f"Sign Hit Rate: {metrics['sign_hit_rate']:.4f} | "
            f"n: {metrics['n_preds']}"
        )

        results.append({
            "fold": fold_key,
            "n_features": len(selected),
            "ic": metrics["ic"],
            "spearman_ic": metrics["spearman_ic"],
            "sign_hit_rate": metrics["sign_hit_rate"],
            "n_preds": metrics["n_preds"],
        })

    results_df = pd.DataFrame(results)

    avg_ic = results_df["ic"].mean()
    std_ic = results_df["ic"].std()
    icir = avg_ic / std_ic if std_ic > 0 else 0.0

    avg_spearman = results_df["spearman_ic"].mean()
    std_spearman = results_df["spearman_ic"].std()
    spearman_icir = avg_spearman / std_spearman if std_spearman > 0 else 0.0

    negative_ic_folds = int((results_df["ic"] < 0).sum())
    negative_spearman_folds = int((results_df["spearman_ic"] < 0).sum())

    print("\n============================")
    print("Average Tuned Performance")
    print("============================")
    print(f"Avg IC:                 {avg_ic:.6f}")
    print(f"Avg Spearman IC:        {avg_spearman:.6f}")
    print(f"ICIR:                   {icir:.6f}")
    print(f"Spearman ICIR:          {spearman_icir:.6f}")
    print(f"Negative IC folds:      {negative_ic_folds}/{len(results_df)}")
    print(f"Negative Spearman folds:{negative_spearman_folds}/{len(results_df)}")

    return results_df, {
        "avg_ic": float(avg_ic),
        "avg_spearman_ic": float(avg_spearman),
        "icir": float(icir),
        "spearman_icir": float(spearman_icir),
        "negative_ic_folds": negative_ic_folds,
        "negative_spearman_folds": negative_spearman_folds,
    }


def main():
    print("Loading dataset...")
    df, feature_cols, target_col = load_data()

    stable_features = load_stable_features()

    print("\n============================")
    print("Walk-Forward Split")
    print("============================")

    splitter = WalkForwardSplit()
    folds, fold_info = splitter.split(df)
    folds = list(folds)

    print(f"Total folds: {len(folds)}")

    if len(folds) != 15:
        print(f"Warning: expected 15 folds, got {len(folds)}")

    print(f"Tuning folds: {[f + 1 for f in TUNE_FOLDS]}")

    if fold_info is not None:
        try:
            print("\nFold boundaries preview:")
            print(fold_info.head())
        except Exception:
            pass

    optuna.logging.set_verbosity(optuna.logging.WARNING)

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=42),
        pruner=optuna.pruners.MedianPruner(
            n_startup_trials=10,
            n_warmup_steps=2,
        ),
    )

    print("\n============================")
    print("Starting Optuna tuning")
    print("============================")

    study.optimize(
        lambda trial: objective(
            trial=trial,
            df=df,
            feature_cols=feature_cols,
            target_col=target_col,
            folds=folds,
            stable_features=stable_features,
        ),
        n_trials=60,
        show_progress_bar=True,
    )

    print("\n============================")
    print("Best Trial")
    print("============================")
    print(f"Best representative-fold Spearman IC: {study.best_value:.6f}")
    print("Best params:")

    for k, v in study.best_params.items():
        print(f"  {k}: {v}")

    best_params = {
        **study.best_params,
        "objective": "reg:squarederror",
        "eval_metric": "rmse",
        "tree_method": "hist",
        "random_state": 42,
        "n_jobs": -1,
    }

    results_df, summary = run_full_validation(
        best_params=best_params,
        df=df,
        feature_cols=feature_cols,
        target_col=target_col,
        folds=folds,
        stable_features=stable_features,
    )

    out_path = WALKFORWARD_BASELINE_DIR / "xgboost_tuned_results.csv"
    params_path = WALKFORWARD_BASELINE_DIR / "xgboost_best_params.json"
    summary_path = WALKFORWARD_BASELINE_DIR / "xgboost_tuned_summary.json"

    results_df.to_csv(out_path, index=False)

    with open(params_path, "w") as f:
        json.dump(best_params, f, indent=2)

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n============================")
    print("Saved")
    print("============================")
    print(f"Results saved to: {out_path}")
    print(f"Best params saved to: {params_path}")
    print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()