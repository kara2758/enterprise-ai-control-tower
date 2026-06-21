"""
Manual test / smoke check for the risk engine.

Loads all synthetic datasets, builds the executive risk register, prints the key
results, and verifies the output contract (required keys present, risks found,
at least one Critical risk). This is a quick verification script, not a unit-test
suite.

Usage:
    python scripts/test_risk_engine.py
"""

import os
import sys

# Make the project root importable so 'src' can be found when run directly.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd  # noqa: E402

from src.data_loader import DataLoadingError, load_all_data  # noqa: E402
from src.risk_engine import create_executive_risk_register  # noqa: E402

DATA_DIR = os.path.join(PROJECT_ROOT, "data")

REQUIRED_KEYS = [
    "risk_summary",
    "top_risks",
    "invoice_risks",
    "ticket_risks",
    "approval_risks",
    "all_risks",
]


def main() -> int:
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)

    print("=" * 70)
    print("Enterprise AI Control Tower — Risk Engine Test")
    print("=" * 70)

    try:
        all_data = load_all_data(data_dir=DATA_DIR)
    except DataLoadingError as exc:
        print(f"\n[FAILED] Data loading error: {exc}")
        return 1

    register = create_executive_risk_register(all_data)
    summary = register["risk_summary"]
    all_risks = register["all_risks"]
    top_risks = register["top_risks"]

    print("\n--- Risk Summary ---")
    for key, value in summary.items():
        print(f"  {key:<36}: {value}")

    print("\n--- Count by Risk Level ---")
    print(all_risks["risk_level"].value_counts().to_string())

    print("\n--- Count by Source ---")
    print(all_risks["source"].value_counts().to_string())

    print(f"\n--- Top risk category   : {summary['top_risk_category']}")
    print(f"--- Top risk department : {summary['top_risk_department']}")
    print(
        f"--- Financial exposure  : "
        f"{summary['financial_exposure_from_risks_usd']:,.2f} USD"
    )

    print("\n--- First 10 Top Risks ---")
    print(top_risks.head(10).to_string(index=False))

    # ---- Verification ----
    print("\n" + "=" * 70)
    errors = []

    missing_keys = [k for k in REQUIRED_KEYS if k not in register]
    if missing_keys:
        errors.append(f"Missing register keys: {missing_keys}")

    if all_risks.empty:
        errors.append("all_risks DataFrame is empty.")

    if summary["critical_risk_count"] < 1:
        errors.append("Expected at least one Critical risk, found none.")

    if errors:
        print("[FAILED] Risk engine verification failed:")
        for err in errors:
            print(f"  - {err}")
        print("=" * 70)
        return 1

    print("[SUCCESS] Risk engine ran correctly and all checks passed.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
