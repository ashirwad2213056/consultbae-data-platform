from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")


def inspect_gig_anomalies() -> None:
    path = RAW_DIR / "source2_gig_workers.csv"

    df = pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
    )

    print("\n" + "=" * 100)
    print("GIG — SUSPICIOUS RECORDS")
    print("=" * 100)

    # Valid canonical status values
    valid_statuses = {
        "active",
        "inactive",
        "paused",
        "",
    }

    suspicious_status = df[
        ~df["status"].str.strip().str.lower().isin(valid_statuses)
    ]

    print("\nRows with unexpected status:")
    if suspicious_status.empty:
        print("None")
    else:
        print(suspicious_status.to_string(index=True))

    # Expected rate formats:
    # 1415/hr
    # 15k/month
    # 15.5k/month
    valid_rate_pattern = (
        r"^\d+(?:\.\d+)?(?:k)?/"
        r"(?:hr|month)$"
    )

    suspicious_rate = df[
        (
            ~df["rate"].str.strip().str.match(
                valid_rate_pattern,
                case=False,
                na=False,
            )
        )
        & (df["rate"].str.strip() != "")
    ]

    print("\nRows with unexpected rate:")
    if suspicious_rate.empty:
        print("None")
    else:
        print(suspicious_rate.to_string(index=True))

    # Completely blank rows
    blank_mask = df.apply(
        lambda row: all(
            str(value).strip() == ""
            for value in row
        ),
        axis=1,
    )

    print("\nCompletely blank rows:")
    if blank_mask.any():
        print(df[blank_mask].to_string(index=True))
    else:
        print("None")

    # Show rows around all anomalies
    anomaly_indexes = sorted(
        set(suspicious_status.index)
        | set(suspicious_rate.index)
        | set(df.index[blank_mask])
    )

    print("\nRows around detected anomalies:")

    if not anomaly_indexes:
        print("None")
        return

    displayed = set()

    for index in anomaly_indexes:
        start = max(0, index - 1)
        end = min(len(df), index + 2)

        for row_index in range(start, end):
            if row_index not in displayed:
                print(f"\nRow index: {row_index}")
                print(df.iloc[[row_index]].to_string(index=True))
                displayed.add(row_index)


def inspect_cbnexus_header() -> None:
    path = RAW_DIR / "source3_cbnexus_contacts.csv"

    df = pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
    )

    print("\n" + "=" * 100)
    print("CBNEXUS — REPEATED HEADER")
    print("=" * 100)

    header_mask = df.apply(
        lambda row: all(
            str(row[column]).strip().lower()
            == column.strip().lower()
            for column in df.columns
        ),
        axis=1,
    )

    if header_mask.any():
        print(df[header_mask].to_string(index=True))
    else:
        print("No repeated header detected")


def main() -> None:
    inspect_gig_anomalies()
    inspect_cbnexus_header()


if __name__ == "__main__":
    main()