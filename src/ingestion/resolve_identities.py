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

    # +91XXXXXXXXXX / 91XXXXXXXXXX
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    # 0XXXXXXXXXX
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]

    # Project standard:
    # canonical 10-digit Indian number.
    if len(digits) == 10:
        return digits

    return ""


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


def prepare_naukri(df):
    result = df.copy()

    result["source"] = "naukri"
    result["source_row"] = result.index

    result["email_normalized"] = (
        result["Email"].map(normalize_email)
    )

    result["phone_normalized"] = (
        result["Phone"].map(normalize_phone)
    )

    return result


def prepare_gig(df):
    result = df.copy()

    # Remove completely blank record.
    result = result[
        ~(
            result["email_id"].eq("")
            & result["worker_name"].eq("")
            & result["rate"].eq("")
            & result["location"].eq("")
            & result["status"].eq("")
            & result["skill_tags"].eq("")
        )
    ].copy()

    result["source"] = "gig"
    result["source_row"] = result.index

    result["email_normalized"] = (
        result["email_id"].map(normalize_email)
    )

    return result


def prepare_cbnexus(df):
    result = df.copy()

    # Remove repeated header.
    result = result[
        result["Name"].str.strip().str.lower()
        != "name"
    ].copy()

    result["source"] = "cbnexus"
    result["source_row"] = result.index

    result["phone_normalized"] = (
        result["Phone Number"].map(normalize_phone)
    )

    return result


class UnionFind:

    def __init__(self):
        self.parent = {}

    def add(self, item):
        if item not in self.parent:
            self.parent[item] = item

    def find(self, item):
        if self.parent[item] != item:
            self.parent[item] = self.find(
                self.parent[item]
            )

        return self.parent[item]

    def union(self, first, second):
        self.add(first)
        self.add(second)

        root_first = self.find(first)
        root_second = self.find(second)

        if root_first != root_second:
            self.parent[root_second] = root_first

    def groups(self):
        groups = {}

        for item in self.parent:
            root = self.find(item)

            groups.setdefault(
                root,
                [],
            ).append(item)

        return groups


class WorkerIdAllocator:

    def __init__(self, start: int):
        self.next_number = start

    def next_id(self) -> str:
        worker_id = f"W{self.next_number:06d}"
        self.next_number += 1
        return worker_id


def build_naukri_identity_clusters(naukri):
    """
    Build identity clusters inside Naukri first.

    Exact normalized email OR exact normalized phone
    connects Naukri records to the same identity.
    """

    uf = UnionFind()

    records = {}

    for _, row in naukri.iterrows():

        record_id = row["source_row"]

        uf.add(record_id)

        records[record_id] = row

    email_lookup = {}
    phone_lookup = {}

    conflicts = []

    for _, row in naukri.iterrows():

        record_id = row["source_row"]

        email = row["email_normalized"]
        phone = row["phone_normalized"]

        if email:

            if email in email_lookup:
                uf.union(
                    record_id,
                    email_lookup[email],
                )
            else:
                email_lookup[email] = record_id

        if phone:

            if phone in phone_lookup:
                uf.union(
                    record_id,
                    phone_lookup[phone],
                )
            else:
                phone_lookup[phone] = record_id

    return uf, records, conflicts


def assign_worker_ids(
    uf,
):
    """
    Assign one WorkerID to each identity cluster.
    """

    groups = uf.groups()

    worker_map = {}

    worker_number = 1

    for root, members in groups.items():

        worker_id = (
            f"W{worker_number:06d}"
        )

        worker_number += 1

        for member in members:
            worker_map[member] = worker_id

    return worker_map


def build_naukri_lookups(
    naukri,
    worker_map,
):
    email_lookup = {}
    phone_lookup = {}

    for _, row in naukri.iterrows():

        worker_id = worker_map[
            row["source_row"]
        ]

        email = row["email_normalized"]
        phone = row["phone_normalized"]

        if email:
            email_lookup.setdefault(
                email,
                set(),
            ).add(worker_id)

        if phone:
            phone_lookup.setdefault(
                phone,
                set(),
            ).add(worker_id)

    return email_lookup, phone_lookup


def resolve_gig(
    gig,
    email_lookup,
    worker_id_allocator,
):
    results = []

    for _, row in gig.iterrows():

        email = row["email_normalized"]

        worker_ids = email_lookup.get(
            email,
            set(),
        )

        if len(worker_ids) == 1:

            worker_id = next(iter(worker_ids))

            results.append(
                {
                    "worker_id": worker_id,
                    "source": "gig",
                    "source_row": row["source_row"],
                    "match_method": "EXACT_EMAIL",
                    "confidence": "HIGH",
                }
            )

        elif len(worker_ids) == 0:

            worker_id = worker_id_allocator.next_id()

            results.append(
                {
                    "worker_id": worker_id,
                    "source": "gig",
                    "source_row": row["source_row"],
                    "match_method": "SOURCE_ONLY",
                    "confidence": "BASE",
                }
            )

        else:

            results.append(
                {
                    "worker_id": None,
                    "source": "gig",
                    "source_row": row["source_row"],
                    "match_method": "EMAIL_CONFLICT",
                    "confidence": "REVIEW",
                }
            )

    return results


def resolve_cbnexus(
    cbnexus,
    phone_lookup,
    worker_id_allocator,
):
    results = []

    for _, row in cbnexus.iterrows():

        phone = row["phone_normalized"]

        worker_ids = phone_lookup.get(
            phone,
            set(),
        )

        if len(worker_ids) == 1:

            worker_id = next(iter(worker_ids))

            results.append(
                {
                    "worker_id": worker_id,
                    "source": "cbnexus",
                    "source_row": row["source_row"],
                    "match_method": "EXACT_PHONE",
                    "confidence": "HIGH",
                }
            )

        elif len(worker_ids) == 0:

            worker_id = worker_id_allocator.next_id()

            results.append(
                {
                    "worker_id": worker_id,
                    "source": "cbnexus",
                    "source_row": row["source_row"],
                    "match_method": "SOURCE_ONLY",
                    "confidence": "BASE",
                }
            )

        else:

            results.append(
                {
                    "worker_id": None,
                    "source": "cbnexus",
                    "source_row": row["source_row"],
                    "match_method": "PHONE_CONFLICT",
                    "confidence": "REVIEW",
                }
            )

    return results


def print_naukri_clusters(
    naukri,
    worker_map,
):
    print("\n" + "=" * 100)
    print("NAUKRI — IDENTITY CLUSTERS")
    print("=" * 100)

    grouped = {}

    for _, row in naukri.iterrows():

        worker_id = worker_map[
            row["source_row"]
        ]

        grouped.setdefault(
            worker_id,
            [],
        ).append(row)

    duplicate_clusters = 0

    for worker_id, rows in grouped.items():

        if len(rows) <= 1:
            continue

        duplicate_clusters += 1

        print(
            f"\n{worker_id}"
        )

        for row in rows:

            print(
                f"  Row: {row['source_row']} | "
                f"Name: {row['Full Name']} | "
                f"Email: {row['email_normalized']} | "
                f"Phone: {row['phone_normalized']}"
            )

    if duplicate_clusters == 0:
        print("No duplicate Naukri identity clusters.")


def print_summary(
    naukri,
    gig,
    cbnexus,
    results,
):
    print("\n" + "=" * 100)
    print("ENTITY RESOLUTION SUMMARY")
    print("=" * 100)

    print("\nSource records:")
    print(
        f"Naukri : {len(naukri)}"
    )
    print(
        f"Gig    : {len(gig)}"
    )
    print(
        f"CBNexus: {len(cbnexus)}"
    )

    print("\nResult records:")
    print(
        results["source"]
        .value_counts()
        .to_string()
    )

    print("\nMatch methods:")
    print(
        results["match_method"]
        .value_counts()
        .to_string()
    )

    print("\nConfidence:")
    print(
        results["confidence"]
        .value_counts()
        .to_string()
    )

    print("\nWorkerID count:")

    print(
        results["worker_id"]
        .dropna()
        .nunique()
    )

    print("\nReview records:")

    review = results[
        results["confidence"] == "REVIEW"
    ]

    if review.empty:
        print("None")
    else:
        print(
            review.to_string(index=False)
        )


def resolve_all_identities():
    """
    Resolve all source records against the Naukri identity anchor.

    Identity rules:
    - Naukri identities are clustered by exact normalized
      email OR exact normalized phone.
    - Gig matches Naukri by exact normalized email.
    - CBNexus matches Naukri by exact normalized phone.
    - Unmatched Gig and CBNexus records receive new WorkerIDs.
    - Name and city are never used for identity resolution.

    Returns:
        tuple:
            naukri,
            gig,
            cbnexus,
            results
    """

    naukri, gig, cbnexus = load_sources()

    naukri = prepare_naukri(naukri)
    gig = prepare_gig(gig)
    cbnexus = prepare_cbnexus(cbnexus)

    (
        naukri_uf,
        _,
        _,
    ) = build_naukri_identity_clusters(
        naukri
    )

    worker_map = assign_worker_ids(
        naukri_uf
    )

    worker_id_allocator = WorkerIdAllocator(
        start=len(set(worker_map.values())) + 1
    )

    (
        email_lookup,
        phone_lookup,
    ) = build_naukri_lookups(
        naukri,
        worker_map,
    )

    gig_results = resolve_gig(
        gig,
        email_lookup,
        worker_id_allocator,
    )

    cbnexus_results = resolve_cbnexus(
        cbnexus,
        phone_lookup,
        worker_id_allocator,
    )

    naukri_results = []

    for _, row in naukri.iterrows():
        naukri_results.append(
            {
                "worker_id": worker_map[
                    row["source_row"]
                ],
                "source": "naukri",
                "source_row": row["source_row"],
                "match_method": "NAUKRI_ANCHOR",
                "confidence": "BASE",
            }
        )

    results = pd.DataFrame(
        naukri_results
        + gig_results
        + cbnexus_results
    )

    return (
        naukri,
        gig,
        cbnexus,
        results,
        worker_map,
    )


def main():

    (
        naukri,
        gig,
        cbnexus,
        results,
        worker_map,
    ) = resolve_all_identities()

    print_naukri_clusters(
        naukri,
        worker_map,
    )

    print_summary(
        naukri,
        gig,
        cbnexus,
        results,
    )


if __name__ == "__main__":
    main()