# Dashboard Design — Enterprise AI Control Tower

This document describes the Streamlit executive dashboard implemented in
`app.py` for Stage 6.

> ⚠️ The dashboard runs entirely on **synthetic data** generated for the
> fictional company **ABC Global Services**. It is for portfolio and
> demonstration purposes only.

---

## 1. Purpose

The dashboard is the presentation layer of the Enterprise AI Control Tower. It
turns the structured output of the completed modules — data loader, KPI engine,
and risk engine — into an executive-friendly, single-screen view of business
health, risk, and operational pressure.

It is intentionally **read-only**: it visualizes existing logic and does not
re-implement any calculations. It performs no AI calls and connects to no
external services.

### Data flow

```
load_all_data()  ->  calculate_all_kpis()  ->  create_executive_risk_register()
       │                      │                          │
       └──────────────────────┴──────────────┬──────────┘
                                              ▼
                              get_dashboard_data()  (@st.cache_data)
                                              ▼
                                  Streamlit UI sections
```

Data is loaded once and cached with `@st.cache_data` so interactions stay fast.

---

## 2. Dashboard Sections

1. **Header** — project title, subtitle, and a synthetic-data note.
2. **Executive Overview (KPI cards)** — the highest-level metrics.
3. **Risk Summary** — counts and severity of detected risks.
4. **Risk & Operational Charts** — six Plotly charts.
5. **Top Risk Findings** — the prioritized risk register table.
6. **KPI Details** — tabbed Metric | Value tables per KPI group.
7. **Dataset Preview** — expandable preview of each raw dataset.
8. **Disclaimer** — the synthetic-data portfolio notice.

---

## 3. KPI Cards

The **Executive Overview** uses `st.metric` cards sourced from
`all_kpis["executive_kpis"]` and `risk_register["risk_summary"]`:

- Total Open Work Items
- Total Attention Items
- Total Financial Exposure (formatted as `$18,000,640.98`)
- Customer SLA Pressure
- Process Bottleneck Indicators
- Highest Severity Score

The **Risk Summary** block adds: total findings, critical / high / medium
counts, average severity score, top risk category, and top risk department.

---

## 4. Risk Charts

Built with Plotly Express using default colors:

| Chart | Source | Type |
|-------|--------|------|
| Risk Findings by Risk Level | `all_risks.risk_level` | Bar |
| Risk Findings by Source | `all_risks.source` | Bar |
| Top Risk Categories (top 8) | `all_risks.risk_category` | Bar |
| Financial Exposure by Department | `all_risks` (non-null `amount_usd`) grouped by department | Bar |
| SLA Status Distribution | `customer_tickets.sla_status` | Pie |
| Approval Bottlenecks by Department | `approval_requests` where `bottleneck_flag` | Bar |

Each chart guards against empty or missing data and shows an informational
message instead of erroring.

---

## 5. Risk Register Table

The **Top Risk Findings** table renders `risk_register["top_risks"]` via
`st.dataframe`. It displays the available preferred columns: `source`,
`record_id`, `department`, `risk_name`, `risk_category`, `risk_level`,
`severity_score`, `amount_usd`, `days_overdue`, `waiting_days`, and
`recommended_action`. Columns that are not present are skipped gracefully.

---

## 6. KPI Detail Tabs

Four tabs — Invoice, Ticket, Approval, and Executive KPIs — each render the
corresponding KPI dictionary as a simple two-column **Metric | Value**
DataFrame, giving the full numeric breakdown behind the headline cards.

---

## 7. Dataset Preview

An expandable **Dataset Preview** section contains tabs for Invoices, Customer
Tickets, Approval Requests, and Risk Rules, each showing the first 20 rows of the
raw (loaded) dataset for transparency.

---

## 8. Error Handling

The dashboard is designed not to fail silently or crash with raw stack traces:

- Data-loading failures (e.g. missing CSVs) are caught and shown via `st.error`
  with guidance to run the generator script.
- Empty risk DataFrames render informational messages instead of charts/tables.
- Optional columns (`amount_usd`, `waiting_days`, `days_overdue`) and missing
  `resolved_date` values are handled defensively — present columns are used,
  absent ones are skipped.

---

## 9. Why Synthetic Data

The project is a portfolio demonstration. Using synthetic data lets the
dashboard show realistic financial, SLA, and approval scenarios — including
deliberate anomalies — without exposing any real company, customer, vendor,
invoice, or personal information.

---

## 10. Future Improvements

- **AI Executive Summary (Stage 7):** generate a natural-language briefing of the
  KPIs and top risks directly in the dashboard.
- **AI Manager Assistant (Stage 8):** add a conversational panel for ad-hoc
  questions over the metrics and risks.
- **Automation (Stage 9):** trigger n8n workflows (alerts / scheduled reports)
  from the risk findings.
- **Interactivity:** filters by department, date range, and risk level.
