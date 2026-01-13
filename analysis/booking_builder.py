from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from parse_amenities_cell import parse_amenities_cell


def price_to_float(series: pd.Series) -> pd.Series:
    s = series.astype("string")
    s = s.str.replace(r"[^\d\.\-]", "", regex=True)
    return pd.to_numeric(s, errors="coerce")


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
            [
                "listing_id",
                "price",
                "room_type",
                "accommodates",
                "bedrooms",
                "beds",
                "bathrooms",
                "minimum_nights",
                "maximum_nights",
                "amenities",
                "host_is_superhost",
                "property_type",
                "minimum_minimum_nights",
                "maximum_minimum_nights",
                "minimum_maximum_nights",
                "maximum_maximum_nights",
                "number_of_reviews",
                "host_response_time",
                "host_response_rate",
            ],
        ]
    )
    out["price"] = price_to_float(out["price"])
    out["min_ge_7"] = (out["minimum_nights"] >= 7).astype("int8")
    out["max_lt_7"] = (out["maximum_nights"] < 7).astype("int8")
    return out


def load_user_features(path: Path) -> pd.DataFrame:
    users = pd.read_csv(
        path,
        dtype={"id": "string", "city": "string", "postal_code": "string"},
    )
    users["postal_prefix2"] = users["postal_code"].str.slice(0, 2)
    return (
        users.rename(columns={"id": "user_id", "city": "user_city"})[
            ["user_id", "user_city", "postal_prefix2"]
        ]
        .dropna(subset=["user_id"])
        .drop_duplicates(subset=["user_id"])
    )


def build_bookings_from_sessions(sessions: pd.DataFrame) -> pd.DataFrame:
    book = sessions[sessions["action"] == "book_listing"].copy()

    book["checkin"] = pd.to_datetime(book.get("booking_date"), errors="coerce")
    book["checkout"] = pd.to_datetime(
        book.get("booking_duration"),
        errors="coerce",
    )
    book["booking_ts"] = pd.to_datetime(book.get("timestamp"), errors="coerce")

    book["nights"] = (book["checkout"] - book["checkin"]).dt.days
    book = book[book["nights"].notna()]
    book = book[(book["nights"] > 0) & (book["nights"] <= 365)]

    book["lead_time_days"] = (book["checkin"] - book["booking_ts"]).dt.days
    book["long_stay"] = (book["nights"] >= 7).astype("int8")

    book["checkin_quarter"] = (
        book["checkin"]
        .dt.to_period("Q")
        .astype(
            "string",
        )
    )
    book["checkin_month"] = book["checkin"].dt.month

    if "price" in book.columns:
        book["price"] = pd.to_numeric(book["price"], errors="coerce")

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


def topk_amenities(amen_lists: pd.Series, k: int = 100) -> list[str]:
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

    b["amenities_list"] = b["amenities"].apply(parse_amenities_cell)
    b["amenities_count"] = b["amenities_list"].apply(len).astype("int16")

    top = topk_amenities(b["amenities_list"], k=k)

    colnames = {}
    used = set()
    for a in top:
        base = f"amen_{slugify_amenity(a)}"
        name = base
        i = 2
        while name in used:
            name = f"{base}_{i}"
            i += 1
        used.add(name)
        colnames[a] = name

    matrix = []
    for xs in b["amenities_list"]:
        s = set(xs)
        matrix.append([int(a in s) for a in top])

    amen_df = pd.DataFrame(
        matrix,
        columns=[colnames[a] for a in top],
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
    bookings["city_missing"] = bookings["user_city"].isna().astype("int8")

    bookings = encode_amenities_topk(bookings, k=amen_topk)

    out = drop_unused_columns(bookings)

    return out


if __name__ == "__main__":
    data_dir = Path("data")

    sessions = load_sessions(data_dir / "sessions.csv")
    listing_feats = load_listing_features(data_dir / "listings.csv")
    user_feats = load_user_features(data_dir / "users.csv")
    sessions = sessions.merge(
        listing_feats, on="listing_id", how="left", validate="m:1"
    )

    bookings_prepared = prepare_bookings_to_train(
        sessions,
        user_feats,
        amen_topk=100,
    )
    bookings_prepared.to_csv(data_dir / "bookings_prepared.csv", index=False)
    print(
        "Saved:",
        data_dir / "bookings_prepared.csv",
        "rows:",
        len(bookings_prepared),
    )
