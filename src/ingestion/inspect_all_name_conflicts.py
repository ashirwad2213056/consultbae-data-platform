from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")


def normalize_name(value: str) -> str:
    return " ".join(
        value.strip().lower().split()
    )


def show_duplicates(
    source_name: str,
    df: pd.DataFrame,
    name_column: str,
) -> None:

    df = df.copy()

    df["name_normalized"] = (
        df[name_column].map(normalize_name)
    )

    duplicates = df[
        df["name_normalized"].duplicated(
            keep=False
        )
    ].sort_values("name_normalized")

    print("\n" + "=" * 100)
    print(f"{source_name} — DUPLICATE NORMALIZED NAMES")
    print("=" * 100)

    if duplicates.empty:
        print("None")
        return

    print(
        duplicates.to_string(index=True)
    )


def main() -> None:

    naukri = pd.read_csv(
        RAW_DIR / "source1_naukri_applicants.csv",
        dtype=str,
        keep_default_na=False,
    )

    gig = pd.read_csv(
        RAW_DIR / "source2_gig_workers.csv",
        dtype=str,
        keep_default_na=False,
    )

    cbnexus = pd.read_csv(
        RAW_DIR / "source3_cbnexus_contacts.csv",
        dtype=str,
        keep_default_na=False,
    )

    # Remove structural anomalies.
    gig = gig[
        ~(
            gig["email_id"].eq("")
            & gig["worker_name"].eq("")
            & gig["rate"].eq("")
            & gig["location"].eq("")
            & gig["status"].eq("")
            & gig["skill_tags"].eq("")
        )
    ]

    cbnexus = cbnexus[
        cbnexus["Name"].str.strip().str.lower()
        != "name"
    ]

    show_duplicates(
        "NAUKRI",
        naukri,
        "Full Name",
    )

    show_duplicates(
        "GIG",
        gig,
        "worker_name",
    )

    show_duplicates(
        "CBNEXUS",
        cbnexus,
        "Name",
    )


if __name__ == "__main__":
    main()