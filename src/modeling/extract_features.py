import pandas as pd
import shap
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


def top_logreg_features(model: LogisticRegression, X: pd.DataFrame, n_features: int = 20):
    if n_features <= 0:
        raise ValueError("n_features must be > 0")

    if not hasattr(model, "coef_"):
        raise TypeError("model must be a fitted LogisticRegression")

    explainer = shap.LinearExplainer(model, X)
    sv = explainer.shap_values(X)

    shap.summary_plot(sv, X)


def top_xgb_shap_features(model: XGBClassifier, X: pd.DataFrame, n_features: int = 20):
    if n_features <= 0:
        raise ValueError("n_features must be > 0")

    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(X)

    shap.summary_plot(sv, X)
