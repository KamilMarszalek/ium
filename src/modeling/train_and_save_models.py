import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from src.modeling.preprocess import make_preprocess
from src.modeling.train_baseline import (
    DATA,
    load_dataset,
    pick_feature_columns,
    prepare_xyg,
)
from src.utils.constants import MODEL_A_PATH, MODEL_B_PATH, MODELS_DIR
from src.utils.models import get_models


def main() -> None:
    df = load_dataset(DATA)
    X, y, _ = prepare_xyg(df)
    num_cols, cat_cols = pick_feature_columns(X)

    preprocess = make_preprocess(num_cols, cat_cols)
    models = get_models()
    model_a = models["logreg"]
    model_b = models["xgboost"]

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
