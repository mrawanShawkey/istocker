import pandas as pd
import numpy as np
import json

from ml.evaluation.walkforward_strategy import WalkForwardStrategy
from config.paths import (
    LSTM_RESULTS_FILE,
    XGBOOST_RESULTS_FILE,
    WALKFORWARD_RESULTS_DIR
)


# ─────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────
def to_array(x):
    if isinstance(x, str):
        try:
            return np.array(json.loads(x))
        except Exception:
            try:
                return np.array([float(p.replace(",", ""))
                                for p in x.strip("[]").split()])
            except Exception:
                return None
    return np.array(x) if x is not None else None


def load_results(path):
    df = pd.read_csv(path)
    df["preds"]  = df["preds"].apply(to_array)
    df["y_true"] = df["y_true"].apply(to_array)
    df = df[df["preds"].notna() & df["y_true"].notna()]
    return df.sort_values("fold").reset_index(drop=True)


# ─────────────────────────────────────────────
# Ensemble combination methods
# ─────────────────────────────────────────────
def combine_equal_weight(xgb_preds, lstm_preds):
    """Simple average of raw predictions."""
    return 0.5 * xgb_preds + 0.5 * lstm_preds


def combine_ic_weight(xgb_preds, lstm_preds, xgb_ic, lstm_ic):
    """
    Weight each model by absolute IC for this fold.
    Better model gets more weight automatically.
    """
    xgb_w  = abs(xgb_ic)
    lstm_w = abs(lstm_ic)
    total  = xgb_w + lstm_w + 1e-9
    return (xgb_w / total) * xgb_preds + (lstm_w / total) * lstm_preds


def combine_rank_average(xgb_preds, lstm_preds):
    """
    Rank-normalize each model's predictions independently,
    then average ranks. Most robust to scale differences
    between XGBoost and LSTM output ranges.
    """
    def rank_norm(arr):
        ranks = arr.argsort().argsort().astype(float)
        return (ranks - ranks.mean()) / (ranks.std() + 1e-9)

    return 0.5 * rank_norm(xgb_preds) + 0.5 * rank_norm(lstm_preds)


# ─────────────────────────────────────────────
# Build ensemble CSV per mode
# ─────────────────────────────────────────────
def build_ensemble_df(xgb_df, lstm_df, mode="rank_average"):

    assert len(xgb_df) == len(lstm_df), "Fold count mismatch between models"

    rows = []
    for i in range(len(xgb_df)):
        xgb_row  = xgb_df.iloc[i]
        lstm_row = lstm_df.iloc[i]

        assert xgb_row["fold"] == lstm_row["fold"], \
            f"Fold mismatch at index {i}"

        xgb_preds  = np.asarray(xgb_row["preds"],  dtype=np.float64).flatten()
        lstm_preds = np.asarray(lstm_row["preds"], dtype=np.float64).flatten()
        y_true     = np.asarray(xgb_row["y_true"], dtype=np.float64).flatten()

        # Align lengths (LSTM may differ slightly due to windowing)
        min_len    = min(len(xgb_preds), len(lstm_preds), len(y_true))
        xgb_preds  = xgb_preds[-min_len:]
        lstm_preds = lstm_preds[-min_len:]
        y_true     = y_true[-min_len:]

        if mode == "equal_weight":
            ensemble_preds = combine_equal_weight(xgb_preds, lstm_preds)
        elif mode == "ic_weight":
            ensemble_preds = combine_ic_weight(
                xgb_preds, lstm_preds,
                xgb_row["information_coefficient"],
                lstm_row["information_coefficient"]
            )
        elif mode == "rank_average":
            ensemble_preds = combine_rank_average(xgb_preds, lstm_preds)
        else:
            raise ValueError(f"Unknown mode: {mode}")

        # Compute ensemble IC for reporting
        mask = np.isfinite(ensemble_preds) & np.isfinite(y_true)
        ic   = float(np.corrcoef(ensemble_preds[mask], y_true[mask])[0, 1]) \
            if mask.sum() >= 5 else np.nan

        row = xgb_row.to_dict()
        row["preds"]  = json.dumps(ensemble_preds.tolist())
        row["y_true"] = json.dumps(y_true.tolist())
        row["information_coefficient"] = ic
        row["xgb_ic"]  = xgb_row["information_coefficient"]
        row["lstm_ic"] = lstm_row["information_coefficient"]
        rows.append(row)

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():

    print("Loading XGBoost results...")
    xgb_df  = load_results(XGBOOST_RESULTS_FILE)
    print("Loading LSTM results...")
    lstm_df = load_results(LSTM_RESULTS_FILE)

    print(f"\nXGBoost folds : {len(xgb_df)}")
    print(f"LSTM folds    : {len(lstm_df)}")

    modes = ["equal_weight", "ic_weight", "rank_average"]
    summary = []

    for mode in modes:
        print(f"\n{'='*52}")
        print(f"Ensemble Mode: {mode.upper()}")
        print(f"{'='*52}")

        # Build combined predictions
        ensemble_df = build_ensemble_df(xgb_df, lstm_df, mode=mode)

        # Save to temp CSV so WalkForwardStrategy can load it
        out_path = WALKFORWARD_RESULTS_DIR / f"ensemble_{mode}_results.csv"
        ensemble_df.to_csv(out_path, index=False)

        # Run strategy on ensemble predictions
        strategy = WalkForwardStrategy(
            str(out_path),
            top_pct=0.2,
            regime_ic_threshold=0.05
        )
        results = strategy.run()

        # Collect summary row
        fold_rets = results["fold_return"].values
        cum       = np.cumsum(fold_rets)
        peak      = np.maximum.accumulate(cum)
        dd        = (cum - peak) / (np.abs(peak) + 1e-9)

        summary.append({
            "mode":              mode,
            "avg_fold_return":   float(results["fold_return"].mean()),
            "fold_sharpe":       float(results["fold_return"].mean() /
                                    (results["fold_return"].std() + 1e-9)),
            "cum_return":        float(cum[-1]),
            "max_drawdown":      float(np.min(dd)),
            "avg_hit_rate":      float(results["hit_rate"].mean()),
            "negative_folds":    int((results["fold_return"] < 0).sum()),
        })

    # ── Final comparison table ──
    print(f"\n{'='*52}")
    print("ENSEMBLE MODE COMPARISON")
    print(f"{'='*52}")
    summary_df = pd.DataFrame(summary)
    print(summary_df.to_string(index=False))

    # Also print individual model baselines for reference
    print(f"\n{'='*52}")
    print("REFERENCE — Individual Models")
    print(f"{'='*52}")
    print("  XGBoost : Cum=1.586  Sharpe=1.04  MaxDD=-0.150  NegFolds=3")
    print("  LSTM    : Cum=1.997  Sharpe=1.48  MaxDD= 0.000  NegFolds=0")


if __name__ == "__main__":
    main()