"""
Manual test / smoke check for the KPI engine.

Loads all synthetic datasets, calculates every KPI group, prints them clearly,
and verifies that all expected KPI keys are present. This is a quick verification
script, not a unit-test suite.

Usage:
    python scripts/test_kpi_engine.py
"""

import os
import sys

# Make the project root importable so 'src' can be found when run directly.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_loader import DataLoadingError, load_all_data  # noqa: E402
from src.kpi_engine import calculate_all_kpis  # noqa: E402

DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# Expected keys per KPI group, used to verify the engine's output contract.
EXPECTED_KEYS = {
    "invoice_kpis": [
        "total_invoices",
        "total_invoice_amount_usd",
        "average_invoice_amount_usd",
        "paid_invoice_count",
        "unpaid_invoice_count",
        "partially_paid_invoice_count",
        "on_hold_invoice_count",
        "pending_approval_invoice_count",
        "approved_invoice_count",
        "rejected_invoice_count",
        "under_review_invoice_count",
        "overdue_invoice_count",
        "overdue_more_than_7_days_count",
        "high_value_pending_invoice_count",
    ],
    "ticket_kpis": [
        "total_tickets",
        "open_ticket_count",
        "in_progress_ticket_count",
        "resolved_ticket_count",
        "escalated_ticket_count",
        "waiting_for_customer_count",
        "critical_ticket_count",
        "high_priority_ticket_count",
        "sla_within_count",
        "sla_at_risk_count",
        "sla_breached_count",
        "average_response_time_hours",
        "average_resolution_time_hours",
        "unresolved_ticket_count",
    ],
    "approval_kpis": [
        "total_approval_requests",
        "pending_approval_requests",
        "approved_approval_requests",
        "rejected_approval_requests",
        "escalated_approval_requests",
        "bottleneck_count",
        "critical_business_impact_count",
        "critical_pending_count",
        "average_waiting_days",
        "average_waiting_days_pending",
        "total_pending_amount_usd",
    ],
    "executive_kpis": [
        "total_open_work_items",
        "total_attention_items",
        "total_financial_exposure_usd",
        "operational_delay_indicators",
        "process_bottleneck_indicators",
        "customer_sla_pressure_count",
    ],
}


def _print_group(title: str, kpis: dict) -> None:
    print(f"\n--- {title} ---")
    for key, value in kpis.items():
        print(f"  {key:<34}: {value}")


def main() -> int:
    print("=" * 70)
    print("Enterprise AI Control Tower — KPI Engine Test")
    print("=" * 70)

    try:
        all_data = load_all_data(data_dir=DATA_DIR)
    except DataLoadingError as exc:
        print(f"\n[FAILED] Data loading error: {exc}")
        return 1

    kpis = calculate_all_kpis(all_data)

    _print_group("Invoice KPIs", kpis["invoice_kpis"])
    _print_group("Ticket KPIs", kpis["ticket_kpis"])
    _print_group("Approval KPIs", kpis["approval_kpis"])
    _print_group("Executive KPIs", kpis["executive_kpis"])

    # Verify expected keys exist in each group.
    missing_report = {}
    for group, keys in EXPECTED_KEYS.items():
        missing = [k for k in keys if k not in kpis.get(group, {})]
        if missing:
            missing_report[group] = missing

    print("\n" + "=" * 70)
    if missing_report:
        print("[FAILED] Missing KPI keys detected:")
        for group, missing in missing_report.items():
            print(f"  {group}: {missing}")
        print("=" * 70)
        return 1

    print("[SUCCESS] KPI engine ran correctly and all expected keys are present.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
