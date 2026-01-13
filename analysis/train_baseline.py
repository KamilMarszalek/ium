from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    # classification_report,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

DATA = Path("data/bookings_prepared.csv")

df = pd.read_csv(DATA)
y = df["long_stay"].astype(int)
groups = df["listing_id"]
X = df.drop(columns=["long_stay", "listing_id"])
if "user_id" in X.columns:
    X = X.drop(columns=["user_id"])
for c in ["user_city", "checkin_month"]:
    if c in X.columns:
        X[c] = X[c].astype("object")
pd.set_option("future.no_silent_downcasting", True)
X = X.replace({pd.NA: np.nan}).infer_objects(copy=False)

num_cols = [
    c
    for c in [
        # "lead_time_days",
        # "checkin_year",
        # "price",
        "accommodates",
        "bedrooms",
        "beds",
        "bathrooms",
        "minimum_nights",
        "maximum_nights",
    ]
    if c in X.columns
]
cat_cols = [
    c
    for c in [
        "user_city",
        "postal_prefix2",
        # "checkin_month",
        # "checkin_dow",
        # "checkin_is_weekend",
        # "booking_month",
        # "booking_dow",
        # "booking_hour",
        # "lead_time_bucket",
        "city_missing",
        "room_type",
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

models = {
    "dummy_most_frequent": DummyClassifier(strategy="most_frequent"),
    "logreg": LogisticRegression(max_iter=50000, n_jobs=-1),
    "random_forest": RandomForestClassifier(n_jobs=-1, random_state=42),
    "xgboost": XGBClassifier(
        # use_label_encoder=False,
        eval_metric="logloss",
        n_jobs=-1,
        random_state=42,
    ),
}
sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
for name, clf in models.items():
    aucs, aps, pos_rates = [], [], []
    for fold, (tr, te) in enumerate(sgkf.split(X, y, groups=groups), 1):
        X_tr, X_te = X.iloc[tr], X.iloc[te]
        y_tr, y_te = y.iloc[tr], y.iloc[te]
        print("pos rates per fold:", [round(x, 4) for x in pos_rates])

        pipe = Pipeline([("prep", preprocess), ("clf", clf)])
        pipe.fit(X_tr, y_tr)

        proba = pipe.predict_proba(X_te)[:, 1]
        aucs.append(roc_auc_score(y_te, proba))
        aps.append(average_precision_score(y_te, proba))
        pos_rates.append(y_te.mean())

    print(
        name,
        "ROC-AUC mean±std:",
        np.mean(aucs),
        np.std(aucs),
        "PR-AUC mean±std:",
        np.mean(aps),
        np.std(aps),
        "test pos rate mean:",
        np.mean(pos_rates),
    )
