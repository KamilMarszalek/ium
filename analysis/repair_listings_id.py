import re
from pathlib import Path

import pandas as pd

ROOMS_RE = re.compile(r"/rooms/(\d+)")


def main() -> None:
    in_path = Path("data/listings.csv")
    out_path = Path("data/listings_repaired.csv")

    df = pd.read_csv(
        in_path,
        dtype={"id": "string", "listing_url": "string"},
    )
    df["id_original"] = df["id"]
    df["id_from_url"] = df["listing_url"].str.extract(ROOMS_RE)[0]
    id_missing = df["id"].isna() | (df["id"].str.strip() == "")
    df.loc[id_missing, "id"] = df.loc[id_missing, "id_from_url"]
    both = df["id_original"].notna() & df["id_from_url"].notna()
    conflicts = (df.loc[both, "id_original"] != df.loc[both, "id_from_url"]).sum()
    dups = df["id"].dropna().duplicated().sum()
    still_missing = df["id"].isna().sum()
    print(f"Rows: {len(df)}")
    print(f"Missing id before: {df['id_original'].isna().sum()}")
    print(f"Filled from url: {(id_missing & df['id_from_url'].notna()).sum()}")
    print(f"Conflicts (id_original vs id_from_url): {conflicts}")
    print(f"Duplicate ids after repair: {dups}")
    print(f"Missing id after: {still_missing}")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
