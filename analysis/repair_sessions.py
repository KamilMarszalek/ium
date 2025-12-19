from pathlib import Path

import pandas as pd


def main() -> None:
    in_path = Path("data/sessions.csv")
    out_path = Path("data/sessions_repaired.csv")
    df = pd.read_csv(
        in_path,
        dtype={"user_id": "string", "listing_id": "string", "booking_id": "string"},
    )
    df["action_original"] = df["action"]
    df["action"] = df["action"].str.strip().str.lower()
    for row in df.itertuples():
        if (
            pd.isna(row.action)
            and pd.notna(row.booking_date)
            and pd.notna(row.booking_duration)
        ):
            df.at[row.Index, "action"] = "book_listing"
    changes = (df["action_original"] != df["action"]).sum()
    still_missing = df["action"].isna().sum()
    print(f"Rows: {len(df)}")
    print(f"Missing action before: {df['action_original'].isna().sum()}")
    print(f"Filled action based on booking_date and booking_duration: {changes}")
    print(f"Missing action after: {still_missing}")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
