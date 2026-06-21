"""
Manual test / smoke check for the data loader module.

Loads all synthetic datasets via ``src.data_loader.load_all_data`` and prints a
short report: row counts, column names, and the data types of the important date
and numeric columns. This is a quick verification script, not a unit-test suite.

Usage:
    python scripts/test_data_loader.py
"""

import os
import sys

# Make the project root importable so 'src' can be found when run directly.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_loader import DataLoadingError, load_all_data  # noqa: E402

# Important columns to display dtypes for, per dataset.
KEY_COLUMNS = {
    "invoices": ["invoice_date", "due_date", "amount_usd", "days_overdue"],
    "customer_tickets": [
        "opened_date",
        "sla_deadline",
        "resolved_date",
        "response_time_hours",
        "resolution_time_hours",
    ],
    "approval_requests": [
        "requested_date",
        "approval_deadline",
        "waiting_days",
        "amount_usd",
        "bottleneck_flag",
    ],
    "risk_rules": [],
}

DATA_DIR = os.path.join(PROJECT_ROOT, "data")


def main() -> int:
    print("=" * 70)
    print("Enterprise AI Control Tower — Data Loader Test")
    print("=" * 70)

    try:
        datasets = load_all_data(data_dir=DATA_DIR)
    except DataLoadingError as exc:
        print(f"\n[FAILED] Data loading error: {exc}")
        return 1

    for name, df in datasets.items():
        print(f"\n--- {name} ---")
        print(f"  rows   : {len(df)}")
        print(f"  columns: {list(df.columns)}")

        key_cols = KEY_COLUMNS.get(name, [])
        if key_cols:
            print("  key column dtypes:")
            for col in key_cols:
                print(f"    - {col}: {df[col].dtype}")

    print("\n" + "=" * 70)
    print("[SUCCESS] All datasets loaded and validated successfully.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
