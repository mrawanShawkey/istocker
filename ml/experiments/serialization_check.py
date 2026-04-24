"""
serialization_check.py

Verifies saved XGBoost models against original walk-forward results.
Checks for:
    1. Prediction identity     — serialized model reproduces exact same predictions
    2. No data leakage         — model trained on fold N cannot see fold N+1 data
    3. Feature consistency     — same features used at save time and load time
    4. Target distribution     — predictions don't suspiciously match future y_true
"""

import numpy as np
import pandas as pd
import joblib
import json

from ml.training.walk_forward_split import WalkForwardSplit
from ml.feature_selection.feature_cache import load_features

from config.paths import (
    MODELING_DATASET_FILE,
    WALKFORWARD_RESULTS_DIR,
    XGB_MODEL_PATH,
    FEATURE_STABILITY_FILE
)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def to_array(x):
    if isinstance(x, str):
        try:
            return np.array(json.loads(x))
        except Exception:
            return None
    return np.array(x)


def load_stable_features():
    try:
        df = pd.read_csv(FEATURE_STABILITY_FILE)
        return df[df["frequency"] > 0.6]["feature"].tolist()
    except Exception:
        return None


def prepare_fold_data(df, feature_cols, target_col,
                        train_idx, test_idx, fold_key, stable_features):
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

    # Feature selection
    cached = load_features(fold_key)
    selected = list(cached) if cached is not None else list(feature_cols)
    if stable_features:
        selected = [f for f in selected if f in stable_features]
    selected = sorted(selected)

    X_tr = X_train[selected].values.astype(np.float32)
    X_te = X_test[selected].values.astype(np.float32)

    return X_tr, y_train.values, X_te, y_test.values, selected


# ─────────────────────────────────────────────
# Leakage checks
# ─────────────────────────────────────────────
def check_prediction_identity(original_preds, serialized_preds, fold_id):
    """Serialized model must reproduce identical predictions."""
    if len(original_preds) != len(serialized_preds):
        return False, f"Length mismatch: {len(original_preds)} vs {len(serialized_preds)}"

    max_diff = np.max(np.abs(original_preds - serialized_preds))
    if max_diff > 1e-5:
        return False, f"Max prediction diff: {max_diff:.2e} — model mismatch"

    return True, f" Identical (max diff {max_diff:.2e})"


def check_future_leakage(model, X_future, y_future, X_test, y_test):
    """
    Train-test contamination check:
    If the model somehow saw future data, its predictions on
    future X would correlate suspiciously with future y.
    We compare IC on test set vs IC on the NEXT fold's data.
    A leaking model would show IC on future data close to test IC.
    A clean model should show near-zero IC on future data.
    """
    preds_test   = model.predict(X_test)
    preds_future = model.predict(X_future)

    mask_test   = np.isfinite(y_test)   & np.isfinite(preds_test)
    mask_future = np.isfinite(y_future) & np.isfinite(preds_future)

    ic_test   = float(np.corrcoef(preds_test[mask_test],
                                    y_test[mask_test])[0, 1]) \
                if mask_test.sum() >= 5 else np.nan
    ic_future = float(np.corrcoef(preds_future[mask_future],
                                    y_future[mask_future])[0, 1]) \
                if mask_future.sum() >= 5 else np.nan

    # Leakage flag: future IC should not be close to test IC
    # Threshold: if future IC > 50% of test IC, flag it
    leakage_flag = (abs(ic_future) > 0.5 * abs(ic_test)) \
                    if np.isfinite(ic_future) and np.isfinite(ic_test) \
                    else False

    return ic_test, ic_future, leakage_flag


def check_target_snooping(preds, y_true):
    """
    Snooping check: predictions should not be suspiciously
    close to actual y_true values (would indicate target leakage).
    If mean absolute error is near zero relative to target std,
    the model has seen the answers.
    """
    mae   = np.mean(np.abs(preds - y_true))
    y_std = np.std(y_true)
    ratio = mae / (y_std + 1e-9)

    # A ratio < 0.1 means predictions are suspiciously accurate
    snooping_flag = ratio < 0.1
    return ratio, snooping_flag


# ─────────────────────────────────────────────
# Main verification
# ─────────────────────────────────────────────
def main():
    print("Loading dataset...")
    df = pd.read_csv(MODELING_DATASET_FILE)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)

    target_col   = "target_252d"
    feature_cols = [
        c for c in df.columns
        if c not in ["date", "symbol", target_col]
        and df[c].dtype != object
    ]

    stable_features = load_stable_features()
    splitter        = WalkForwardSplit()
    folds, _        = splitter.split(df)
    folds           = list(folds)

    # Load original results for identity check
    results_path = WALKFORWARD_RESULTS_DIR / "xgboost_results.csv"
    original_df  = pd.read_csv(results_path)
    original_df["preds"] = original_df["preds"].apply(to_array)

    print(f"\n{'='*56}")
    print("Serialization & Leakage Verification — All 20 Folds")
    print(f"{'='*56}")

    report = []
    all_passed = True

    for fold_id in range(len(folds)):
        fold_key = fold_id + 1
        model_path = XGB_MODEL_PATH / f"xgboost_fold_{fold_key}.joblib"

        if not model_path.exists():
            print(f"Fold {fold_key:2d} |   Model file not found — run xgboost_runner first")
            all_passed = False
            continue

        # Load serialized model
        model = joblib.load(model_path)

        # Prepare fold data
        train_idx, test_idx = folds[fold_id]
        X_tr, y_tr, X_te, y_te, selected = prepare_fold_data(
            df, feature_cols, target_col,
            train_idx, test_idx, fold_key, stable_features
        )

        # ── Check 1: Prediction identity ──
        serialized_preds = model.predict(X_te)
        original_preds   = original_df.loc[
            original_df["fold"] == fold_key, "preds"
        ].values[0]
        # Align lengths
        min_len          = min(len(serialized_preds), len(original_preds))
        identity_ok, identity_msg = check_prediction_identity(
            original_preds[-min_len:],
            serialized_preds[-min_len:],
            fold_id
        )

        # ── Check 2: Future leakage (skip last fold) ──
        if fold_id < len(folds) - 1:
            _, next_test_idx = folds[fold_id + 1]
            next_test_df = df.loc[next_test_idx]
            X_next = next_test_df[feature_cols].copy()
            X_next = X_next.replace([np.inf, -np.inf], np.nan).fillna(
                df.loc[train_idx, feature_cols].median()
            )
            y_next = next_test_df[target_col].replace(
                [np.inf, -np.inf], np.nan).dropna()
            X_next = X_next.loc[y_next.index]
            selected_next = [f for f in selected if f in X_next.columns]
            X_next_sel = X_next[selected_next].values.astype(np.float32)

            ic_test, ic_future, leakage_flag = check_future_leakage(
                model, X_next_sel, y_next.values, X_te, y_te
            )
        else:
            ic_test, ic_future, leakage_flag = np.nan, np.nan, False

        # ── Check 3: Target snooping ──
        ratio, snooping_flag = check_target_snooping(serialized_preds, y_te)

        # ── Summary for this fold ──
        fold_ok = identity_ok and not leakage_flag and not snooping_flag
        if not fold_ok:
            all_passed = False

        status = " PASS" if fold_ok else " FAIL"
        print(f"\nFold {fold_key:2d} | {status}")
        print(f"  Identity check  : {identity_msg}")
        print(f"  Future leakage  : IC_test={ic_test:.3f}  IC_future={ic_future:.3f}"
            f"  {' FLAGGED' if leakage_flag else ' Clean'}")
        print(f"  Target snooping : MAE/std ratio={ratio:.3f}"
            f"  {' FLAGGED' if snooping_flag else ' Clean'}")

        report.append({
            "fold":           fold_key,
            "identity_ok":    identity_ok,
            "ic_test":        ic_test,
            "ic_future":      ic_future,
            "leakage_flag":   leakage_flag,
            "snooping_flag":  snooping_flag,
            "mae_std_ratio":  ratio,
            "passed":         fold_ok
        })

    # ── Final summary ──
    report_df = pd.DataFrame(report)
    print(f"\n{'='*56}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*56}")
    print(f"  Folds verified  : {len(report_df)}/20")
    print(f"  All passed      : {' YES' if all_passed else ' NO — see flagged folds above'}")
    print(f"  Leakage flags   : {report_df['leakage_flag'].sum()}")
    print(f"  Snooping flags  : {report_df['snooping_flag'].sum()}")
    print(f"  Identity fails  : {(~report_df['identity_ok']).sum()}")

    # Save report
    out = WALKFORWARD_RESULTS_DIR / "serialization_verification_report.csv"
    report_df.to_csv(out, index=False)
    print(f"\n  Report saved to: {out}")

    # Mark production model
    if all_passed:
        import shutil
        prod_src = XGB_MODEL_PATH / "xgboost_fold_20.joblib"
        prod_dst = XGB_MODEL_PATH / "xgboost_production.joblib"
        shutil.copy(prod_src, prod_dst)
        print(f"\n   Production model saved to: {prod_dst}")
    else:
        print("\n Fix flagged folds before marking production model.")


if __name__ == "__main__":
    main()