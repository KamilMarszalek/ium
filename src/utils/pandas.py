import pandas as pd


def require_series(df: pd.DataFrame, column: str) -> pd.Series:
    """Extract a single column as a Series.

    Pandas returns a DataFrame for `df[column]` when column labels are duplicated.
    This helper enforces 1D output and raises a clear error otherwise.
    """

    col = df[column]
    if isinstance(col, pd.DataFrame):
        raise ValueError(
            f"Expected 1D column {column!r}, got DataFrame (duplicate cols?)"
        )
    return col
