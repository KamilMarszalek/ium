import json

import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from src.utils.constants import AB_LOG_PATH

if not AB_LOG_PATH.exists():
    raise SystemExit(f"Missing log file: {AB_LOG_PATH}")

rows = [
    json.loads(line) for line in AB_LOG_PATH.read_text(encoding="utf-8").splitlines()
]
df = pd.DataFrame(rows)

pred: pd.DataFrame = df.loc[
    df["event"] == "predict", ["request_id", "variant", "model", "prob"]
]
fb: pd.DataFrame = df.loc[df["event"] == "feedback", ["request_id", "true"]]

m = pred.merge(fb, on="request_id", how="inner")
for v in ["A", "B"]:
    mv = m[m["variant"] == v]
    if mv.empty:
        print(v, "no data")
        continue
    y = mv["true"].astype(int)
    p = mv["prob"].astype(float)
    print("Variant", v, "n=", len(mv))
    print("ROC-AUC:", roc_auc_score(y, p))
    print("PR-AUC:", average_precision_score(y, p))
