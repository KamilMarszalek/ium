from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

from src.utils.constants import LOGREG_CONFIG, XGB_CONFIG


def get_models() -> dict[str, object]:
    return {
        "dummy_most_frequent": DummyClassifier(strategy="most_frequent"),
        "logreg": LogisticRegression(**LOGREG_CONFIG),
        "xgboost": XGBClassifier(**XGB_CONFIG),
    }
