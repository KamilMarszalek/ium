from __future__ import annotations

import sys
from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from preprocess import make_preprocess  # noqa: E402
from project_paths import MODEL_A_PATH, MODEL_B_PATH, MODELS_DIR  # noqa: E402
from train_baseline import (  # noqa: E402
    DATA,
    load_dataset,
    pick_feature_columns,
    prepare_xyg,
)


def main() -> None:
    df = load_dataset(DATA)
    X, y, _ = prepare_xyg(df)
    num_cols, cat_cols = pick_feature_columns(X)

    preprocess = make_preprocess(num_cols, cat_cols)

    model_a = LogisticRegression(max_iter=1000, n_jobs=-1)
    model_b = XGBClassifier(
        eval_metric="logloss",
        n_jobs=-1,
        random_state=42,
    )

    pipe_a = Pipeline([("prep", preprocess), ("clf", model_a)])
    pipe_b = Pipeline([("prep", preprocess), ("clf", model_b)])

    pipe_a.fit(X, y)
    pipe_b.fit(X, y)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe_a, MODEL_A_PATH)
    joblib.dump(pipe_b, MODEL_B_PATH)

    print(f"Saved model A to: {MODEL_A_PATH}")
    print(f"Saved model B to: {MODEL_B_PATH}")


if __name__ == "__main__":
    main()
