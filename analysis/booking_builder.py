from pathlib import Path

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
    bookings = bookings.reindex(
        columns=["checkin_month", "lead_time_days", "user_city", "long_stay"]
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
