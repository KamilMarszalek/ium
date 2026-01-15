import sys
from pathlib import Path

import pandas as pd


def list_attributes(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    print(f"Total attributes: {len(df.columns)}")
    print(f"Total records: {len(df)}")
    print(f"Attributes: {list(df.columns)}")
    pd.set_option("display.max_rows", None)
    attribute_df = pd.DataFrame(
        {
            "Attribute": df.columns,
            "Data Type": df.dtypes.astype(str),
            "Non-Null Count": df.notnull().sum(),
            "Null Count": df.isnull().sum(),
            "Null Percentage": df.isnull().mean() * 100,
        }
    )
    output_dir = file_path.parent / "attributes"
    output_dir.mkdir(exist_ok=True)
    pd.DataFrame.to_csv(
        attribute_df,
        output_dir / f"{file_path.stem}_attributes.csv",
        index=False,
    )
    return attribute_df


def main(args: list[str]) -> None:
    if len(args) != 1:
        print("Usage: python3 attribute_reader.py <path_to_csv_file>")
        sys.exit(1)
    file_path = Path(args[0])
    print(list_attributes(file_path))


if __name__ == "__main__":
    main(sys.argv[1:])
