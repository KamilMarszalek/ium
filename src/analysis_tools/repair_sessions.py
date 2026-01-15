from pathlib import Path

import pandas as pd


def main() -> None:
    in_path = Path("data/sessions.csv")
    out_path = Path("data/sessions_repaired.csv")
    df = pd.read_csv(
        in_path,
        dtype={
            "user_id": "string",
            "listing_id": "string",
            "booking_id": "string",
        },
    )
    df["action_original"] = df["action"]
    df["action"] = df["action"].astype("string").str.strip().str.lower()
    df.loc[df["action_original"].isna(), "action"] = pd.NA
    fill_mask = (
        df["action"].isna()
        & df["booking_date"].notna()
        & df["booking_duration"].notna()
    )
    filled = int(fill_mask.sum())
    df.loc[fill_mask, "action"] = "book_listing"
    print(f"Rows: {len(df)}")
    print(f"Missing action before: {df['action_original'].isna().sum()}")
    print(f"Filled action to 'book_listing': {filled}")
    print(f"Missing action after: {df['action'].isna().sum()}")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
