"""
Risk Engine module.

Applies clear, record-level business rules to the synthetic datasets and produces
prioritized risk findings for the future dashboard and executive-summary stages.

Each detected risk becomes one row in a findings DataFrame, carrying a risk name,
category, level, numeric severity score, and a recommended action. The module
also produces summary metrics and an "executive risk register" that bundles
everything together.

This module performs deterministic rule-based detection only. It does NOT build
dashboards, generate AI text, or call any external API. AI-generated risk
explanations arrive later in Stage 7.
"""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd

# Severity score mapping shared across all risk types.
SEVERITY_SCORES: Dict[str, int] = {
    "Critical": 100,
    "High": 75,
    "Medium": 50,
    "Low": 25,
}

# Core columns kept in the combined ``all_risks`` view (always present).
COMMON_RISK_COLUMNS = [
    "source",
    "record_id",
    "department",
    "risk_name",
    "risk_category",
    "risk_level",
    "severity_score",
    "recommended_action",
]

# Optional metric columns carried into the combined view when available. They are
# NaN for sources that don't have them (e.g. tickets have no amount_usd). This
# lets the summary compute financial exposure and lets get_top_risks tie-break.
OPTIONAL_RISK_COLUMNS = ["amount_usd", "days_overdue", "waiting_days"]

ALL_RISK_COLUMNS = COMMON_RISK_COLUMNS + OPTIONAL_RISK_COLUMNS


def _severity(level: str) -> int:
    """Return the numeric severity score for a risk level (default Low=25)."""
    return SEVERITY_SCORES.get(level, SEVERITY_SCORES["Low"])


# --------------------------------------------------------------------------- #
# Invoice risks
# --------------------------------------------------------------------------- #

def detect_invoice_risks(invoices_df: pd.DataFrame) -> pd.DataFrame:
    """Detect record-level risks in the invoices dataset."""
    columns = [
        "source",
        "record_id",
        "department",
        "risk_name",
        "risk_category",
        "risk_level",
        "severity_score",
        "amount_usd",
        "days_overdue",
        "current_status",
        "recommended_action",
    ]

    df = invoices_df
    amount = pd.to_numeric(df["amount_usd"], errors="coerce")
    days_overdue = pd.to_numeric(df["days_overdue"], errors="coerce")
    current_status = (
        df["approval_status"].astype(str) + " / " + df["payment_status"].astype(str)
    )

    findings = []

    def _add(mask: pd.Series, risk_name: str, category: str, level: str, action: str):
        for idx in df.index[mask.fillna(False)]:
            findings.append(
                {
                    "source": "invoices",
                    "record_id": df.at[idx, "invoice_id"],
                    "department": df.at[idx, "department"],
                    "risk_name": risk_name,
                    "risk_category": category,
                    "risk_level": level,
                    "severity_score": _severity(level),
                    "amount_usd": amount.at[idx],
                    "days_overdue": days_overdue.at[idx],
                    "current_status": current_status.at[idx],
                    "recommended_action": action,
                }
            )

    # A) Overdue invoice more than 7 days
    _add(
        days_overdue > 7,
        "Overdue Invoice (> 7 days)",
        "Financial Delay",
        "High",
        "Escalate overdue invoice review and confirm payment plan.",
    )
    # B) High-value pending invoice
    _add(
        (amount > 50_000) & (df["approval_status"] == "Pending"),
        "High-Value Pending Invoice",
        "Financial Exposure",
        "High",
        "Prioritize approval review for high-value pending invoice.",
    )
    # C) Invoice on hold
    _add(
        df["payment_status"] == "On Hold",
        "Invoice On Hold",
        "Payment Hold",
        "Medium",
        "Review hold reason and resolve payment blockage.",
    )

    return pd.DataFrame(findings, columns=columns)


# --------------------------------------------------------------------------- #
# Ticket risks
# --------------------------------------------------------------------------- #

def detect_ticket_risks(tickets_df: pd.DataFrame) -> pd.DataFrame:
    """Detect record-level risks in the customer tickets dataset."""
    columns = [
        "source",
        "record_id",
        "department",
        "risk_name",
        "risk_category",
        "risk_level",
        "severity_score",
        "priority",
        "status",
        "sla_status",
        "response_time_hours",
        "resolution_time_hours",
        "recommended_action",
    ]

    df = tickets_df
    response = pd.to_numeric(df["response_time_hours"], errors="coerce")
    resolution = pd.to_numeric(df["resolution_time_hours"], errors="coerce")

    findings = []

    def _add(mask: pd.Series, risk_name: str, category: str, level: str, action: str):
        for idx in df.index[mask.fillna(False)]:
            findings.append(
                {
                    "source": "customer_tickets",
                    "record_id": df.at[idx, "ticket_id"],
                    "department": df.at[idx, "department"],
                    "risk_name": risk_name,
                    "risk_category": category,
                    "risk_level": level,
                    "severity_score": _severity(level),
                    "priority": df.at[idx, "priority"],
                    "status": df.at[idx, "status"],
                    "sla_status": df.at[idx, "sla_status"],
                    "response_time_hours": response.at[idx],
                    "resolution_time_hours": resolution.at[idx],
                    "recommended_action": action,
                }
            )

    # A) SLA breached
    _add(
        df["sla_status"] == "Breached",
        "SLA Breached",
        "Customer SLA",
        "High",
        "Escalate breached SLA ticket and review root cause.",
    )
    # B) Ticket at risk
    _add(
        df["sla_status"] == "At Risk",
        "Ticket At Risk",
        "Customer SLA Pressure",
        "Medium",
        "Prioritize ticket before SLA breach.",
    )
    # C) Critical open ticket
    _add(
        (df["priority"] == "Critical") & (df["status"] != "Resolved"),
        "Critical Open Ticket",
        "Customer Impact",
        "High",
        "Assign immediate ownership and monitor until resolution.",
    )

    return pd.DataFrame(findings, columns=columns)


# --------------------------------------------------------------------------- #
# Approval risks
# --------------------------------------------------------------------------- #

def detect_approval_risks(approvals_df: pd.DataFrame) -> pd.DataFrame:
    """Detect record-level risks in the approval requests dataset."""
    columns = [
        "source",
        "record_id",
        "department",
        "risk_name",
        "risk_category",
        "risk_level",
        "severity_score",
        "amount_usd",
        "waiting_days",
        "business_impact",
        "current_status",
        "recommended_action",
    ]

    df = approvals_df
    amount = pd.to_numeric(df["amount_usd"], errors="coerce")
    waiting_days = pd.to_numeric(df["waiting_days"], errors="coerce")
    bottleneck = df["bottleneck_flag"].astype(bool)

    findings = []

    def _add(mask: pd.Series, risk_name: str, category: str, level: str, action: str):
        for idx in df.index[mask.fillna(False)]:
            findings.append(
                {
                    "source": "approval_requests",
                    "record_id": df.at[idx, "request_id"],
                    "department": df.at[idx, "department"],
                    "risk_name": risk_name,
                    "risk_category": category,
                    "risk_level": level,
                    "severity_score": _severity(level),
                    "amount_usd": amount.at[idx],
                    "waiting_days": waiting_days.at[idx],
                    "business_impact": df.at[idx, "business_impact"],
                    "current_status": df.at[idx, "approval_status"],
                    "recommended_action": action,
                }
            )

    # A) Approval bottleneck
    _add(
        bottleneck,
        "Approval Bottleneck",
        "Process Bottleneck",
        "High",
        "Escalate delayed approval and review responsible approver workload.",
    )
    # B) Critical pending request
    _add(
        (df["business_impact"] == "Critical") & (df["approval_status"] == "Pending"),
        "Critical Pending Request",
        "Critical Business Impact",
        "Critical",
        "Prioritize immediate management decision.",
    )
    # C) Escalated approval request
    _add(
        df["approval_status"] == "Escalated",
        "Escalated Approval Request",
        "Approval Escalation",
        "High",
        "Review escalation reason and assign senior decision owner.",
    )

    return pd.DataFrame(findings, columns=columns)


# --------------------------------------------------------------------------- #
# Combine
# --------------------------------------------------------------------------- #

def detect_all_risks(all_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Run all detectors and return per-source plus a combined risk DataFrame.

    The combined ``all_risks`` DataFrame keeps the common risk columns, is sorted
    by ``severity_score`` descending, and uses a stable sort so equal-severity
    findings retain their original (invoice -> ticket -> approval) order.
    """
    invoice_risks = detect_invoice_risks(all_data["invoices"])
    ticket_risks = detect_ticket_risks(all_data["customer_tickets"])
    approval_risks = detect_approval_risks(all_data["approval_requests"])

    # Reindex each per-source frame to the unified column set; metric columns a
    # source doesn't have (e.g. tickets have no amount_usd) become NaN.
    combined = pd.concat(
        [
            invoice_risks.reindex(columns=ALL_RISK_COLUMNS),
            ticket_risks.reindex(columns=ALL_RISK_COLUMNS),
            approval_risks.reindex(columns=ALL_RISK_COLUMNS),
        ],
        ignore_index=True,
    )
    combined = combined.sort_values(
        by="severity_score", ascending=False, kind="stable"
    ).reset_index(drop=True)

    return {
        "invoice_risks": invoice_risks,
        "ticket_risks": ticket_risks,
        "approval_risks": approval_risks,
        "all_risks": combined,
    }


# --------------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------------- #

def calculate_risk_summary(all_risks_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate summary metrics over the combined risk findings."""
    total = int(len(all_risks_df))

    if total == 0:
        return {
            "total_risk_findings": 0,
            "critical_risk_count": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "average_severity_score": 0.0,
            "highest_severity_score": 0,
            "top_risk_category": None,
            "top_risk_department": None,
            "financial_exposure_from_risks_usd": 0.0,
        }

    level = all_risks_df["risk_level"]
    severity = pd.to_numeric(all_risks_df["severity_score"], errors="coerce")

    # amount_usd may not exist in the common view; pull from the column if present.
    if "amount_usd" in all_risks_df.columns:
        amount = pd.to_numeric(all_risks_df["amount_usd"], errors="coerce")
        financial_exposure = float(amount.dropna().sum())
    else:
        financial_exposure = 0.0

    top_category = all_risks_df["risk_category"].value_counts().idxmax()
    top_department = all_risks_df["department"].value_counts().idxmax()

    return {
        "total_risk_findings": total,
        "critical_risk_count": int((level == "Critical").sum()),
        "high_risk_count": int((level == "High").sum()),
        "medium_risk_count": int((level == "Medium").sum()),
        "low_risk_count": int((level == "Low").sum()),
        "average_severity_score": round(float(severity.mean()), 2),
        "highest_severity_score": int(severity.max()),
        "top_risk_category": top_category,
        "top_risk_department": top_department,
        "financial_exposure_from_risks_usd": round(financial_exposure, 2),
    }


# --------------------------------------------------------------------------- #
# Top risks
# --------------------------------------------------------------------------- #

def get_top_risks(all_risks_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the top ``n`` risk findings.

    Sorted by severity_score (desc), then amount_usd (desc) and a combined
    delay metric (waiting_days / days_overdue, desc) where those columns exist.
    A stable sort preserves original order for fully-tied rows.
    """
    if all_risks_df.empty:
        return all_risks_df.copy()

    df = all_risks_df.copy()
    sort_columns = ["severity_score"]

    if "amount_usd" in df.columns:
        df["_amount_sort"] = pd.to_numeric(df["amount_usd"], errors="coerce").fillna(-1)
        sort_columns.append("_amount_sort")

    # Combine the two delay-style metrics if present, so a single column drives sort.
    delay = pd.Series(-1.0, index=df.index)
    has_delay = False
    if "days_overdue" in df.columns:
        delay = delay.combine(
            pd.to_numeric(df["days_overdue"], errors="coerce").fillna(-1), max
        )
        has_delay = True
    if "waiting_days" in df.columns:
        delay = delay.combine(
            pd.to_numeric(df["waiting_days"], errors="coerce").fillna(-1), max
        )
        has_delay = True
    if has_delay:
        df["_delay_sort"] = delay
        sort_columns.append("_delay_sort")

    df = df.sort_values(by=sort_columns, ascending=False, kind="stable")
    df = df.drop(columns=[c for c in ["_amount_sort", "_delay_sort"] if c in df.columns])
    return df.head(n).reset_index(drop=True)


# --------------------------------------------------------------------------- #
# Executive risk register
# --------------------------------------------------------------------------- #

def create_executive_risk_register(
    all_data: Dict[str, pd.DataFrame]
) -> Dict[str, Any]:
    """Build the full executive risk register used by later stages.

    Returns a dictionary with the risk summary, top risks, the per-source risk
    DataFrames, and the combined ``all_risks`` DataFrame.
    """
    risks = detect_all_risks(all_data)
    summary = calculate_risk_summary(risks["all_risks"])
    top_risks = get_top_risks(risks["all_risks"], n=10)

    return {
        "risk_summary": summary,
        "top_risks": top_risks,
        "invoice_risks": risks["invoice_risks"],
        "ticket_risks": risks["ticket_risks"],
        "approval_risks": risks["approval_risks"],
        "all_risks": risks["all_risks"],
    }
