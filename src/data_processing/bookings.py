import re
from pathlib import Path

import pandas as pd
from src.data_processing.features import (
    host_features,
    listing_features,
    night_limit_cols,
    parse_amenities_cell,
    review_features,
)
from src.utils.constants import LONG_STAY_DURATION
from src.utils.pandas import require_series

DATA_DIR = Path("data")


def _to_numeric_series(x: pd.Series) -> pd.Series:
    out = pd.to_numeric(x, errors="coerce")
    return out if isinstance(out, pd.Series) else pd.Series(out, index=x.index)


def price_to_float(series: pd.Series) -> pd.Series:
    s = series.astype("string").str.replace(r"[^\d.\-]", "", regex=True)
    return _to_numeric_series(s)


def cut_percent_signs(series: pd.Series) -> pd.Series:
    s = series.astype("string").str.replace(r"[%]", "", regex=True)
    return _to_numeric_series(s)


def load_sessions(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        dtype={
            "user_id": "string",
            "listing_id": "string",
            "booking_id": "string",
            "action": "string",
        },
    )


def load_listing_features(path: Path) -> pd.DataFrame:
    listings = pd.read_csv(path, dtype={"id": "string"})
    out = (
        listings.rename(columns={"id": "listing_id"})
        .dropna(subset=["listing_id"])
        .drop_duplicates(subset=["listing_id"])
        .loc[
            :,
            listing_features + night_limit_cols + host_features + review_features,
        ]
    )
    segment_df = pd.read_csv(
        "data/listing_segments.csv", dtype={"listing_id": "string"}
    )
    out = out.merge(segment_df, on="listing_id", how="left", validate="1:1")
    out["price"] = price_to_float(out["price"])
    out["host_response_rate"] = cut_percent_signs(out["host_response_rate"])
    out["host_acceptance_rate"] = cut_percent_signs(out["host_acceptance_rate"])
    out["min_ge_7"] = (
        (out["minimum_nights"] >= LONG_STAY_DURATION).fillna(False).astype("int8")
    )
    out["max_lt_7"] = (
        (out["maximum_nights"] < LONG_STAY_DURATION).fillna(False).astype("int8")
    )
    out["bath_is_shared"] = (
        (out["bathrooms_text"].astype("string").str.contains("shared", case=False))
        .fillna(False)
        .astype("int8")
    )
    out["bath_is_private"] = (
        (out["bathrooms_text"].astype("string").str.contains("private", case=False))
        .fillna(False)
        .astype("int8")
    )
    return out


def load_user_features(path: Path) -> pd.DataFrame:
    users = pd.read_csv(
        path,
        dtype={"id": "string", "city": "string", "postal_code": "string"},
    )
    users["postal_prefix2"] = users["postal_code"].str.slice(0, 2)

    df = users.rename(columns={"id": "user_id", "city": "user_city"})
    df = df.loc[:, ["user_id", "user_city", "postal_prefix2"]]
    return df.dropna(subset=["user_id"]).drop_duplicates(subset=["user_id"])


def build_bookings_from_sessions(sessions: pd.DataFrame) -> pd.DataFrame:
    action = require_series(sessions, "action")
    book = sessions.loc[action == "book_listing"].copy()
    booking_date = require_series(book, "booking_date")
    booking_duration = require_series(book, "booking_duration")
    timestamp = require_series(book, "timestamp")
    checkin: pd.Series = pd.to_datetime(booking_date, errors="coerce")
    checkout: pd.Series = pd.to_datetime(booking_duration, errors="coerce")
    booking_ts: pd.Series = pd.to_datetime(timestamp, errors="coerce")
    nights: pd.Series = (checkout - checkin).dt.days
    book = book.assign(
        checkin=checkin,
        checkout=checkout,
        booking_ts=booking_ts,
        nights=nights,
    )
    nights_nonnull = require_series(book, "nights").notna()
    book = book.loc[nights_nonnull].copy()
    nights2 = require_series(book, "nights")
    book = book.loc[(nights2 > 0) & (nights2 <= 365)].copy()  # noqa: PLR2004
    checkin2 = require_series(book, "checkin")
    booking_ts2 = require_series(book, "booking_ts")
    book["lead_time_days"] = (checkin2 - booking_ts2).dt.days
    nights3 = require_series(book, "nights")
    book["long_stay"] = (nights3 >= LONG_STAY_DURATION).astype("int8")
    book["checkin_quarter"] = (
        require_series(book, "checkin").dt.to_period("Q").astype("string")
    )
    book["checkin_month"] = require_series(book, "checkin").dt.month
    if "price" in book.columns:
        price = require_series(book, "price")
        out = pd.to_numeric(price, errors="coerce")
        book["price"] = (
            out if isinstance(out, pd.Series) else pd.Series(out, index=price.index)
        )
    return book


def add_time_features(bookings: pd.DataFrame) -> pd.DataFrame:
    b = bookings.copy()

    b["checkin_year"] = b["checkin"].dt.year
    b["checkin_month"] = b["checkin"].dt.month
    b["checkin_dow"] = b["checkin"].dt.dayofweek
    b["checkin_is_weekend"] = b["checkin_dow"].isin([5, 6]).astype("int8")

    b["booking_month"] = b["booking_ts"].dt.month
    b["booking_dow"] = b["booking_ts"].dt.dayofweek
    b["booking_hour"] = b["booking_ts"].dt.hour

    lt = b["lead_time_days"].clip(lower=0)
    b["lead_time_bucket"] = pd.cut(
        lt,
        bins=[-0.1, 0, 1, 3, 7, 14, 30, 90, 10**9],
        labels=["0", "1", "2-3", "4-7", "8-14", "15-30", "31-90", "91+"],
    )
    return b


_slug_re = re.compile(r"[^a-z0-9_]+")


def slugify_amenity(a: str) -> str:
    s = a.strip().lower().replace(" ", "_")
    s = _slug_re.sub("_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "amenity"


def topk_amenities(amen_lists: list[list[str]], k: int = 100) -> list[str]:
    vc = pd.Series([a for row in amen_lists for a in row]).value_counts()
    return list(vc.head(k).index)


def encode_amenities_topk(
    bookings: pd.DataFrame,
    k: int = 100,
) -> pd.DataFrame:
    b = bookings.copy()
    if "amenities" not in b.columns:
        b["amenities_count"] = 0
        return b

    amenities = require_series(b, "amenities")
    parsed: list[list[str]] = [parse_amenities_cell(x) for x in amenities.tolist()]

    b["amenities_list"] = pd.Series(parsed, index=b.index)
    b["amenities_count"] = pd.Series((len(xs) for xs in parsed), index=b.index).astype(
        "int16"
    )

    top = topk_amenities(parsed, k=k)

    colnames: dict[str, str] = {}
    used: set[str] = set()
    for a in top:
        base = f"amen_{slugify_amenity(a)}"
        name = base
        i = 2
        while name in used:
            name = f"{base}_{i}"
            i += 1
        used.add(name)
        colnames[a] = name

    matrix: list[list[int]] = []
    for xs in parsed:
        s = set(xs)
        matrix.append([int(a in s) for a in top])

    columns: list[str] = [colnames[a] for a in top]
    amen_df = pd.DataFrame(
        matrix,
        columns=pd.Index(columns),
        index=b.index,
    )
    b = pd.concat([b, amen_df], axis=1)

    return b


def drop_unused_columns(bookings: pd.DataFrame) -> pd.DataFrame:
    return bookings.drop(
        columns=[
            "action",
            "checkin",
            "checkout",
            "booking_ts",
            "nights",
            "checkin_quarter",
            "timestamp",
            "booking_date",
            "booking_duration",
            "booking_id",
            "action_original",
            "amenities",
            "amenities_list",
        ],
        errors="ignore",
    )


def prepare_bookings_to_train(
    sessions: pd.DataFrame,
    user_feats: pd.DataFrame,
    *,
    amen_topk: int = 100,
) -> pd.DataFrame:
    bookings = build_bookings_from_sessions(sessions)
    bookings = add_time_features(bookings)

    bookings = bookings.merge(
        user_feats,
        on="user_id",
        how="left",
        validate="m:1",
    )

    bookings = encode_amenities_topk(bookings, k=amen_topk)

    out = drop_unused_columns(bookings)

    return out
