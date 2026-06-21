# Risk Methodology — Enterprise AI Control Tower

This document explains how the risk engine (`src/risk_engine.py`) turns the clean
datasets into prioritized, record-level risk findings.

> ⚠️ All risk findings are derived from **synthetic data** generated for the
> fictional company **ABC Global Services**. They are for demonstration only.

> 🤖 **Scope note:** This stage produces deterministic, rule-based findings only.
> AI-generated risk explanations and executive narratives arrive later in
> **Stage 7 — AI Executive Summary**.

---

## 1. Purpose of the Risk Engine

The KPI engine (Stage 4) answers *"what are the aggregate numbers?"* The risk
engine answers *"which specific records need attention, and why?"*

It applies clear business rules to individual records and emits one finding per
triggered rule, each carrying a risk name, category, level, numeric severity
score, and a recommended action. These findings feed the future dashboard and
executive summary.

---

## 2. KPI Calculations vs. Risk Detection

| | KPI Engine (Stage 4) | Risk Engine (Stage 5) |
|---|----------------------|------------------------|
| **Granularity** | Aggregated metrics | Record-level findings |
| **Output** | Dictionaries of numbers | DataFrames of rows |
| **Question** | "How are we doing overall?" | "Which items are risky?" |
| **Example** | `sla_breached_count = 153` | One row per breached ticket, with action |
| **Labels** | None | Risk level + severity score |

The two are complementary: KPIs give the headline numbers; risk findings give
the actionable detail behind them.

---

## 3. Risk Categories

Each rule maps a record to a **risk category** describing the type of business
risk:

| Source | Risk Name | Risk Category |
|--------|-----------|---------------|
| invoices | Overdue Invoice (> 7 days) | Financial Delay |
| invoices | High-Value Pending Invoice | Financial Exposure |
| invoices | Invoice On Hold | Payment Hold |
| customer_tickets | SLA Breached | Customer SLA |
| customer_tickets | Ticket At Risk | Customer SLA Pressure |
| customer_tickets | Critical Open Ticket | Customer Impact |
| approval_requests | Approval Bottleneck | Process Bottleneck |
| approval_requests | Critical Pending Request | Critical Business Impact |
| approval_requests | Escalated Approval Request | Approval Escalation |

A single record can produce multiple findings if it triggers more than one rule
(e.g. an invoice can be both overdue and on hold).

---

## 4. Risk Levels and Severity Scores

Every finding is assigned a qualitative **risk level** and a matching numeric
**severity score**, enabling consistent sorting and roll-ups:

| Risk Level | Severity Score |
|------------|----------------|
| Critical | 100 |
| High | 75 |
| Medium | 50 |
| Low | 25 |

The numeric score lets the engine rank findings across all sources on one scale
and compute an average severity for the register.

---

## 5. Record-Level Risk Output Design

Each detector returns a DataFrame whose rows are individual findings. All
findings share a common core:

- `source` — which dataset the finding came from
- `record_id` — the originating record's id (invoice / ticket / request)
- `department` — owning department
- `risk_name`, `risk_category`, `risk_level`, `severity_score`
- `recommended_action`

Source-specific detectors also include contextual columns (e.g. `amount_usd`,
`days_overdue`, `priority`, `sla_status`, `waiting_days`, `business_impact`).

### Combined view (`all_risks`)
`detect_all_risks` concatenates every finding into one DataFrame, sorted by
`severity_score` descending (stable sort preserves invoice → ticket → approval
order for ties). The combined view keeps the common columns plus the optional
metric columns `amount_usd`, `days_overdue`, and `waiting_days` (NaN where a
source doesn't have them) so that:

- `calculate_risk_summary` can compute `financial_exposure_from_risks_usd`,
  safely ignoring missing amounts.
- `get_top_risks` can tie-break by amount and delay where those values exist.

### Risk summary
`calculate_risk_summary` reports totals, counts per level, average and highest
severity, the most common risk category and department, and the total financial
exposure across findings that carry an amount.

### Executive risk register
`create_executive_risk_register` bundles the summary, the top risks, the
per-source frames, and the combined `all_risks` frame into a single dictionary.

---

## 6. How Risk Findings Support the Dashboard

In later stages these outputs power:

- **Executive KPIs panel** — summary counts and severity at a glance.
- **Top risks table** — the highest-priority items needing action.
- **Drill-downs** — filter findings by source, category, level, or department.
- **AI executive summary (Stage 7)** — natural-language narratives built on top
  of this structured register.

Because findings are plain DataFrames and dictionaries, no visualization or AI
logic is embedded here — those layers consume this output without re-computing
it.

---

## 7. Notes

- All names and values are **synthetic**; no real company, customer, vendor,
  invoice, or personal data is used.
- Detection is fully deterministic and reproducible given the fixed synthetic
  datasets.
- No external API is called at this stage.
