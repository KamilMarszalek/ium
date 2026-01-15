import pandas as pd


def build_text(listings: pd.DataFrame) -> pd.Series:
    text_cols = [
        "name",
        "description",
        "neighborhood_overview",
        "host_about",
        "bathrooms_text",
    ]
    parts = []
    for c in text_cols:
        if c in listings.columns:
            parts.append(listings[c].astype("string").fillna(""))
    if not parts:
        return pd.Series([""] * len(listings), index=listings.index)

    txt = parts[0]
    for p in parts[1:]:
        txt = txt + " " + p

    txt = txt.str.replace(r"<[^>]+>", " ", regex=True)
    txt = txt.str.replace(r"\s+", " ", regex=True).str.strip().str.lower()
    return txt
