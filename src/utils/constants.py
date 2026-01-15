from pathlib import Path

LONG_STAY_DURATION = 7

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"
DATA = DATA_DIR / "bookings_prepared.csv"

TARGET = "long_stay"

MODELS_DIR = ROOT_DIR / "models"
MODEL_A_PATH = MODELS_DIR / "model_a.joblib"
MODEL_B_PATH = MODELS_DIR / "model_b.joblib"

LOG_DIR = ROOT_DIR / "logs"
AB_LOG_PATH = LOG_DIR / "ab_log.jsonl"
