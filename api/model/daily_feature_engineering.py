from __future__ import annotations

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from api.app import db
from api.models import StockPrice
from api.market.repositories import get_latest_date
from config.paths import MACRO_DATA


# =====================================================
# Constants
# =====================================================
IDENTIFIER_COLUMNS = ["date", "symbol"]

BASE_REQUIRED_COLUMNS = [
    "date",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
]

MACRO_FEATURES = [
    "exchange_rate",
    "gdp",
    "inflation_rate",
    "interest_rate",
    "unemployment_rate",
]

FINAL_MODEL_FEATURES = [
    "atr_14",
    "exchange_rate",
    "gdp",
    "inflation_rate",
    "interest_rate",
    "ma_60_slope",
    "mom60_x_vol20",
    "mom_126",
    "mom_252",
    "month",
    "price_to_ma252",
    "realized_vol_20",
    "unemployment_rate",
    "vol_60",
    "volume",
]

OUTPUT_COLUMNS = IDENTIFIER_COLUMNS + FINAL_MODEL_FEATURES

MA_SLOPE_LAG = 5


# =====================================================
# Database Loading
# =====================================================
def get_last_2_market_years() -> pd.DataFrame:
    """
    Load the last two calendar years of historical OHLCV data from the database.

    This is required because production features use rolling windows up to
    252 trading days. We should not use only today's row.
    """

    latest_date = get_latest_date()

    if latest_date is None:
        return pd.DataFrame()

    latest_date = pd.to_datetime(latest_date).date()
    cutoff_date = latest_date - relativedelta(years=2)

    stmt = (
        db.select(StockPrice)
        .where(StockPrice.date >= cutoff_date)
        .order_by(StockPrice.symbol.asc(), StockPrice.date.asc())
    )

    rows = db.session.execute(stmt).scalars().all()

    data = []

    for row in rows:
        data.append(
            {
                "date": row.date,
                "symbol": row.symbol,
                "open": row.open,
                "high": row.high,
                "low": row.low,
                "close": row.close,
                "volume": row.volume,
            }
        )

    df = pd.DataFrame(data)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])

    return df


# =====================================================
# Macro Loading / Merging
# =====================================================
def load_macro_data() -> pd.DataFrame:
    """
    Load yearly macro data from the configured macro Excel file.

    Expected macro columns after normalization:
        year
        exchange_rate
        gdp
        inflation_rate
        interest_rate
        unemployment_rate
    """

    if not MACRO_DATA.exists():
        raise FileNotFoundError(f"Macro data file not found: {MACRO_DATA}")

    macro_df = pd.read_excel(MACRO_DATA)

    macro_df.columns = (
        macro_df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # If there is no explicit year column, derive it from date
    if "year" not in macro_df.columns:
        if "date" in macro_df.columns:
            macro_df["date"] = pd.to_datetime(macro_df["date"], errors="coerce")
            macro_df["year"] = macro_df["date"].dt.year
        else:
            raise ValueError(
                "Macro data must contain either a 'year' column or a 'date' column."
            )

    required_cols = ["year"] + MACRO_FEATURES
    missing = [col for col in required_cols if col not in macro_df.columns]

    if missing:
        raise ValueError(
            f"Missing required macro columns: {missing}. "
            f"Available columns: {list(macro_df.columns)}"
        )

    macro_df = macro_df[required_cols].copy()
    macro_df["year"] = macro_df["year"].astype(int)

    # One macro row per year
    macro_df = (
        macro_df.sort_values("year")
        .drop_duplicates(subset=["year"], keep="last")
        .reset_index(drop=True)
    )

    return macro_df


def merge_macro_by_year(
    market_df: pd.DataFrame,
    macro_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge yearly macro features into market data.

    If the latest market year does not exist in the macro file yet,
    the latest available previous macro year is used.
    """

    if market_df.empty:
        return market_df

    market_df = market_df.copy()
    macro_df = macro_df.copy()

    market_df["date"] = pd.to_datetime(market_df["date"], errors="coerce")
    market_df["year"] = market_df["date"].dt.year.astype(int)

    macro_df["year"] = macro_df["year"].astype(int)
    macro_df = macro_df.sort_values("year").reset_index(drop=True)

    # merge_asof requires sorting by the merge key
    market_df = market_df.sort_values("year").reset_index(drop=True)

    out = pd.merge_asof(
        market_df,
        macro_df[["year"] + MACRO_FEATURES],
        on="year",
        direction="backward",
    )

    missing_after_merge = [
        col for col in MACRO_FEATURES
        if col not in out.columns or out[col].isna().any()
    ]

    if missing_after_merge:
        raise ValueError(
            f"Macro merge still has missing values: {missing_after_merge}. "
            "Check that macro data covers the market date range."
        )

    out = out.drop(columns=["year"], errors="ignore")
    out = out.sort_values(["symbol", "date"]).reset_index(drop=True)

    return out


def get_last_2_market_years_with_macro() -> pd.DataFrame:
    """
    Load last two years of OHLCV data from DB and merge yearly macro features.

    This dataframe is ready to be passed into build_production_features().
    """

    market_df = get_last_2_market_years()

    if market_df.empty:
        return market_df

    macro_df = load_macro_data()
    combined_df = merge_macro_by_year(market_df, macro_df)

    return combined_df


# =====================================================
# Feature Engineering Helpers
# =====================================================
def _missing_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    """Return requested columns that are absent from a dataframe."""
    return [column for column in columns if column not in df.columns]


def _compute_atr(group: pd.DataFrame, window: int = 14) -> pd.Series:
    """Compute Average True Range for one symbol using high, low, and close."""

    high = group["high"]
    low = group["low"]
    close = group["close"]
    previous_close = close.shift(1)

    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return true_range.rolling(window).mean()


def validate_required_features(df: pd.DataFrame) -> None:
    """Raise a clear error if any final model feature is missing."""

    missing = _missing_columns(df, FINAL_MODEL_FEATURES)

    if missing:
        macro_missing = [feature for feature in missing if feature in MACRO_FEATURES]

        message = f"Missing required production model features: {missing}"

        if macro_missing:
            message += (
                ". Macro features must be merged into the historical market "
                "data before inference; they are not generated from OHLCV."
            )

        raise ValueError(message)


def get_latest_features_per_symbol(features_df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the most recent engineered row for each stock symbol."""

    missing = _missing_columns(features_df, IDENTIFIER_COLUMNS)

    if missing:
        raise ValueError(f"Missing identifier columns: {missing}")

    latest_df = (
        features_df.sort_values(["symbol", "date"])
        .groupby("symbol", as_index=False, group_keys=False)
        .tail(1)
        .reset_index(drop=True)
    )

    return latest_df


# =====================================================
# Main Production Feature Engineering
# =====================================================
def build_production_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the final production feature rows expected by the XGBoost model.

    The input must contain historical daily rows, not just today's row, because
    the model depends on rolling windows up to 252 trading days.

    Missing feature values are intentionally left as NaN so the inference stage
    can fill them using feature_medians.json.
    """

    missing_base = _missing_columns(df, BASE_REQUIRED_COLUMNS)

    if missing_base:
        raise ValueError(f"Missing required historical market columns: {missing_base}")

    missing_macro = _missing_columns(df, MACRO_FEATURES)

    if missing_macro:
        raise ValueError(
            "Missing macro columns required by the final model: "
            f"{missing_macro}. Merge macro features before calling "
            "build_production_features()."
        )

    features_df = df.copy()

    features_df["date"] = pd.to_datetime(features_df["date"], errors="coerce")
    features_df = features_df.sort_values(["symbol", "date"]).reset_index(drop=True)

    grouped = features_df.groupby("symbol", group_keys=False)

    close = features_df["close"]

    # Returns
    features_df["simple_return_1d"] = grouped["close"].pct_change()
    features_df["log_return_1d"] = grouped["close"].transform(
        lambda series: np.log(series / series.shift(1))
    )

    # Momentum
    features_df["mom_60"] = grouped["close"].transform(
        lambda series: np.log(series / series.shift(60))
    )

    features_df["mom_126"] = grouped["close"].transform(
        lambda series: np.log(series / series.shift(126))
    )

    features_df["mom_252"] = grouped["close"].transform(
        lambda series: np.log(series / series.shift(252))
    )

    # Moving averages / trend
    features_df["ma_60"] = grouped["close"].transform(
        lambda series: series.rolling(60).mean()
    )

    features_df["ma_252"] = grouped["close"].transform(
        lambda series: series.rolling(252).mean()
    )

    features_df["price_to_ma252"] = close / features_df["ma_252"]

    features_df["ma_60_slope"] = grouped["ma_60"].transform(
        lambda series: series - series.shift(MA_SLOPE_LAG)
    )

    # Volatility
    features_df["vol_20"] = grouped["log_return_1d"].transform(
        lambda series: series.rolling(20).std()
    )

    features_df["vol_60"] = grouped["log_return_1d"].transform(
        lambda series: series.rolling(60).std()
    )

    features_df["realized_vol_20"] = grouped["log_return_1d"].transform(
        lambda series: np.sqrt((series**2).rolling(20).sum())
    )

    # ATR
    features_df["atr_14"] = (
        grouped[["high", "low", "close"]]
        .apply(lambda group: _compute_atr(group, window=14))
        .reset_index(level=0, drop=True)
    )

    # Interaction feature
    features_df["mom60_x_vol20"] = features_df["mom_60"] * features_df["vol_20"]

    # Calendar
    features_df["month"] = features_df["date"].dt.month

    # Safety cleanup
    features_df = features_df.replace([np.inf, -np.inf], np.nan)

    validate_required_features(features_df)

    latest_df = get_latest_features_per_symbol(features_df)

    return latest_df[OUTPUT_COLUMNS]


# =====================================================
# CLI Smoke Test
# =====================================================
def _main() -> None:
    """Run a lightweight CLI smoke test for production feature creation."""

    print("Loading last two market years from database...")
    print("Merging macro features from MACRO_DATA...")

    df = get_last_2_market_years_with_macro()

    if df.empty:
        print("No market data found in database.")
        return

    print(f"Input source: database StockPrice + {MACRO_DATA}")
    print(f"Input rows: {len(df):,}")
    print(f"Number of symbols: {df['symbol'].nunique()}")

    dates = pd.to_datetime(df["date"], errors="coerce")
    print(f"Date range: {dates.min().date()} to {dates.max().date()}")
    print(f"Latest date: {dates.max().date()}")

    missing_input_features = _missing_columns(df, MACRO_FEATURES)

    if missing_input_features:
        print(f"Missing macro features: {missing_input_features}")
        return

    latest_features = build_production_features(df)

    missing_output_features = _missing_columns(
        latest_features,
        FINAL_MODEL_FEATURES,
    )

    print(f"Output shape: {latest_features.shape}")
    print(f"Output columns: {list(latest_features.columns)}")
    print(f"Missing required features, if any: {missing_output_features}")

    print("\nPreview of latest engineered rows:")
    print(latest_features.head().to_string(index=False))


if __name__ == "__main__":
    _main()