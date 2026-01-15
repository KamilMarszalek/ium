import hashlib
import json
import uuid
from datetime import UTC, datetime
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.pipeline import Pipeline
from src.utils.constants import AB_LOG_PATH, MODEL_A_PATH, MODEL_B_PATH

AB_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

model_a: Pipeline = joblib.load(MODEL_A_PATH)
model_b: Pipeline = joblib.load(MODEL_B_PATH)

app = FastAPI()


class PredictIn(BaseModel):
    user_id: str | None = None
    listing_id: str | None = None
    features: dict[str, Any]


class ExplanationItem(BaseModel):
    feature: str
    contribution: float


class PredictOut(BaseModel):
    request_id: str
    variant: str
    model: str
    prob_long_stay: float
    pred_label: int


class FeedbackIn(BaseModel):
    request_id: str
    true_long_stay: int


def choose_variant(user_id: str | None, listing_id: str | None) -> str:
    key = user_id or listing_id or str(uuid.uuid4())
    h = hashlib.md5(key.encode("utf-8")).hexdigest()  # noqa: S324
    return "A" if int(h, 16) % 2 == 0 else "B"


def log_event(obj: dict[str, Any]) -> None:
    obj["ts"] = datetime.now(UTC).isoformat()
    with AB_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictOut)
def predict(inp: PredictIn):
    variant = choose_variant(inp.user_id, inp.listing_id)
    model = model_a if variant == "A" else model_b
    model_name = "baseline" if variant == "A" else "target"

    X = pd.DataFrame([inp.features])

    proba = float(model.predict_proba(X)[:, 1][0])
    pred = int(proba >= 0.5)  # noqa: PLR2004
    rid = str(uuid.uuid4())

    log_event(
        {
            "event": "predict",
            "request_id": rid,
            "variant": variant,
            "model": model_name,
            "user_id": inp.user_id,
            "listing_id": inp.listing_id,
            "prob": proba,
            "pred": pred,
        }
    )

    return PredictOut(
        request_id=rid,
        variant=variant,
        model=model_name,
        prob_long_stay=proba,
        pred_label=pred,
    )


@app.post("/feedback")
@app.post("/ium/feedback")
def feedback(inp: FeedbackIn):
    log_event(
        {
            "event": "feedback",
            "request_id": inp.request_id,
            "true": int(inp.true_long_stay),
        }
    )
    return {"status": "ok"}
