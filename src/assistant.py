"""
AI Manager Assistant module.

Lets executives and operations managers ask natural-language questions about the
current synthetic business data, KPI results, and risk register. Like the AI
summary module, it works in two modes:

- **Demo mode**  — deterministic, rule-based answers built from the KPI/risk
  context. Used when no OpenAI credentials are configured (or ``force_demo``),
  so the project always runs without API access.
- **Live mode**  — calls the OpenAI API with only a compact KPI/risk context
  when both ``OPENAI_API_KEY`` and ``OPENAI_MODEL`` are present.

Privacy/safety: only aggregated KPIs, the risk summary, and the top risk records
are ever sent to the API — never the full datasets. API keys are read from the
environment via python-dotenv and are never printed, logged, or returned.

No external API is called at import time, and live mode is only triggered when
``answer_manager_question`` is explicitly invoked (e.g. via the dashboard
button), not automatically.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import pandas as pd

try:
    from dotenv import load_dotenv

    load_dotenv()  # Load .env if present; harmless if absent.
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass

# Keys every assistant response dictionary must contain.
ANSWER_KEYS = ["mode", "question", "answer", "confidence_note"]


# --------------------------------------------------------------------------- #
# Context construction
# --------------------------------------------------------------------------- #

def build_assistant_context(
    all_kpis: Dict[str, Any], risk_register: Dict[str, Any]
) -> Dict[str, Any]:
    """Build a compact context with only what the assistant needs.

    Deliberately excludes the raw datasets — only aggregated KPIs, the risk
    summary, and the top 10 risk records are included.
    """
    invoice_kpis = all_kpis.get("invoice_kpis", {})
    ticket_kpis = all_kpis.get("ticket_kpis", {})
    approval_kpis = all_kpis.get("approval_kpis", {})
    executive_kpis = all_kpis.get("executive_kpis", {})
    risk_summary = risk_register.get("risk_summary", {})

    top_risks = risk_register.get("top_risks", pd.DataFrame())
    if isinstance(top_risks, pd.DataFrame):
        top_risk_records = (
            top_risks.head(10)
            .where(pd.notna(top_risks.head(10)), None)
            .to_dict(orient="records")
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
        "invoice_highlights": invoice_highlights,
        "ticket_highlights": ticket_highlights,
        "approval_highlights": approval_highlights,
        "risk_summary": risk_summary,
        "top_risks": top_risk_records,
        "top_risk_category": risk_summary.get("top_risk_category"),
        "top_risk_department": risk_summary.get("top_risk_department"),
    }


# --------------------------------------------------------------------------- #
# Demo intent classification + answers
# --------------------------------------------------------------------------- #

# Intent -> keywords that suggest it. Order matters: first match wins.
_INTENT_KEYWORDS = [
    ("management_briefing", ["briefing", "meeting", "monday", "prepare", "summary for"]),
    ("financial_exposure", ["financial", "exposure", "money", "cost", "amount", "$", "spend"]),
    ("sla_pressure", ["sla", "ticket", "customer", "support", "service level"]),
    ("approval_bottlenecks", ["approval", "bottleneck", "waiting", "stuck", "pending request"]),
    ("department_risk", ["department", "which area", "which team", "who has", "most risk"]),
    ("top_risks", ["top risk", "risks", "risk", "biggest", "critical", "priority", "prioritize", "attention"]),
]


def classify_demo_question(question: str) -> str:
    """Classify a question into a coarse intent for demo mode (keyword-based)."""
    if not question or not question.strip():
        return "general_summary"

    q = question.lower()

    # "department" combined with risk should map to department_risk first.
    if "department" in q and ("risk" in q or "attention" in q or "most" in q):
        return "department_risk"

    for intent, keywords in _INTENT_KEYWORDS:
        if any(kw in q for kw in keywords):
            return intent

    return "general_summary"


def _money(value: Any) -> str:
    """Format a value as USD for narrative text."""
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return "N/A"


def answer_demo_question(question: str, context: Dict[str, Any]) -> str:
    """Return a deterministic, management-ready answer string for demo mode."""
    intent = classify_demo_question(question)

    exec_kpis = context.get("executive_kpis", {})
    risk_summary = context.get("risk_summary", {})
    invoice = context.get("invoice_highlights", {})
    ticket = context.get("ticket_highlights", {})
    approval = context.get("approval_highlights", {})
    top_dept = context.get("top_risk_department", "N/A")
    top_cat = context.get("top_risk_category", "N/A")

    if intent == "financial_exposure":
        return (
            f"Current total financial exposure is "
            f"{_money(exec_kpis.get('total_financial_exposure_usd', 0))}.\n\n"
            f"- Unpaid / partially paid / on-hold invoices and pending approvals "
            f"are the main drivers.\n"
            f"- {invoice.get('high_value_pending_invoice_count', 0)} high-value "
            f"invoices remain pending approval.\n"
            f"- {approval.get('total_pending_amount_usd', 0):,.0f} USD is held in "
            f"pending/escalated approval requests."
        )

    if intent == "sla_pressure":
        return (
            f"Customer SLA pressure currently affects "
            f"{exec_kpis.get('customer_sla_pressure_count', 0)} tickets.\n\n"
            f"- {ticket.get('sla_breached_count', 0)} tickets have already "
            f"breached SLA.\n"
            f"- {ticket.get('sla_at_risk_count', 0)} tickets are at risk and "
            f"approaching their deadline.\n"
            f"- {ticket.get('critical_ticket_count', 0)} critical-priority "
            f"tickets and {ticket.get('unresolved_ticket_count', 0)} unresolved "
            f"tickets remain open."
        )

    if intent == "approval_bottlenecks":
        return (
            f"There are {approval.get('bottleneck_count', 0)} approval "
            f"bottlenecks right now.\n\n"
            f"- Average wait for pending/escalated requests is "
            f"{approval.get('average_waiting_days_pending', 0)} days.\n"
            f"- {approval.get('critical_pending_count', 0)} critical-impact "
            f"requests are still pending a decision.\n"
            f"- {_money(approval.get('total_pending_amount_usd', 0))} in value is "
            f"held up awaiting approval."
        )

    if intent == "department_risk":
        return (
            f"The {top_dept} department currently has the most risk findings.\n\n"
            f"- The most common risk category overall is '{top_cat}'.\n"
            f"- Total risk findings: {risk_summary.get('total_risk_findings', 0)} "
            f"({risk_summary.get('critical_risk_count', 0)} critical, "
            f"{risk_summary.get('high_risk_count', 0)} high).\n"
            f"- Recommend focusing management attention on {top_dept} first."
        )

    if intent == "top_risks":
        return (
            f"Top operational risks (of "
            f"{risk_summary.get('total_risk_findings', 0)} total findings):\n\n"
            f"- {risk_summary.get('critical_risk_count', 0)} critical and "
            f"{risk_summary.get('high_risk_count', 0)} high-severity findings.\n"
            f"- Leading category: '{top_cat}'; most-affected department: "
            f"{top_dept}.\n"
            f"- {invoice.get('overdue_more_than_7_days_count', 0)} invoices "
            f"overdue >7 days; {ticket.get('sla_breached_count', 0)} SLA breaches; "
            f"{approval.get('bottleneck_count', 0)} approval bottlenecks.\n"
            f"- Highest severity score observed: "
            f"{risk_summary.get('highest_severity_score', 0)}."
        )

    if intent == "management_briefing":
        return (
            "Executive briefing (synthetic data):\n\n"
            f"- {exec_kpis.get('total_open_work_items', 0)} open work items; "
            f"{exec_kpis.get('total_attention_items', 0)} need attention.\n"
            f"- Financial exposure: "
            f"{_money(exec_kpis.get('total_financial_exposure_usd', 0))}.\n"
            f"- Risk: {risk_summary.get('critical_risk_count', 0)} critical / "
            f"{risk_summary.get('high_risk_count', 0)} high; top category "
            f"'{top_cat}', top department {top_dept}.\n"
            f"- SLA: {ticket.get('sla_breached_count', 0)} breached, "
            f"{ticket.get('sla_at_risk_count', 0)} at risk.\n"
            f"- Approvals: {approval.get('bottleneck_count', 0)} bottlenecks, "
            f"{approval.get('critical_pending_count', 0)} critical pending."
        )

    # general_summary (default)
    return (
        "Here is a quick overview of the current position (synthetic data):\n\n"
        f"- Open work items: {exec_kpis.get('total_open_work_items', 0)}; "
        f"attention items: {exec_kpis.get('total_attention_items', 0)}.\n"
        f"- Financial exposure: "
        f"{_money(exec_kpis.get('total_financial_exposure_usd', 0))}.\n"
        f"- Risk findings: {risk_summary.get('total_risk_findings', 0)} "
        f"({risk_summary.get('critical_risk_count', 0)} critical). Top category "
        f"'{top_cat}', top department {top_dept}.\n\n"
        "Try asking about financial exposure, SLA pressure, approval "
        "bottlenecks, or for a management briefing."
    )


# --------------------------------------------------------------------------- #
# Live (OpenAI) answer
# --------------------------------------------------------------------------- #

def _fallback_answer(
    question: str, context: Dict[str, Any], reason: str
) -> Dict[str, Any]:
    """Return a demo-based answer marked as a fallback, with an explanation."""
    return {
        "mode": "fallback",
        "question": question,
        "answer": answer_demo_question(question, context),
        "confidence_note": (
            f"Live AI was unavailable ({reason}); a deterministic demo fallback "
            "answer is shown instead. Figures reflect synthetic data."
        ),
    }


def answer_live_question(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Answer a question via the OpenAI API using only the compact context.

    Returns a response dictionary with ``mode = "live"`` on success, or a
    ``mode = "fallback"`` demo answer if anything goes wrong.
    """
    import json

    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")

    if not api_key or not model:
        return _fallback_answer(
            question, context, "missing OPENAI_API_KEY or OPENAI_MODEL"
        )

    try:
        from openai import OpenAI
    except Exception:
        return _fallback_answer(question, context, "openai SDK not installed")

    system_instruction = (
        "You are an executive operations analyst for a business control tower. "
        "Answer the manager's question using ONLY the provided KPI and risk "
        "context (synthetic data). Do not invent facts or reference anything not "
        "present in the context. Be concise and management-ready: a short answer "
        "with 2-4 bullet points where useful. If the answer cannot be determined "
        "from the context, say so clearly."
    )
    user_content = (
        "KPI and risk context (JSON):\n"
        + json.dumps(context, indent=2, default=str)
        + f"\n\nManager's question: {question}"
    )

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content},
            ],
            temperature=0.3,
        )
        answer_text = (response.choices[0].message.content or "").strip()
    except Exception as exc:  # noqa: BLE001 - never leak details/secrets
        return _fallback_answer(
            question, context, f"API call failed ({type(exc).__name__})"
        )

    if not answer_text:
        return _fallback_answer(question, context, "empty AI response")

    return {
        "mode": "live",
        "question": question,
        "answer": answer_text,
        "confidence_note": (
            "Live AI answer generated from aggregated synthetic KPI and risk "
            "context only (no raw datasets were sent)."
        ),
    }


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #

def answer_manager_question(
    question: str,
    all_kpis: Dict[str, Any],
    risk_register: Dict[str, Any],
    force_demo: bool = False,
) -> Dict[str, Any]:
    """Answer a manager's question, choosing demo or live mode automatically.

    Always returns a dictionary with keys: ``mode``, ``question``, ``answer``,
    ``confidence_note``.
    """
    if not question or not question.strip():
        return {
            "mode": "demo",
            "question": "",
            "answer": (
                "Please enter a question. For example: 'What are the top risks "
                "right now?' or 'Summarize approval bottlenecks.'"
            ),
            "confidence_note": "No question was provided.",
        }

    context = build_assistant_context(all_kpis, risk_register)

    if force_demo:
        return {
            "mode": "demo",
            "question": question,
            "answer": answer_demo_question(question, context),
            "confidence_note": (
                "Demo mode: this answer was generated deterministically from "
                "aggregated KPI and risk values (no AI model was called). Figures "
                "reflect synthetic data."
            ),
        }

    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")
    if not api_key or not model:
        return {
            "mode": "demo",
            "question": question,
            "answer": answer_demo_question(question, context),
            "confidence_note": (
                "Demo mode (no OpenAI credentials found): answer generated "
                "deterministically from synthetic KPI and risk values."
            ),
        }

    return answer_live_question(question, context)


def get_suggested_questions() -> List[str]:
    """Return a list of suggested executive questions for the dashboard."""
    return [
        "What are the top 5 risks right now?",
        "Which department needs management attention first?",
        "What is the current financial exposure?",
        "Summarize customer SLA pressure.",
        "Summarize approval bottlenecks.",
        "Prepare a 5-bullet executive briefing.",
        "What should management prioritize this week?",
    ]
