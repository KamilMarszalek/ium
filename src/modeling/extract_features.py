from collections.abc import Sequence

import numpy as np
import pandas as pd
import shap
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


def top_logreg_features(
    model: LogisticRegression, X: pd.DataFrame, feature_names: Sequence[str], n_features: int = 20, plot: bool = True
) -> pd.DataFrame:
    if n_features <= 0:
        raise ValueError("n_features must be > 0")

    if not hasattr(model, "coef_"):
        raise TypeError("model must be a fitted LogisticRegression")

    explainer = shap.LinearExplainer(model, X)
    sv = explainer(X)

    shap_values = sv.values

    mean_abs = np.mean(np.abs(shap_values), axis=0)
    mean_signed = np.mean(shap_values, axis=0)
    pct_pos = np.mean(shap_values > 0, axis=0)

    out = pd.DataFrame(
        {
            "feature": list(feature_names),
            "mean_abs_shap": mean_abs,
            "mean_signed_shap": mean_signed,
            "pct_positive_shap": pct_pos,
            "direction": np.where(
                mean_signed > 0,
                "pushes toward class=1",
                "pushes toward class=0",
            ),
        }
    )

    out = out.sort_values("mean_abs_shap", ascending=False).head(n_features).reset_index(drop=True)

    if plot:
        shap.summary_plot(shap_values, X)

    return out


def top_xgb_shap_features(
    model: XGBClassifier, X: pd.DataFrame, n_features: int = 20, plot: bool = True
) -> pd.DataFrame:
    if n_features <= 0:
        raise ValueError("n_features must be > 0")

    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(X)

    shap_values_arr = np.asarray(sv)

    mean_abs = np.mean(np.abs(shap_values_arr), axis=0)
    mean_signed = np.mean(shap_values_arr, axis=0)

    summary = (
        pd.DataFrame(
            {
                "feature": X.columns,
                "mean_abs_shap": mean_abs,
                "mean_signed_shap": mean_signed,
                "direction": np.where(
                    mean_signed > 0,
                    "pushes toward class=1",
                    "pushes toward class=0",
                ),
            }
        )
        .sort_values("mean_abs_shap", ascending=False)
        .head(n_features)
        .reset_index(drop=True)
    )

    if plot:
        shap.summary_plot(shap_values_arr, X)

    return summary
