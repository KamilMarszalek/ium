import pathlib
import sys

import pandas as pd


def join_coverage_report(
    df_left: pd.DataFrame,
    df_right: pd.DataFrame,
    left_on: list[str],
    right_on: list[str],
) -> dict[str, float]:
    right_keys = df_right[right_on].drop_duplicates()
    merged = df_left.merge(
        right_keys,
        left_on=left_on,
        right_on=right_on,
        how="left",
        indicator=True,
    )
    left_has_key = merged[left_on].notna().all(axis=1)
    matched = (merged["_merge"] == "both") & left_has_key
    total = len(merged)
    non_null = left_has_key.sum()
    left_unique = df_left[left_on].dropna().drop_duplicates()
    right_unique = df_right[right_on].dropna().drop_duplicates()
    unique_cov = left_unique.merge(
        right_unique, left_on=left_on, right_on=right_on, how="inner"
    ).shape[0] / max(len(left_unique), 1)

    return {
        "row_coverage": matched.mean(),
        "key_completeness": non_null / max(total, 1),
        "match_given_key": matched.sum() / max(non_null, 1),
        "unique_key_coverage": unique_cov,
    }


def main(args: list[str]) -> None:
    left_path = pathlib.Path(args[0])
    right_path = pathlib.Path(args[1])
    left_col, right_col = args[2].split(",")
    df_left = pd.read_csv(left_path, dtype={left_col: "string"})
    df_right = pd.read_csv(right_path, dtype={right_col: "string"})
    if "action" in df_left.columns:
        df_left = df_left[df_left["action"] == "book_listing"]
    coverage = join_coverage_report(df_left, df_right, [left_col], [right_col])
    print(coverage)


if __name__ == "__main__":
    main(sys.argv[1:])
