import pandas as pd
import numpy as np
from pathlib import Path

import sys
ROOT_DIR = Path().resolve()
sys.path.append(str(ROOT_DIR))
from config.paths import MACROECNOMIC_ALIGNMENT_FILE, MODELING_DATASET_FILE

# Regime dummy: choose your own break date (e.g., currency float regime)
REGIME_BREAK_DATE = pd.Timestamp("2016-11-03")  # adjust if you use a different breakpoint

# Rolling windows
MOM_WINDOWS = [60, 126, 252]
VOL_WINDOWS = [20, 60]
MA_WINDOWS = [60, 252]
ATR_WINDOW = 14
RSI_WINDOW = 14
REALIZED_VOL_WINDOW = 20
VOLUME_Z_WINDOW = 20
VOLUME_GROWTH_WINDOW = 60
MA_SLOPE_LAG = 5  # slope over 5 trading days


def _compute_atr(group: pd.DataFrame, window: int = 14) -> pd.Series:
    """ATR using True Range (Wilder-style TR, simple rolling mean)."""
    high = group["high"]
    low = group["low"]
    close = group["close"]
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window).mean()
    return atr


def _compute_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """RSI (Wilder) using exponential smoothing of gains/losses."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)

    # Wilder smoothing ~ EMA with alpha=1/window
    avg_gain = gain.ewm(alpha=1 / window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


class FeatureEngineer:
    def __init__(self, input_file: Path = MACROECNOMIC_ALIGNMENT_FILE):
        self.input_file = input_file
        self.df: pd.DataFrame | None = None

    def load(self):
        print(f"Loading: {self.input_file}")
        self.df = pd.read_csv(self.input_file)

        self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")


        # Ensure required columns exist
        required = {"date", "symbol", "open", "high", "low", "close", "volume"}
        missing = required - set(self.df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Sort for time-series operations
        self.df = self.df.sort_values(["symbol", "date"]).reset_index(drop=True)

    def compute_features(self):
        print("Computing features (per symbol)...")
        g = self.df.groupby("symbol", group_keys=False)

        # --- Base transformation ---
        self.df["log_return_1d"] = g["close"].transform(lambda x: np.log(x / x.shift(1)))

        # --- Trend & Momentum ---
        for w in MOM_WINDOWS:
            self.df[f"mom_{w}"] = g["close"].transform(lambda x, w=w: np.log(x / x.shift(w)))

        # Moving averages
        for w in MA_WINDOWS:
            self.df[f"ma_{w}"] = g["close"].transform(lambda x, w=w: x.rolling(w).mean())
            self.df[f"price_to_ma{w}"] = self.df["close"] / self.df[f"ma_{w}"]

        # 60d MA slope (trend velocity)
        # slope = MA60(t) - MA60(t-5)  (you can divide by 5 if you want "per day")
        self.df["ma_60_slope"] = g["ma_60"].transform(lambda x: x - x.shift(MA_SLOPE_LAG))

        # --- Volatility ---
        for w in VOL_WINDOWS:
            self.df[f"vol_{w}"] = g["log_return_1d"].transform(lambda x, w=w: x.rolling(w).std())

        # ATR (14)
        self.df["atr_14"] = g.apply(lambda grp: _compute_atr(grp, ATR_WINDOW))

        # 20d realized volatility (based on log returns)
        # realized_vol_20 = sqrt(sum_{i=1..20} r_i^2)
        self.df["realized_vol_20"] = g["log_return_1d"].transform(
            lambda x: np.sqrt((x ** 2).rolling(REALIZED_VOL_WINDOW).sum())
        )

        # --- Liquidity ---
        # 20d volume z-score
        vol_mean = g["volume"].transform(lambda x: x.rolling(VOLUME_Z_WINDOW).mean())
        vol_std = g["volume"].transform(lambda x: x.rolling(VOLUME_Z_WINDOW).std())
        self.df["volume_z_20"] = (self.df["volume"] - vol_mean) / vol_std

        # 60d volume growth (log growth to match log-return style)
        self.df["volume_growth_60"] = g["volume"].transform(
            lambda x: np.log(x / x.shift(VOLUME_GROWTH_WINDOW))
        )

        # --- Seasonality ---
        self.df["month"] = self.df["date"].dt.month
        self.df["quarter"] = self.df["date"].dt.quarter
        self.df["regime_post_2016"] = (self.df["date"] >= REGIME_BREAK_DATE).astype(int)

        # Month + Quarter dummies (as requested)
        month_dummies = pd.get_dummies(self.df["month"], prefix="m", drop_first=False)
        quarter_dummies = pd.get_dummies(self.df["quarter"], prefix="q", drop_first=False)
        self.df = pd.concat([self.df, month_dummies, quarter_dummies], axis=1)

        # --- Nonlinearity ---
        # RSI (14)
        self.df["rsi_14"] = g["close"].transform(lambda x: _compute_rsi(x, RSI_WINDOW))

        # Momentum × Volatility interaction (use 60d momentum × 20d vol)
        self.df["mom60_x_vol20"] = self.df["mom_60"] * self.df["vol_20"]

        print("Feature computation complete.")

    def compute_target(self):
        print("Computing target: 252-day forward log return (per symbol)...")
        g = self.df.groupby("symbol")
        self.df["target_252d"] = g["close"].transform(lambda x: np.log(x.shift(-252) / x))
        print("Target computation complete.")

    def finalize(self):
        print("Finalizing dataset (dropping invalid rows)...")

        # Drop rows where target is missing (last 252 rows per symbol)
        # Drop rows where rolling features are missing (first max window per symbol)
        # Keep macro NaNs? You can drop them now or later; recommended to drop here.
        macro_cols = ["gdp", "inflation_rate", "interest_rate", "exchange_rate", "unemployment_rate"]
        existing_macro = [c for c in macro_cols if c in self.df.columns]

        # Drop if any engineered features/target are NaN; and also drop macro-missing rows
        self.df = self.df.dropna(subset=["target_252d"] + existing_macro)
        self.df = self.df.dropna().reset_index(drop=True)

        print(f"Final rows: {len(self.df)}")

    def save(self, output_file: Path = MODELING_DATASET_FILE):
        output_file.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(output_file, index=False)
        print(f"Saved: {output_file}")


if __name__ == "__main__":
    fe = FeatureEngineer()
    fe.load()
    fe.compute_features()
    fe.compute_target()
    fe.finalize()
    fe.save()
