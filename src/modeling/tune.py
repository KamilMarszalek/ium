from dataclasses import dataclass

import numpy as np
import optuna
import pandas as pd
from optuna.samplers import TPESampler
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from xgboost import XGBClassifier

from src.modeling.preprocess import make_preprocess


@dataclass
class XGBoostTuneConfig:
    X: pd.DataFrame
    y: pd.Series
    groups: pd.Series
    num_cols: list[str]
    cat_cols: list[str]
    n_trials: int = 20


def tune_xgboost(config: XGBoostTuneConfig) -> dict[str, object]:
    print(f"\n{'=' * 30} START TUNING {'=' * 30}")

    def objective(trial: optuna.Trial) -> float:
        param = {
            "verbosity": 0,
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "n_estimators": 100,
            "n_jobs": -1,
            "random_state": 42,
            "tree_method": "hist",
            "early_stopping_rounds": 50,
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float(
                "colsample_bytree",
                0.5,
                1.0,
            ),
            "reg_alpha": trial.suggest_float("reg_alpha", 0.0, 10.0),
            "reg_lambda": trial.suggest_float("reg_lambda", 0.0, 10.0),
            "scale_pos_weight": trial.suggest_float(
                "scale_pos_weight",
                0.5,
                2.0,
            ),
        }

        sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
        aucs = []

        for tr_idx, te_idx in sgkf.split(
            config.X,
            config.y,
            groups=config.groups,
        ):
            X_tr, X_te = config.X.iloc[tr_idx], config.X.iloc[te_idx]
            y_tr, y_te = config.y.iloc[tr_idx], config.y.iloc[te_idx]
            preprocessor = make_preprocess(config.num_cols, config.cat_cols)

            X_tr_trans = preprocessor.fit_transform(X_tr)
            X_te_trans = preprocessor.transform(X_te)

            model = XGBClassifier(**param)
            model.fit(
                X_tr_trans,
                y_tr,
                eval_set=[(X_te_trans, y_te)],
                verbose=False,
            )

            preds = model.predict_proba(X_te_trans)[:, 1]
            roc = roc_auc_score(y_te, preds)
            aucs.append(roc)

        return float(np.mean(aucs))

    sampler = TPESampler(seed=42)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    study.optimize(objective, n_trials=config.n_trials)

    print(f"Best ROC AUC: {study.best_value:.4f}")
    print("Best params:", study.best_params)
    return study.best_params


if __name__ == "__main__":
    pass
