import sys
from pathlib import Path

import pandas as pd


def get_attribute_values(file_path: Path, attribute_name: str) -> pd.Series:
    pd.set_option("display.max_rows", None)
    file_name = file_path.stem
    df = pd.read_csv(file_path)
    if attribute_name not in df.columns:
        raise ValueError(f"Attribute '{attribute_name}' not found in the df.")
    col = df[attribute_name]
    output_dir = file_path.parent / "values"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{file_name}_{attribute_name}.csv"
    col.to_csv(output_file, index=False)
    return col


def main(args: list[str]) -> None:
    if len(args) != 2:
        print(
            "Usage: python3 get_attribute_values.py <path_to_csv_file> <col>",
        )
        return
    file_path = Path(args[0])
    attribute_name = args[1]
    values = get_attribute_values(file_path, attribute_name)
    print(f"Values for attribute '{attribute_name}':")
    print(values)


if __name__ == "__main__":
    main(sys.argv[1:])
