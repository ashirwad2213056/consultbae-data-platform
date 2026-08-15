from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")


def normalize_name(value: str) -> str:
    return " ".join(value.strip().lower().split())


def normalize_city(value: str) -> str:
    value = value.strip().lower()

    city_map = {
        "bangalore": "bengaluru",
        "bengaluru": "bengaluru",
        "gurgaon": "gurugram",
        "gurugram": "gurugram",
        "noida": "noida",
        "pune": "pune",
        "delhi": "delhi",
        "new delhi": "delhi",
        "delhi ncr": "delhi",
    }

    return city_map.get(value, value)


def load_sources() -> tuple[pd.DataFrame, pd.DataFrame]:
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

    return gig, cbnexus


def remove_structural_anomalies(
    gig: pd.DataFrame,
    cbnexus: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    # Remove completely blank Gig rows.
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

    # Remove the repeated CBNexus header.
    cbnexus = cbnexus[
        cbnexus["Name"].str.strip().str.lower() != "name"
    ].copy()

    return gig, cbnexus


def prepare_sources(
    gig: pd.DataFrame,
    cbnexus: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    gig["name_normalized"] = (
        gig["worker_name"].map(normalize_name)
    )

    gig["city_normalized"] = (
        gig["location"].map(normalize_city)
    )

    cbnexus["name_normalized"] = (
        cbnexus["Name"].map(normalize_name)
    )

    cbnexus["city_normalized"] = (
        cbnexus["City"].map(normalize_city)
    )

    return gig, cbnexus


def find_name_location_matches(
    gig: pd.DataFrame,
    cbnexus: pd.DataFrame,
) -> pd.DataFrame:

    matches = []

    for gig_index, gig_row in gig.iterrows():

        for cbnexus_index, cbnexus_row in cbnexus.iterrows():

            name_match = (
                gig_row["name_normalized"]
                == cbnexus_row["name_normalized"]
            )

            city_match = (
                gig_row["city_normalized"]
                == cbnexus_row["city_normalized"]
            )

            if name_match and city_match:
                matches.append(
                    {
                        "gig_row": gig_index,
                        "gig_name": gig_row["worker_name"],
                        "gig_location": gig_row["location"],
                        "cbnexus_row": cbnexus_index,
                        "cbnexus_name": cbnexus_row["Name"],
                        "cbnexus_city": cbnexus_row["City"],
                        "match_type": "EXACT_NAME_AND_CITY",
                    }
                )

    return pd.DataFrame(matches)


def main() -> None:

    gig, cbnexus = load_sources()

    gig, cbnexus = remove_structural_anomalies(
        gig,
        cbnexus,
    )

    gig, cbnexus = prepare_sources(
        gig,
        cbnexus,
    )

    matches = find_name_location_matches(
        gig,
        cbnexus,
    )

    print("\n" + "=" * 100)
    print("GIG ↔ CBNEXUS — EXACT NAME + CITY CANDIDATES")
    print("=" * 100)

    if matches.empty:
        print("No exact name + city candidates found.")
    else:
        print(matches.to_string(index=False))

        print(
            f"\nTotal candidates: {len(matches)}"
        )


if __name__ == "__main__":
    main()