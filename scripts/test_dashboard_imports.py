"""
Dashboard import / data smoke test.

Verifies that the dashboard's data pipeline works end-to-end WITHOUT launching
Streamlit: it imports the three module entry points, loads the data, computes the
KPIs and risk register, and confirms the keys the dashboard relies on exist.

Usage:
    python scripts/test_dashboard_imports.py
"""

import os
import sys

# Make the project root importable so 'src' can be found when run directly.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_loader import DataLoadingError, load_all_data  # noqa: E402
from src.kpi_engine import calculate_all_kpis  # noqa: E402
from src.risk_engine import create_executive_risk_register  # noqa: E402

DATA_DIR = os.path.join(PROJECT_ROOT, "data")

REQUIRED_DATA_KEYS = [
    "invoices",
    "customer_tickets",
    "approval_requests",
    "risk_rules",
]
REQUIRED_KPI_KEYS = [
    "invoice_kpis",
    "ticket_kpis",
    "approval_kpis",
    "executive_kpis",
]
REQUIRED_REGISTER_KEYS = [
    "risk_summary",
    "top_risks",
    "invoice_risks",
    "ticket_risks",
    "approval_risks",
    "all_risks",
]


def main() -> int:
    print("=" * 70)
    print("Enterprise AI Control Tower — Dashboard Import Smoke Test")
    print("=" * 70)

    try:
        all_data = load_all_data(data_dir=DATA_DIR)
        all_kpis = calculate_all_kpis(all_data)
        risk_register = create_executive_risk_register(all_data)
    except DataLoadingError as exc:
        print(f"\n[FAILED] Data loading error: {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"\n[FAILED] Unexpected error: {exc}")
        return 1

    errors = []
    for key in REQUIRED_DATA_KEYS:
        if key not in all_data:
            errors.append(f"all_data missing key: {key}")
    for key in REQUIRED_KPI_KEYS:
        if key not in all_kpis:
            errors.append(f"all_kpis missing key: {key}")
    for key in REQUIRED_REGISTER_KEYS:
        if key not in risk_register:
            errors.append(f"risk_register missing key: {key}")

    print("\nLoaded datasets:")
    for key in REQUIRED_DATA_KEYS:
        if key in all_data:
            print(f"  - {key:<20}: {len(all_data[key])} rows")

    print("\nKPI groups present     :", list(all_kpis.keys()))
    print("Risk register keys     :", list(risk_register.keys()))
    print(
        "Total risk findings    :",
        risk_register.get("risk_summary", {}).get("total_risk_findings", "N/A"),
    )

    print("\n" + "=" * 70)
    if errors:
        print("[FAILED] Dashboard contract verification failed:")
        for err in errors:
            print(f"  - {err}")
        print("=" * 70)
        return 1

    print("[SUCCESS] Dashboard data pipeline is ready. Run: streamlit run app.py")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
