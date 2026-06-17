"""
xgboost_backtest.py

Lightweight portfolio backtest for tuned XGBoost model.

Strategy:
    For each walk-forward test fold:
        1. Train XGBoost using selected V1 params.
        2. Predict target_252d on the test fold.
        3. Rank stocks by prediction.
        4. Buy Top 20%.
        5. Compare against:
            - Equal-weight universe
            - Bottom 20%
            - Top - Bottom spread

Usage:
    python -m ml.experiments.xgboost_backtest
"""

import json
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ml.training.walk_forward_split import WalkForwardSplit
from ml.feature_selection.feature_cache import load_features
from ml.models.xgboost_model import XGBoostModel

from config.paths import (
    MODELING_DATASET_FILE,
    WALKFORWARD_BASELINE_DIR,
    FEATURE_STABILITY_FILE,
)

warnings.filterwarnings("ignore")


# =====================================================
# Selected final tuning version: V1
# =====================================================
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


# =====================================================
# Backtest settings
# =====================================================
TOP_FRAC = 0.20
BOTTOM_FRAC = 0.20

# Recommended for target_252d:
#   "FOLD_START" = one clean 1-year holding decision per fold
#   "MONTHLY"    = more observations, but overlapping 1-year forward returns
REBALANCE_MODE = "FOLD_START"

# Optional transaction cost assumption.
# 0.001 = 10 bps = 0.10%
TRANSACTION_COST = 0.001

OUT_DIR = WALKFORWARD_BASELINE_DIR / "xgboost_backtest"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    df = pd.read_csv(MODELING_DATASET_FILE)

    df["date"] = pd.to_datetime(df["date"])
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


def load_stable_features():
    stability_df = pd.read_csv(FEATURE_STABILITY_FILE)

    stable_features = stability_df[
        stability_df["frequency"] > 0.6
    ]["feature"].tolist()

    return stable_features


def prepare_fold(
    df,
    feature_cols,
    target_col,
    train_idx,
    test_idx,
    fold_key,
    stable_features,
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
    test_symbols = test_df["symbol"].copy()

    # Clean features
    X_train = X_train.replace([np.inf, -np.inf], np.nan)
    X_test = X_test.replace([np.inf, -np.inf], np.nan)

    # Train-only medians
    medians = X_train.median()
    X_train = X_train.fillna(medians)
    X_test = X_test.fillna(medians)

    # Clean target
    y_train = y_train.replace([np.inf, -np.inf], np.nan)
    y_test = y_test.replace([np.inf, -np.inf], np.nan)

    valid_train = y_train.notna()
    valid_test = y_test.notna()

    X_train = X_train.loc[valid_train]
    y_train = y_train.loc[valid_train]

    X_test = X_test.loc[valid_test]
    y_test = y_test.loc[valid_test]
    test_dates = test_dates.loc[valid_test]
    test_symbols = test_symbols.loc[valid_test]

    # Fold-specific cached selected features
    cached = load_features(fold_key)

    if cached is not None:
        selected = list(cached)
    else:
        selected = list(feature_cols)

    # Stability filter
    selected = [f for f in selected if f in stable_features]
    selected = [f for f in selected if f in X_train.columns]
    selected = sorted(selected)

    if len(selected) == 0:
        raise ValueError(f"No selected features found for fold {fold_key}")

    X_tr = X_train[selected].values.astype(np.float32)
    X_te = X_test[selected].values.astype(np.float32)

    y_tr = y_train.values.astype(np.float32)
    y_te = y_test.values.astype(np.float32)

    meta_test = pd.DataFrame({
        "date": pd.to_datetime(test_dates.values),
        "symbol": test_symbols.values,
        "actual_return": y_te,
    })

    return X_tr, y_tr, X_te, meta_test, selected


def apply_rebalance_filter(pred_df, mode):
    pred_df = pred_df.copy()
    pred_df["date"] = pd.to_datetime(pred_df["date"])

    if mode == "ALL_DATES":
        return pred_df

    if mode == "FOLD_START":
        # First rebalance date inside each walk-forward fold
        first_dates = pred_df.groupby("fold")["date"].transform("min")
        return pred_df[pred_df["date"] == first_dates].copy()

    if mode == "MONTHLY":
        pred_df["period"] = pred_df["date"].dt.to_period("M")
        first_dates = pred_df.groupby(["fold", "period"])["date"].transform("min")
        out = pred_df[pred_df["date"] == first_dates].copy()
        return out.drop(columns=["period"])

    raise ValueError(f"Unknown REBALANCE_MODE: {mode}")

def calculate_turnover(current_symbols, previous_symbols):
    if previous_symbols is None:
        return 1.0

    current_symbols = set(current_symbols)
    previous_symbols = set(previous_symbols)

    if len(current_symbols) == 0:
        return 0.0

    overlap = len(current_symbols.intersection(previous_symbols))
    turnover = 1 - (overlap / len(current_symbols))

    return float(turnover)


def backtest_predictions(pred_df):
    pred_df = pred_df.copy()
    pred_df = apply_rebalance_filter(pred_df, REBALANCE_MODE)

    rows = []
    previous_top_symbols = None
    previous_bottom_symbols = None

    for date, g in pred_df.groupby("date"):
        g = g.dropna(subset=["prediction", "actual_return"]).copy()

        if len(g) < 5:
            continue

        g = g.sort_values("prediction", ascending=False)

        top_n = max(1, int(np.floor(len(g) * TOP_FRAC)))
        bottom_n = max(1, int(np.floor(len(g) * BOTTOM_FRAC)))

        top = g.head(top_n)
        bottom = g.tail(bottom_n)

        top_symbols = top["symbol"].tolist()
        bottom_symbols = bottom["symbol"].tolist()

        top_turnover = calculate_turnover(top_symbols, previous_top_symbols)
        bottom_turnover = calculate_turnover(bottom_symbols, previous_bottom_symbols)

        previous_top_symbols = top_symbols
        previous_bottom_symbols = bottom_symbols

        top_return = top["actual_return"].mean()
        bottom_return = bottom["actual_return"].mean()
        benchmark_return = g["actual_return"].mean()

        active_return = top_return - benchmark_return
        long_short_spread = top_return - bottom_return

        # Simple cost adjustment
        top_return_after_cost = top_return - (TRANSACTION_COST * top_turnover)
        active_after_cost = top_return_after_cost - benchmark_return

        long_short_after_cost = long_short_spread - (
            TRANSACTION_COST * top_turnover
            + TRANSACTION_COST * bottom_turnover
        )

        rows.append({
            "date": date,
            "n_stocks": len(g),
            "top_n": top_n,
            "bottom_n": bottom_n,

            "top_return": top_return,
            "bottom_return": bottom_return,
            "benchmark_return": benchmark_return,

            "active_return": active_return,
            "long_short_spread": long_short_spread,

            "top_turnover": top_turnover,
            "bottom_turnover": bottom_turnover,

            "top_return_after_cost": top_return_after_cost,
            "active_after_cost": active_after_cost,
            "long_short_after_cost": long_short_after_cost,
        })

    return pd.DataFrame(rows)


def summarize_backtest(bt_df):
    if len(bt_df) == 0:
        raise ValueError("Backtest dataframe is empty.")

    def safe_sharpe(x):
        x = pd.Series(x).dropna()
        if len(x) < 2 or x.std() == 0:
            return np.nan
        return x.mean() / x.std()

    summary = {
        "rebalance_mode": REBALANCE_MODE,
        "n_rebalances": int(len(bt_df)),

        "avg_top_return": float(bt_df["top_return"].mean()),
        "avg_bottom_return": float(bt_df["bottom_return"].mean()),
        "avg_benchmark_return": float(bt_df["benchmark_return"].mean()),

        "avg_active_return": float(bt_df["active_return"].mean()),
        "avg_long_short_spread": float(bt_df["long_short_spread"].mean()),

        "avg_top_return_after_cost": float(bt_df["top_return_after_cost"].mean()),
        "avg_active_after_cost": float(bt_df["active_after_cost"].mean()),
        "avg_long_short_after_cost": float(bt_df["long_short_after_cost"].mean()),

        "top_beats_benchmark_rate": float((bt_df["top_return"] > bt_df["benchmark_return"]).mean()),
        "top_beats_bottom_rate": float((bt_df["top_return"] > bt_df["bottom_return"]).mean()),
        "positive_long_short_rate": float((bt_df["long_short_spread"] > 0).mean()),

        "avg_top_turnover": float(bt_df["top_turnover"].mean()),
        "avg_bottom_turnover": float(bt_df["bottom_turnover"].mean()),

        "active_return_sharpe_like": float(safe_sharpe(bt_df["active_return"])),
        "long_short_sharpe_like": float(safe_sharpe(bt_df["long_short_spread"])),
        "active_after_cost_sharpe_like": float(safe_sharpe(bt_df["active_after_cost"])),
        "long_short_after_cost_sharpe_like": float(safe_sharpe(bt_df["long_short_after_cost"])),
    }

    return summary


def plot_backtest(bt_df):
    plot_df = bt_df.sort_values("date").copy()

    plot_df["cum_top"] = (1 + plot_df["top_return_after_cost"]).cumprod()
    plot_df["cum_benchmark"] = (1 + plot_df["benchmark_return"]).cumprod()
    plot_df["cum_long_short"] = (1 + plot_df["long_short_after_cost"]).cumprod()

    # Chart 1: average returns
    avg_returns = pd.Series({
        "Top 20%": plot_df["top_return"].mean(),
        "Benchmark": plot_df["benchmark_return"].mean(),
        "Bottom 20%": plot_df["bottom_return"].mean(),
        "Top-Bottom": plot_df["long_short_spread"].mean(),
    })

    plt.figure(figsize=(8, 5))
    avg_returns.plot(kind="bar")
    plt.title("Average Forward Return by Portfolio")
    plt.ylabel("Average target_252d return")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "avg_forward_returns.png", dpi=300)
    plt.close()

    # Chart 2: active return by rebalance
    plt.figure(figsize=(11, 5))
    plt.plot(plot_df["date"], plot_df["active_return"], marker="o", label="Top - Benchmark")
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.title("Active Return by Rebalance Date")
    plt.xlabel("Date")
    plt.ylabel("Active Return")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "active_return_by_rebalance.png", dpi=300)
    plt.close()

    # Chart 3: long-short spread
    plt.figure(figsize=(11, 5))
    plt.plot(plot_df["date"], plot_df["long_short_spread"], marker="o", label="Top - Bottom")
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.title("Long-Short Spread by Rebalance Date")
    plt.xlabel("Date")
    plt.ylabel("Top - Bottom Return")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "long_short_spread_by_rebalance.png", dpi=300)
    plt.close()

    # Chart 4: indicative cumulative curve
    plt.figure(figsize=(11, 5))
    plt.plot(plot_df["date"], plot_df["cum_top"], label="Top 20% after cost")
    plt.plot(plot_df["date"], plot_df["cum_benchmark"], label="Benchmark")
    plt.plot(plot_df["date"], plot_df["cum_long_short"], label="Long-Short after cost")
    plt.title("Indicative Cumulative Performance")
    plt.xlabel("Date")
    plt.ylabel("Growth of 1")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "indicative_cumulative_performance.png", dpi=300)
    plt.close()


def main():
    print("Loading data...")
    df, feature_cols, target_col = load_data()
    stable_features = load_stable_features()

    splitter = WalkForwardSplit()
    folds, fold_info = splitter.split(df)
    folds = list(folds)

    print(f"Total folds: {len(folds)}")
    print(f"Backtest mode: {REBALANCE_MODE}")
    print(f"Top fraction: {TOP_FRAC}")
    print(f"Transaction cost: {TRANSACTION_COST}")

    all_predictions = []

    for fold_id, (train_idx, test_idx) in enumerate(folds):
        fold_key = fold_id + 1

        print("\n============================")
        print(f"Fold {fold_key}/{len(folds)}")
        print("============================")

        X_tr, y_tr, X_te, meta_test, selected = prepare_fold(
            df=df,
            feature_cols=feature_cols,
            target_col=target_col,
            train_idx=train_idx,
            test_idx=test_idx,
            fold_key=fold_key,
            stable_features=stable_features,
        )

        print(f"Features: {len(selected)}")
        print(f"Train rows: {len(X_tr)}")
        print(f"Test rows: {len(X_te)}")

        model = XGBoostModel(params=BEST_PARAMS)
        model.fit(X_tr, y_tr)

        preds = model.predict(X_te)

        fold_pred = meta_test.copy()
        fold_pred["fold"] = fold_key
        fold_pred["prediction"] = preds

        all_predictions.append(fold_pred)

    pred_df = pd.concat(all_predictions, ignore_index=True)

    pred_path = OUT_DIR / "xgboost_backtest_predictions.csv"
    pred_df.to_csv(pred_path, index=False)

    print("\nRunning portfolio backtest...")
    bt_df = backtest_predictions(pred_df)

    bt_path = OUT_DIR / "xgboost_portfolio_backtest.csv"
    bt_df.to_csv(bt_path, index=False)

    summary = summarize_backtest(bt_df)

    summary_path = OUT_DIR / "xgboost_backtest_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    plot_backtest(bt_df)

    print("\n============================")
    print("Backtest Summary")
    print("============================")

    for k, v in summary.items():
        if isinstance(v, float):
            print(f"{k}: {v:.6f}")
        else:
            print(f"{k}: {v}")

    print("\nSaved:")
    print(f"Predictions: {pred_path}")
    print(f"Backtest results: {bt_path}")
    print(f"Summary: {summary_path}")
    print(f"Charts: {OUT_DIR}")


if __name__ == "__main__":
    main()