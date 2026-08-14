from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")


def print_section(title: str) -> None:
    print("\n" + "-" * 80)
    print(title)
    print("-" * 80)


def profile_naukri(path: Path) -> None:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)

    print_section("NAUKRI — Phone values")
    print(df["Phone"].value_counts().to_string())

    print_section("NAUKRI — CTC values")
    print(df["Current CTC"].value_counts().to_string())

    print_section("NAUKRI — Applied Date values")
    print(df["Applied Date"].value_counts().to_string())

    print_section("NAUKRI — City values")
    print(df["City"].value_counts().to_string())


def profile_gig(path: Path) -> None:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)

    print_section("GIG — Rate values")
    print(df["rate"].value_counts().to_string())

    print_section("GIG — Status values")
    print(df["status"].value_counts().to_string())

    print_section("GIG — Location values")
    print(df["location"].value_counts().to_string())


def profile_cbnexus(path: Path) -> None:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)

    print_section("CBNEXUS — Verified values")
    print(df["Verified"].value_counts().to_string())

    print_section("CBNEXUS — Projects Completed values")
    print(df["Projects Completed"].value_counts().to_string())

    print_section("CBNEXUS — City values")
    print(df["City"].value_counts().to_string())

    print_section("CBNEXUS — Phone values")
    print(df["Phone Number"].value_counts().to_string())


def main() -> None:
    profile_naukri(
        RAW_DIR / "source1_naukri_applicants.csv"
    )

    profile_gig(
        RAW_DIR / "source2_gig_workers.csv"
    )

    profile_cbnexus(
        RAW_DIR / "source3_cbnexus_contacts.csv"
    )


if __name__ == "__main__":
    main()