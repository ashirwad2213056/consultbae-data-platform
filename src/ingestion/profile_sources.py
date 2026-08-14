from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")


def profile_file(file_path: Path) -> None:
    print("\n" + "=" * 90)
    print(f"FILE: {file_path.name}")
    print("=" * 90)

    df = pd.read_csv(
        file_path,
        dtype=str,
        keep_default_na=False,
    )

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nMissing / empty values:")
    for column in df.columns:
        empty_count = (df[column].str.strip() == "").sum()
        print(f"  {column}: {empty_count}")

    print("\nDuplicate rows:")
    print(f"  Exact duplicate rows: {df.duplicated().sum()}")

    print("\nBlank rows:")
    blank_rows = df.apply(
        lambda row: all(str(value).strip() == "" for value in row),
        axis=1,
    )
    print(f"  Completely blank rows: {blank_rows.sum()}")

    print("\nPotential repeated headers:")

    header_matches = df.apply(
        lambda row: all(
            str(row[column]).strip().lower() == column.strip().lower()
            for column in df.columns
        ),
        axis=1,
    )

    repeated_header_rows = df.index[header_matches].tolist()

    if repeated_header_rows:
        print(f"  Found at row indexes: {repeated_header_rows}")
    else:
        print("  None detected")

    print("\nUnique values by column:")

    for column in df.columns:
        unique_count = df[column].nunique(dropna=False)
        print(f"  {column}: {unique_count}")

    print("\nFirst 5 rows:")
    print(df.head(5).to_string(index=False))


def main() -> None:
    csv_files = sorted(RAW_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in data/raw/")
        return

    for file_path in csv_files:
        profile_file(file_path)


if __name__ == "__main__":
    main()