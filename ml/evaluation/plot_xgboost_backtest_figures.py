from pathlib import Path
import sys
import json

import pandas as pd
import matplotlib.pyplot as plt


# =====================================================
# Make project root importable when running directly
# =====================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))


from config.paths import (
    XGBOOST_BACKTEST_DOCS_DIR,
    XGBOOST_BACKTEST_FIGURES_DIR,
    XGBOOST_BACKTEST_SUMMARY_FILE,
    XGBOOST_PORTFOLIO_BACKTEST_FILE,
)


# =====================================================
# Visual Settings
# =====================================================
COLORS = {
    "Top": "#2E7D32",
    "Benchmark": "#1565C0",
    "Bottom": "#C62828",
    "Active": "#6A1B9A",
    "LongShort": "#EF6C00",
    "Neutral": "#424242",
}

DPI = 300


# =====================================================
# Helpers
# =====================================================
def ensure_dirs():
    XGBOOST_BACKTEST_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    XGBOOST_BACKTEST_FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    return pd.read_csv(path)


def pick_col(df: pd.DataFrame, candidates: list[str]) -> str:
    for col in candidates:
        if col in df.columns:
            return col

    raise ValueError(
        f"None of these columns found: {candidates}\n"
        f"Available columns: {list(df.columns)}"
    )


def get_rebalance_col(df: pd.DataFrame) -> str:
    return pick_col(df, ["fold", "rebalance", "rebalance_id", "date"])


def add_value_labels(ax, bars, fmt="{:.2%}"):
    for bar in bars:
        value = bar.get_height()
        offset = abs(value) * 0.03 if value != 0 else 0.01

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + offset,
            fmt.format(value),
            ha="center",
            va="bottom",
            fontsize=9,
        )


# =====================================================
# Figure 1: Average Forward Returns
# =====================================================
def plot_average_forward_returns(summary: dict):
    data = pd.DataFrame([
        {
            "portfolio": "Top 20%",
            "return": summary["avg_top_return"],
        },
        {
            "portfolio": "Benchmark",
            "return": summary["avg_benchmark_return"],
        },
        {
            "portfolio": "Bottom 20%",
            "return": summary["avg_bottom_return"],
        },
    ])

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(
        data["portfolio"],
        data["return"],
        color=[COLORS["Top"], COLORS["Benchmark"], COLORS["Bottom"]],
    )

    add_value_labels(ax, bars)

    ax.set_title(
        "Average Forward Returns by Portfolio Group",
        fontsize=13,
        fontweight="bold",
    )
    ax.set_xlabel("Portfolio Group")
    ax.set_ylabel("Average Forward Return")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    output_path = XGBOOST_BACKTEST_FIGURES_DIR / "avg_forward_returns.png"
    plt.savefig(output_path, dpi=DPI)
    plt.close()

    print(f"Saved: {output_path}")


# =====================================================
# Figure 2: Active Return by Rebalance
# =====================================================
def plot_active_return_by_rebalance(df: pd.DataFrame):
    rebalance_col = get_rebalance_col(df)
    active_col = pick_col(df, ["active_return", "active_after_cost"])

    plot_df = df.copy()

    if rebalance_col == "date":
        plot_df[rebalance_col] = pd.to_datetime(plot_df[rebalance_col])
        plot_df = plot_df.sort_values(rebalance_col)
        plot_df["rebalance_label"] = plot_df[rebalance_col].dt.strftime("%Y-%m-%d")
        x_col = "rebalance_label"
    else:
        plot_df = plot_df.sort_values(rebalance_col)
        x_col = rebalance_col

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.bar(
        plot_df[x_col],
        plot_df[active_col],
        color=[
            COLORS["Top"] if value >= 0 else COLORS["Bottom"]
            for value in plot_df[active_col]
        ],
    )

    ax.axhline(0, linestyle="--", linewidth=1.2, color=COLORS["Neutral"])

    ax.set_title(
        "Active Return by Rebalance Period",
        fontsize=13,
        fontweight="bold",
    )
    ax.set_xlabel("Rebalance Period")
    ax.set_ylabel("Top Portfolio Return - Benchmark Return")
    ax.grid(axis="y", alpha=0.3)

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_path = XGBOOST_BACKTEST_FIGURES_DIR / "active_return_by_rebalance.png"
    plt.savefig(output_path, dpi=DPI)
    plt.close()

    print(f"Saved: {output_path}")

# =====================================================
# Figure 3: Long-Short Spread by Rebalance
# =====================================================
def plot_long_short_spread_by_rebalance(df: pd.DataFrame):
    rebalance_col = get_rebalance_col(df)
    spread_col = pick_col(df, ["long_short_spread", "long_short_after_cost"])

    plot_df = df.copy()

    if rebalance_col == "date":
        plot_df[rebalance_col] = pd.to_datetime(plot_df[rebalance_col])
        plot_df = plot_df.sort_values(rebalance_col)
        plot_df["rebalance_label"] = plot_df[rebalance_col].dt.strftime("%Y-%m-%d")
        x_col = "rebalance_label"
    else:
        plot_df = plot_df.sort_values(rebalance_col)
        x_col = rebalance_col

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.bar(
        plot_df[x_col],
        plot_df[spread_col],
        color=[
            COLORS["LongShort"] if value >= 0 else COLORS["Bottom"]
            for value in plot_df[spread_col]
        ],
    )

    ax.axhline(0, linestyle="--", linewidth=1.2, color=COLORS["Neutral"])

    ax.set_title(
        "Long-Short Spread by Rebalance Period",
        fontsize=13,
        fontweight="bold",
    )
    ax.set_xlabel("Rebalance Period")
    ax.set_ylabel("Top 20% Return - Bottom 20% Return")
    ax.grid(axis="y", alpha=0.3)

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_path = XGBOOST_BACKTEST_FIGURES_DIR / "long_short_spread_by_rebalance.png"
    plt.savefig(output_path, dpi=DPI)
    plt.close()

    print(f"Saved: {output_path}")


# =====================================================
# Figure 4: Indicative Cumulative Performance
# =====================================================
def plot_indicative_cumulative_performance(df: pd.DataFrame):
    rebalance_col = get_rebalance_col(df)

    top_col = pick_col(df, ["top_return_after_cost", "top_return"])
    benchmark_col = pick_col(df, ["benchmark_return"])
    bottom_col = pick_col(df, ["bottom_return"])

    plot_df = df[[rebalance_col, top_col, benchmark_col, bottom_col]].copy()

    if rebalance_col == "date":
        plot_df[rebalance_col] = pd.to_datetime(plot_df[rebalance_col])
        plot_df = plot_df.sort_values(rebalance_col)
        plot_df["rebalance_label"] = plot_df[rebalance_col].dt.strftime("%Y-%m-%d")
        x_col = "rebalance_label"
    else:
        plot_df = plot_df.sort_values(rebalance_col)
        x_col = rebalance_col

    plot_df["Top 20%"] = (1 + plot_df[top_col]).cumprod()
    plot_df["Benchmark"] = (1 + plot_df[benchmark_col]).cumprod()
    plot_df["Bottom 20%"] = (1 + plot_df[bottom_col]).cumprod()

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.plot(
        plot_df[x_col],
        plot_df["Top 20%"],
        marker="o",
        linewidth=2.2,
        label="Top 20%",
        color=COLORS["Top"],
    )

    ax.plot(
        plot_df[x_col],
        plot_df["Benchmark"],
        marker="o",
        linewidth=2.2,
        label="Benchmark",
        color=COLORS["Benchmark"],
    )

    ax.plot(
        plot_df[x_col],
        plot_df["Bottom 20%"],
        marker="o",
        linewidth=2.2,
        label="Bottom 20%",
        color=COLORS["Bottom"],
    )

    ax.set_title(
        "Indicative Cumulative Performance Across Rebalance Periods",
        fontsize=13,
        fontweight="bold",
    )
    ax.set_xlabel("Rebalance Period")
    ax.set_ylabel("Cumulative Growth of 1.0")
    ax.grid(alpha=0.3)
    ax.legend()

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_path = XGBOOST_BACKTEST_FIGURES_DIR / "indicative_cumulative_performance.png"
    plt.savefig(output_path, dpi=DPI)
    plt.close()

    print(f"Saved: {output_path}")


# =====================================================
# Figure 5: Backtest Summary Table
# =====================================================
def plot_backtest_summary_table(summary: dict):
    rows = [
        ("Rebalance Mode", summary.get("rebalance_mode", "N/A")),
        ("Number of Rebalances", summary.get("n_rebalances", "N/A")),
        ("Avg Top 20% Return", f"{summary['avg_top_return']:.2%}"),
        ("Avg Benchmark Return", f"{summary['avg_benchmark_return']:.2%}"),
        ("Avg Bottom 20% Return", f"{summary['avg_bottom_return']:.2%}"),
        ("Avg Active Return", f"{summary['avg_active_return']:.2%}"),
        ("Avg Long-Short Spread", f"{summary['avg_long_short_spread']:.2%}"),
        ("Avg Top Return After Cost", f"{summary['avg_top_return_after_cost']:.2%}"),
        ("Avg Active Return After Cost", f"{summary['avg_active_after_cost']:.2%}"),
        ("Avg Long-Short After Cost", f"{summary['avg_long_short_after_cost']:.2%}"),
        ("Top Beats Benchmark Rate", f"{summary['top_beats_benchmark_rate']:.2%}"),
        ("Top Beats Bottom Rate", f"{summary['top_beats_bottom_rate']:.2%}"),
        ("Positive Long-Short Rate", f"{summary['positive_long_short_rate']:.2%}"),
    ]

    table_df = pd.DataFrame(rows, columns=["Metric", "Value"])

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.axis("off")

    table = ax.table(
        cellText=table_df.values,
        colLabels=table_df.columns,
        cellLoc="left",
        colLoc="left",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.45)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold", color="white")
            cell.set_facecolor(COLORS["Neutral"])
        elif row in [3, 4, 5, 6, 7]:
            cell.set_facecolor("#E8F5E9")
        else:
            cell.set_facecolor("#F7F7F7" if row % 2 == 0 else "white")

    ax.set_title(
        "XGBoost Portfolio Backtesting Summary",
        fontsize=14,
        fontweight="bold",
        pad=18,
    )

    plt.tight_layout()

    output_path = XGBOOST_BACKTEST_FIGURES_DIR / "xgboost_backtest_summary_table.png"
    plt.savefig(output_path, dpi=DPI)
    plt.close()

    print(f"Saved: {output_path}")


# =====================================================
# Main
# =====================================================
def main():
    ensure_dirs()

    summary = load_json(XGBOOST_BACKTEST_SUMMARY_FILE)
    portfolio_df = read_csv(XGBOOST_PORTFOLIO_BACKTEST_FILE)

    plot_average_forward_returns(summary)
    plot_active_return_by_rebalance(portfolio_df)
    plot_long_short_spread_by_rebalance(portfolio_df)
    plot_indicative_cumulative_performance(portfolio_df)
    plot_backtest_summary_table(summary)

    print("All XGBoost backtesting figures generated successfully.")


if __name__ == "__main__":
    main()