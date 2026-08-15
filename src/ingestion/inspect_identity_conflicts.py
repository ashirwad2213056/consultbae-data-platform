from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")


def normalize_name(value: str) -> str:
    return " ".join(
        value.strip().lower().split()
    )


def main() -> None:

    path = RAW_DIR / "source3_cbnexus_contacts.csv"

    df = pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
    )

    # Remove repeated header.
    df = df[
        df["Name"].str.strip().str.lower() != "name"
    ].copy()

    df["name_normalized"] = (
        df["Name"].map(normalize_name)
    )

    duplicate_names = (
        df[
            df["name_normalized"].duplicated(
                keep=False
            )
        ]
        .sort_values("name_normalized")
    )

    print("\n" + "=" * 100)
    print("CBNEXUS — DUPLICATE NORMALIZED NAMES")
    print("=" * 100)

    if duplicate_names.empty:
        print("No duplicate names found.")
    else:
        print(
            duplicate_names[
                [
                    "Name",
                    "Phone Number",
                    "City",
                    "Verified",
                    "Projects Completed",
                ]
            ].to_string(index=True)
        )

        print(
            f"\nDuplicate-name rows: "
            f"{len(duplicate_names)}"
        )


if __name__ == "__main__":
    main()