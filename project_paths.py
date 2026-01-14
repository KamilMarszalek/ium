from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

MODELS_DIR = ROOT_DIR / "models"
MODEL_A_PATH = MODELS_DIR / "model_a.joblib"
MODEL_B_PATH = MODELS_DIR / "model_b.joblib"

LOG_DIR = ROOT_DIR / "logs"
AB_LOG_PATH = LOG_DIR / "ab_log.jsonl"
