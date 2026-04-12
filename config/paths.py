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
PROCESSED_DIR = MARKET_DIR / "processed"
ML_DIR = DATA_DIR / "ml_data"

# -------------------------
# Market Data Files
# -------------------------
OPTIONS = DATABASE_DIR / "options.csv"
QUESTIONS = DATABASE_DIR / "questions.csv"
SECTORS = DATABASE_DIR / "sectors.csv"
STOCKS = DATABASE_DIR / "stocks.csv"

# -------------------------
# Market Data Files
# -------------------------
RAW_MARKET_FILE = RAW_DIR / "EGX30_Full_Dataset_Ready.csv"
CLEANED_MARKET_FILE = PROCESSED_DIR / "egx30_clean.csv"
MACRO_FILE = RAW_DIR / "Egypt_Economic_Data.xlsx"
MACROECNOMIC_ALIGNMENT_FILE = PROCESSED_DIR / "egx30_with_macro.csv"
MODELING_DATASET_FILE = ML_DIR / "datasets" / "EGX30_modeling_dataset.csv"

# -------------------------
# ML Datasets 
# -------------------------
FEATURES_DIR = ML_DIR / "features"
FEATURE_CACHE_DIR = FEATURES_DIR / "feature_cache"
FEATURE_CACHE_FILE = FEATURE_CACHE_DIR / "feature_cache.csv"
FEATURE_STABILITY_FILE = FEATURES_DIR / "feature_stability.csv"

# Walk-forward evaluation results
WALKFORWARD_RESULTS_DIR = ML_DIR / "metadata" / "walkforward_results"
WALKFORWARD_RESULTS_FILE = WALKFORWARD_RESULTS_DIR / "walkforward_results.csv"
LSTM_RESULTS_FILE = WALKFORWARD_RESULTS_DIR / "lstm_results.csv"
XGBOOST_RESULTS_FILE = WALKFORWARD_RESULTS_DIR / "xgboost_results.csv"  


# -------------------------
# Model Comparison Results
# -------------------------
RESULT_BY_FOLD_FILE = ML_DIR / "metadata" / "all_fold_results.csv"
MODEL_COMPARISON_DIR = ML_DIR / "metadata" 
MODEL_COMPARISON_FILE = MODEL_COMPARISON_DIR / "model_comparison.csv"

# -------------------------
# EDA Output Folder
# -------------------------
EDA_OUTPUT_DIR = BASE_DIR / "research" / "EDA" / "outputs"
EDA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------
# HTML TEMPLATES
# -------------------------
APP = BASE_DIR / "api" / "app.py"
MODELS = BASE_DIR / "api" / "models.py"
ROUTES = BASE_DIR / "api" / "routes.py"
RUN = BASE_DIR / "api" / "run.py"
TEMPLATE_HTML = BASE_DIR / "api" / "templates"