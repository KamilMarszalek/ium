from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

DATA = Path("data/bookings_prepared.csv")

df = pd.read_csv(DATA)
y = df["long_stay"].astype(int)
groups = df["user_id"] if "user_id" in df.columns else None
X = df.drop(columns=["long_stay"])
if "user_id" in X.columns:
    X = X.drop(columns=["user_id"])
for c in ["user_city", "checkin_month"]:
    if c in X.columns:
        X[c] = X[c].astype("object")
pd.set_option("future.no_silent_downcasting", True)
X = X.replace({pd.NA: np.nan}).infer_objects(copy=False)

num_cols = [c for c in ["lead_time_days", "checkin_year"] if c in X.columns]
cat_cols = [
    c
    for c in [
        "user_city",
        "postal_prefix2",
        "checkin_month",
        "checkin_dow",
        "checkin_is_weekend",
        "booking_month",
        "booking_dow",
        "booking_hour",
        "lead_time_bucket",
        "city_missing",
    ]
    if c in X.columns
]

preprocess = ColumnTransformer(
    transformers=[
        (
            "num",
            Pipeline([("imputer", SimpleImputer(strategy="median"))]),
            num_cols,
        ),
        (
            "cat",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("ohe", OneHotEncoder(handle_unknown="ignore")),
                ]
            ),
            cat_cols,
        ),
    ],
    remainder="drop",
)


def run_split(X, y, groups=None):
    if groups is None:
        return train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    ((train_idx, test_idx),) = gss.split(X, y, groups=groups)
    return (
        X.iloc[train_idx],
        X.iloc[test_idx],
        y.iloc[train_idx],
        y.iloc[test_idx],
    )


X_train, X_test, y_train, y_test = run_split(X, y, groups=groups)

models = {
    "dummy_most_frequent": DummyClassifier(strategy="most_frequent"),
    "logreg": LogisticRegression(max_iter=10000),
}

for name, clf in models.items():
    pipe = Pipeline([("prep", preprocess), ("clf", clf)])
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    proba = (
        pipe.predict_proba(X_test)[:, 1]
        if hasattr(
            clf,
            "predict_proba",
        )
        else None
    )
    print("\n" + "=" * 80)
    print(name)
    print(classification_report(y_test, pred, digits=4, zero_division=0))
    if proba is not None:
        print("ROC-AUC:", roc_auc_score(y_test, proba))
