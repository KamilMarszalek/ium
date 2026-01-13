import pandas as pd


def get_amen_col_names(bookings_df: pd.Dataframe) -> list[str]:
    amen_cols = [col for col in bookings_df.columns if col.startswith("amen_")]
    return amen_cols
