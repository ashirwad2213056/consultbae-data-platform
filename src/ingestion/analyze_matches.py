from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")


def normalize_email(value: str) -> str:
    return value.strip().lower()


def normalize_phone(value: str) -> str:
    digits = "".join(
        character
        for character in value
        if character.isdigit()
    )

    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]

    if digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]

    if len(digits) == 10:
        return digits

    return ""


def normalize_name(value: str) -> str:
    return " ".join(
        value.strip().lower().split()
    )


def load_sources() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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

    return naukri, gig, cbnexus


def prepare_naukri(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["email_normalized"] = (
        result["Email"].map(normalize_email)
    )

    result["phone_normalized"] = (
        result["Phone"].map(normalize_phone)
    )

    result["name_normalized"] = (
        result["Full Name"].map(normalize_name)
    )

    return result


def prepare_gig(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["email_normalized"] = (
        result["email_id"].map(normalize_email)
    )

    result["phone_normalized"] = ""

    result["name_normalized"] = (
        result["worker_name"].map(normalize_name)
    )

    return result


def prepare_cbnexus(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["email_normalized"] = ""

    result["phone_normalized"] = (
        result["Phone Number"].map(normalize_phone)
    )

    result["name_normalized"] = (
        result["Name"].map(normalize_name)
    )

    return result


def exact_email_matches(
    naukri: pd.DataFrame,
    gig: pd.DataFrame,
) -> None:

    print("\n" + "=" * 90)
    print("NAUKRI ↔ GIG — EXACT EMAIL MATCHES")
    print("=" * 90)

    gig_emails = set(
        email
        for email in gig["email_normalized"]
        if email
    )

    matches = naukri[
        naukri["email_normalized"].isin(gig_emails)
    ]

    if matches.empty:
        print("No exact email matches.")
    else:
        print(
            matches[
                [
                    "Full Name",
                    "Email",
                    "phone_normalized",
                ]
            ].to_string(index=False)
        )


def exact_phone_matches(
    naukri: pd.DataFrame,
    cbnexus: pd.DataFrame,
) -> None:

    print("\n" + "=" * 90)
    print("NAUKRI ↔ CBNEXUS — EXACT PHONE MATCHES")
    print("=" * 90)

    cbnexus_phones = set(
        phone
        for phone in cbnexus["phone_normalized"]
        if phone
    )

    matches = naukri[
        naukri["phone_normalized"].isin(cbnexus_phones)
    ]

    if matches.empty:
        print("No exact phone matches.")
    else:
        print(
            matches[
                [
                    "Full Name",
                    "Email",
                    "phone_normalized",
                ]
            ].to_string(index=False)
        )


def main() -> None:

    naukri, gig, cbnexus = load_sources()

    # Remove the known structural anomalies for
    # entity-resolution analysis.
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

    naukri = prepare_naukri(naukri)
    gig = prepare_gig(gig)
    cbnexus = prepare_cbnexus(cbnexus)

    exact_email_matches(naukri, gig)
    exact_phone_matches(naukri, cbnexus)


if __name__ == "__main__":
    main()