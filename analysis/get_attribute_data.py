import sys
from pathlib import Path

import pandas as pd


def list_attributes(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    print(f"Total attributes: {len(df.columns)}")
    print(f"Total records: {len(df)}")
    print(f"Attributes: {list(df.columns)}")
    return pd.DataFrame(
        {
            "Attribute": df.columns,
            "Data Type": df.dtypes.astype(str),
            "Non-Null Count": df.notnull().sum(),
            "Null Count": df.isnull().sum(),
            "Null Percentage": df.isnull().mean() * 100,
        }
    )


def main(args):
    if len(args) != 1:
        print("Usage: python attribute_reader.py <path_to_csv_file>")
        sys.exit(1)
    file_path = Path(args[0])
    print(list_attributes(file_path))


if __name__ == "__main__":
    main(sys.argv[1:])
