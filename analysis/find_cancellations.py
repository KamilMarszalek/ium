from pathlib import Path

import pandas as pd


def main() -> None:
    in_path = Path("data/sessions.csv")
    out_path = Path("data/cancellations.csv")
    df = pd.read_csv(
        in_path,
        dtype={
            "user_id": "string",
            "listing_id": "string",
            "booking_id": "string",
        },
    )
    cancellations = df[df["action"] == "cancel_booking"].copy()
    has_booking_date_and_duration = any(
        cancellations["booking_date"].notna()
        & cancellations["booking_duration"].notna()
    )
    print(f"Has booking_date and booking_duration: {has_booking_date_and_duration}")
    cancellations.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
