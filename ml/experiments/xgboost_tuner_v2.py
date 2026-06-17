"""
xgboost_tuner_v2.py

Robust Optuna tuning for XGBoostModel.

Goal:
    Tune XGBoost not only for high average Spearman IC,
    but also for stability across all 15 walk-forward folds.

Objective:
    robust_score = avg_spearman
                   - STD_PENALTY * std_spearman
                   - NEGATIVE_PENALTY * negative_fold_ratio

Usage:
    python -m ml.experiments.xgboost_tuner_v2
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
# Baseline / previous tuned reference
# ─────────────────────────────────────────────
BASELINE_AVG_IC = 0.178358
BASELINE_AVG_SPEARMAN = 0.149970
BASELINE_ICIR = 1.206694

PREVIOUS_TUNED_AVG_IC = 0.181379
PREVIOUS_TUNED_AVG_SPEARMAN = 0.154177
PREVIOUS_TUNED_ICIR = 1.346039


# ─────────────────────────────────────────────
# Robust objective weights
# ─────────────────────────────────────────────
STD_PENALTY = 0.25
NEGATIVE_PENALTY = 0.05


# ─────────────────────────────────────────────
# Fold order for tuning
#
# We put harder / previously weak folds early so pruning
# can stop weak trials faster.
#
# Fold IDs are 0-indexed:
#   0  = Fold 1
#   5  = Fold 6
#   12 = Fold 13
#   14 = Fold 15
# ─────────────────────────────────────────────
TUNING_FOLD_ORDER = [
    0,   # Fold 1  - weak/stress
    5,   # Fold 6  - weak/stress
    12,  # Fold 13 - weak/stress
    14,  # Fold 15 - stress
    8,   # Fold 9
    9,   # Fold 10
    10,  # Fold 11
    11,  # Fold 12
    1,   # Fold 2
    2,   # Fold 3
    3,   # Fold 4
    4,   # Fold 5
    6,   # Fold 7
    7,   # Fold 8
    13,  # Fold 14
]


N_TRIALS = 150


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

    print(f"Dataset size: {len(df)}")
    print(f"Total numeric features: {len(feature_cols)}")

    return df, feature_cols, target_col


def load_stable_features():
    try:
        stability_df = pd.read_csv(FEATURE_STABILITY_FILE)

        stable_features = stability_df[
            stability_df["frequency"] > 0.6
        ]["feature"].tolist()

        if len(stable_features) == 0:
            print("Warning: no features passed frequency > 0.6")
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
    train_df = df.loc[train_idx]
    test_df = df.loc[test_idx]

    X_train = train_df[feature_cols].copy()
    y_train = train_df[target_col].copy()

    X_test = test_df[feature_cols].copy()
    y_test = test_df[target_col].copy()

    # Clean feature values
    X_train = X_train.replace([np.inf, -np.inf], np.nan)
    X_test = X_test.replace([np.inf, -np.inf], np.nan)

    # Train-only medians
    medians = X_train.median()
    X_train = X_train.fillna(medians)
    X_test = X_test.fillna(medians)

    # Clean targets
    y_train = y_train.replace([np.inf, -np.inf], np.nan)
    y_test = y_test.replace([np.inf, -np.inf], np.nan)

    valid_train = y_train.notna()
    valid_test = y_test.notna()

    X_train = X_train.loc[valid_train]
    y_train = y_train.loc[valid_train]

    X_test = X_test.loc[valid_test]
    y_test = y_test.loc[valid_test]

    # Fold-specific cached features
    cached = load_features(fold_key)

    if cached is not None:
        selected = list(cached)
    else:
        selected = list(feature_cols)

    # Stability filter
    if stable_features:
        selected = [f for f in selected if f in stable_features]

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


def robust_score_from_spearman_scores(scores):
    scores = np.array(scores, dtype=float)
    scores = scores[np.isfinite(scores)]

    if len(scores) == 0:
        return -999.0, {
            "avg_spearman_ic": np.nan,
            "std_spearman_ic": np.nan,
            "spearman_icir": np.nan,
            "negative_spearman_folds": 999,
            "negative_fold_ratio": 1.0,
            "robust_score": -999.0,
        }

    avg_spearman = float(np.mean(scores))
    std_spearman = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0
    spearman_icir = avg_spearman / std_spearman if std_spearman > 0 else 0.0

    negative_folds = int(np.sum(scores < 0))
    negative_ratio = float(negative_folds / len(scores))

    robust_score = (
        avg_spearman
        - STD_PENALTY * std_spearman
        - NEGATIVE_PENALTY * negative_ratio
    )

    summary = {
        "avg_spearman_ic": avg_spearman,
        "std_spearman_ic": std_spearman,
        "spearman_icir": float(spearman_icir),
        "negative_spearman_folds": negative_folds,
        "negative_fold_ratio": negative_ratio,
        "robust_score": float(robust_score),
    }

    return float(robust_score), summary


def objective(trial, df, feature_cols, target_col, folds, stable_features):
    """
    Robust objective.

    This search space is intentionally more stability-focused than v1:
        - max_depth capped at 4
        - stronger regularization allowed
        - higher min_child_weight range
        - gamma can be larger
    """

    params = {
        "n_estimators": trial.suggest_int("n_estimators", 180, 750),
        "max_depth": trial.suggest_int("max_depth", 2, 4),
        "learning_rate": trial.suggest_float("learning_rate", 0.006, 0.06, log=True),
        "subsample": trial.suggest_float("subsample", 0.60, 0.95),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.50, 0.90),
        "min_child_weight": trial.suggest_int("min_child_weight", 8, 35),
        "gamma": trial.suggest_float("gamma", 0.0, 5.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.01, 25.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 2.0, 80.0, log=True),

        "objective": "reg:squarederror",
        "eval_metric": "rmse",
        "tree_method": "hist",
        "random_state": 42,
        "n_jobs": -1,
    }

    spearman_scores = []

    for step, fold_id in enumerate(TUNING_FOLD_ORDER):
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
            spearman_scores.append(fold_spearman)
        else:
            spearman_scores.append(0.0)

        current_score, current_summary = robust_score_from_spearman_scores(
            spearman_scores
        )

        trial.report(current_score, step=step)

        if step >= 5 and trial.should_prune():
            raise optuna.TrialPruned()

    final_score, final_summary = robust_score_from_spearman_scores(
        spearman_scores
    )

    trial.set_user_attr("avg_spearman_ic", final_summary["avg_spearman_ic"])
    trial.set_user_attr("std_spearman_ic", final_summary["std_spearman_ic"])
    trial.set_user_attr("spearman_icir", final_summary["spearman_icir"])
    trial.set_user_attr(
        "negative_spearman_folds",
        final_summary["negative_spearman_folds"],
    )
    trial.set_user_attr("robust_score", final_summary["robust_score"])

    return final_score


def run_full_validation(best_params, df, feature_cols, target_col, folds, stable_features):
    results = []

    print("\n===================================")
    print("Full validation with robust best params")
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

    avg_ic = float(results_df["ic"].mean())
    std_ic = float(results_df["ic"].std())
    icir = avg_ic / std_ic if std_ic > 0 else 0.0

    avg_spearman = float(results_df["spearman_ic"].mean())
    std_spearman = float(results_df["spearman_ic"].std())
    spearman_icir = avg_spearman / std_spearman if std_spearman > 0 else 0.0

    negative_ic_folds = int((results_df["ic"] < 0).sum())
    negative_spearman_folds = int((results_df["spearman_ic"] < 0).sum())

    robust_score, robust_summary = robust_score_from_spearman_scores(
        results_df["spearman_ic"].values
    )

    summary = {
        "avg_ic": avg_ic,
        "std_ic": std_ic,
        "icir": float(icir),
        "avg_spearman_ic": avg_spearman,
        "std_spearman_ic": std_spearman,
        "spearman_icir": float(spearman_icir),
        "negative_ic_folds": negative_ic_folds,
        "negative_spearman_folds": negative_spearman_folds,
        "robust_score": robust_score,
        "std_penalty": STD_PENALTY,
        "negative_penalty": NEGATIVE_PENALTY,
    }

    print("\n============================")
    print("Robust Tuned Performance")
    print("============================")
    print(f"Avg IC:                  {avg_ic:.6f}")
    print(f"Avg Spearman IC:         {avg_spearman:.6f}")
    print(f"ICIR:                    {icir:.6f}")
    print(f"Spearman ICIR:           {spearman_icir:.6f}")
    print(f"Negative IC folds:       {negative_ic_folds}/{len(results_df)}")
    print(f"Negative Spearman folds: {negative_spearman_folds}/{len(results_df)}")
    print(f"Robust Score:            {robust_score:.6f}")

    print("\n============================")
    print("Comparison")
    print("============================")
    print(f"Baseline Avg Spearman:       {BASELINE_AVG_SPEARMAN:.6f}")
    print(f"Previous Tuned Avg Spearman: {PREVIOUS_TUNED_AVG_SPEARMAN:.6f}")
    print(f"V2 Avg Spearman:             {avg_spearman:.6f}")
    print("")
    print(f"Baseline ICIR:               {BASELINE_ICIR:.6f}")
    print(f"Previous Tuned ICIR:         {PREVIOUS_TUNED_ICIR:.6f}")
    print(f"V2 Spearman ICIR:            {spearman_icir:.6f}")

    return results_df, summary


def save_trial_history(study, out_path):
    rows = []

    for trial in study.trials:
        row = {
            "number": trial.number,
            "state": str(trial.state),
            "value": trial.value,
            **trial.params,
            "avg_spearman_ic": trial.user_attrs.get("avg_spearman_ic"),
            "std_spearman_ic": trial.user_attrs.get("std_spearman_ic"),
            "spearman_icir": trial.user_attrs.get("spearman_icir"),
            "negative_spearman_folds": trial.user_attrs.get("negative_spearman_folds"),
            "robust_score": trial.user_attrs.get("robust_score"),
        }
        rows.append(row)

    pd.DataFrame(rows).to_csv(out_path, index=False)


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

    print(f"Tuning fold order: {[f + 1 for f in TUNING_FOLD_ORDER]}")

    if fold_info is not None:
        try:
            print("\nFold boundaries preview:")
            print(fold_info.head())
        except Exception:
            pass

    optuna.logging.set_verbosity(optuna.logging.WARNING)

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(
            seed=42,
            n_startup_trials=20,
            multivariate=True,
        ),
        pruner=optuna.pruners.MedianPruner(
            n_startup_trials=20,
            n_warmup_steps=5,
        ),
    )

    print("\n============================")
    print("Starting Robust Optuna Tuning V2")
    print("============================")
    print(f"Trials: {N_TRIALS}")
    print(f"STD_PENALTY: {STD_PENALTY}")
    print(f"NEGATIVE_PENALTY: {NEGATIVE_PENALTY}")

    study.optimize(
        lambda trial: objective(
            trial=trial,
            df=df,
            feature_cols=feature_cols,
            target_col=target_col,
            folds=folds,
            stable_features=stable_features,
        ),
        n_trials=N_TRIALS,
        show_progress_bar=True,
    )

    print("\n============================")
    print("Best Trial V2")
    print("============================")
    print(f"Best robust score: {study.best_value:.6f}")
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

    out_path = WALKFORWARD_BASELINE_DIR / "xgboost_tuned_v2_results.csv"
    params_path = WALKFORWARD_BASELINE_DIR / "xgboost_best_params_v2.json"
    summary_path = WALKFORWARD_BASELINE_DIR / "xgboost_tuned_v2_summary.json"
    trials_path = WALKFORWARD_BASELINE_DIR / "xgboost_tuned_v2_trials.csv"

    results_df.to_csv(out_path, index=False)

    with open(params_path, "w", encoding="utf-8") as f:
        json.dump(best_params, f, indent=2)

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    save_trial_history(study, trials_path)

    print("\n============================")
    print("Saved")
    print("============================")
    print(f"Results saved to: {out_path}")
    print(f"Best params saved to: {params_path}")
    print(f"Summary saved to: {summary_path}")
    print(f"Trials saved to: {trials_path}")


if __name__ == "__main__":
    main()