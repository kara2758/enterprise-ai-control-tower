"""
AI Summary module.

Generates a concise, management-ready executive summary from the already-computed
KPI results and risk register. It works in two modes:

- **Demo mode**  — a deterministic, offline summary built from the payload values.
  Used when no OpenAI credentials are configured, so the portfolio project always
  runs without API access.
- **Live mode**  — calls the OpenAI API to generate a real summary when both
  ``OPENAI_API_KEY`` and ``OPENAI_MODEL`` are present in the environment.

Privacy/safety: only aggregated KPIs and the top risk records are ever sent to
the API — never the full datasets. API keys are read from the environment via
python-dotenv and are never printed, logged, or returned.

No external API is called at import time, and live mode is only triggered when
this module's public function is explicitly invoked (e.g. via the dashboard
button), not automatically.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import pandas as pd

try:
    from dotenv import load_dotenv

    load_dotenv()  # Load .env if present; harmless if absent.
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass

# The structured keys every summary dictionary must contain.
SUMMARY_KEYS = [
    "mode",
    "executive_summary",
    "key_risks",
    "recommended_actions",
    "management_questions",
    "confidence_note",
]


# --------------------------------------------------------------------------- #
# Payload construction
# --------------------------------------------------------------------------- #

def build_executive_summary_payload(
    all_kpis: Dict[str, Any], risk_register: Dict[str, Any]
) -> Dict[str, Any]:
    """Build a compact payload with only the info needed for the AI summary.

    Deliberately excludes the raw datasets — only aggregated KPIs and the top 10
    risk records are included.
    """
    invoice_kpis = all_kpis.get("invoice_kpis", {})
    ticket_kpis = all_kpis.get("ticket_kpis", {})
    approval_kpis = all_kpis.get("approval_kpis", {})
    executive_kpis = all_kpis.get("executive_kpis", {})

    top_risks = risk_register.get("top_risks", pd.DataFrame())
    if isinstance(top_risks, pd.DataFrame):
        # Convert to plain records; NaN -> None for clean JSON serialization.
        top_risk_records = (
            top_risks.head(10).where(pd.notna(top_risks.head(10)), None).to_dict(
                orient="records"
            )
        )
    else:
        top_risk_records = list(top_risks)[:10]

    invoice_highlights = {
        k: invoice_kpis.get(k)
        for k in [
            "total_invoices",
            "total_invoice_amount_usd",
            "overdue_more_than_7_days_count",
            "high_value_pending_invoice_count",
            "on_hold_invoice_count",
        ]
    }
    ticket_highlights = {
        k: ticket_kpis.get(k)
        for k in [
            "total_tickets",
            "sla_breached_count",
            "sla_at_risk_count",
            "critical_ticket_count",
            "unresolved_ticket_count",
        ]
    }
    approval_highlights = {
        k: approval_kpis.get(k)
        for k in [
            "total_approval_requests",
            "bottleneck_count",
            "critical_pending_count",
            "average_waiting_days_pending",
            "total_pending_amount_usd",
        ]
    }

    return {
        "executive_kpis": executive_kpis,
        "risk_summary": risk_register.get("risk_summary", {}),
        "top_risks": top_risk_records,
        "invoice_highlights": invoice_highlights,
        "ticket_highlights": ticket_highlights,
        "approval_highlights": approval_highlights,
    }


# --------------------------------------------------------------------------- #
# Demo (mock) summary
# --------------------------------------------------------------------------- #

def _money(value: Any) -> str:
    """Format a value as USD for narrative text."""
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return "N/A"


def generate_mock_executive_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return a deterministic demo summary derived from payload values."""
    exec_kpis = payload.get("executive_kpis", {})
    risk_summary = payload.get("risk_summary", {})
    invoice = payload.get("invoice_highlights", {})
    ticket = payload.get("ticket_highlights", {})
    approval = payload.get("approval_highlights", {})

    total_findings = risk_summary.get("total_risk_findings", 0)
    critical = risk_summary.get("critical_risk_count", 0)
    high = risk_summary.get("high_risk_count", 0)
    exposure = exec_kpis.get("total_financial_exposure_usd", 0)
    top_category = risk_summary.get("top_risk_category", "N/A")
    top_department = risk_summary.get("top_risk_department", "N/A")

    executive_summary = (
        f"The control tower currently tracks {exec_kpis.get('total_open_work_items', 0)} "
        f"open work items, with {exec_kpis.get('total_attention_items', 0)} items "
        f"requiring management attention. Total financial exposure stands at "
        f"{_money(exposure)}, driven mainly by unpaid/on-hold invoices and pending "
        f"approvals. Risk detection produced {total_findings} findings "
        f"({critical} critical, {high} high), concentrated in '{top_category}' and "
        f"most frequently in the {top_department} department. Customer SLA pressure "
        f"({exec_kpis.get('customer_sla_pressure_count', 0)} tickets) and approval "
        f"bottlenecks ({approval.get('bottleneck_count', 0)}) are the leading "
        f"operational concerns."
    )

    key_risks = [
        f"{critical} critical risk finding(s) require immediate management decisions.",
        f"{invoice.get('overdue_more_than_7_days_count', 0)} invoices overdue by more "
        f"than 7 days and {invoice.get('high_value_pending_invoice_count', 0)} "
        f"high-value invoices still pending approval.",
        f"{ticket.get('sla_breached_count', 0)} customer tickets have breached SLA, "
        f"with {ticket.get('sla_at_risk_count', 0)} more at risk.",
        f"{approval.get('bottleneck_count', 0)} approval requests are bottlenecked "
        f"(avg wait {approval.get('average_waiting_days_pending', 0)} days), holding "
        f"{_money(approval.get('total_pending_amount_usd', 0))} in pending value.",
    ]

    recommended_actions = [
        "Convene a rapid review of all critical-impact pending approvals and assign "
        "decision owners today.",
        "Prioritize payment/approval of overdue and high-value pending invoices to "
        "reduce financial exposure.",
        "Escalate SLA-breached tickets to the escalations team and triage at-risk "
        "tickets before deadlines.",
        "Address approval bottlenecks by rebalancing approver workload and setting "
        "clear turnaround targets.",
    ]

    management_questions = [
        "Which critical pending approvals can be decided within the next 24 hours?",
        "What is the root cause of the recurring SLA breaches in the top-risk "
        "department?",
        "Are current approver capacity and thresholds appropriate for the volume of "
        "high-value requests?",
    ]

    confidence_note = (
        "Demo mode: this summary was generated deterministically from aggregated "
        "KPI and risk values (no AI model was called). Figures reflect synthetic "
        "data for demonstration."
    )

    return {
        "mode": "demo",
        "executive_summary": executive_summary,
        "key_risks": key_risks,
        "recommended_actions": recommended_actions,
        "management_questions": management_questions,
        "confidence_note": confidence_note,
    }


# --------------------------------------------------------------------------- #
# Live (OpenAI) summary
# --------------------------------------------------------------------------- #

def _fallback_summary(payload: Dict[str, Any], reason: str) -> Dict[str, Any]:
    """Return a demo-based summary marked as a fallback, with an explanation."""
    summary = generate_mock_executive_summary(payload)
    summary["mode"] = "fallback"
    summary["confidence_note"] = (
        f"Live AI generation was unavailable ({reason}); a deterministic demo "
        "fallback summary is shown instead. Figures reflect synthetic data."
    )
    return summary


def _coerce_str_list(value: Any) -> List[str]:
    """Coerce a model-provided value into a list of strings."""
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def generate_live_executive_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a real executive summary via the OpenAI API.

    Returns a summary dictionary with ``mode = "live"`` on success, or a
    ``mode = "fallback"`` demo summary if anything goes wrong (missing SDK,
    API error, or unparsable response).
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")

    if not api_key or not model:
        return _fallback_summary(payload, "missing OPENAI_API_KEY or OPENAI_MODEL")

    try:
        from openai import OpenAI
    except Exception:
        return _fallback_summary(payload, "openai SDK not installed")

    system_instruction = (
        "You are an executive operations analyst for a business control tower. "
        "Given aggregated KPIs and the top risk findings, produce a concise, "
        "management-ready briefing. Be specific and reference the numbers provided. "
        "Respond ONLY with a JSON object using exactly these keys: "
        "executive_summary (string), key_risks (array of strings), "
        "recommended_actions (array of strings), management_questions (array of "
        "strings), confidence_note (string). Keep the executive_summary to a short "
        "paragraph and each list to 3-5 succinct items."
    )
    user_content = (
        "Here is the aggregated business data (synthetic). Base your briefing only "
        "on these figures:\n\n"
        + json.dumps(payload, indent=2, default=str)
    )

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        content = response.choices[0].message.content
    except Exception as exc:  # noqa: BLE001 - never leak details/secrets
        # Use only the exception type, not its message, to avoid leaking anything.
        return _fallback_summary(payload, f"API call failed ({type(exc).__name__})")

    try:
        parsed = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return _fallback_summary(payload, "could not parse AI response as JSON")

    return {
        "mode": "live",
        "executive_summary": str(parsed.get("executive_summary", "")).strip()
        or "No summary text was returned by the model.",
        "key_risks": _coerce_str_list(parsed.get("key_risks")),
        "recommended_actions": _coerce_str_list(parsed.get("recommended_actions")),
        "management_questions": _coerce_str_list(parsed.get("management_questions")),
        "confidence_note": str(
            parsed.get(
                "confidence_note",
                "Live AI summary generated from aggregated synthetic KPI and risk "
                "data.",
            )
        ),
    }


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #

def generate_executive_summary(
    all_kpis: Dict[str, Any],
    risk_register: Dict[str, Any],
    force_demo: bool = False,
) -> Dict[str, Any]:
    """Generate an executive summary, choosing demo or live mode automatically.

    Args:
        all_kpis: Output of ``calculate_all_kpis``.
        risk_register: Output of ``create_executive_risk_register``.
        force_demo: If True, always return the deterministic demo summary.

    Returns:
        A summary dictionary with a consistent structure (see ``SUMMARY_KEYS``).
    """
    payload = build_executive_summary_payload(all_kpis, risk_register)

    if force_demo:
        return generate_mock_executive_summary(payload)

    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")
    if not api_key or not model:
        return generate_mock_executive_summary(payload)

    return generate_live_executive_summary(payload)


# --------------------------------------------------------------------------- #
# Display formatting
# --------------------------------------------------------------------------- #

def format_summary_for_display(summary: Dict[str, Any]) -> str:
    """Render a summary dictionary as clean markdown for Streamlit."""
    lines: List[str] = []
    mode = summary.get("mode", "demo")
    lines.append(f"**Mode:** `{mode}`")
    lines.append("")
    lines.append("### Executive Summary")
    lines.append(summary.get("executive_summary", ""))

    def _section(title: str, items: List[str]) -> None:
        lines.append("")
        lines.append(f"### {title}")
        if items:
            for item in items:
                lines.append(f"- {item}")
        else:
            lines.append("_None_")

    _section("Key Risks", summary.get("key_risks", []))
    _section("Recommended Actions", summary.get("recommended_actions", []))
    _section("Management Questions", summary.get("management_questions", []))

    lines.append("")
    lines.append(f"> {summary.get('confidence_note', '')}")
    return "\n".join(lines)
