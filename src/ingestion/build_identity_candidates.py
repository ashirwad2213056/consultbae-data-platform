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

    # 12-digit Indian number with 91 prefix
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    # 11-digit Indian number with leading zero
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]

    # 10-digit canonical representation
    if len(digits) == 10:
        return digits

    return ""


def normalize_name(value: str) -> str:
    return " ".join(
        value.strip().lower().split()
    )


def normalize_city(value: str) -> str:
    value = value.strip().lower()

    city_map = {
        "bangalore": "bengaluru",
        "bengaluru": "bengaluru",
        "gurgaon": "gurgaon",
        "gurugram": "gurgaon",
        "noida": "noida",
        "pune": "pune",
        "delhi": "delhi",
        "new delhi": "delhi",
        "delhi ncr": "delhi",
    }

    return city_map.get(value, value)


def load_sources():
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


def remove_structural_anomalies(
    naukri,
    gig,
    cbnexus,
):
    # Remove completely blank Gig records.
    gig = gig[
        ~(
            gig["email_id"].eq("")
            & gig["worker_name"].eq("")
            & gig["rate"].eq("")
            & gig["location"].eq("")
            & gig["status"].eq("")
            & gig["skill_tags"].eq("")
        )
    ].copy()

    # Remove repeated CBNexus header.
    cbnexus = cbnexus[
        cbnexus["Name"].str.strip().str.lower() != "name"
    ].copy()

    return naukri.copy(), gig, cbnexus


def prepare_naukri(df):
    df = df.copy()

    df["source"] = "naukri"
    df["source_row"] = df.index + 2

    df["email_normalized"] = (
        df["Email"].map(normalize_email)
    )

    df["phone_normalized"] = (
        df["Phone"].map(normalize_phone)
    )

    df["name_normalized"] = (
        df["Full Name"].map(normalize_name)
    )

    df["city_normalized"] = (
        df["City"].map(normalize_city)
    )

    return df


def prepare_gig(df):
    df = df.copy()

    df["source"] = "gig"
    df["source_row"] = df.index + 2

    df["email_normalized"] = (
        df["email_id"].map(normalize_email)
    )

    # Gig has no phone field.
    df["phone_normalized"] = ""

    df["name_normalized"] = (
        df["worker_name"].map(normalize_name)
    )

    df["city_normalized"] = (
        df["location"].map(normalize_city)
    )

    return df


def prepare_cbnexus(df):
    df = df.copy()

    df["source"] = "cbnexus"
    df["source_row"] = df.index + 2

    # CBNexus has no email field.
    df["email_normalized"] = ""

    df["phone_normalized"] = (
        df["Phone Number"].map(normalize_phone)
    )

    df["name_normalized"] = (
        df["Name"].map(normalize_name)
    )

    df["city_normalized"] = (
        df["City"].map(normalize_city)
    )

    return df


def compare_records(
    source_a,
    row_a,
    source_b,
    row_b,
):
    email_match = (
        bool(row_a["email_normalized"])
        and bool(row_b["email_normalized"])
        and row_a["email_normalized"]
        == row_b["email_normalized"]
    )

    phone_match = (
        bool(row_a["phone_normalized"])
        and bool(row_b["phone_normalized"])
        and row_a["phone_normalized"]
        == row_b["phone_normalized"]
    )

    name_match = (
        bool(row_a["name_normalized"])
        and bool(row_b["name_normalized"])
        and row_a["name_normalized"]
        == row_b["name_normalized"]
    )

    city_match = (
        bool(row_a["city_normalized"])
        and bool(row_b["city_normalized"])
        and row_a["city_normalized"]
        == row_b["city_normalized"]
    )

    if email_match and phone_match:
        confidence = "DETERMINISTIC"

    elif email_match:
        confidence = "HIGH_EMAIL"

    elif phone_match:
        confidence = "HIGH_PHONE"

    elif name_match and city_match:
        confidence = "CANDIDATE_NAME_CITY"

    else:
        return None

    return {
        "source_a": source_a,
        "row_a": row_a["source_row"],
        "source_b": source_b,
        "row_b": row_b["source_row"],
        "email_match": email_match,
        "phone_match": phone_match,
        "name_match": name_match,
        "city_match": city_match,
        "confidence": confidence,
    }


def generate_pairwise_candidates(
    source_a_name,
    source_a,
    source_b_name,
    source_b,
):
    candidates = []

    for _, row_a in source_a.iterrows():
        for _, row_b in source_b.iterrows():

            result = compare_records(
                source_a_name,
                row_a,
                source_b_name,
                row_b,
            )

            if result:
                candidates.append(result)

    return candidates


def print_candidates(
    title,
    candidates,
):
    print("\n" + "=" * 110)
    print(title)
    print("=" * 110)

    if not candidates:
        print("No candidates found.")
        return

    result = pd.DataFrame(candidates)

    print(
        result.to_string(index=False)
    )

    print(
        f"\nTotal candidates: {len(result)}"
    )

    print("\nConfidence distribution:")
    print(
        result["confidence"]
        .value_counts()
        .to_string()
    )


def main():
    naukri, gig, cbnexus = load_sources()

    naukri, gig, cbnexus = (
        remove_structural_anomalies(
            naukri,
            gig,
            cbnexus,
        )
    )

    naukri = prepare_naukri(naukri)
    gig = prepare_gig(gig)
    cbnexus = prepare_cbnexus(cbnexus)

    naukri_gig = generate_pairwise_candidates(
        "naukri",
        naukri,
        "gig",
        gig,
    )

    naukri_cbnexus = generate_pairwise_candidates(
        "naukri",
        naukri,
        "cbnexus",
        cbnexus,
    )

    gig_cbnexus = generate_pairwise_candidates(
        "gig",
        gig,
        "cbnexus",
        cbnexus,
    )

    print_candidates(
        "NAUKRI ↔ GIG",
        naukri_gig,
    )

    print_candidates(
        "NAUKRI ↔ CBNEXUS",
        naukri_cbnexus,
    )

    print_candidates(
        "GIG ↔ CBNEXUS",
        gig_cbnexus,
    )


if __name__ == "__main__":
    main()