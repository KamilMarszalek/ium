from math import sqrt

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.feature_selection import mutual_info_classif

from utils.constants import DATA, TARGET


def cramers_v(
    x: pd.Series, y: pd.Series, *, top_k: int = 50
) -> tuple[float, float, int]:
    s = x.copy()
    s = s.astype("string").fillna("MISSING")
    vc = s.value_counts()
    if len(vc) > top_k:
        top = vc.head(top_k).index
        s = s.where(s.isin(top), other="OTHER")
    ct = pd.crosstab(s, y)
    chi2, p, _, _ = chi2_contingency(ct)
    n = ct.to_numpy().sum()
    phi2 = chi2 / n
    r, k = ct.shape
    denom = min(k - 1, r - 1)
    v = sqrt(phi2 / denom) if denom > 0 else 0.0
    return v, float(p), int(ct.shape[0])


def mutual_info_univariate(x: pd.Series, y: pd.Series) -> float:
    s = x.copy()
    if s.dtype == "object" or str(s.dtype).startswith("string"):
        s = s.astype("string").fillna("MISSING")
        codes, _ = pd.factorize(s)
        return float(
            mutual_info_classif(
                codes.reshape(-1, 1),
                y,
                discrete_features=True,
                random_state=42,
            )[0]
        )
    raw = pd.to_numeric(s, errors="coerce").to_numpy()
    mask = ~np.isnan(raw)
    uniq = np.unique(raw[mask])
    if len(uniq) <= 50 and np.all(np.isclose(uniq, np.round(uniq))):
        raw = np.where(np.isnan(raw), -999999, raw).astype(int)
        return float(
            mutual_info_classif(
                raw.reshape(-1, 1), y, discrete_features=True, random_state=42
            )[0]
        )
    med = np.nanmedian(raw)
    raw = np.where(np.isnan(raw), med, raw)
    return float(
        mutual_info_classif(
            raw.reshape(-1, 1), y, discrete_features=False, random_state=42
        )[0]
    )


def main() -> None:
    df = pd.read_csv(DATA)
    y = df[TARGET].astype(int)
    X = df.drop(columns=[TARGET]).copy()
    X = X.replace({pd.NA: np.nan}).infer_objects(copy=False)
    num_cols = [c for c in X.columns if X[c].dtype != "object"]
    pearson = (
        df[num_cols + [TARGET]]
        .corr(numeric_only=True)[TARGET]
        .drop(
            TARGET,
        )
    )
    spearman = (
        df[num_cols + [TARGET]]
        .corr(method="spearman", numeric_only=True)[TARGET]
        .drop(TARGET)
    )
    rows = []
    for col in X.columns:
        miss = float(X[col].isna().mean())
        nunique = int(X[col].nunique(dropna=True))
        mi = mutual_info_univariate(X[col], y)
        v = p = levels = None
        if X[col].dtype == "object" or nunique <= 50:
            v, p, levels = cramers_v(X[col], y, top_k=50)

        rows.append(
            {
                "feature": col,
                "missing_rate": miss,
                "n_unique": nunique,
                "pearson_corr": float(
                    pearson[col],
                )
                if col in pearson.index
                else np.nan,
                "spearman_corr": float(spearman[col])
                if col in spearman.index
                else np.nan,
                "mutual_info": mi,
                "cramers_v": v,
                "chi2_p": p,
                "levels_used": levels,
            }
        )

    out = pd.DataFrame(rows).sort_values("mutual_info", ascending=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
