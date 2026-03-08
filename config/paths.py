from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# Data Directories
# -------------------------
DATA_DIR = BASE_DIR / "data"
MARKET_DIR = DATA_DIR / "market_data"
ML_DIR = DATA_DIR / "ml_data"
RAW_DIR = MARKET_DIR / "raw"
PROCESSED_DIR = MARKET_DIR / "processed"
ML_DIR = DATA_DIR / "ml_data"

# -------------------------
# Market Data Files |
# -------------------------
RAW_MARKET_FILE = RAW_DIR / "EGX30_Full_Dataset_Ready.csv"
CLEANED_MARKET_FILE = PROCESSED_DIR / "egx30_clean.csv"
MACRO_FILE = RAW_DIR / "Egypt_Economic_Data.xlsx"
MACROECNOMIC_ALIGNMENT_FILE = PROCESSED_DIR / "egx30_with_macro.csv"
CATEGORIZED_FILE = PROCESSED_DIR / "egx30_categorized.csv"
MODELING_DATASET_FILE = ML_DIR / "datasets" / "EGX30_modeling_dataset.csv"
# -------------------------
# ML Datasets (Optional for EDA)
# -------------------------
TRAIN_DATA = ML_DIR / "datasets" / "train.csv"
TEST_DATA = ML_DIR / "datasets" / "test.csv"

# -------------------------
# EDA Output Folder
# -------------------------
EDA_OUTPUT_DIR = BASE_DIR / "research" / "EDA" / "outputs"
EDA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------
# TEMPLATE

TEMPLATE_HTML = BASE_DIR / "presentation"