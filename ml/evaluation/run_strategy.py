from ml.evaluation.walkforward_strategy import WalkForwardStrategy
from pathlib import Path
import sys

ROOT_DIR = Path().resolve().parents[0]
sys.path.append(str(ROOT_DIR))
from config.paths import XGBOOST_RESULTS_FILE as results_path

if __name__ == "__main__":

    strategy = WalkForwardStrategy(
        results_path= results_path
    )

    strategy.run()