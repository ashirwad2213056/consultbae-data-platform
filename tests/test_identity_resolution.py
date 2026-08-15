from pathlib import Path

import pandas as pd

from src.ingestion.resolve_identities import (
    WorkerIdAllocator,
    resolve_all_identities,
)


RAW_DIR = Path("data/raw")


def normalize_email(value: str) -> str:
    return value.strip().lower()


def normalize_phone(value: str) -> str:
    digits = "".join(
        character
        for character in value
        if character.isdigit()
    )

    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]

    if len(digits) == 10:
        return digits

    return ""


def test_nikhil_duplicate_identity():
    df = pd.read_csv(
        RAW_DIR / "source1_naukri_applicants.csv",
        dtype=str,
        keep_default_na=False,
    )

    rows = df[
        df["Full Name"]
        .str.strip()
        .str.lower()
        .eq("nikhil chopra")
    ]

    assert len(rows) == 2

    phones = {
        normalize_phone(value)
        for value in rows["Phone"]
    }

    assert phones == {"9000000103"}


def test_rohit_verma_duplicate_identity():
    df = pd.read_csv(
        RAW_DIR / "source1_naukri_applicants.csv",
        dtype=str,
        keep_default_na=False,
    )

    rows = df[
        df["Phone"].map(normalize_phone)
        == "9000000294"
    ]

    assert len(rows) == 2

    emails = {
        normalize_email(value)
        for value in rows["Email"]
    }

    assert emails == {
        "rohit.verma13@mailtest.example.org"
    }


def test_phone_normalization():
    assert (
        normalize_phone("+91-9000000131")
        == "9000000131"
    )

    assert (
        normalize_phone("919000000231")
        == "9000000231"
    )

    assert (
        normalize_phone("09000000287")
        == "9000000287"
    )


def test_repeated_cbnexus_arjun_is_not_same_phone():
    df = pd.read_csv(
        RAW_DIR / "source3_cbnexus_contacts.csv",
        dtype=str,
        keep_default_na=False,
    )

    df = df[
        df["Name"].str.strip().str.lower()
        != "name"
    ]

    rows = df[
        df["Name"]
        .str.strip()
        .str.lower()
        .eq("arjun mehta")
    ]

    phones = {
        normalize_phone(value)
        for value in rows["Phone Number"]
    }

    assert phones == {
        "9000000131",
        "9000000272",
    }

def test_worker_id_allocator_is_sequential():
    allocator = WorkerIdAllocator(start=41)

    assert allocator.next_id() == "W000041"
    assert allocator.next_id() == "W000042"
    assert allocator.next_id() == "W000043"




def test_resolve_all_identities_contract():
    (
        naukri,
        gig,
        cbnexus,
        results,
        worker_map,
    ) = resolve_all_identities()

    assert len(naukri) == 42
    assert len(gig) == 31
    assert len(cbnexus) == 30

    assert len(results) == 103

    assert results["worker_id"].notna().all()

    assert (
        results["worker_id"].nunique()
        == 61
    )

    assert set(results["source"]) == {
        "naukri",
        "gig",
        "cbnexus",
    }

    assert set(
        results["match_method"]
    ) == {
        "NAUKRI_ANCHOR",
        "EXACT_EMAIL",
        "EXACT_PHONE",
        "SOURCE_ONLY",
    }