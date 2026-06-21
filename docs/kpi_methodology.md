# KPI Methodology — Enterprise AI Control Tower

This document explains how the KPI engine (`src/kpi_engine.py`) turns the clean
datasets from the data loader into executive-level metrics.

> ⚠️ All KPIs are computed from **synthetic data** generated for the fictional
> company **ABC Global Services**. They are for demonstration only.

> 🔎 **Scope note:** This stage performs **aggregation only**. It deliberately
> does **not** assign risk labels (Low / Medium / High). Rule-based risk
> classification using `risk_rules.csv` is implemented later in **Stage 5 — Risk
> Detection Engine**.

---

## 1. Purpose of the KPI Engine

The KPI engine provides a single, consistent layer of business metrics that
later modules (dashboard, AI summary, manager assistant) can consume without
re-implementing calculations. It answers questions like:

- How much money is tied up in unpaid or pending items?
- How healthy is customer support against its SLAs?
- Where are approvals getting stuck?
- What requires executive attention right now?

All calculations rely on the fixed reference date (`2026-06-22`) already baked
into the synthetic data (via `days_overdue`, `waiting_days`, and SLA status), so
results are fully reproducible.

---

## 2. KPI Categories

The engine produces four KPI groups via `calculate_all_kpis(all_data)`:

| Group | Function | Source dataset |
|-------|----------|----------------|
| Invoice KPIs | `calculate_invoice_kpis` | `invoices` |
| Ticket KPIs | `calculate_ticket_kpis` | `customer_tickets` |
| Approval KPIs | `calculate_approval_kpis` | `approval_requests` |
| Executive KPIs | `calculate_executive_kpis` | roll-up of the three above |

---

## 3. KPI Definitions

### 3.1 Invoice KPIs — accounts-payable health

| KPI | Definition |
|-----|------------|
| `total_invoices` | Count of invoice records. |
| `total_invoice_amount_usd` | Sum of `amount_usd`. |
| `average_invoice_amount_usd` | Mean of `amount_usd`. |
| `paid_invoice_count` | `payment_status == "Paid"`. |
| `unpaid_invoice_count` | `payment_status == "Unpaid"`. |
| `partially_paid_invoice_count` | `payment_status == "Partially Paid"`. |
| `on_hold_invoice_count` | `payment_status == "On Hold"`. |
| `pending_approval_invoice_count` | `approval_status == "Pending"`. |
| `approved_invoice_count` | `approval_status == "Approved"`. |
| `rejected_invoice_count` | `approval_status == "Rejected"`. |
| `under_review_invoice_count` | `approval_status == "Under Review"`. |
| `overdue_invoice_count` | `days_overdue > 0`. |
| `overdue_more_than_7_days_count` | `days_overdue > 7`. |
| `high_value_pending_invoice_count` | `amount_usd > 50000` AND `approval_status == "Pending"`. |

### 3.2 Ticket KPIs — customer support / SLA health

| KPI | Definition |
|-----|------------|
| `total_tickets` | Count of ticket records. |
| `open_ticket_count` | `status == "Open"`. |
| `in_progress_ticket_count` | `status == "In Progress"`. |
| `resolved_ticket_count` | `status == "Resolved"`. |
| `escalated_ticket_count` | `status == "Escalated"`. |
| `waiting_for_customer_count` | `status == "Waiting for Customer"`. |
| `critical_ticket_count` | `priority == "Critical"`. |
| `high_priority_ticket_count` | `priority == "High"`. |
| `sla_within_count` | `sla_status == "Within SLA"`. |
| `sla_at_risk_count` | `sla_status == "At Risk"`. |
| `sla_breached_count` | `sla_status == "Breached"`. |
| `average_response_time_hours` | Mean of `response_time_hours` (missing ignored). |
| `average_resolution_time_hours` | Mean of `resolution_time_hours` (missing ignored). |
| `unresolved_ticket_count` | Records where `resolved_date` is missing / `NaT`. |

### 3.3 Approval KPIs — approval-workflow health

| KPI | Definition |
|-----|------------|
| `total_approval_requests` | Count of approval records. |
| `pending_approval_requests` | `approval_status == "Pending"`. |
| `approved_approval_requests` | `approval_status == "Approved"`. |
| `rejected_approval_requests` | `approval_status == "Rejected"`. |
| `escalated_approval_requests` | `approval_status == "Escalated"`. |
| `bottleneck_count` | `bottleneck_flag == True`. |
| `critical_business_impact_count` | `business_impact == "Critical"`. |
| `critical_pending_count` | `business_impact == "Critical"` AND `approval_status == "Pending"`. |
| `average_waiting_days` | Mean of `waiting_days` across all requests. |
| `average_waiting_days_pending` | Mean of `waiting_days` for Pending or Escalated requests. |
| `total_pending_amount_usd` | Sum of `amount_usd` for Pending or Escalated requests. |

### 3.4 Executive KPIs — cross-domain roll-up

| KPI | Definition |
|-----|------------|
| `total_open_work_items` | Unresolved tickets + pending-approval invoices + pending/escalated approval requests. |
| `total_attention_items` | `overdue_more_than_7_days_count` + `high_value_pending_invoice_count` + `sla_at_risk_count` + `sla_breached_count` + `bottleneck_count` + `critical_pending_count`. |
| `total_financial_exposure_usd` | Sum of unpaid / partially-paid / on-hold invoice amounts + `total_pending_amount_usd`. |
| `operational_delay_indicators` | `overdue_more_than_7_days_count` + `sla_breached_count` + `bottleneck_count`. |
| `process_bottleneck_indicators` | `bottleneck_count` + `pending_approval_requests` + `escalated_approval_requests`. |
| `customer_sla_pressure_count` | `sla_at_risk_count` + `sla_breached_count`. |

---

## 4. Business Meaning of Each KPI Group

- **Invoice KPIs** show financial discipline: how much is owed, how much is
  overdue, and whether large invoices are stuck awaiting approval.
- **Ticket KPIs** show service quality: SLA adherence, escalations, and how fast
  the support organization responds and resolves issues.
- **Approval KPIs** show process efficiency: where decisions stall, how long
  requests wait, and how much value is held up in the approval pipeline.
- **Executive KPIs** give leadership a consolidated "single pane of glass":
  total open work, items needing attention, financial exposure, and indicators
  of operational delay, process bottlenecks, and customer SLA pressure.

---

## 5. Implementation Notes

- A helper, `_safe_mean(series)`, returns `0` when a series is empty or contains
  no valid numeric values, so averages never produce `NaN`.
- Monetary and time averages are rounded to 2 decimal places.
- No row counts are hardcoded; every metric is computed from the data.
- The engine does not modify the input DataFrames.

---

## 6. What Comes Next

Stage 5 will introduce the **Risk Detection Engine**, which applies the rules in
`risk_rules.csv` to these KPIs and the underlying records to produce prioritized
risk findings (e.g. severity levels and recommended actions). That risk
classification is intentionally **not** part of the KPI engine.
