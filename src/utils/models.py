from collections.abc import Iterator
from dataclasses import dataclass, fields

from sklearn.base import BaseEstimator
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

from src.utils.constants import LOGREG_CONFIG, XGB_CONFIG


@dataclass
class Models:
    dummy: DummyClassifier
    logreg: LogisticRegression
    xgboost: XGBClassifier

    def items(self) -> Iterator[tuple[str, BaseEstimator]]:
        for f in fields(self):
            value = getattr(self, f.name)
            if isinstance(value, BaseEstimator):
                yield f.name, value


def get_models() -> Models:
    return Models(
        DummyClassifier(strategy="most_frequent"),
        LogisticRegression(**LOGREG_CONFIG),
        XGBClassifier(**XGB_CONFIG),
    )
