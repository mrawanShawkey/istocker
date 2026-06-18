import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from config.paths import WALKFORWARD_BASELINE_DIR


OUT_DIR = WALKFORWARD_BASELINE_DIR / "xgboost_tuning_visuals"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# Summary comparison
# =========================
summary = pd.DataFrame({
    "version": ["V1", "V2", "V3"],
    "avg_ic": [0.181379, 0.195689, 0.178590],
    "avg_spearman": [0.154177, 0.164362, 0.143696],
    "stability_metric": [1.175202, 1.061773, 0.856451],
    "negative_folds": [1, 3, 3],
})

# Chart 1: Avg IC
plt.figure(figsize=(8, 5))
plt.bar(summary["version"], summary["avg_ic"])
plt.title("Average IC Comparison")
plt.xlabel("Tuning Version")
plt.ylabel("Average IC")
plt.tight_layout()
plt.savefig(OUT_DIR / "avg_ic_comparison.png", dpi=300)
plt.close()

# Chart 2: Avg Spearman
plt.figure(figsize=(8, 5))
plt.bar(summary["version"], summary["avg_spearman"])
plt.title("Average Spearman IC Comparison")
plt.xlabel("Tuning Version")
plt.ylabel("Average Spearman IC")
plt.tight_layout()
plt.savefig(OUT_DIR / "avg_spearman_comparison.png", dpi=300)
plt.close()

# Chart 3: Stability
plt.figure(figsize=(8, 5))
plt.bar(summary["version"], summary["stability_metric"])
plt.title("Stability Comparison")
plt.xlabel("Tuning Version")
plt.ylabel("ICIR / Date Spearman ICIR")
plt.tight_layout()
plt.savefig(OUT_DIR / "stability_comparison.png", dpi=300)
plt.close()

# Chart 4: Negative folds
plt.figure(figsize=(8, 5))
plt.bar(summary["version"], summary["negative_folds"])
plt.title("Negative Spearman Folds")
plt.xlabel("Tuning Version")
plt.ylabel("Number of Negative Folds")
plt.tight_layout()
plt.savefig(OUT_DIR / "negative_folds_comparison.png", dpi=300)
plt.close()


# =========================
# Per-fold comparison
# =========================
folds = list(range(1, 16))

v1_spearman = [
    0.014508, 0.399397, 0.313938, 0.186057, 0.352892,
    0.095994, 0.177328, 0.215435, 0.130131, 0.050776,
    0.084558, 0.117181, -0.087111, 0.204330, 0.057243
]

v2_spearman = [
    -0.0196, 0.3978, 0.3358, 0.2598, 0.4406,
    -0.0227, 0.2249, 0.2464, 0.1162, 0.0724,
    0.0808, 0.1453, -0.0736, 0.2010, 0.0603
]

v3_global_spearman = [
    0.1052, 0.2184, 0.3806, 0.3759, 0.1915,
    0.2434, 0.1473, 0.1031, 0.0381, -0.1435,
    0.1106, 0.1308, -0.0483, 0.2572, 0.0453
]

v3_date_spearman = [
    0.1882, 0.2269, 0.3850, 0.3327, 0.2628,
    0.0056, 0.1519, 0.2633, 0.3397, -0.0830,
    0.0711, -0.0720, -0.0998, 0.1154, 0.0043
]

per_fold = pd.DataFrame({
    "fold": folds,
    "V1 Spearman": v1_spearman,
    "V2 Spearman": v2_spearman,
    "V3 Global Spearman": v3_global_spearman,
    "V3 Date Spearman": v3_date_spearman,
})

# Chart 5: Per-fold Spearman comparison
plt.figure(figsize=(11, 6))
plt.plot(per_fold["fold"], per_fold["V1 Spearman"], marker="o", label="V1 Spearman")
plt.plot(per_fold["fold"], per_fold["V2 Spearman"], marker="o", label="V2 Spearman")
plt.plot(per_fold["fold"], per_fold["V3 Global Spearman"], marker="o", label="V3 Global Spearman")
plt.axhline(0, linestyle="--", linewidth=1)
plt.title("Per-Fold Spearman IC Comparison")
plt.xlabel("Fold")
plt.ylabel("Spearman IC")
plt.xticks(folds)
plt.legend()
plt.tight_layout()
plt.savefig(OUT_DIR / "per_fold_spearman_comparison.png", dpi=300)
plt.close()

# Chart 6: V3 Global vs Date Spearman
plt.figure(figsize=(11, 6))
plt.plot(per_fold["fold"], per_fold["V3 Global Spearman"], marker="o", label="V3 Global Spearman")
plt.plot(per_fold["fold"], per_fold["V3 Date Spearman"], marker="o", label="V3 Date Spearman")
plt.axhline(0, linestyle="--", linewidth=1)
plt.title("V3 Global vs Per-Date Spearman IC")
plt.xlabel("Fold")
plt.ylabel("Spearman IC")
plt.xticks(folds)
plt.legend()
plt.tight_layout()
plt.savefig(OUT_DIR / "v3_global_vs_date_spearman.png", dpi=300)
plt.close()


summary.to_csv(OUT_DIR / "xgboost_tuning_summary.csv", index=False)
per_fold.to_csv(OUT_DIR / "xgboost_per_fold_comparison.csv", index=False)

print(f"Visualizations saved to: {OUT_DIR}")