from pathlib import Path
from typing import Any

LONG_STAY_DURATION = 7

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"
DATA = DATA_DIR / "bookings_prepared.csv"

TARGET = "long_stay"

MODELS_DIR = ROOT_DIR / "models"
MODEL_A_PATH = MODELS_DIR / "regression.joblib"
MODEL_B_PATH = MODELS_DIR / "xgboost.joblib"

LOG_DIR = ROOT_DIR / "logs"
AB_LOG_PATH = LOG_DIR / "ab_log.jsonl"


XGB_CONFIG: dict[str, Any] = {
    "eval_metric": "logloss",
    "n_jobs": -1,
    "random_state": 42,
}
LOGREG_CONFIG: dict[str, Any] = {"max_iter": 500, "n_jobs": -1}
