from src.data_processing.bookings import (
    load_listing_features,
    load_sessions,
    load_user_features,
    prepare_bookings_to_train,
)
from src.utils.constants import DATA_DIR

if __name__ == "__main__":
    sessions = load_sessions(DATA_DIR / "sessions.csv")
    listing_feats = load_listing_features(DATA_DIR / "listings.csv")
    user_feats = load_user_features(DATA_DIR / "users.csv")
    sessions = sessions.merge(
        listing_feats, on="listing_id", how="left", validate="m:1"
    )

    bookings_prepared = prepare_bookings_to_train(
        sessions,
        user_feats,
        amen_topk=50,
    )
    bookings_prepared.to_csv(DATA_DIR / "bookings_prepared.csv", index=False)
    print(
        "Saved:",
        DATA_DIR / "bookings_prepared.csv",
        "rows:",
        len(bookings_prepared),
    )
