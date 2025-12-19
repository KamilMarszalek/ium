from pathlib import Path

import numpy as np
import pandas as pd


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

    if "booking_ts" in book.columns:
        book["lead_time_days"] = (book["checkin"] - book["booking_ts"]).dt.days
    book["long_stay"] = book["nights"] >= 7
    book["checkin_quarter"] = book["checkin"].dt.to_period("Q").astype("string")
    book["checkin_month"] = book["checkin"].dt.month
    return book


def prepare_bookings_to_train(sessions: pd.DataFrame) -> pd.DataFrame:
    bookings = build_bookings_from_sessions(sessions)
    bookings["checkin_year"] = bookings["checkin"].dt.year
    bookings["checkin_month"] = bookings["checkin"].dt.month
    bookings["checkin_dow"] = bookings["checkin"].dt.dayofweek
    bookings["checkin_is_weekend"] = bookings["checkin_dow"].isin([5, 6]).astype("int8")

    bookings["booking_month"] = bookings["booking_ts"].dt.month
    bookings["booking_dow"] = bookings["booking_ts"].dt.dayofweek
    bookings["booking_hour"] = bookings["booking_ts"].dt.hour

    lt = bookings["lead_time_days"].clip(lower=0)
    bookings["lead_time_log1p"] = np.log1p(lt)

    bookings["lead_time_bucket"] = pd.cut(
        lt,
        bins=[-0.1, 0, 1, 3, 7, 14, 30, 90, 10**9],
        labels=["0", "1", "2-3", "4-7", "8-14", "15-30", "31-90", "91+"],
    )
    users = pd.read_csv(
        "data/users.csv",
        dtype={"id": "string", "city": "string", "postal_code": "string"},
    )
    users["postal_prefix2"] = users["postal_code"].str.slice(0, 2)
    user_feats = users.rename(columns={"id": "user_id", "city": "user_city"})[
        ["user_id", "user_city", "postal_prefix2"]
    ]
    user_feats = user_feats.drop_duplicates(subset=["user_id"])
    bookings = bookings.merge(user_feats, on="user_id", how="left", validate="m:1")
    bookings["city_missing"] = bookings["user_city"].isna().astype("int8")
    users = pd.read_csv(
        Path("data/users.csv"),
        usecols=["id", "city"],
        dtype={"id": "string", "city": "string"},
    )

    user_cities = (
        users.rename(columns={"id": "user_id", "city": "user_city"})
        .dropna(subset=["user_id"])
        .drop_duplicates(subset=["user_id"])
    )

    bookings = bookings.merge(
        user_cities,
        on="user_id",
        how="left",
        validate="m:1",
    )

    bookings = bookings.drop(
        columns=[
            "action",
            "checkin",
            "checkout",
            "booking_ts",
            "nights",
            "checkin_quarter",
            "user_id",
            "timestamp",
            "listing_id",
            "booking_date",
            "booking_duration",
            "booking_id",
            "action_original",
        ],
        errors="ignore",
    )

    bookings.to_csv(Path("data/bookings_prepared.csv"), index=False)
    return bookings


if __name__ == "__main__":
    sessions_df = pd.read_csv(
        "data/sessions_repaired.csv",
        dtype={
            "user_id": "string",
            "listing_id": "string",
            "booking_id": "string",
            "action": "string",
        },
    )

    bookings_df = prepare_bookings_to_train(sessions_df)
    print(f"Prepared {len(bookings_df)} bookings for training.")
