"""
strategy.py — fixed drawdown, cleaned metrics
"""

import pandas as pd
import numpy as np
import json


class WalkForwardStrategy:

    def __init__(self, results_path, top_pct=0.2, regime_ic_threshold=0.05):
        self.top_pct = top_pct
        self.regime_ic_threshold = regime_ic_threshold

        self.df = pd.read_csv(results_path)
        self.df["preds"]  = self.df["preds"].apply(self._to_array)
        self.df["y_true"] = self.df["y_true"].apply(self._to_array)
        self.df = self.df[self.df["preds"].notna() & self.df["y_true"].notna()]
        print(f"Valid folds loaded: {len(self.df)}")

    def _to_array(self, x):
        if isinstance(x, str):
            try:
                return np.array(json.loads(x))
            except Exception:
                try:
                    return np.array([float(p.replace(",",""))
                                     for p in x.strip("[]").split()])
                except Exception:
                    return None
        return np.array(x) if x is not None else None

    def _build_signal(self, preds, fold_ic):
        preds = np.asarray(preds, dtype=np.float64).flatten()
        preds = np.where(np.isfinite(preds), preds, 0.0)
        if fold_ic < 0:
            preds = -preds
        mu, sigma = np.mean(preds), np.std(preds)
        return (preds - mu) / (sigma + 1e-9)

    def _build_positions(self, signal, regime_flag):
        upper = np.quantile(signal, 1 - self.top_pct)
        lower = np.quantile(signal, self.top_pct)
        positions = np.where(signal >= upper,  1,
                    np.where(signal <= lower, -1, 0))
        if regime_flag:
            positions = positions * 0.5
        return positions

    def _compute_fold(self, preds, y_true, fold_ic):
        y_true      = np.asarray(y_true, dtype=np.float64).flatten()
        regime_flag = abs(fold_ic) < self.regime_ic_threshold
        signal      = self._build_signal(preds, fold_ic)
        positions   = self._build_positions(signal, regime_flag)

        active_mask = positions != 0
        n_active    = active_mask.sum()

        if n_active == 0:
            return {"fold_return": 0.0, "sharpe": 0.0,
                    "long_return": np.nan, "short_return": np.nan,
                    "hit_rate": np.nan, "n_long": 0, "n_short": 0,
                    "regime_flag": regime_flag}

        raw_returns = positions[active_mask] * y_true[active_mask]

        long_mask  = positions ==  1
        short_mask = positions == -1

        return {
            "fold_return":  float(np.mean(raw_returns)),
            "sharpe":       float(np.mean(raw_returns) /
                                  (np.std(raw_returns) + 1e-9)),
            "long_return":  float(np.mean(y_true[long_mask]))  if long_mask.any()  else np.nan,
            "short_return": float(np.mean(-y_true[short_mask])) if short_mask.any() else np.nan,
            "hit_rate":     float(np.mean(raw_returns > 0)),
            "n_long":       int(long_mask.sum()),
            "n_short":      int(short_mask.sum()),
            "regime_flag":  regime_flag,
        }

    def _equity_curve_stats(self, fold_returns):
        """
        All drawdown computed here — on the fold-level equity curve.
        This is the only valid time dimension available.
        """
        cum   = np.cumsum(fold_returns)
        peak  = np.maximum.accumulate(cum)
        dd    = (cum - peak) / (np.abs(peak) + 1e-9)

        max_dd      = float(np.min(dd))
        sharpe      = float(np.mean(fold_returns) /
                            (np.std(fold_returns) + 1e-9))
        cum_return  = float(cum[-1])

        # Calmar = annualized return / max drawdown
        n_years = len(fold_returns)          # 1 fold ≈ 1 year
        ann_return = cum_return / n_years
        calmar  = ann_return / (abs(max_dd) + 1e-9)

        return cum, dd, {
            "cumulative_return": cum_return,
            "fold_sharpe":       sharpe,
            "max_drawdown":      max_dd,
            "calmar_ratio":      calmar,
            "ann_return":        ann_return,
        }

    def run(self):
        records = []
        for _, row in self.df.iterrows():
            fold_ic = float(row["information_coefficient"])
            result  = self._compute_fold(row["preds"], row["y_true"], fold_ic)
            result["fold"] = int(row["fold"])
            result["ic"]   = fold_ic
            records.append(result)

        self.results = (pd.DataFrame(records)
                          .sort_values("fold")
                          .reset_index(drop=True))

        # ── Equity curve stats (the only valid drawdown) ──
        cum, dd_series, eq_stats = self._equity_curve_stats(
            self.results["fold_return"].values
        )
        self.results["cum_return"] = cum
        self.results["drawdown"]   = dd_series

        self._print_summary(eq_stats)
        return self.results

    def _print_summary(self, eq_stats):
        r        = self.results
        flagged  = r["regime_flag"].sum()
        active   = r[~r["regime_flag"]]

        print("\n" + "="*60)
        print("Strategy Results — Per Fold")
        print("="*60)
        print(r[["fold","ic","fold_return","sharpe",
                  "hit_rate","drawdown","regime_flag"]].to_string(index=False))

        print("\n" + "="*60)
        print("Aggregate — All 20 Folds")
        print("="*60)
        print(f"  Avg Fold Return  : {r['fold_return'].mean():.4f}")
        print(f"  Avg Fold Sharpe  : {r['sharpe'].mean():.4f}")
        print(f"  Avg Hit Rate     : {r['hit_rate'].mean():.4f}")
        print(f"  Regime-flagged   : {flagged}/20 folds")

        if len(active) > 0:
            print("\n" + "="*60)
            print(f"Aggregate — Strong Folds Only ({len(active)}/20)")
            print("="*60)
            print(f"  Avg Fold Return  : {active['fold_return'].mean():.4f}")
            print(f"  Avg Fold Sharpe  : {active['sharpe'].mean():.4f}")
            print(f"  Avg Hit Rate     : {active['hit_rate'].mean():.4f}")

        print("\n" + "="*60)
        print("Equity Curve (fold-level, 1 fold ≈ 1 year)")
        print("="*60)
        print(f"  Cumulative Return : {eq_stats['cumulative_return']:.4f}")
        print(f"  Annualized Return : {eq_stats['ann_return']:.4f}")
        print(f"  Fold-level Sharpe : {eq_stats['fold_sharpe']:.4f}")
        print(f"  Max Drawdown      : {eq_stats['max_drawdown']:.4f}")
        print(f"  Calmar Ratio      : {eq_stats['calmar_ratio']:.4f}")