"""
plot_final_production_figures.py

Creates production documentation figures for:
6.6 Final Model Training and Production Serialization

Usage:
    python -m ml.evaluation.plot_final_production_figures
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from config.paths import (
    XGBOOST_FINAL_FIGURES_DIR,
    XGB_MODEL,
    XGB_MODEL_META,
    XGB_FEATURE_COLUMNS,
    XGB_FEATURE_MEDIANS,
    XGB_FINAL_PARAMS,
)


DPI = 300


# =====================================================
# Helpers
# =====================================================
def ensure_output_dir():
    XGBOOST_FINAL_FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def save_figure(fig, filename):
    output_path = XGBOOST_FINAL_FIGURES_DIR / filename
    fig.savefig(output_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output_path}")


def draw_box(ax, x, y, w, h, text, fontsize=10):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.03,rounding_size=0.03",
        linewidth=1.5,
        edgecolor="#263238",
        facecolor="#E3F2FD",
    )
    ax.add_patch(box)

    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color="#102027",
        wrap=True,
    )


def draw_arrow(ax, start, end):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=18,
        linewidth=1.4,
        color="#37474F",
    )
    ax.add_patch(arrow)


def setup_canvas(width=12, height=7):
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


# =====================================================
# Figure 1: Final Retraining Workflow
# =====================================================
def plot_final_retraining_workflow():
    fig, ax = setup_canvas(width=12, height=7)

    ax.set_title(
        "Final Model Retraining Workflow",
        fontsize=15,
        fontweight="bold",
        pad=20,
    )

    boxes = [
        (
            0.08,
            0.72,
            "Selected Tuned\nXGBoost V1\nConfiguration",
        ),
        (
            0.32,
            0.72,
            "Load Full Modeling\nDataset\n2003-06-16 to 2025-05-28",
        ),
        (
            0.56,
            0.72,
            "Apply Stable\nFeature Set\nfrequency > 0.6",
        ),
        (
            0.32,
            0.38,
            "Internal Validation\nLast 15% of Data\nEarly Stopping = 30",
        ),
        (
            0.56,
            0.38,
            "Select Final\nn_estimators\n33 Trees",
        ),
        (
            0.80,
            0.38,
            "Retrain Final Model\non All Available\nRows",
        ),
        (
            0.80,
            0.08,
            "Save Production\nArtifacts",
        ),
    ]

    w, h = 0.16, 0.16

    for x, y, text in boxes:
        draw_box(ax, x, y, w, h, text)

    # Top row arrows
    draw_arrow(ax, (0.24, 0.80), (0.32, 0.80))
    draw_arrow(ax, (0.48, 0.80), (0.56, 0.80))

    # Down arrow
    draw_arrow(ax, (0.64, 0.72), (0.40, 0.54))

    # Bottom row arrows
    draw_arrow(ax, (0.48, 0.46), (0.56, 0.46))
    draw_arrow(ax, (0.72, 0.46), (0.80, 0.46))

    # Save arrow
    draw_arrow(ax, (0.88, 0.38), (0.88, 0.24))

    save_figure(fig, "final_retraining_workflow.png")


# =====================================================
# Figure 2: Production Artifact Structure
# =====================================================
def plot_production_artifact_structure():
    fig, ax = setup_canvas(width=12, height=7)

    ax.set_title(
        "Final Production Artifact Structure",
        fontsize=15,
        fontweight="bold",
        pad=20,
    )

    tree_text = (
        "data/ml_data/artifacts/xgboost/final\n"
        "├── docs\n"
        "│   ├── feature_columns.json\n"
        "│   ├── feature_medians.json\n"
        "│   ├── model_metadata.json\n"
        "│   └── xgboost_final_params.json\n"
        "├── figures\n"
        "└── model\n"
        "    └── xgboost_model.json"
    )

    ax.text(
        0.06,
        0.55,
        tree_text,
        fontsize=13,
        family="monospace",
        va="center",
        ha="left",
        color="#102027",
        bbox=dict(
            boxstyle="round,pad=0.6",
            facecolor="#F5F5F5",
            edgecolor="#263238",
            linewidth=1.5,
        ),
    )

    summary = (
        "Production assets are separated from experimental results.\n\n"
        "Model file stores the trained XGBoost structure.\n"
        "Docs files store schema, medians, parameters, and metadata.\n"
        "Figures folder stores documentation visuals."
    )

    ax.text(
        0.63,
        0.55,
        summary,
        fontsize=11,
        va="center",
        ha="left",
        color="#102027",
        bbox=dict(
            boxstyle="round,pad=0.6",
            facecolor="#E8F5E9",
            edgecolor="#263238",
            linewidth=1.5,
        ),
    )

    save_figure(fig, "production_artifact_structure.png")


# =====================================================
# Figure 3: Deployment Inference Pipeline
# =====================================================
def plot_deployment_inference_pipeline():
    fig, ax = setup_canvas(width=13, height=7)

    ax.set_title(
        "Deployment-Ready Inference Pipeline",
        fontsize=15,
        fontweight="bold",
        pad=20,
    )

    boxes = [
        (0.05, 0.68, "Load\nxgboost_model.json"),
        (0.25, 0.68, "Load\nfeature_columns.json"),
        (0.45, 0.68, "Load\nfeature_medians.json"),
        (0.65, 0.68, "Prepare Latest\nMarket Features"),
        (0.25, 0.34, "Align Columns\nto Saved Feature\nOrder"),
        (0.45, 0.34, "Replace Infinite\nValues and Fill\nMissing Values"),
        (0.65, 0.34, "Generate\nPredictions"),
        (0.85, 0.34, "Rank Stocks and\nReturn\nRecommendations"),
    ]

    w, h = 0.14, 0.16

    for x, y, text in boxes:
        draw_box(ax, x, y, w, h, text, fontsize=9.5)

    # Top arrows
    draw_arrow(ax, (0.19, 0.76), (0.25, 0.76))
    draw_arrow(ax, (0.39, 0.76), (0.45, 0.76))
    draw_arrow(ax, (0.59, 0.76), (0.65, 0.76))

    # Down from market features to align
    draw_arrow(ax, (0.72, 0.68), (0.32, 0.50))

    # Bottom arrows
    draw_arrow(ax, (0.39, 0.42), (0.45, 0.42))
    draw_arrow(ax, (0.59, 0.42), (0.65, 0.42))
    draw_arrow(ax, (0.79, 0.42), (0.85, 0.42))

    save_figure(fig, "deployment_inference_pipeline.png")


# =====================================================
# Figure 4: Final Feature Groups
# =====================================================
def plot_final_feature_groups():
    feature_groups = {
        "Momentum": ["mom_126", "mom_252", "mom60_x_vol20"],
        "Volatility\nand Risk": ["atr_14", "realized_vol_20", "vol_60"],
        "Trend": ["ma_60_slope", "price_to_ma252"],
        "Volume": ["volume"],
        "Macroeconomic": [
            "exchange_rate",
            "gdp",
            "inflation_rate",
            "interest_rate",
            "unemployment_rate",
        ],
        "Calendar": ["month"],
    }

    groups = list(feature_groups.keys())
    counts = [len(feature_groups[group]) for group in groups]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(groups, counts, color="#1565C0", edgecolor="#263238")

    ax.set_title(
        "Final Production Feature Groups",
        fontsize=15,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Feature Group")
    ax.set_ylabel("Number of Features")
    ax.set_ylim(0, max(counts) + 1)
    ax.grid(axis="y", alpha=0.25)

    for bar, value in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.08,
            str(value),
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    plt.tight_layout()
    save_figure(fig, "final_feature_groups.png")


# =====================================================
# Optional Validation: Check Artifact Files
# =====================================================
def validate_artifacts_exist():
    paths = [
        XGB_MODEL,
        XGB_MODEL_META,
        XGB_FEATURE_COLUMNS,
        XGB_FEATURE_MEDIANS,
        XGB_FINAL_PARAMS,
    ]

    missing = [path for path in paths if not path.exists()]

    if missing:
        print("Warning: Some production artifacts are missing:")
        for path in missing:
            print(f"  - {path}")
    else:
        print("All production artifacts found.")


# =====================================================
# Main
# =====================================================
def main():
    ensure_output_dir()
    validate_artifacts_exist()

    plot_final_retraining_workflow()
    plot_production_artifact_structure()
    plot_deployment_inference_pipeline()
    plot_final_feature_groups()

    print("\nDone. Figures saved to:")
    print(XGBOOST_FINAL_FIGURES_DIR)


if __name__ == "__main__":
    main()
