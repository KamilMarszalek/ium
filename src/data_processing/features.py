import ast
import json

import pandas as pd

listing_features = [
    "listing_id",
    "price",
    "room_type",
    "accommodates",
    "bedrooms",
    "beds",
    "bathrooms",
    "bathrooms_text",
    "amenities",
    "property_type",
    "instant_bookable",
    # "segment_id",
]

night_limit_cols = [
    "minimum_nights",
    "maximum_nights",
    "minimum_minimum_nights",
    "maximum_minimum_nights",
    "minimum_maximum_nights",
    "maximum_maximum_nights",
]

host_features = [
    "host_is_superhost",
    "host_response_time",
    "host_response_rate",
    "number_of_reviews",
    "host_acceptance_rate",
]

review_features = [
    "review_scores_rating",
    "review_scores_accuracy",
    "review_scores_cleanliness",
    "review_scores_checkin",
    "review_scores_communication",
    "review_scores_location",
    "review_scores_value",
]


def parse_amenities_cell(x: object) -> list[str]:
    if pd.isna(x):
        return []
    if isinstance(x, list):
        return [str(a).strip() for a in x]
    s = str(x).strip()
    if not s:
        return []

    try:
        obj = json.loads(s)
        if isinstance(obj, list):
            return [str(a).strip() for a in obj]
    except Exception:
        pass

    try:
        obj = ast.literal_eval(s)
        if isinstance(obj, list):
            return [str(a).strip() for a in obj]
    except Exception:
        pass

    s = s.strip("{}[]")
    return [t.strip().strip('"').strip("'") for t in s.split(",") if t.strip()]


def get_amen_col_names(df: pd.DataFrame) -> list[str]:
    return [col for col in df.columns if col.startswith("amen_")]
