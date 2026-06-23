"""
Enterprise AI Control Tower — Streamlit executive dashboard.

This dashboard presents KPI insights, risk findings, financial exposure, SLA
pressure, and approval bottlenecks using the already-completed data, KPI, and
risk modules. It is read-only and built entirely on synthetic data.

It does NOT call any external API and contains no AI functionality yet (that
arrives in later stages).

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

# Make the project root importable so 'src' resolves when Streamlit runs app.py.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_loader import DataLoadingError, load_all_data  # noqa: E402
from src.kpi_engine import calculate_all_kpis  # noqa: E402
from src.risk_engine import create_executive_risk_register  # noqa: E402
from src.ai_summary import (  # noqa: E402
    format_summary_for_display,
    generate_executive_summary,
)
from src.assistant import (  # noqa: E402
    answer_manager_question,
    get_suggested_questions,
)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")

DISCLAIMER = (
    "This dashboard uses only synthetic data and is built for portfolio and "
    "demonstration purposes. It does not contain real company, customer, "
    "invoice, vendor, or personal data."
)


# --------------------------------------------------------------------------- #
# Data loading (cached)
# --------------------------------------------------------------------------- #

@st.cache_data
def get_dashboard_data() -> Tuple[
    Dict[str, pd.DataFrame], Dict[str, Any], Dict[str, Any]
]:
    """Load data and compute KPIs + risk register, cached for performance."""
    all_data = load_all_data(data_dir=DATA_DIR)
    all_kpis = calculate_all_kpis(all_data)
    risk_register = create_executive_risk_register(all_data)
    return all_data, all_kpis, risk_register


# --------------------------------------------------------------------------- #
# Formatting helpers
# --------------------------------------------------------------------------- #

def format_money(value: Any) -> str:
    """Format a number as USD currency, e.g. $18,000,640.98."""
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "N/A"


def format_int(value: Any) -> str:
    """Format a number as a thousands-separated integer string."""
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "N/A"


def kpi_dict_to_frame(kpis: Dict[str, Any]) -> pd.DataFrame:
    """Convert a flat KPI dictionary into a Metric | Value DataFrame."""
    return pd.DataFrame(
        [{"Metric": k, "Value": v} for k, v in kpis.items()]
    )


# --------------------------------------------------------------------------- #
# Section renderers
# --------------------------------------------------------------------------- #

def render_header() -> None:
    """Render the dashboard title, subtitle, and portfolio note."""
    st.title("🛡️ Enterprise AI Control Tower")
    st.subheader(
        "AI-powered business process intelligence, risk monitoring, "
        "and executive decision support"
    )
    st.caption(
        "Built with synthetic business data for portfolio demonstration purposes."
    )


def render_executive_cards(
    exec_kpis: Dict[str, Any], risk_summary: Dict[str, Any]
) -> None:
    """Render the top-level executive KPI metric cards."""
    st.markdown("### Executive Overview")
    row1 = st.columns(3)
    row1[0].metric(
        "Total Open Work Items",
        format_int(exec_kpis.get("total_open_work_items", 0)),
    )
    row1[1].metric(
        "Total Attention Items",
        format_int(exec_kpis.get("total_attention_items", 0)),
    )
    row1[2].metric(
        "Total Financial Exposure",
        format_money(exec_kpis.get("total_financial_exposure_usd", 0)),
    )

    row2 = st.columns(3)
    row2[0].metric(
        "Customer SLA Pressure",
        format_int(exec_kpis.get("customer_sla_pressure_count", 0)),
    )
    row2[1].metric(
        "Process Bottleneck Indicators",
        format_int(exec_kpis.get("process_bottleneck_indicators", 0)),
    )
    row2[2].metric(
        "Highest Severity Score",
        format_int(risk_summary.get("highest_severity_score", 0)),
    )


def render_risk_summary(risk_summary: Dict[str, Any]) -> None:
    """Render the risk summary metrics block."""
    st.markdown("### Risk Summary")
    row1 = st.columns(4)
    row1[0].metric(
        "Total Risk Findings",
        format_int(risk_summary.get("total_risk_findings", 0)),
    )
    row1[1].metric(
        "Critical Risks", format_int(risk_summary.get("critical_risk_count", 0))
    )
    row1[2].metric(
        "High Risks", format_int(risk_summary.get("high_risk_count", 0))
    )
    row1[3].metric(
        "Medium Risks", format_int(risk_summary.get("medium_risk_count", 0))
    )

    row2 = st.columns(3)
    row2[0].metric(
        "Average Severity Score",
        risk_summary.get("average_severity_score", 0),
    )
    row2[1].metric(
        "Top Risk Category", risk_summary.get("top_risk_category") or "N/A"
    )
    row2[2].metric(
        "Top Risk Department", risk_summary.get("top_risk_department") or "N/A"
    )


def render_ai_summary(
    all_kpis: Dict[str, Any], risk_register: Dict[str, Any]
) -> None:
    """Render the AI Executive Summary section (button-triggered only)."""
    st.markdown("### AI Executive Summary")
    st.write(
        "This section generates a management-ready summary from KPI and risk "
        "outputs."
    )

    use_demo_mode = st.checkbox("Use demo mode", value=True)
    if not use_demo_mode:
        st.caption(
            "Live mode requires `OPENAI_API_KEY` and `OPENAI_MODEL` in your `.env`. "
            "If they are missing or the call fails, a demo fallback is shown."
        )

    if st.button("Generate Executive Summary"):
        with st.spinner("Generating executive summary..."):
            summary = generate_executive_summary(
                all_kpis, risk_register, force_demo=use_demo_mode
            )
        # Surface the mode prominently.
        mode = summary.get("mode", "demo")
        if mode == "live":
            st.success("Generated with live AI (OpenAI).")
        elif mode == "fallback":
            st.warning("Live AI unavailable — showing demo fallback summary.")
        else:
            st.info("Generated in demo mode (no AI model called).")
        st.markdown(format_summary_for_display(summary))


def render_manager_assistant(
    all_kpis: Dict[str, Any], risk_register: Dict[str, Any]
) -> None:
    """Render the AI Manager Assistant section (button-triggered only)."""
    st.markdown("### AI Manager Assistant")
    st.write("Ask management-level questions about KPI and risk outputs.")

    use_demo_mode = st.checkbox(
        "Use demo mode for assistant", value=True, key="assistant_demo_mode"
    )
    if not use_demo_mode:
        st.caption(
            "Live mode requires `OPENAI_API_KEY` and `OPENAI_MODEL` in your `.env`. "
            "If they are missing or the call fails, a demo fallback is shown."
        )

    # Selecting a suggestion fills the question box. The on_change callback runs
    # before the text_input is re-created on rerun, so writing its session_state
    # key here is allowed and makes the choice visibly appear in the box.
    def _apply_suggestion() -> None:
        selected = st.session_state.get("assistant_suggestion", "—")
        if selected and selected != "—":
            st.session_state["assistant_question"] = selected

    suggestions = get_suggested_questions()
    st.selectbox(
        "Suggested questions (optional)",
        ["—"] + suggestions,
        index=0,
        key="assistant_suggestion",
        on_change=_apply_suggestion,
    )
    question = st.text_input("Ask a question", key="assistant_question")

    if st.button("Ask Assistant"):
        with st.spinner("Thinking..."):
            result = answer_manager_question(
                question, all_kpis, risk_register, force_demo=use_demo_mode
            )
        mode = result.get("mode", "demo")
        if mode == "live":
            st.success("Answered with live AI (OpenAI).")
        elif mode == "fallback":
            st.warning("Live AI unavailable — showing demo fallback answer.")
        else:
            st.info("Answered in demo mode (no AI model called).")

        if result.get("question"):
            st.markdown(f"**Question:** {result['question']}")
        st.markdown(result.get("answer", ""))
        st.caption(result.get("confidence_note", ""))


def _bar_from_counts(series: pd.Series, x_label: str, title: str):
    """Build a Plotly bar chart from a value_counts-style series."""
    counts = series.value_counts().reset_index()
    counts.columns = [x_label, "count"]
    return px.bar(counts, x=x_label, y="count", title=title)


def render_charts(
    all_risks: pd.DataFrame, all_data: Dict[str, pd.DataFrame]
) -> None:
    """Render the six analytical charts across a two-column layout."""
    st.markdown("### Risk & Operational Charts")

    # Row 1: risk level + source
    col1, col2 = st.columns(2)
    with col1:
        if not all_risks.empty and "risk_level" in all_risks.columns:
            st.plotly_chart(
                _bar_from_counts(
                    all_risks["risk_level"], "risk_level",
                    "Risk Findings by Risk Level",
                ),
                use_container_width=True,
            )
        else:
            st.info("No risk findings available for risk-level chart.")
    with col2:
        if not all_risks.empty and "source" in all_risks.columns:
            st.plotly_chart(
                _bar_from_counts(
                    all_risks["source"], "source", "Risk Findings by Source"
                ),
                use_container_width=True,
            )
        else:
            st.info("No risk findings available for source chart.")

    # Row 2: top categories + financial exposure by department
    col3, col4 = st.columns(2)
    with col3:
        if not all_risks.empty and "risk_category" in all_risks.columns:
            cat = all_risks["risk_category"].value_counts().head(8).reset_index()
            cat.columns = ["risk_category", "count"]
            st.plotly_chart(
                px.bar(
                    cat, x="risk_category", y="count",
                    title="Top Risk Categories",
                ),
                use_container_width=True,
            )
        else:
            st.info("No risk findings available for category chart.")
    with col4:
        if (
            not all_risks.empty
            and "amount_usd" in all_risks.columns
            and all_risks["amount_usd"].notna().any()
        ):
            exposure = (
                all_risks.dropna(subset=["amount_usd"])
                .groupby("department", as_index=False)["amount_usd"]
                .sum()
                .sort_values("amount_usd", ascending=False)
            )
            st.plotly_chart(
                px.bar(
                    exposure, x="department", y="amount_usd",
                    title="Financial Exposure by Department (USD)",
                ),
                use_container_width=True,
            )
        else:
            st.info("No financial exposure data available.")

    # Row 3: SLA status + approval bottlenecks
    col5, col6 = st.columns(2)
    with col5:
        tickets = all_data.get("customer_tickets", pd.DataFrame())
        if not tickets.empty and "sla_status" in tickets.columns:
            sla = tickets["sla_status"].value_counts().reset_index()
            sla.columns = ["sla_status", "count"]
            st.plotly_chart(
                px.pie(
                    sla, names="sla_status", values="count",
                    title="SLA Status Distribution",
                ),
                use_container_width=True,
            )
        else:
            st.info("No customer ticket SLA data available.")
    with col6:
        approvals = all_data.get("approval_requests", pd.DataFrame())
        if not approvals.empty and "bottleneck_flag" in approvals.columns:
            bottlenecks = approvals[approvals["bottleneck_flag"].astype(bool)]
            if not bottlenecks.empty:
                by_dept = (
                    bottlenecks.groupby("department", as_index=False)
                    .size()
                    .rename(columns={"size": "count"})
                    .sort_values("count", ascending=False)
                )
                st.plotly_chart(
                    px.bar(
                        by_dept, x="department", y="count",
                        title="Approval Bottlenecks by Department",
                    ),
                    use_container_width=True,
                )
            else:
                st.info("No approval bottlenecks detected.")
        else:
            st.info("No approval request data available.")


def render_top_risks_table(top_risks: pd.DataFrame) -> None:
    """Render the Top Risk Findings table with available preferred columns."""
    st.markdown("### Top Risk Findings")
    if top_risks.empty:
        st.info("No risk findings to display.")
        return

    preferred = [
        "source", "record_id", "department", "risk_name", "risk_category",
        "risk_level", "severity_score", "amount_usd", "days_overdue",
        "waiting_days", "recommended_action",
    ]
    columns = [c for c in preferred if c in top_risks.columns]
    st.dataframe(top_risks[columns], use_container_width=True, hide_index=True)


def render_kpi_tabs(all_kpis: Dict[str, Any]) -> None:
    """Render KPI detail tabs, each showing a Metric | Value table."""
    st.markdown("### KPI Details")
    tabs = st.tabs(
        ["Invoice KPIs", "Ticket KPIs", "Approval KPIs", "Executive KPIs"]
    )
    keys = ["invoice_kpis", "ticket_kpis", "approval_kpis", "executive_kpis"]
    for tab, key in zip(tabs, keys):
        with tab:
            st.dataframe(
                kpi_dict_to_frame(all_kpis.get(key, {})),
                use_container_width=True,
                hide_index=True,
            )


def render_dataset_preview(all_data: Dict[str, pd.DataFrame]) -> None:
    """Render an expandable dataset preview (first 20 rows of each dataset)."""
    with st.expander("Dataset Preview"):
        tabs = st.tabs(
            ["Invoices", "Customer Tickets", "Approval Requests", "Risk Rules"]
        )
        keys = ["invoices", "customer_tickets", "approval_requests", "risk_rules"]
        for tab, key in zip(tabs, keys):
            with tab:
                df = all_data.get(key, pd.DataFrame())
                if df.empty:
                    st.info(f"No data available for '{key}'.")
                else:
                    st.dataframe(
                        df.head(20), use_container_width=True, hide_index=True
                    )


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    st.set_page_config(
        page_title="Enterprise AI Control Tower",
        page_icon="🛡️",
        layout="wide",
    )

    render_header()

    try:
        all_data, all_kpis, risk_register = get_dashboard_data()
    except DataLoadingError as exc:
        st.error(
            "Failed to load the synthetic datasets.\n\n"
            f"Details: {exc}\n\n"
            "Generate the data first with: "
            "`python scripts/generate_synthetic_data.py`"
        )
        return
    except Exception as exc:  # noqa: BLE001 - surface any error cleanly
        st.error(f"An unexpected error occurred while preparing the dashboard: {exc}")
        return

    risk_summary = risk_register.get("risk_summary", {})
    all_risks = risk_register.get("all_risks", pd.DataFrame())
    top_risks = risk_register.get("top_risks", pd.DataFrame())

    render_executive_cards(all_kpis.get("executive_kpis", {}), risk_summary)
    st.divider()
    render_ai_summary(all_kpis, risk_register)
    st.divider()
    render_manager_assistant(all_kpis, risk_register)
    st.divider()
    render_risk_summary(risk_summary)
    st.divider()
    render_charts(all_risks, all_data)
    st.divider()
    render_top_risks_table(top_risks)
    st.divider()
    render_kpi_tabs(all_kpis)
    st.divider()
    render_dataset_preview(all_data)

    st.divider()
    st.caption(DISCLAIMER)


if __name__ == "__main__":
    main()
