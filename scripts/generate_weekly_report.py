"""
Weekly management report generator.

Produces a management-ready weekly executive risk report in Markdown from the
KPI results, risk register, and the (demo-mode) AI executive summary, then saves
it to ``reports/weekly_management_report.md``.

This is the local generator that the Stage 9 n8n automation demo would invoke on
a weekly schedule. It runs entirely offline:

- Uses demo mode for the AI summary (no OpenAI API required).
- Sends no emails and calls no external services.
- Uses only synthetic data.

Usage:
    python scripts/generate_weekly_report.py
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

# Make the project root importable so 'src' can be found when run directly.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ai_summary import generate_executive_summary  # noqa: E402
from src.data_loader import load_all_data  # noqa: E402
from src.kpi_engine import calculate_all_kpis  # noqa: E402
from src.risk_engine import create_executive_risk_register  # noqa: E402

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
REPORT_PATH = os.path.join(REPORTS_DIR, "weekly_management_report.md")

DISCLAIMER = (
    "This report uses only synthetic data and is built for portfolio and "
    "demonstration purposes. It does not contain real company, customer, "
    "invoice, vendor, or personal data."
)


def _kpi_table(kpis: Dict[str, Any]) -> str:
    """Render a flat KPI dictionary as a Markdown Metric | Value table."""
    lines = ["| Metric | Value |", "| --- | --- |"]
    for key, value in kpis.items():
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def _bullets(items: List[str]) -> str:
    """Render a list of strings as Markdown bullets."""
    if not items:
        return "_None_"
    return "\n".join(f"- {item}" for item in items)


def _top_risks_table(top_risks: pd.DataFrame) -> str:
    """Render the top-risk findings as a Markdown table."""
    if not isinstance(top_risks, pd.DataFrame) or top_risks.empty:
        return "_No risk findings available._"

    preferred = [
        "source", "record_id", "department", "risk_name", "risk_category",
        "risk_level", "severity_score", "amount_usd", "days_overdue",
        "waiting_days", "recommended_action",
    ]
    columns = [c for c in preferred if c in top_risks.columns]
    view = top_risks.head(10)[columns].where(
        pd.notna(top_risks.head(10)[columns]), ""
    )

    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    rows = [
        "| " + " | ".join(str(view.iloc[i][c]) for c in columns) + " |"
        for i in range(len(view))
    ]
    return "\n".join([header, sep] + rows)


def build_weekly_report() -> str:
    """Build the full weekly report as a Markdown string (demo mode only)."""
    all_data = load_all_data(data_dir=DATA_DIR)
    all_kpis = calculate_all_kpis(all_data)
    risk_register = create_executive_risk_register(all_data)
    summary = generate_executive_summary(all_kpis, risk_register, force_demo=True)

    exec_kpis = all_kpis.get("executive_kpis", {})
    risk_summary = risk_register.get("risk_summary", {})
    top_risks = risk_register.get("top_risks", pd.DataFrame())

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sections: List[str] = []
    sections.append("# Weekly Executive Risk Report")
    sections.append(f"_Generated: {generated_at}_")
    sections.append(f"> {DISCLAIMER}")

    sections.append("## Executive KPI Summary")
    sections.append(_kpi_table(exec_kpis))

    sections.append("## Risk Summary")
    sections.append(_kpi_table(risk_summary))

    sections.append("## AI Executive Summary")
    sections.append(f"_Mode: {summary.get('mode', 'demo')}_")
    sections.append(summary.get("executive_summary", ""))

    sections.append("## Key Risks")
    sections.append(_bullets(summary.get("key_risks", [])))

    sections.append("## Recommended Actions")
    sections.append(_bullets(summary.get("recommended_actions", [])))

    sections.append("## Top 10 Risk Findings")
    sections.append(_top_risks_table(top_risks))

    sections.append("## Management Questions")
    sections.append(_bullets(summary.get("management_questions", [])))

    sections.append("---")
    sections.append(
        "_Portfolio/demo note: this report was generated automatically by "
        "`scripts/generate_weekly_report.py` in demo mode (no AI API, no email "
        "sent). It is intended to demonstrate automated weekly executive "
        "reporting via n8n._"
    )

    return "\n\n".join(sections) + "\n"


def generate_weekly_report(output_path: str = REPORT_PATH) -> str:
    """Generate the weekly report and save it to ``output_path``.

    Returns:
        The path the report was written to.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    content = build_weekly_report()
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(content)
    return output_path


def main() -> int:
    path = generate_weekly_report()
    print("Weekly management report generated successfully (demo mode).")
    print(f"Saved to: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
