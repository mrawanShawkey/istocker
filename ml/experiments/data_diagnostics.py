"""
data_diagnostics.py

This script checks for numerical instability and data quality issues
in the modeling dataset before training.

Run this before any experiment to ensure feature reliability.
"""

import pandas as pd
import numpy as np

from config.paths import MODELING_DATASET_FILE as MODELING_DATASET_PATH


class DataDiagnostics:

    def __init__(self):
        print("Loading dataset...")
        self.df = pd.read_csv(MODELING_DATASET_PATH)

        # Ensure datetime
        self.df["date"] = pd.to_datetime(self.df["date"])

        self.target = "target_252d"

        self.features = [
            c for c in self.df.columns
            if c not in ["date", "symbol", self.target]
        ]

        print(f"Dataset shape: {self.df.shape}")
        print(f"Total features: {len(self.features)}")

    # ---------------------------------------------------------
    # 1. Missing values
    # ---------------------------------------------------------
    def check_missing(self):

        print("\n============================")
        print("Missing Values Check")
        print("============================")

        missing = self.df[self.features].isna().sum()
        missing = missing[missing > 0].sort_values(ascending=False)

        if missing.empty:
            print("No missing values ✔")
        else:
            print(missing.head(20))

    # ---------------------------------------------------------
    # 2. Infinite values
    # ---------------------------------------------------------
    def check_infinite(self):

        print("\n============================")
        print("Infinite Values Check")
        print("============================")

        inf_counts = np.isinf(self.df[self.features]).sum()
        inf_counts = pd.Series(inf_counts, index=self.features)
        inf_counts = inf_counts[inf_counts > 0]

        if inf_counts.empty:
            print("No infinite values ✔")
        else:
            print(inf_counts)

    # ---------------------------------------------------------
    # 3. Zero variance features
    # ---------------------------------------------------------
    def check_constant(self):

        print("\n============================")
        print("Constant Features Check")
        print("============================")

        constant_cols = [
            col for col in self.features
            if self.df[col].nunique() <= 1
        ]

        if not constant_cols:
            print("No constant features ✔")
        else:
            print("Constant features:", constant_cols)

    # ---------------------------------------------------------
    # 4. Extreme values (outliers)
    # ---------------------------------------------------------
    def check_outliers(self):

        print("\n============================")
        print("Outlier Check (Z-score > 10)")
        print("============================")

        extreme_features = []

        for col in self.features:
            series = self.df[col]

            if series.std() == 0:
                continue

            z = (series - series.mean()) / series.std()
            if (np.abs(z) > 10).sum() > 0:
                extreme_features.append(col)

        if not extreme_features:
            print("No extreme outliers ✔")
        else:
            print("Extreme features:", extreme_features)

    # ---------------------------------------------------------
    # 5. Scale check
    # ---------------------------------------------------------
    def check_scale(self):

        print("\n============================")
        print("Feature Scale Check")
        print("============================")

        stats = self.df[self.features].describe().T

        stats["range"] = stats["max"] - stats["min"]

        print(stats[["mean", "std", "min", "max"]].sort_values("std", ascending=False).head(10))

    # ---------------------------------------------------------
    # 6. Target sanity check
    # ---------------------------------------------------------
    def check_target(self):

        print("\n============================")
        print("Target Distribution")
        print("============================")

        print(self.df[self.target].describe())

        print("\nExtreme target values:")
        print(self.df[self.target].nlargest(5))
        print(self.df[self.target].nsmallest(5))

    # ---------------------------------------------------------
    # Run all checks
    # ---------------------------------------------------------
    def run_all(self):

        self.check_missing()
        self.check_infinite()
        self.check_constant()
        self.check_outliers()
        self.check_scale()
        self.check_target()


# ---------------------------------------------------------
# Run diagnostics
# ---------------------------------------------------------
if __name__ == "__main__":

    diag = DataDiagnostics()
    diag.run_all()