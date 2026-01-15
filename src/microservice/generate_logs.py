import argparse
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from src.utils.constants import AB_LOG_PATH, DATA, MODEL_A_PATH, MODEL_B_PATH, TARGET

GROUP_COL = "listing_id"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--n",
        type=int,
        default=3000,
        help="Number of samples to generate",
    )
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument(
        "--out",
        type=Path,
        default=AB_LOG_PATH,
        help="Output JSONL path (default: AB_LOG_PATH)",
    )
    ap.add_argument(
        "--feedback-rate",
        type=float,
        default=1.0,
        help="What percentage of predictions should receive feedback (0..1)",
    )
    ap.add_argument(
        "--p-b",
        type=float,
        default=0.5,
        help="Probability of assignment to variant B",
    )
    return ap.parse_args()


def log_event(path: Path, obj: dict) -> None:
    obj["ts"] = datetime.now(UTC).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)

    df = pd.read_csv(DATA)
    model_a: Pipeline = joblib.load(MODEL_A_PATH)
    model_b: Pipeline = joblib.load(MODEL_B_PATH)

    if TARGET not in df.columns:
        raise ValueError(f"Missing target column {TARGET!r} in {DATA}")
    if GROUP_COL not in df.columns:
        raise ValueError(f"Missing group column {GROUP_COL!r} in {DATA}")
    idx = rng.integers(0, len(df), size=args.n)
    sample = df.iloc[idx].copy()
    y_true = sample[TARGET].astype(int).to_numpy()
    X = sample.drop(columns=[TARGET, GROUP_COL], errors="ignore")
    user_id = (
        sample["user_id"].astype("string") if "user_id" in sample.columns else None
    )
    listing_id = sample[GROUP_COL].astype("string")

    if args.out.exists():
        args.out.unlink()

    for i in range(args.n):
        rid = str(uuid.uuid4())

        variant = "B" if rng.random() < args.p_b else "A"
        model = model_b if variant == "B" else model_a
        model_name = "target" if variant == "B" else "baseline"

        row = X.iloc[i : i + 1]
        proba = float(model.predict_proba(row)[:, 1][0])
        pred = int(proba >= 0.5)

        log_event(
            args.out,
            {
                "event": "predict",
                "request_id": rid,
                "variant": variant,
                "model": model_name,
                "user_id": (None if user_id is None else str(user_id.iloc[i])),
                "listing_id": str(listing_id.iloc[i]),
                "prob": proba,
                "pred": pred,
            },
        )

        if rng.random() < args.feedback_rate:
            log_event(
                args.out,
                {
                    "event": "feedback",
                    "request_id": rid,
                    "true": int(y_true[i]),
                },
            )

    print(f"Saved log to: {args.out}")
    print(f"Lines: {sum(1 for _ in args.out.open('r', encoding='utf-8'))}")


if __name__ == "__main__":
    main()
