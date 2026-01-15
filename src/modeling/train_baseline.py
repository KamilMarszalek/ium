from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

import src.utils.pandas as pandas_utils
from src.data_processing.features import get_amen_col_names, review_features
from src.modeling.preprocess import make_preprocess
from src.modeling.tune import XGBoostTuneConfig, tune_xgboost
from src.utils.constants import DATA, TARGET

GROUP_COL = "listing_id"
DROP_ALWAYS = {"user_id"}

NUM_CANDIDATES = [
    "accommodates",
    "bedrooms",
    "beds",
    "bathrooms",
    "minimum_nights",
    "maximum_nights",
    "minimum_minimum_nights",
    "maximum_minimum_nights",
    "minimum_maximum_nights",
    "maximum_maximum_nights",
    "number_of_reviews",
    "amenities_count",
    "host_response_rate",
    "host_acceptance_rate",
    "segment_id",
] + review_features
CAT_CANDIDATES = [
    "room_type",
    "min_ge_7",
    "max_lt_7",
    "host_is_superhost",
    "host_response_time",
    "bath_is_shared",
    "bath_is_private",
    "instant_bookable",
    "segment_id",
    "property_type",
]


@dataclass(frozen=True)
class FoldResult:
    model: str
    fold: int
    roc_auc: float
    pr_auc: float
    pos_rate: float


@dataclass(frozen=True)
class CVConvig:
    X: pd.DataFrame
    y: pd.Series
    groups: pd.Series
    preprocess: ColumnTransformer
    models: dict[str, object]
    n_splits: int = 5
    random_state: int = 42
    print_reports: bool = True


def load_dataset(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def prepare_xyg(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    if TARGET not in df.columns:
        raise ValueError(f"Missing target column: {TARGET}")
    if GROUP_COL not in df.columns:
        raise ValueError(f"Missing group column: {GROUP_COL}")

    y: pd.Series = pandas_utils.require_series(df, TARGET)
    groups: pd.Series = pandas_utils.require_series(df, GROUP_COL)

    X = df.drop(columns=[TARGET, GROUP_COL]).copy()

    for col in DROP_ALWAYS:
        if col in X.columns:
            X = X.drop(columns=[col])

    pd.set_option("future.no_silent_downcasting", True)
    X = X.replace({pd.NA: np.nan}).infer_objects(copy=False)
    for c in CAT_CANDIDATES:
        if c in X.columns:
            X[c] = X[c].astype("object")

    return X, y, groups


def pick_feature_columns(X: pd.DataFrame) -> tuple[list[str], list[str]]:
    num_cols = [c for c in NUM_CANDIDATES if c in X.columns]
    cat_cols = [c for c in CAT_CANDIDATES if c in X.columns]
    cat_cols.extend(get_amen_col_names(X))

    if not num_cols and not cat_cols:
        raise ValueError(
            "No features selected. Check NUM_CANDIDATES/CAT_CANDIDATES.",
        )

    return num_cols, cat_cols


def get_models() -> dict[str, object]:
    return {
        "dummy_most_frequent": DummyClassifier(strategy="most_frequent"),
        "logreg": LogisticRegression(max_iter=1000, n_jobs=-1),
        "xgboost": XGBClassifier(
            eval_metric="logloss",
            n_jobs=-1,
            random_state=42,
        ),
    }


def evaluate_cv(config: CVConvig) -> list[FoldResult]:
    sgkf = StratifiedGroupKFold(
        n_splits=config.n_splits,
        shuffle=True,
        random_state=config.random_state,
    )
    X, y, groups = config.X, config.y, config.groups

    results: list[FoldResult] = []

    for model_name, clf in config.models.items():
        aucs, aps, pos_rates = [], [], []

        for fold, (tr, te) in enumerate(sgkf.split(X, y, groups=groups), 1):
            X_tr, X_te = X.iloc[tr], X.iloc[te]
            y_tr, y_te = y.iloc[tr], y.iloc[te]

            pipe = Pipeline([("prep", config.preprocess), ("clf", clf)])
            pipe.fit(X_tr, y_tr)

            proba = pipe.predict_proba(X_te)[:, 1]
            pred = pipe.predict(X_te)

            roc = roc_auc_score(y_te, proba)
            pr = average_precision_score(y_te, proba)
            pos = float(y_te.mean())

            results.append(
                FoldResult(
                    model=model_name,
                    fold=fold,
                    roc_auc=float(roc),
                    pr_auc=float(pr),
                    pos_rate=pos,
                )
            )
            aucs.append(roc)
            aps.append(pr)
            pos_rates.append(pos)

            if config.print_reports:
                print(f"\n{'=' * 80}\n{model_name} — fold {fold}")
                print(
                    classification_report(
                        y_te,
                        pred,
                        digits=4,
                    )
                )
                print(
                    f"ROC-AUC: {roc:.6f}  PR-AUC: {pr:.6f}  pos_rate: {pos:.4f}",
                )

        print(f"\n{model_name} summary")
        print("pos rates per fold:", [round(x, 4) for x in pos_rates])
        print(
            "ROC-AUC mean±std:",
            float(np.mean(aucs)),
            float(np.std(aucs)),
            "PR-AUC mean±std:",
            float(np.mean(aps)),
            float(np.std(aps)),
            "test pos rate mean:",
            float(np.mean(pos_rates)),
        )

    return results


def results_to_table(results: list[FoldResult]) -> pd.DataFrame:
    df = pd.DataFrame([r.__dict__ for r in results])
    summary = (
        df.groupby("model")
        .agg(
            roc_auc_mean=("roc_auc", "mean"),
            roc_auc_std=("roc_auc", "std"),
            pr_auc_mean=("pr_auc", "mean"),
            pr_auc_std=("pr_auc", "std"),
            pos_rate_mean=("pos_rate", "mean"),
        )
        .reset_index()
        .sort_values("roc_auc_mean", ascending=False)
    )
    return summary


@dataclass(frozen=True)
class BaselineConfig:
    do_tuning: bool = True
    tuning_trials: int = 15
    cv_splits: int = 5
    random_state: int = 42
    print_reports: bool = True


class BaselineTrainer:
    def __init__(self, *, config: BaselineConfig | None = None):
        if config is None:
            config = BaselineConfig()
        self.config = config

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        X, y, groups = prepare_xyg(df)
        num_cols, cat_cols = pick_feature_columns(X)

        xgb_params: dict[str, object] = {
            "eval_metric": "logloss",
            "n_jobs": -1,
            "random_state": self.config.random_state,
            "n_estimators": 100,
        }

        if self.config.do_tuning:
            tune_config = XGBoostTuneConfig(
                X,
                y,
                groups,
                num_cols,
                cat_cols,
                n_trials=self.config.tuning_trials,
            )
            best_params = tune_xgboost(tune_config)
            xgb_params.update(best_params)
            xgb_params["n_estimators"] = 100

        print("Using numeric:", num_cols)
        print("Using categorical:", cat_cols)
        print("N:", len(y), "pos_rate:", float(y.mean()))
        print("Unique groups:", int(groups.nunique()))

        preprocess = make_preprocess(num_cols, cat_cols)
        models = get_models()
        models["xgboost"] = XGBClassifier(**xgb_params)

        cv_config = CVConvig(
            X,
            y,
            groups,
            preprocess,
            models,
            n_splits=self.config.cv_splits,
            random_state=self.config.random_state,
            print_reports=self.config.print_reports,
        )
        results = evaluate_cv(cv_config)

        return results_to_table(results)


def main() -> None:
    trainer = BaselineTrainer()
    df = load_dataset(DATA)

    summary = trainer.run(df)
    print("\n" + "=" * 80)
    print("CV summary (mean±std)")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
