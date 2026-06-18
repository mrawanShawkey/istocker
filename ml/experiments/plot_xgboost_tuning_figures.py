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
    # Summary files
    XGBOOST_TUNED_SUMMARY_FILE,
    XGBOOST_TUNED_V2_SUMMARY_FILE,
    XGBOOST_TUNED_V3_SUMMARY_FILE,

    # Per-fold result files
    XGBOOST_TUNED_RESULTS_FILE,
    XGBOOST_TUNED_V2_RESULTS_FILE,
    XGBOOST_TUNED_V3_RESULTS_FILE,

    # Params files
    XGBOOST_BEST_PARAMS_FILE,
    XGBOOST_BEST_PARAMS_V2_FILE,
    XGBOOST_BEST_PARAMS_V3_FILE,

    # Version figure folders
    XGBOOST_TUNING_V1_FIGURES_DIR,
    XGBOOST_TUNING_V2_FIGURES_DIR,
    XGBOOST_TUNING_V3_FIGURES_DIR,

    # Comparison output folders
    XGBOOST_TUNING_COMPARISON_DOCS_DIR,
    XGBOOST_TUNING_COMPARISON_FIGURES_DIR,
)


# =====================================================
# Visual Settings
# =====================================================
COLORS = {
    "V1": "#2E7D32",       # green - selected
    "V2": "#1565C0",       # blue
    "V3": "#EF6C00",       # orange
    "IC": "#6A1B9A",       # purple
    "Spearman": "#00838F", # teal
    "Negative": "#C62828", # red
    "Neutral": "#424242",  # dark gray
}

DPI = 300


# =====================================================
# Helpers
# =====================================================
def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    return pd.read_csv(path)


def ensure_dirs():
    for folder in [
        XGBOOST_TUNING_V1_FIGURES_DIR,
        XGBOOST_TUNING_V2_FIGURES_DIR,
        XGBOOST_TUNING_V3_FIGURES_DIR,
        XGBOOST_TUNING_COMPARISON_DOCS_DIR,
        XGBOOST_TUNING_COMPARISON_FIGURES_DIR,
    ]:
        folder.mkdir(parents=True, exist_ok=True)


def find_column(df: pd.DataFrame, candidates: list[str], keyword: str | None = None):
    for col in candidates:
        if col in df.columns:
            return col

    if keyword:
        for col in df.columns:
            if keyword.lower() in col.lower():
                return col

    return None


def add_value_labels(ax, bars, fmt="{:.4f}"):
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


def save_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    ylabel: str,
    output_path: Path,
    color: str | list[str],
    value_format: str = "{:.4f}",
):
    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(df[x_col], df[y_col], color=color)
    add_value_labels(ax, bars, value_format)

    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Tuning Version")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI)
    plt.close()

    print(f"Saved: {output_path}")


def save_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list[str],
    title: str,
    ylabel: str,
    output_path: Path,
    colors: list[str],
):
    fig, ax = plt.subplots(figsize=(11, 6))

    for col, color in zip(y_cols, colors):
        ax.plot(
            df[x_col],
            df[col],
            marker="o",
            linewidth=2.2,
            label=col,
            color=color,
        )

    ax.axhline(0, linestyle="--", linewidth=1.2, color=COLORS["Negative"])
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Walk-Forward Fold")
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI)
    plt.close()

    print(f"Saved: {output_path}")


# =====================================================
# Build Summary Data
# =====================================================
def build_summary_dataframe() -> pd.DataFrame:
    v1 = load_json(XGBOOST_TUNED_SUMMARY_FILE)
    v2 = load_json(XGBOOST_TUNED_V2_SUMMARY_FILE)
    v3 = load_json(XGBOOST_TUNED_V3_SUMMARY_FILE)

    summary_df = pd.DataFrame([
        {
            "version": "V1",
            "avg_ic": v1["avg_ic"],
            "avg_spearman": v1["avg_spearman_ic"],
            "stability": v1["spearman_icir"],
            "negative_folds": v1["negative_spearman_folds"],
            "decision": "Selected",
        },
        {
            "version": "V2",
            "avg_ic": v2["avg_ic"],
            "avg_spearman": v2["avg_spearman_ic"],
            "stability": v2["spearman_icir"],
            "negative_folds": v2["negative_spearman_folds"],
            "decision": "Rejected",
        },
        {
            "version": "V3",
            "avg_ic": v3["avg_ic"],
            "avg_spearman": v3["avg_date_spearman_ic"],
            "stability": v3["date_spearman_icir"],
            "negative_folds": v3["negative_date_spearman_folds"],
            "decision": "Rejected",
        },
    ])

    output_file = (
        XGBOOST_TUNING_COMPARISON_DOCS_DIR
        / "xgboost_tuning_summary.csv"
    )

    summary_df.to_csv(output_file, index=False)
    print(f"Saved: {output_file}")

    return summary_df


# =====================================================
# Individual Version Graphs
# =====================================================
def plot_v1_graphs():
    df = read_csv(XGBOOST_TUNED_RESULTS_FILE)

    spearman_col = find_column(df, ["spearman_ic"], keyword="spearman")
    ic_col = find_column(df, ["ic"], keyword="ic")

    if spearman_col is None:
        raise ValueError("V1 Spearman column not found.")

    v1_df = df[["fold", spearman_col]].rename(
        columns={spearman_col: "V1 Spearman IC"}
    )

    save_line_chart(
        df=v1_df,
        x_col="fold",
        y_cols=["V1 Spearman IC"],
        title="Version 1 Walk-Forward Spearman IC Across Folds",
        ylabel="Spearman IC",
        output_path=XGBOOST_TUNING_V1_FIGURES_DIR / "v1_walkforward_spearman_ic.png",
        colors=[COLORS["V1"]],
    )

    if ic_col is not None:
        summary_df = df[["fold", ic_col, spearman_col]].rename(
            columns={
                ic_col: "Information Coefficient",
                spearman_col: "Spearman IC",
            }
        )

        save_line_chart(
            df=summary_df,
            x_col="fold",
            y_cols=["Information Coefficient", "Spearman IC"],
            title="Version 1 IC and Spearman IC Across Folds",
            ylabel="Metric Value",
            output_path=XGBOOST_TUNING_V1_FIGURES_DIR / "v1_ic_spearman_summary.png",
            colors=[COLORS["IC"], COLORS["Spearman"]],
        )


def plot_v2_graphs():
    df = read_csv(XGBOOST_TUNED_V2_RESULTS_FILE)

    spearman_col = find_column(df, ["spearman_ic"], keyword="spearman")
    ic_col = find_column(df, ["ic"], keyword="ic")

    if spearman_col is None:
        raise ValueError("V2 Spearman column not found.")

    v2_df = df[["fold", spearman_col]].rename(
        columns={spearman_col: "V2 Spearman IC"}
    )

    save_line_chart(
        df=v2_df,
        x_col="fold",
        y_cols=["V2 Spearman IC"],
        title="Version 2 Walk-Forward Spearman IC Across Folds",
        ylabel="Spearman IC",
        output_path=XGBOOST_TUNING_V2_FIGURES_DIR / "v2_walkforward_spearman_ic.png",
        colors=[COLORS["V2"]],
    )

    if ic_col is not None:
        summary_df = df[["fold", ic_col, spearman_col]].rename(
            columns={
                ic_col: "Information Coefficient",
                spearman_col: "Spearman IC",
            }
        )

        save_line_chart(
            df=summary_df,
            x_col="fold",
            y_cols=["Information Coefficient", "Spearman IC"],
            title="Version 2 IC and Spearman IC Across Folds",
            ylabel="Metric Value",
            output_path=XGBOOST_TUNING_V2_FIGURES_DIR / "v2_ic_spearman_summary.png",
            colors=[COLORS["IC"], COLORS["Spearman"]],
        )


def plot_v3_graphs():
    df = read_csv(XGBOOST_TUNED_V3_RESULTS_FILE)

    date_spearman_col = find_column(
        df,
        ["date_spearman_ic", "avg_date_spearman_ic"],
        keyword="date_spearman",
    )

    global_spearman_col = find_column(
        df,
        ["global_spearman_ic", "spearman_ic"],
        keyword="global",
    )

    ic_col = find_column(df, ["ic"], keyword="ic")

    if date_spearman_col is None:
        date_spearman_col = find_column(df, [], keyword="spearman")

    if date_spearman_col is None:
        raise ValueError("V3 date/global Spearman column not found.")

    v3_df = df[["fold", date_spearman_col]].rename(
        columns={date_spearman_col: "V3 Date Spearman IC"}
    )

    save_line_chart(
        df=v3_df,
        x_col="fold",
        y_cols=["V3 Date Spearman IC"],
        title="Version 3 Date-Level Spearman IC Across Folds",
        ylabel="Date-Level Spearman IC",
        output_path=XGBOOST_TUNING_V3_FIGURES_DIR / "v3_walkforward_date_spearman_ic.png",
        colors=[COLORS["V3"]],
    )

    y_cols = []
    colors = []

    if ic_col is not None:
        df = df.rename(columns={ic_col: "Information Coefficient"})
        y_cols.append("Information Coefficient")
        colors.append(COLORS["IC"])

    if global_spearman_col is not None:
        df = df.rename(columns={global_spearman_col: "Global Spearman IC"})
        y_cols.append("Global Spearman IC")
        colors.append(COLORS["Spearman"])

    if date_spearman_col is not None:
        df = df.rename(columns={date_spearman_col: "Date Spearman IC"})
        y_cols.append("Date Spearman IC")
        colors.append(COLORS["V3"])

    if y_cols:
        save_line_chart(
            df=df,
            x_col="fold",
            y_cols=y_cols,
            title="Version 3 IC, Global Spearman, and Date Spearman Across Folds",
            ylabel="Metric Value",
            output_path=XGBOOST_TUNING_V3_FIGURES_DIR / "v3_ic_global_date_spearman_summary.png",
            colors=colors,
        )


# =====================================================
# Comparison Graphs
# =====================================================
def plot_comparison_summary_charts(summary_df: pd.DataFrame):
    version_colors = [
        COLORS["V1"],
        COLORS["V2"],
        COLORS["V3"],
    ]

    save_bar_chart(
        df=summary_df,
        x_col="version",
        y_col="avg_ic",
        title="Average IC Comparison Across Tuning Versions",
        ylabel="Average IC",
        output_path=XGBOOST_TUNING_COMPARISON_FIGURES_DIR / "avg_ic_comparison.png",
        color=version_colors,
    )

    save_bar_chart(
        df=summary_df,
        x_col="version",
        y_col="avg_spearman",
        title="Average Spearman IC Comparison Across Tuning Versions",
        ylabel="Average Spearman IC",
        output_path=XGBOOST_TUNING_COMPARISON_FIGURES_DIR / "avg_spearman_comparison.png",
        color=version_colors,
    )

    save_bar_chart(
        df=summary_df,
        x_col="version",
        y_col="stability",
        title="Stability Comparison Across Tuning Versions",
        ylabel="ICIR / Stability Metric",
        output_path=XGBOOST_TUNING_COMPARISON_FIGURES_DIR / "stability_comparison.png",
        color=version_colors,
    )

    save_bar_chart(
        df=summary_df,
        x_col="version",
        y_col="negative_folds",
        title="Negative Folds Across Tuning Versions",
        ylabel="Number of Negative Folds",
        output_path=XGBOOST_TUNING_COMPARISON_FIGURES_DIR / "negative_folds_comparison.png",
        color=version_colors,
        value_format="{:.0f}",
    )


def plot_v3_global_vs_date():
    v3 = load_json(XGBOOST_TUNED_V3_SUMMARY_FILE)

    df = pd.DataFrame([
        {
            "metric": "Global Spearman IC",
            "value": v3["avg_global_spearman_ic"],
        },
        {
            "metric": "Date Spearman IC",
            "value": v3["avg_date_spearman_ic"],
        },
    ])

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(
        df["metric"],
        df["value"],
        color=[COLORS["Spearman"], COLORS["V3"]],
    )

    add_value_labels(ax, bars, "{:.4f}")

    ax.set_title("V3 Global vs Date-Level Spearman IC", fontsize=13, fontweight="bold")
    ax.set_xlabel("Metric")
    ax.set_ylabel("Average Spearman IC")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    output_path = (
        XGBOOST_TUNING_COMPARISON_FIGURES_DIR
        / "v3_global_vs_date_spearman.png"
    )
    plt.savefig(output_path, dpi=DPI)
    plt.close()

    print(f"Saved: {output_path}")


def build_per_fold_dataframe() -> pd.DataFrame:
    files = [
        {
            "version": "V1",
            "path": XGBOOST_TUNED_RESULTS_FILE,
            "preferred": ["spearman_ic"],
        },
        {
            "version": "V2",
            "path": XGBOOST_TUNED_V2_RESULTS_FILE,
            "preferred": ["spearman_ic"],
        },
        {
            "version": "V3",
            "path": XGBOOST_TUNED_V3_RESULTS_FILE,
            "preferred": [
                "date_spearman_ic",
                "avg_date_spearman_ic",
                "global_spearman_ic",
                "spearman_ic",
            ],
        },
    ]

    frames = []

    for item in files:
        df = read_csv(item["path"])

        if "fold" not in df.columns:
            raise ValueError(f"Missing fold column in {item['path']}")

        spearman_col = find_column(
            df,
            item["preferred"],
            keyword="spearman",
        )

        if spearman_col is None:
            raise ValueError(f"No Spearman column found in {item['path']}")

        temp = df[["fold", spearman_col]].copy()
        temp = temp.rename(
            columns={spearman_col: f"{item['version']} Spearman IC"}
        )

        frames.append(temp)

    final_df = frames[0]

    for frame in frames[1:]:
        final_df = final_df.merge(frame, on="fold", how="outer")

    final_df = final_df.sort_values("fold").reset_index(drop=True)

    output_file = (
        XGBOOST_TUNING_COMPARISON_DOCS_DIR
        / "xgboost_per_fold_comparison.csv"
    )

    final_df.to_csv(output_file, index=False)
    print(f"Saved: {output_file}")

    return final_df


def plot_per_fold_comparison(per_fold_df: pd.DataFrame):
    save_line_chart(
        df=per_fold_df,
        x_col="fold",
        y_cols=[
            "V1 Spearman IC",
            "V2 Spearman IC",
            "V3 Spearman IC",
        ],
        title="Per-Fold Spearman IC Comparison Across Tuning Versions",
        ylabel="Spearman IC",
        output_path=XGBOOST_TUNING_COMPARISON_FIGURES_DIR / "per_fold_spearman_comparison.png",
        colors=[COLORS["V1"], COLORS["V2"], COLORS["V3"]],
    )


def plot_final_decision_tradeoff(summary_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 6))

    sizes = (summary_df["negative_folds"] + 1) * 140
    colors = [COLORS["V1"], COLORS["V2"], COLORS["V3"]]

    ax.scatter(
        summary_df["avg_spearman"],
        summary_df["stability"],
        s=sizes,
        color=colors,
        alpha=0.85,
        edgecolors="black",
        linewidth=0.8,
    )

    for _, row in summary_df.iterrows():
        ax.text(
            row["avg_spearman"],
            row["stability"],
            f"  {row['version']} ({row['decision']})",
            va="center",
            fontsize=10,
            fontweight="bold" if row["version"] == "V1" else "normal",
        )

    ax.set_title("Final Tuning Decision Trade-Off", fontsize=13, fontweight="bold")
    ax.set_xlabel("Average Spearman IC")
    ax.set_ylabel("Stability Metric")
    ax.grid(alpha=0.3)

    note = "Bubble size represents number of negative folds"
    ax.text(
        0.5,
        -0.14,
        note,
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color=COLORS["Neutral"],
    )

    plt.tight_layout()

    output_path = (
        XGBOOST_TUNING_COMPARISON_FIGURES_DIR
        / "final_tuning_decision_tradeoff.png"
    )

    plt.savefig(output_path, dpi=DPI)
    plt.close()

    print(f"Saved: {output_path}")


# =====================================================
# Params / Final Configuration Figures
# =====================================================
def build_params_dataframe() -> pd.DataFrame:
    v1_params = load_json(XGBOOST_BEST_PARAMS_FILE)
    v2_params = load_json(XGBOOST_BEST_PARAMS_V2_FILE)
    v3_params = load_json(XGBOOST_BEST_PARAMS_V3_FILE)

    selected_params = [
        "n_estimators",
        "max_depth",
        "learning_rate",
        "subsample",
        "colsample_bytree",
        "min_child_weight",
        "gamma",
        "reg_alpha",
        "reg_lambda",
    ]

    rows = []

    for param in selected_params:
        rows.append({
            "parameter": param,
            "V1": v1_params.get(param),
            "V2": v2_params.get(param),
            "V3": v3_params.get(param),
        })

    params_df = pd.DataFrame(rows)

    output_file = (
        XGBOOST_TUNING_COMPARISON_DOCS_DIR
        / "xgboost_tuning_params_comparison.csv"
    )

    params_df.to_csv(output_file, index=False)
    print(f"Saved: {output_file}")

    return params_df


def plot_final_selected_params_table():
    params = load_json(XGBOOST_BEST_PARAMS_FILE)

    selected_params = [
        ("Selected Version", "Version 1"),
        ("n_estimators", params["n_estimators"]),
        ("max_depth", params["max_depth"]),
        ("learning_rate", f"{params['learning_rate']:.6f}"),
        ("subsample", f"{params['subsample']:.4f}"),
        ("colsample_bytree", f"{params['colsample_bytree']:.4f}"),
        ("min_child_weight", params["min_child_weight"]),
        ("gamma", f"{params['gamma']:.4f}"),
        ("reg_alpha", f"{params['reg_alpha']:.4f}"),
        ("reg_lambda", f"{params['reg_lambda']:.4f}"),
        ("objective", params["objective"]),
        ("eval_metric", params["eval_metric"]),
        ("tree_method", params["tree_method"]),
    ]

    table_df = pd.DataFrame(selected_params, columns=["Parameter", "Value"])

    fig, ax = plt.subplots(figsize=(9, 6))
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
        elif row == 1:
            cell.set_facecolor("#DDEEDB")
            cell.set_text_props(weight="bold")
        else:
            cell.set_facecolor("#F7F7F7" if row % 2 == 0 else "white")

    ax.set_title(
        "Final Selected XGBoost Configuration",
        fontsize=14,
        fontweight="bold",
        pad=18,
    )

    plt.tight_layout()

    output_path = (
        XGBOOST_TUNING_COMPARISON_FIGURES_DIR
        / "final_selected_xgboost_configuration.png"
    )

    plt.savefig(output_path, dpi=DPI)
    plt.close()

    print(f"Saved: {output_path}")


def plot_params_comparison(params_df: pd.DataFrame):
    normalized_df = params_df.copy()

    for version in ["V1", "V2", "V3"]:
        normalized_df[version] = pd.to_numeric(normalized_df[version], errors="coerce")

    for index, row in normalized_df.iterrows():
        values = row[["V1", "V2", "V3"]].astype(float)
        max_value = values.max()

        if max_value != 0:
            normalized_df.loc[index, ["V1", "V2", "V3"]] = values / max_value

    fig, ax = plt.subplots(figsize=(10, 7))

    y = range(len(normalized_df))
    bar_height = 0.25

    ax.barh(
        [i - bar_height for i in y],
        normalized_df["V1"],
        height=bar_height,
        label="V1",
        color=COLORS["V1"],
    )

    ax.barh(
        y,
        normalized_df["V2"],
        height=bar_height,
        label="V2",
        color=COLORS["V2"],
    )

    ax.barh(
        [i + bar_height for i in y],
        normalized_df["V3"],
        height=bar_height,
        label="V3",
        color=COLORS["V3"],
    )

    ax.set_yticks(list(y))
    ax.set_yticklabels(normalized_df["parameter"])
    ax.set_xlabel("Normalized Parameter Value")
    ax.set_title(
        "Normalized Hyperparameter Comparison Across Tuning Versions",
        fontsize=13,
        fontweight="bold",
    )
    ax.grid(axis="x", alpha=0.3)
    ax.legend()

    plt.tight_layout()

    output_path = (
        XGBOOST_TUNING_COMPARISON_FIGURES_DIR
        / "xgboost_tuning_params_comparison.png"
    )

    plt.savefig(output_path, dpi=DPI)
    plt.close()

    print(f"Saved: {output_path}")


# =====================================================
# Main
# =====================================================
def main():
    ensure_dirs()

    summary_df = build_summary_dataframe()

    # Individual version figures
    plot_v1_graphs()
    plot_v2_graphs()
    plot_v3_graphs()

    # Comparison figures
    plot_comparison_summary_charts(summary_df)
    plot_v3_global_vs_date()

    per_fold_df = build_per_fold_dataframe()
    plot_per_fold_comparison(per_fold_df)

    plot_final_decision_tradeoff(summary_df)

    # Final configuration figures
    params_df = build_params_dataframe()
    plot_final_selected_params_table()
    plot_params_comparison(params_df)

    print("All tuning figures generated successfully.")


if __name__ == "__main__":
    main()