"""
KPI Engine module.

Calculates executive-level KPIs from the clean pandas DataFrames produced by
``src.data_loader``. KPIs are grouped into four categories:

- invoice KPIs       (accounts-payable health)
- ticket KPIs        (customer support / SLA health)
- approval KPIs      (approval-workflow health)
- executive KPIs     (cross-domain roll-up for leadership)

This module performs aggregation only. It does NOT classify risk (no Low/Medium/
High labels — that is Stage 5), build dashboards, or call any external API.

The ``risk_rules`` dataset is available in ``all_data`` but is intentionally not
used here; it is a reference table consumed by the future risk engine.
"""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd


def _safe_mean(series: pd.Series) -> float:
    """Return the mean of a series, or 0 if it is empty / has no valid values.

    Non-numeric and missing (NaN) values are ignored. If nothing valid remains,
    0 is returned instead of NaN so downstream consumers get a clean number.
    """
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return 0.0
    return float(numeric.mean())


def _round2(value: float) -> float:
    """Round a float to 2 decimal places (currency / hours friendly)."""
    return round(float(value), 2)


# --------------------------------------------------------------------------- #
# Invoice KPIs
# --------------------------------------------------------------------------- #

def calculate_invoice_kpis(invoices_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate accounts-payable invoice KPIs."""
    df = invoices_df

    approval = df["approval_status"]
    payment = df["payment_status"]
    amount = pd.to_numeric(df["amount_usd"], errors="coerce")
    days_overdue = pd.to_numeric(df["days_overdue"], errors="coerce")

    high_value_pending = (amount > 50_000) & (approval == "Pending")

    return {
        "total_invoices": int(len(df)),
        "total_invoice_amount_usd": _round2(amount.sum()),
        "average_invoice_amount_usd": _round2(_safe_mean(amount)),
        "paid_invoice_count": int((payment == "Paid").sum()),
        "unpaid_invoice_count": int((payment == "Unpaid").sum()),
        "partially_paid_invoice_count": int((payment == "Partially Paid").sum()),
        "on_hold_invoice_count": int((payment == "On Hold").sum()),
        "pending_approval_invoice_count": int((approval == "Pending").sum()),
        "approved_invoice_count": int((approval == "Approved").sum()),
        "rejected_invoice_count": int((approval == "Rejected").sum()),
        "under_review_invoice_count": int((approval == "Under Review").sum()),
        "overdue_invoice_count": int((days_overdue > 0).sum()),
        "overdue_more_than_7_days_count": int((days_overdue > 7).sum()),
        "high_value_pending_invoice_count": int(high_value_pending.sum()),
    }


# --------------------------------------------------------------------------- #
# Customer support ticket KPIs
# --------------------------------------------------------------------------- #

def calculate_ticket_kpis(tickets_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate customer support / SLA KPIs."""
    df = tickets_df

    status = df["status"]
    priority = df["priority"]
    sla = df["sla_status"]

    return {
        "total_tickets": int(len(df)),
        "open_ticket_count": int((status == "Open").sum()),
        "in_progress_ticket_count": int((status == "In Progress").sum()),
        "resolved_ticket_count": int((status == "Resolved").sum()),
        "escalated_ticket_count": int((status == "Escalated").sum()),
        "waiting_for_customer_count": int((status == "Waiting for Customer").sum()),
        "critical_ticket_count": int((priority == "Critical").sum()),
        "high_priority_ticket_count": int((priority == "High").sum()),
        "sla_within_count": int((sla == "Within SLA").sum()),
        "sla_at_risk_count": int((sla == "At Risk").sum()),
        "sla_breached_count": int((sla == "Breached").sum()),
        "average_response_time_hours": _round2(
            _safe_mean(df["response_time_hours"])
        ),
        "average_resolution_time_hours": _round2(
            _safe_mean(df["resolution_time_hours"])
        ),
        "unresolved_ticket_count": int(df["resolved_date"].isna().sum()),
    }


# --------------------------------------------------------------------------- #
# Approval workflow KPIs
# --------------------------------------------------------------------------- #

def calculate_approval_kpis(approvals_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate approval-workflow KPIs."""
    df = approvals_df

    status = df["approval_status"]
    impact = df["business_impact"]
    waiting_days = pd.to_numeric(df["waiting_days"], errors="coerce")
    amount = pd.to_numeric(df["amount_usd"], errors="coerce")
    bottleneck = df["bottleneck_flag"].astype(bool)

    open_mask = status.isin(["Pending", "Escalated"])
    critical_pending = (impact == "Critical") & (status == "Pending")

    return {
        "total_approval_requests": int(len(df)),
        "pending_approval_requests": int((status == "Pending").sum()),
        "approved_approval_requests": int((status == "Approved").sum()),
        "rejected_approval_requests": int((status == "Rejected").sum()),
        "escalated_approval_requests": int((status == "Escalated").sum()),
        "bottleneck_count": int(bottleneck.sum()),
        "critical_business_impact_count": int((impact == "Critical").sum()),
        "critical_pending_count": int(critical_pending.sum()),
        "average_waiting_days": _round2(_safe_mean(waiting_days)),
        "average_waiting_days_pending": _round2(_safe_mean(waiting_days[open_mask])),
        "total_pending_amount_usd": _round2(amount[open_mask].sum()),
    }


# --------------------------------------------------------------------------- #
# Executive roll-up KPIs
# --------------------------------------------------------------------------- #

def calculate_executive_kpis(all_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Calculate high-level executive KPIs by combining the domain KPIs.

    Args:
        all_data: The dictionary returned by ``load_all_data()``.
    """
    invoice_kpis = calculate_invoice_kpis(all_data["invoices"])
    ticket_kpis = calculate_ticket_kpis(all_data["customer_tickets"])
    approval_kpis = calculate_approval_kpis(all_data["approval_requests"])

    invoices_df = all_data["invoices"]
    invoice_amount = pd.to_numeric(invoices_df["amount_usd"], errors="coerce")
    open_payment_mask = invoices_df["payment_status"].isin(
        ["Unpaid", "Partially Paid", "On Hold"]
    )
    open_invoice_exposure = invoice_amount[open_payment_mask].sum()

    total_open_work_items = (
        ticket_kpis["unresolved_ticket_count"]
        + invoice_kpis["pending_approval_invoice_count"]
        + approval_kpis["pending_approval_requests"]
        + approval_kpis["escalated_approval_requests"]
    )

    total_attention_items = (
        invoice_kpis["overdue_more_than_7_days_count"]
        + invoice_kpis["high_value_pending_invoice_count"]
        + ticket_kpis["sla_at_risk_count"]
        + ticket_kpis["sla_breached_count"]
        + approval_kpis["bottleneck_count"]
        + approval_kpis["critical_pending_count"]
    )

    total_financial_exposure_usd = _round2(
        open_invoice_exposure + approval_kpis["total_pending_amount_usd"]
    )

    operational_delay_indicators = (
        invoice_kpis["overdue_more_than_7_days_count"]
        + ticket_kpis["sla_breached_count"]
        + approval_kpis["bottleneck_count"]
    )

    process_bottleneck_indicators = (
        approval_kpis["bottleneck_count"]
        + approval_kpis["pending_approval_requests"]
        + approval_kpis["escalated_approval_requests"]
    )

    customer_sla_pressure_count = (
        ticket_kpis["sla_at_risk_count"] + ticket_kpis["sla_breached_count"]
    )

    return {
        "total_open_work_items": int(total_open_work_items),
        "total_attention_items": int(total_attention_items),
        "total_financial_exposure_usd": total_financial_exposure_usd,
        "operational_delay_indicators": int(operational_delay_indicators),
        "process_bottleneck_indicators": int(process_bottleneck_indicators),
        "customer_sla_pressure_count": int(customer_sla_pressure_count),
    }


# --------------------------------------------------------------------------- #
# Aggregate entry point
# --------------------------------------------------------------------------- #

def calculate_all_kpis(all_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, Any]]:
    """Calculate every KPI group and return them as a nested dictionary.

    Args:
        all_data: The dictionary returned by ``load_all_data()``.

    Returns:
        A dictionary with keys ``invoice_kpis``, ``ticket_kpis``,
        ``approval_kpis``, and ``executive_kpis``.
    """
    return {
        "invoice_kpis": calculate_invoice_kpis(all_data["invoices"]),
        "ticket_kpis": calculate_ticket_kpis(all_data["customer_tickets"]),
        "approval_kpis": calculate_approval_kpis(all_data["approval_requests"]),
        "executive_kpis": calculate_executive_kpis(all_data),
    }
