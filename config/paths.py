from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# Data Directories
# -------------------------
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = DATA_DIR / "database_data"
MARKET_DIR = DATA_DIR / "market_data"
ML_DIR = DATA_DIR / "ml_data"
RAW_DIR = MARKET_DIR / "raw"
DAILY_DIR = RAW_DIR / "daily"
PROCESSED_DIR = MARKET_DIR / "processed"
RESULTS_DIR = ML_DIR / "results"
WALKFORWARD_DIR = RESULTS_DIR / "walkforward"

# -------------------------
# Database Seed Files
# -------------------------
OPTIONS = DATABASE_DIR / "options.csv"
QUESTIONS = DATABASE_DIR / "questions.csv"
SECTORS = DATABASE_DIR / "sectors.csv"
STOCKS = DATABASE_DIR / "stocks.csv"

# -------------------------
# Market Data Files
# -------------------------
DATASETS_DIR = ML_DIR / "datasets"
MODELING_DATASET_DIR = DATASETS_DIR / "modeling"
SPLITS_DIR = DATASETS_DIR / "splits"

MODELING_DATASET_FILE = MODELING_DATASET_DIR / "EGX30_modeling_dataset.csv"

CLEAN_MARKET_DATA = PROCESSED_DIR / "egx30_clean.csv"
CLEAN_MARKET_DATA_WITH_MACRO = PROCESSED_DIR / "egx30_with_macro.csv"
RAW_MARKET_DATA = RAW_DIR / "EGX30_Full_Dataset_Ready.csv"
MACRO_DATA = RAW_DIR / "Egypt_Economic_Data.xlsx"

TARGETS_DIR = ML_DIR / "targets"
TARGETS_FILE = TARGETS_DIR / "labels.csv"


# -------------------------
# Features 
# -------------------------
FEATURES_DIR = ML_DIR / "features"

FEATURE_CACHE_DIR = FEATURES_DIR / "cache"
FEATURE_CACHE_FILE = FEATURE_CACHE_DIR / "feature_cache.csv"

FEATURE_STABILITY_DIR = FEATURES_DIR / "stability"
FEATURE_STABILITY_FILE = FEATURE_STABILITY_DIR / "feature_stability.csv"

# -------------------------
# Walk-forward Baseline
# -------------------------
WALKFORWARD_BASELINE_DIR = WALKFORWARD_DIR / "baseline"

WALKFORWARD_BASELINE_DOCS_DIR = WALKFORWARD_BASELINE_DIR / "docs"
WALKFORWARD_BASELINE_FIGURES_DIR = WALKFORWARD_BASELINE_DIR / "figures"

WALKFORWARD_RESULTS_FILE = WALKFORWARD_BASELINE_DOCS_DIR / "walkforward_results.csv"
LSTM_RESULTS_FILE = WALKFORWARD_BASELINE_DOCS_DIR / "lstm_results.csv"
XGBOOST_RESULTS_FILE = WALKFORWARD_BASELINE_DOCS_DIR / "xgboost_results.csv"  
SARIMAX_RESULTS_FILE = WALKFORWARD_BASELINE_DOCS_DIR / "sarimax_results.csv"

# -------------------------
# Model Files
# -------------------------
XGB_MODEL = WALKFORWARD_BASELINE_DIR /"xgboost_production.pkl"
XGB_MODEL_META = WALKFORWARD_BASELINE_DIR / "xgboost_production_meta.json"

# -------------------------
# Model Comparison Results
# -------------------------
MODEL_COMPARISON_DIR = RESULTS_DIR / "model_comparison"
MODEL_COMPARISON_DOCS_DIR = MODEL_COMPARISON_DIR / "docs"
MODEL_COMPARISON_FIGURES_DIR = MODEL_COMPARISON_DIR / "figures"

MODEL_COMPARISON_FILE = MODEL_COMPARISON_DOCS_DIR / "model_comparison.csv"
RESULT_BY_FOLD_FILE = MODEL_COMPARISON_DOCS_DIR / "all_fold_results.csv"

# -------------------------
# EDA Output Folder
# -------------------------
EDA_OUTPUT_DIR = BASE_DIR / "research" / "EDA" / "outputs"
EDA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STAPLE_FEATURES_FILE = EDA_OUTPUT_DIR/ "top_stable_features.csv"



# =====================================================
# General Metadata
# metadata/ should contain dataset-level metadata only
# =====================================================
METADATA_DIR = ML_DIR / "metadata"
DATASET_VERSION_FILE = METADATA_DIR / "dataset_version.json"

# -------------------------
# Ensemble Results
# -------------------------
ENSEMBLES_DIR = WALKFORWARD_DIR / "ensembles"
ENSEMBLES_DOCS_DIR = ENSEMBLES_DIR / "docs"
ENSEMBLES_FIGURES_DIR = ENSEMBLES_DIR / "figures"

ENSEMBLE_EQUAL_WEIGHT_RESULTS_FILE = ENSEMBLES_DOCS_DIR / "ensemble_equal_weight_results.csv"
ENSEMBLE_IC_WEIGHT_RESULTS_FILE = ENSEMBLES_DOCS_DIR / "ensemble_ic_weight_results.csv"
ENSEMBLE_RANK_AVERAGE_RESULTS_FILE = ENSEMBLES_DOCS_DIR / "ensemble_rank_average_results.csv"

# -------------------------
# XGBoost Tuning Results
# -------------------------
TUNING_DIR = WALKFORWARD_DIR / "tuning"

XGBOOST_TUNING_V1_DIR = TUNING_DIR / "v1"
XGBOOST_TUNING_V1_DOCS_DIR = XGBOOST_TUNING_V1_DIR / "docs"
XGBOOST_TUNING_V1_FIGURES_DIR = XGBOOST_TUNING_V1_DIR / "figures"

XGBOOST_TUNING_V2_DIR = TUNING_DIR / "v2"
XGBOOST_TUNING_V2_DOCS_DIR = XGBOOST_TUNING_V2_DIR / "docs"
XGBOOST_TUNING_V2_FIGURES_DIR = XGBOOST_TUNING_V2_DIR / "figures"

XGBOOST_TUNING_V3_DIR = TUNING_DIR / "v3"
XGBOOST_TUNING_V3_DOCS_DIR = XGBOOST_TUNING_V3_DIR / "docs"
XGBOOST_TUNING_V3_FIGURES_DIR = XGBOOST_TUNING_V3_DIR / "figures"

XGBOOST_TUNING_COMPARISON_DIR = TUNING_DIR / "comparison"
XGBOOST_TUNING_COMPARISON_DOCS_DIR = XGBOOST_TUNING_COMPARISON_DIR / "docs"
XGBOOST_TUNING_COMPARISON_FIGURES_DIR = XGBOOST_TUNING_COMPARISON_DIR / "figures"


# V1 files
XGBOOST_BEST_PARAMS_FILE = XGBOOST_TUNING_V1_DOCS_DIR / "xgboost_best_params.json"
XGBOOST_TUNED_RESULTS_FILE = XGBOOST_TUNING_V1_DOCS_DIR / "xgboost_tuned_results.csv"
XGBOOST_TUNED_SUMMARY_FILE = XGBOOST_TUNING_V1_DOCS_DIR / "xgboost_tuned_summary.json"

# V2 files
XGBOOST_BEST_PARAMS_V2_FILE = XGBOOST_TUNING_V2_DOCS_DIR / "xgboost_best_params_v2.json"
XGBOOST_TUNED_V2_RESULTS_FILE = XGBOOST_TUNING_V2_DOCS_DIR / "xgboost_tuned_v2_results.csv"
XGBOOST_TUNED_V2_SUMMARY_FILE = XGBOOST_TUNING_V2_DOCS_DIR / "xgboost_tuned_v2_summary.json"
XGBOOST_TUNED_V2_TRIALS_FILE = XGBOOST_TUNING_V2_DOCS_DIR / "xgboost_tuned_v2_trials.csv"

# V3 files
XGBOOST_BEST_PARAMS_V3_FILE = XGBOOST_TUNING_V3_DOCS_DIR / "xgboost_best_params_v3.json"
XGBOOST_TUNED_V3_RESULTS_FILE = XGBOOST_TUNING_V3_DOCS_DIR / "xgboost_tuned_v3_results.csv"
XGBOOST_TUNED_V3_SUMMARY_FILE = XGBOOST_TUNING_V3_DOCS_DIR / "xgboost_tuned_v3_summary.json"
XGBOOST_TUNED_V3_TRIALS_FILE = XGBOOST_TUNING_V3_DOCS_DIR / "xgboost_tuned_v3_trials.csv"


# -------------------------
# Backtest Results
# -------------------------
BACKTEST_DIR = WALKFORWARD_DIR / "backtest"

XGBOOST_BACKTEST_DIR = BACKTEST_DIR / "xgboost"
XGBOOST_BACKTEST_DOCS_DIR = XGBOOST_BACKTEST_DIR / "docs"
XGBOOST_BACKTEST_FIGURES_DIR = XGBOOST_BACKTEST_DIR / "figures"

XGBOOST_BACKTEST_PREDICTIONS_FILE = XGBOOST_BACKTEST_DOCS_DIR / "xgboost_backtest_predictions.csv"
XGBOOST_PORTFOLIO_BACKTEST_FILE = XGBOOST_BACKTEST_DOCS_DIR / "xgboost_portfolio_backtest.csv"
XGBOOST_BACKTEST_SUMMARY_FILE = XGBOOST_BACKTEST_DOCS_DIR / "xgboost_backtest_summary.json"

# =====================================================
# Old Production Files
# =====================================================
PRODUCTION_OLD_DIR = RESULTS_DIR / "production_old"
PRODUCTION_OLD_DOCS_DIR = PRODUCTION_OLD_DIR / "docs"
PRODUCTION_OLD_FIGURES_DIR = PRODUCTION_OLD_DIR / "figures"

OLD_XGB_MODEL = PRODUCTION_OLD_DOCS_DIR / "xgboost_production.pkl"
OLD_XGB_MODEL_META = PRODUCTION_OLD_DOCS_DIR / "xgboost_production_meta.json"


# =====================================================
# Final Artifacts
# artifacts/ contains production-ready assets only.
# =====================================================
ARTIFACTS_DIR = ML_DIR / "artifacts"

XGBOOST_FINAL_ARTIFACT_DIR = ARTIFACTS_DIR / "xgboost" / "final"
XGBOOST_FINAL_MODEL_DIR = BASE_DIR / "api" / "model"
XGBOOST_FINAL_DOCS_DIR = XGBOOST_FINAL_ARTIFACT_DIR / "docs"
XGBOOST_FINAL_FIGURES_DIR = XGBOOST_FINAL_ARTIFACT_DIR / "figures"

XGB_MODEL = XGBOOST_FINAL_MODEL_DIR / "xgboost_model.json"
XGB_MODEL_META = XGBOOST_FINAL_DOCS_DIR / "model_metadata.json"
XGB_FEATURE_COLUMNS = XGBOOST_FINAL_DOCS_DIR / "feature_columns.json"
XGB_FEATURE_MEDIANS = XGBOOST_FINAL_DOCS_DIR / "feature_medians.json"
XGB_FINAL_PARAMS = XGBOOST_FINAL_DOCS_DIR / "xgboost_final_params.json"

XGB_MODEL = XGBOOST_FINAL_MODEL_DIR / "xgboost_model.json"
XGB_MODEL_PKL = XGBOOST_FINAL_MODEL_DIR / "xgboost_model.pkl"

# -------------------------
# Log File
# -------------------------
ERROR_LOGS = BASE_DIR / "api" / "common" / "logs" / "errors.log"