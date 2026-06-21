"""
Synthetic data generator for the Enterprise AI Control Tower.

Generates realistic — but entirely fictional — business datasets for the
demonstration company **ABC Global Services** and writes them as CSV files into
the ``data/`` folder.

This script is fully reproducible:
- A fixed random seed is used.
- A fixed reference date (2026-06-22) anchors all "as of today" calculations
  such as ``days_overdue`` and ``waiting_days``.

It uses only pandas and the Python standard library. It does NOT call any
external API, and it contains NO real company, customer, vendor, invoice, or
personal data — every name and value is synthetic.

Usage:
    python scripts/generate_synthetic_data.py
"""

import os
import random
from datetime import date, datetime, timedelta

import pandas as pd

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

RANDOM_SEED = 42
REFERENCE_DATE = date(2026, 6, 22)  # Fixed "today" for reproducible calculations

N_INVOICES = 280
N_TICKETS = 320
N_APPROVALS = 200

# Resolve paths relative to this script so it works from any working directory.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# --------------------------------------------------------------------------- #
# Fictional reference pools (all invented — no real entities)
# --------------------------------------------------------------------------- #

DEPARTMENTS = ["Finance", "Operations", "Procurement", "IT", "Customer Support", "HR"]

VENDORS = [
    "Acme Office Supplies", "Northwind Logistics", "BlueSky Cloud Services",
    "Globex Consulting", "Initech Software", "Umbrella Facilities",
    "Stark Industrial Parts", "Wayne Marketing Group", "Soylent Catering",
    "Hooli Analytics", "Vandelay Imports", "Pied Piper Hosting",
    "Cyberdyne Security", "Wonka Maintenance", "Gekko Financial Tools",
    "Tyrell Hardware", "Massive Dynamic Labs", "Oscorp Materials",
    "Nakatomi Property Mgmt", "Prestige Worldwide Travel",
]

# Synthetic person names (random first/last combinations — not real individuals)
FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Avery",
    "Quinn", "Drew", "Sam", "Cameron", "Reese", "Harper", "Logan", "Sasha",
    "Devin", "Parker", "Rowan", "Emerson", "Blair", "Hayden", "Marlowe", "Noor",
]
LAST_NAMES = [
    "Carter", "Bennett", "Hughes", "Foster", "Reyes", "Murphy", "Sullivan",
    "Patel", "Nguyen", "Okafor", "Larsson", "Ferreira", "Kowalski", "Ibrahim",
    "Tanaka", "Rossi", "Andersen", "Dubois", "Volkov", "Mendez", "Haddad",
    "Schmidt", "Walsh", "Park",
]

INVOICE_CATEGORIES = [
    "Software", "Consulting", "Office Supplies", "Logistics", "Marketing",
    "Utilities", "Travel", "Hardware", "Facilities", "Professional Services",
]

ISSUE_TYPES = [
    "Billing Issue", "Technical Problem", "Service Delay", "Account Request",
    "Complaint", "Data Correction",
]
SUPPORT_TEAMS = [
    "Tier 1 Support", "Tier 2 Support", "Billing Team", "Technical Team",
    "Escalations Team", "Account Management",
]
CUSTOMER_SEGMENTS = ["Enterprise", "SMB", "Startup", "Government", "Individual"]

REQUEST_TYPES = [
    "Purchase Approval", "Payment Approval", "Contract Review", "Budget Request",
    "Vendor Onboarding", "Refund Approval",
]

PRIORITIES = ["Low", "Medium", "High", "Critical"]
IMPACT_LEVELS = ["Low", "Medium", "High", "Critical"]

# SLA targets in hours by ticket priority
SLA_HOURS = {"Low": 72, "Medium": 48, "High": 24, "Critical": 8}


def random_name() -> str:
    """Return a synthetic full name (random first + last combination)."""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def weighted_choice(options, weights):
    """Convenience wrapper around random.choices returning a single value."""
    return random.choices(options, weights=weights, k=1)[0]


# --------------------------------------------------------------------------- #
# Dataset generators
# --------------------------------------------------------------------------- #

def generate_invoices(n: int) -> pd.DataFrame:
    """Generate synthetic accounts-payable invoice records."""
    rows = []
    for i in range(n):
        invoice_id = f"INV-{10001 + i}"
        vendor = random.choice(VENDORS)
        department = random.choice(DEPARTMENTS)

        # Invoice issued sometime in the ~120 days before the reference date.
        invoice_date = REFERENCE_DATE - timedelta(days=random.randint(1, 120))
        net_terms = random.choice([15, 30, 30, 45, 60])
        due_date = invoice_date + timedelta(days=net_terms)

        # Amounts: mostly small/medium, with a tail of high-value invoices.
        if random.random() < 0.15:
            amount = round(random.uniform(50_000, 250_000), 2)  # high-value
        else:
            amount = round(random.uniform(250, 49_000), 2)

        currency = weighted_choice(["USD", "EUR", "GBP"], [0.8, 0.12, 0.08])

        approval_status = weighted_choice(
            ["Approved", "Pending", "Under Review", "Rejected"],
            [0.55, 0.25, 0.12, 0.08],
        )

        # Payment status is loosely correlated with approval status.
        if approval_status == "Approved":
            payment_status = weighted_choice(
                ["Paid", "Unpaid", "Partially Paid", "On Hold"],
                [0.6, 0.25, 0.1, 0.05],
            )
        elif approval_status == "Rejected":
            payment_status = "On Hold"
        else:  # Pending / Under Review
            payment_status = weighted_choice(
                ["Unpaid", "On Hold", "Partially Paid"], [0.7, 0.2, 0.1]
            )

        # days_overdue: only meaningful for not-fully-paid invoices past due.
        if payment_status != "Paid" and due_date < REFERENCE_DATE:
            days_overdue = (REFERENCE_DATE - due_date).days
        else:
            days_overdue = 0

        priority_level = weighted_choice(
            PRIORITIES, [0.3, 0.4, 0.2, 0.1]
        )

        rows.append(
            {
                "invoice_id": invoice_id,
                "vendor_name": vendor,
                "department": department,
                "invoice_date": invoice_date.isoformat(),
                "due_date": due_date.isoformat(),
                "amount_usd": amount,
                "currency": currency,
                "approval_status": approval_status,
                "payment_status": payment_status,
                "assigned_approver": random_name(),
                "days_overdue": days_overdue,
                "invoice_category": random.choice(INVOICE_CATEGORIES),
                "priority_level": priority_level,
            }
        )

    # Guarantee a few clearly high-value invoices that are still pending.
    df = pd.DataFrame(rows)
    pending_high = df.sample(8, random_state=RANDOM_SEED).index
    df.loc[pending_high, "amount_usd"] = [
        round(random.uniform(60_000, 300_000), 2) for _ in pending_high
    ]
    df.loc[pending_high, "approval_status"] = "Pending"
    df.loc[pending_high, "payment_status"] = "Unpaid"
    df.loc[pending_high, "priority_level"] = "High"
    return df


def generate_tickets(n: int) -> pd.DataFrame:
    """Generate synthetic customer support ticket records."""
    ref_dt = datetime.combine(REFERENCE_DATE, datetime.min.time())
    rows = []
    for i in range(n):
        ticket_id = f"TCK-{20001 + i}"
        priority = weighted_choice(PRIORITIES, [0.25, 0.4, 0.25, 0.1])

        status = weighted_choice(
            ["Resolved", "In Progress", "Open", "Waiting for Customer", "Escalated"],
            [0.45, 0.2, 0.15, 0.12, 0.08],
        )

        # Resolved tickets can be historical (opened up to ~45 days ago). Still-open
        # tickets are concentrated in the last few days so their SLA deadlines fall
        # around the reference date, producing a realistic Within/At Risk/Breached mix.
        if status == "Resolved":
            opened_dt = ref_dt - timedelta(
                days=random.randint(0, 45), hours=random.randint(0, 23)
            )
        else:
            opened_dt = ref_dt - timedelta(hours=random.randint(0, 96))
        sla_deadline = opened_dt + timedelta(hours=SLA_HOURS[priority])

        # Response time is generally a fraction of the SLA window.
        response_time_hours = round(
            random.uniform(0.5, SLA_HOURS[priority] * 1.2), 1
        )

        resolved_date = ""
        resolution_time_hours = ""
        if status == "Resolved":
            res_hours = round(random.uniform(1, SLA_HOURS[priority] * 1.8), 1)
            resolved_dt = opened_dt + timedelta(hours=res_hours)
            # Don't resolve in the future relative to the reference date.
            if resolved_dt > ref_dt:
                resolved_dt = ref_dt
                res_hours = round((resolved_dt - opened_dt).total_seconds() / 3600, 1)
            resolved_date = resolved_dt.isoformat(sep=" ")
            resolution_time_hours = res_hours

        # SLA status logic.
        if status == "Resolved":
            sla_status = "Within SLA" if resolved_dt <= sla_deadline else "Breached"
        else:
            hours_to_deadline = (sla_deadline - ref_dt).total_seconds() / 3600
            if hours_to_deadline < 0:
                sla_status = "Breached"
            elif hours_to_deadline <= 12:
                sla_status = "At Risk"
            else:
                sla_status = "Within SLA"

        rows.append(
            {
                "ticket_id": ticket_id,
                "customer_name": random_name(),
                "department": random.choice(DEPARTMENTS),
                "issue_type": random.choice(ISSUE_TYPES),
                "priority": priority,
                "opened_date": opened_dt.isoformat(sep=" "),
                "sla_deadline": sla_deadline.isoformat(sep=" "),
                "resolved_date": resolved_date,
                "status": status,
                "assigned_team": random.choice(SUPPORT_TEAMS),
                "response_time_hours": response_time_hours,
                "resolution_time_hours": resolution_time_hours,
                "sla_status": sla_status,
                "customer_segment": random.choice(CUSTOMER_SEGMENTS),
            }
        )
    return pd.DataFrame(rows)


def generate_approvals(n: int) -> pd.DataFrame:
    """Generate synthetic approval-workflow records."""
    rows = []
    for i in range(n):
        request_id = f"REQ-{30001 + i}"
        request_type = random.choice(REQUEST_TYPES)
        requested_date = REFERENCE_DATE - timedelta(days=random.randint(0, 40))
        sla_days = random.choice([3, 5, 7, 10])
        approval_deadline = requested_date + timedelta(days=sla_days)

        approval_status = weighted_choice(
            ["Approved", "Pending", "Escalated", "Rejected"],
            [0.45, 0.3, 0.13, 0.12],
        )

        if approval_status in ("Pending", "Escalated"):
            # Still open: waiting since it was requested.
            waiting_days = (REFERENCE_DATE - requested_date).days
        else:
            # Decided: waited some days before the decision was made.
            waiting_days = random.randint(0, max(1, sla_days + 3))

        amount = round(random.uniform(500, 200_000), 2)
        business_impact = weighted_choice(IMPACT_LEVELS, [0.3, 0.35, 0.25, 0.1])

        bottleneck_flag = (
            approval_status in ("Pending", "Escalated") and waiting_days > 5
        )

        rows.append(
            {
                "request_id": request_id,
                "request_type": request_type,
                "department": random.choice(DEPARTMENTS),
                "requester": random_name(),
                "approver": random_name(),
                "requested_date": requested_date.isoformat(),
                "approval_deadline": approval_deadline.isoformat(),
                "approval_status": approval_status,
                "waiting_days": waiting_days,
                "amount_usd": amount,
                "business_impact": business_impact,
                "bottleneck_flag": bottleneck_flag,
            }
        )
    return pd.DataFrame(rows)


def generate_risk_rules() -> pd.DataFrame:
    """Return the static risk-rules reference table."""
    rules = [
        {
            "rule_id": "R-001",
            "rule_name": "Overdue Invoice",
            "data_source": "invoices.csv",
            "condition_description": "days_overdue > 7",
            "risk_level": "High",
            "recommended_action": "Escalate to Finance for immediate payment review.",
        },
        {
            "rule_id": "R-002",
            "rule_name": "High-Value Pending Invoice",
            "data_source": "invoices.csv",
            "condition_description": "amount_usd > 50000 AND approval_status = 'Pending'",
            "risk_level": "Critical",
            "recommended_action": "Fast-track approval and notify department head.",
        },
        {
            "rule_id": "R-003",
            "rule_name": "Ticket SLA Breached",
            "data_source": "customer_tickets.csv",
            "condition_description": "sla_status = 'Breached'",
            "risk_level": "High",
            "recommended_action": "Reassign to escalations team and inform the customer.",
        },
        {
            "rule_id": "R-004",
            "rule_name": "Ticket Close to SLA Deadline",
            "data_source": "customer_tickets.csv",
            "condition_description": "sla_status = 'At Risk'",
            "risk_level": "Medium",
            "recommended_action": "Prioritize ticket before the SLA deadline is missed.",
        },
        {
            "rule_id": "R-005",
            "rule_name": "Approval Bottleneck",
            "data_source": "approval_requests.csv",
            "condition_description": "waiting_days > 5 AND approval_status IN ('Pending','Escalated')",
            "risk_level": "Medium",
            "recommended_action": "Remind approver and check for process blockers.",
        },
        {
            "rule_id": "R-006",
            "rule_name": "Critical Request Still Pending",
            "data_source": "approval_requests.csv",
            "condition_description": "business_impact = 'Critical' AND approval_status = 'Pending'",
            "risk_level": "Critical",
            "recommended_action": "Escalate to senior leadership for urgent decision.",
        },
    ]
    return pd.DataFrame(rules)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    random.seed(RANDOM_SEED)

    # Ensure the data folder exists.
    os.makedirs(DATA_DIR, exist_ok=True)

    invoices = generate_invoices(N_INVOICES)
    tickets = generate_tickets(N_TICKETS)
    approvals = generate_approvals(N_APPROVALS)
    risk_rules = generate_risk_rules()

    invoices.to_csv(os.path.join(DATA_DIR, "invoices.csv"), index=False)
    tickets.to_csv(os.path.join(DATA_DIR, "customer_tickets.csv"), index=False)
    approvals.to_csv(os.path.join(DATA_DIR, "approval_requests.csv"), index=False)
    risk_rules.to_csv(os.path.join(DATA_DIR, "risk_rules.csv"), index=False)

    print("Synthetic datasets generated successfully (reference date: 2026-06-22)")
    print(f"  invoices            : {len(invoices)} records")
    print(f"  customer tickets    : {len(tickets)} records")
    print(f"  approval requests   : {len(approvals)} records")
    print(f"  risk rules          : {len(risk_rules)} records")
    print(f"Files written to: {DATA_DIR}")


if __name__ == "__main__":
    main()
