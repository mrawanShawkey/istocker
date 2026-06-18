"""
xgboost_tuner_v3.py

V3 Optuna tuning for XGBoostModel.

Main changes vs V1/V2:
    1. Tunes feature stability threshold.
    2. Uses per-date cross-sectional Spearman IC.
    3. Optimizes a robust score based on:
        - average per-date Spearman IC
        - fold stability
        - negative folds
    4. Keeps early stopping active through XGBoostModel.fit(),
       which already passes eval_set internally.

Usage:
    python -m ml.experiments.xgboost_tuner_v3
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


N_TRIALS = 180

STD_PENALTY = 0.20
NEGATIVE_PENALTY = 0.04
MIN_DATE_STOCKS = 5

TUNING_FOLD_ORDER = [
    0,   # Fold 1
    5,   # Fold 6
    12,  # Fold 13
    14,  # Fold 15
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


def load_data():
    df = pd.read_csv(MODELING_DATASET_FILE)

    df["date"] = pd.to_datetime(df["date"])

    # Important for internal validation split inside XGBoostModel.fit()
    df = df.sort_values(["date", "symbol"]).reset_index(drop=True)

    target_col = "target_252d"

    feature_cols = [
        c for c in df.columns
        if c not in ["date", "symbol", target_col]
        and df[c].dtype != object
    ]

    print(f"Dataset size: {len(df)}")
    print(f"Total numeric features: {len(feature_cols)}")

    return df, feature_cols, target_col


def load_feature_stability_scores():
    stability_df = pd.read_csv(FEATURE_STABILITY_FILE)

    if "feature" not in stability_df.columns or "frequency" not in stability_df.columns:
        raise ValueError("FEATURE_STABILITY_FILE must contain: feature, frequency")

    scores = dict(zip(stability_df["feature"], stability_df["frequency"]))

    print(f"Loaded feature stability scores: {len(scores)}")

    return scores


def prepare_fold(
    df,
    feature_cols,
    target_col,
    train_idx,
    test_idx,
    fold_key,
    stability_scores,
    stability_threshold,
):
    train_df = (
        df.loc[train_idx]
        .sort_values(["date", "symbol"])
        .reset_index(drop=True)
    )

    test_df = (
        df.loc[test_idx]
        .sort_values(["date", "symbol"])
        .reset_index(drop=True)
    )

    X_train = train_df[feature_cols].copy()
    y_train = train_df[target_col].copy()

    X_test = test_df[feature_cols].copy()
    y_test = test_df[target_col].copy()
    test_dates = test_df["date"].copy()

    X_train = X_train.replace([np.inf, -np.inf], np.nan)
    X_test = X_test.replace([np.inf, -np.inf], np.nan)

    medians = X_train.median()
    X_train = X_train.fillna(medians)
    X_test = X_test.fillna(medians)

    y_train = y_train.replace([np.inf, -np.inf], np.nan)
    y_test = y_test.replace([np.inf, -np.inf], np.nan)

    valid_train = y_train.notna()
    valid_test = y_test.notna()

    X_train = X_train.loc[valid_train]
    y_train = y_train.loc[valid_train]

    X_test = X_test.loc[valid_test]
    y_test = y_test.loc[valid_test]
    test_dates = test_dates.loc[valid_test]

    cached = load_features(fold_key)

    if cached is not None:
        selected = list(cached)
    else:
        selected = list(feature_cols)

    selected = [
        f for f in selected
        if f in X_train.columns
        and stability_scores.get(f, 0) >= stability_threshold
    ]

    selected = sorted(selected)

    if len(selected) < 3:
        raise ValueError(
            f"Too few features for fold {fold_key} at threshold {stability_threshold}"
        )

    X_tr = X_train[selected].values.astype(np.float32)
    X_te = X_test[selected].values.astype(np.float32)

    y_tr = y_train.values.astype(np.float32)
    y_te = y_test.values.astype(np.float32)

    dates_te = pd.to_datetime(test_dates.values)

    return X_tr, y_tr, X_te, y_te, dates_te, selected


def per_date_spearman_ic(y_true, preds, dates):
    temp = pd.DataFrame({
        "date": dates,
        "y": y_true,
        "pred": preds,
    })

    date_ics = []

    for _, g in temp.groupby("date"):
        if len(g) < MIN_DATE_STOCKS:
            continue

        if g["y"].nunique() < 2 or g["pred"].nunique() < 2:
            continue

        ic = spearmanr(g["pred"], g["y"]).correlation

        if np.isfinite(ic):
            date_ics.append(ic)

    if len(date_ics) == 0:
        return np.nan, np.nan, 0

    return (
        float(np.mean(date_ics)),
        float(np.std(date_ics, ddof=1)) if len(date_ics) > 1 else 0.0,
        int(len(date_ics)),
    )


def calculate_metrics(y_true, preds, dates):
    mask = np.isfinite(y_true) & np.isfinite(preds)

    if mask.sum() < 5:
        return {
            "ic": np.nan,
            "global_spearman_ic": np.nan,
            "date_spearman_ic": np.nan,
            "date_spearman_std": np.nan,
            "n_dates": 0,
            "sign_hit_rate": np.nan,
            "n_preds": int(mask.sum()),
        }

    yt = y_true[mask]
    pr = preds[mask]
    dt = dates[mask]

    ic = np.corrcoef(pr, yt)[0, 1]
    if not np.isfinite(ic):
        ic = np.nan

    global_spearman = spearmanr(pr, yt).correlation
    if not np.isfinite(global_spearman):
        global_spearman = np.nan

    date_ic, date_ic_std, n_dates = per_date_spearman_ic(yt, pr, dt)

    sign_hit_rate = np.mean(np.sign(pr) == np.sign(yt))

    return {
        "ic": float(ic) if np.isfinite(ic) else np.nan,
        "global_spearman_ic": float(global_spearman) if np.isfinite(global_spearman) else np.nan,
        "date_spearman_ic": float(date_ic) if np.isfinite(date_ic) else np.nan,
        "date_spearman_std": float(date_ic_std) if np.isfinite(date_ic_std) else np.nan,
        "n_dates": int(n_dates),
        "sign_hit_rate": float(sign_hit_rate),
        "n_preds": int(mask.sum()),
    }


def robust_score_from_fold_scores(scores):
    scores = np.array(scores, dtype=float)
    scores = scores[np.isfinite(scores)]

    if len(scores) == 0:
        return -999.0, {}

    avg_score = float(np.mean(scores))
    std_score = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0
    negative_folds = int(np.sum(scores < 0))
    negative_ratio = negative_folds / len(scores)

    robust_score = (
        avg_score
        - STD_PENALTY * std_score
        - NEGATIVE_PENALTY * negative_ratio
    )

    summary = {
        "avg_date_spearman_ic": avg_score,
        "std_date_spearman_ic": std_score,
        "date_spearman_icir": avg_score / std_score if std_score > 0 else 0.0,
        "negative_date_spearman_folds": negative_folds,
        "negative_fold_ratio": negative_ratio,
        "robust_score": float(robust_score),
    }

    return float(robust_score), summary


def objective(trial, df, feature_cols, target_col, folds, stability_scores):
    stability_threshold = trial.suggest_categorical(
        "stability_threshold",
        [0.45, 0.50, 0.55, 0.60, 0.65, 0.70],
    )

    params = {
        "n_estimators": trial.suggest_int("n_estimators", 600, 1600),
        "max_depth": trial.suggest_int("max_depth", 2, 5),
        "learning_rate": trial.suggest_float("learning_rate", 0.004, 0.05, log=True),
        "subsample": trial.suggest_float("subsample", 0.55, 0.95),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.45, 0.95),
        "min_child_weight": trial.suggest_int("min_child_weight", 5, 40),
        "gamma": trial.suggest_float("gamma", 0.0, 6.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.001, 30.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1.0, 100.0, log=True),
        "early_stopping_rounds": trial.suggest_categorical(
            "early_stopping_rounds",
            [20, 30, 50, 80],
        ),

        "objective": "reg:squarederror",
        "eval_metric": "rmse",
        "tree_method": "hist",
        "random_state": 42,
        "n_jobs": -1,
    }

    fold_scores = []

    for step, fold_id in enumerate(TUNING_FOLD_ORDER):
        train_idx, test_idx = folds[fold_id]
        fold_key = fold_id + 1

        try:
            X_tr, y_tr, X_te, y_te, dates_te, selected = prepare_fold(
                df=df,
                feature_cols=feature_cols,
                target_col=target_col,
                train_idx=train_idx,
                test_idx=test_idx,
                fold_key=fold_key,
                stability_scores=stability_scores,
                stability_threshold=stability_threshold,
            )
        except ValueError:
            fold_scores.append(-0.20)
            continue

        model = XGBoostModel(params=params)
        model.fit(X_tr, y_tr)

        preds = model.predict(X_te)

        metrics = calculate_metrics(y_te, preds, dates_te)

        fold_score = metrics["date_spearman_ic"]

        if np.isfinite(fold_score):
            fold_scores.append(fold_score)
        else:
            fold_scores.append(-0.20)

        current_score, _ = robust_score_from_fold_scores(fold_scores)

        trial.report(current_score, step=step)

        if step >= 5 and trial.should_prune():
            raise optuna.TrialPruned()

    final_score, summary = robust_score_from_fold_scores(fold_scores)

    trial.set_user_attr("avg_date_spearman_ic", summary.get("avg_date_spearman_ic"))
    trial.set_user_attr("std_date_spearman_ic", summary.get("std_date_spearman_ic"))
    trial.set_user_attr("date_spearman_icir", summary.get("date_spearman_icir"))
    trial.set_user_attr(
        "negative_date_spearman_folds",
        summary.get("negative_date_spearman_folds"),
    )
    trial.set_user_attr("robust_score", summary.get("robust_score"))

    return final_score


def run_full_validation(best_params, df, feature_cols, target_col, folds, stability_scores):
    stability_threshold = best_params.pop("stability_threshold")

    results = []

    print("\n===================================")
    print("Full validation with V3 best params")
    print("===================================")
    print(f"Best stability threshold: {stability_threshold}")

    for fold_id in range(len(folds)):
        train_idx, test_idx = folds[fold_id]
        fold_key = fold_id + 1

        X_tr, y_tr, X_te, y_te, dates_te, selected = prepare_fold(
            df=df,
            feature_cols=feature_cols,
            target_col=target_col,
            train_idx=train_idx,
            test_idx=test_idx,
            fold_key=fold_key,
            stability_scores=stability_scores,
            stability_threshold=stability_threshold,
        )

        model = XGBoostModel(params=best_params)
        model.fit(X_tr, y_tr)

        preds = model.predict(X_te)

        metrics = calculate_metrics(y_te, preds, dates_te)

        print(
            f"Fold {fold_key:2d} | "
            f"Features: {len(selected):2d} | "
            f"IC: {metrics['ic']:.4f} | "
            f"Global Spearman: {metrics['global_spearman_ic']:.4f} | "
            f"Date Spearman: {metrics['date_spearman_ic']:.4f} | "
            f"Dates: {metrics['n_dates']} | "
            f"n: {metrics['n_preds']}"
        )

        results.append({
            "fold": fold_key,
            "n_features": len(selected),
            "ic": metrics["ic"],
            "global_spearman_ic": metrics["global_spearman_ic"],
            "date_spearman_ic": metrics["date_spearman_ic"],
            "date_spearman_std": metrics["date_spearman_std"],
            "n_dates": metrics["n_dates"],
            "sign_hit_rate": metrics["sign_hit_rate"],
            "n_preds": metrics["n_preds"],
        })

    results_df = pd.DataFrame(results)

    fold_scores = results_df["date_spearman_ic"].values
    robust_score, robust_summary = robust_score_from_fold_scores(fold_scores)

    summary = {
        "avg_ic": float(results_df["ic"].mean()),
        "avg_global_spearman_ic": float(results_df["global_spearman_ic"].mean()),
        "avg_date_spearman_ic": float(results_df["date_spearman_ic"].mean()),
        "std_date_spearman_ic": float(results_df["date_spearman_ic"].std()),
        "date_spearman_icir": (
            float(results_df["date_spearman_ic"].mean() / results_df["date_spearman_ic"].std())
            if results_df["date_spearman_ic"].std() > 0 else 0.0
        ),
        "negative_date_spearman_folds": int((results_df["date_spearman_ic"] < 0).sum()),
        "robust_score": robust_score,
        "stability_threshold": stability_threshold,
        "best_params": best_params,
    }

    print("\n============================")
    print("V3 Tuned Performance")
    print("============================")
    print(f"Avg IC:                    {summary['avg_ic']:.6f}")
    print(f"Avg Global Spearman IC:    {summary['avg_global_spearman_ic']:.6f}")
    print(f"Avg Date Spearman IC:      {summary['avg_date_spearman_ic']:.6f}")
    print(f"Date Spearman ICIR:        {summary['date_spearman_icir']:.6f}")
    print(f"Negative Date folds:       {summary['negative_date_spearman_folds']}/{len(results_df)}")
    print(f"Robust Score:              {summary['robust_score']:.6f}")

    final_params_to_save = {
        **best_params,
        "stability_threshold": stability_threshold,
    }

    return results_df, summary, final_params_to_save


def save_trial_history(study, out_path):
    rows = []

    for trial in study.trials:
        row = {
            "number": trial.number,
            "state": str(trial.state),
            "value": trial.value,
            **trial.params,
            "avg_date_spearman_ic": trial.user_attrs.get("avg_date_spearman_ic"),
            "std_date_spearman_ic": trial.user_attrs.get("std_date_spearman_ic"),
            "date_spearman_icir": trial.user_attrs.get("date_spearman_icir"),
            "negative_date_spearman_folds": trial.user_attrs.get("negative_date_spearman_folds"),
            "robust_score": trial.user_attrs.get("robust_score"),
        }
        rows.append(row)

    pd.DataFrame(rows).to_csv(out_path, index=False)


def main():
    print("Loading dataset...")
    df, feature_cols, target_col = load_data()

    stability_scores = load_feature_stability_scores()

    splitter = WalkForwardSplit()
    folds, fold_info = splitter.split(df)
    folds = list(folds)

    print("\n============================")
    print("Walk-Forward Split")
    print("============================")
    print(f"Total folds: {len(folds)}")

    if len(folds) != 15:
        print(f"Warning: expected 15 folds, got {len(folds)}")

    print(f"Tuning fold order: {[f + 1 for f in TUNING_FOLD_ORDER]}")

    optuna.logging.set_verbosity(optuna.logging.WARNING)

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(
            seed=42,
            n_startup_trials=25,
            multivariate=True,
        ),
        pruner=optuna.pruners.MedianPruner(
            n_startup_trials=25,
            n_warmup_steps=5,
        ),
    )

    print("\n============================")
    print("Starting XGBoost Tuning V3")
    print("============================")
    print(f"Trials: {N_TRIALS}")

    study.optimize(
        lambda trial: objective(
            trial=trial,
            df=df,
            feature_cols=feature_cols,
            target_col=target_col,
            folds=folds,
            stability_scores=stability_scores,
        ),
        n_trials=N_TRIALS,
        show_progress_bar=True,
    )

    print("\n============================")
    print("Best Trial V3")
    print("============================")
    print(f"Best robust score: {study.best_value:.6f}")

    best_params = {
        **study.best_params,
        "objective": "reg:squarederror",
        "eval_metric": "rmse",
        "tree_method": "hist",
        "random_state": 42,
        "n_jobs": -1,
    }

    print("Best params:")
    for k, v in best_params.items():
        print(f"  {k}: {v}")

    results_df, summary, final_params_to_save = run_full_validation(
        best_params=best_params.copy(),
        df=df,
        feature_cols=feature_cols,
        target_col=target_col,
        folds=folds,
        stability_scores=stability_scores,
    )

    out_path = WALKFORWARD_BASELINE_DIR / "xgboost_tuned_v3_results.csv"
    params_path = WALKFORWARD_BASELINE_DIR / "xgboost_best_params_v3.json"
    summary_path = WALKFORWARD_BASELINE_DIR / "xgboost_tuned_v3_summary.json"
    trials_path = WALKFORWARD_BASELINE_DIR / "xgboost_tuned_v3_trials.csv"

    results_df.to_csv(out_path, index=False)

    with open(params_path, "w", encoding="utf-8") as f:
        json.dump(final_params_to_save, f, indent=2)

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