import pandas as pd
import numpy as np
import json
import sys

class WalkForwardStrategy:

    def __init__(self, results_path):
        self.df = pd.read_csv(results_path)

        # ----------------------------------------
        # Safe parsing
        # ----------------------------------------
        self.df["preds"] = self.df["preds"].apply(self._to_array)
        self.df["y_true"] = self.df["y_true"].apply(self._to_array)

        # Drop corrupted rows
        self.df = self.df[
            self.df["preds"].notna() & self.df["y_true"].notna()
        ]

        print(f"Valid folds used: {len(self.df)}")

    # ----------------------------------------
    # Robust array parser
    # ----------------------------------------
    def _to_array(self, x):
        if isinstance(x, str):
            try:
                # JSON format (correct case)
                return np.array(json.loads(x))
            except:
                # fallback (old broken format)
                if "..." in x:
                    return None
                try:
                    x = x.strip("[]")
                    parts = x.split()
                    return np.array([float(p.replace(",", "")) for p in parts])
                except:
                    return None
        return np.array(x)

    # ----------------------------------------
    # Strategy logic (FINAL VERSION)
    # ----------------------------------------
    def _compute_strategy(self, preds, y_true):

        preds = np.asarray(preds).flatten()
        y_true = np.asarray(y_true).flatten()

        # -----------------------------
        # Z-score signal
        # -----------------------------
        preds = preds - np.mean(preds)
        signal = preds / (np.std(preds) + 1e-9)

        # -----------------------------
        # Threshold filtering (KEY)
        # -----------------------------
        percentile = 0.9

        upper = np.quantile(signal, percentile)
        lower = np.quantile(signal, 1 - percentile)

        # compute IC for this fold
        ic = np.corrcoef(preds, y_true)[0, 1]

        # flip signal if needed
        if ic < 0:
            preds = -preds

        # Z-score
        preds = preds - np.mean(preds)
        signal = preds / (np.std(preds) + 1e-9)

        # top/bottom selection
        percentile = 0.9
        upper = np.quantile(signal, percentile)
        lower = np.quantile(signal, 1 - percentile)

        positions = np.where(signal > upper, 1,
            np.where(signal < lower, -1, 0))
        # -----------------------------
        # Strategy returns
        # -----------------------------
        returns = positions * y_true

        # -----------------------------
        # Sharpe
        # -----------------------------
        if np.std(returns) == 0:
            sharpe = 0
        else:
            sharpe = np.mean(returns) / np.std(returns)

        return {
            "z_sharpe": sharpe,
            "n_trades": np.sum(positions != 0),
            "avg_position": np.mean(np.abs(positions))
        }

    # ----------------------------------------
    # Run strategy
    # ----------------------------------------
    def run(self):

        results = []

        for _, row in self.df.iterrows():

            preds = row["preds"]
            y_true = row["y_true"]

            stats = self._compute_strategy(preds, y_true)

            results.append({
                "fold": row["fold"],
                "z_sharpe": stats["z_sharpe"],
                "n_trades": stats["n_trades"]
            })

        self.results = pd.DataFrame(results)

        # ----------------------------------------
        # Summary
        # ----------------------------------------
        print("\n============================")
        print("Z-Score Strategy Results")
        print("============================")

        print("\nAverage Sharpe:")
        print(self.results["z_sharpe"].mean())

        print("\nStability (Std):")
        print(self.results["z_sharpe"].std())

        print("\nWorst Case:")
        print(self.results["z_sharpe"].min())

        print("\nAverage Trades per Fold:")
        print(self.results["n_trades"].mean())

        return self.results