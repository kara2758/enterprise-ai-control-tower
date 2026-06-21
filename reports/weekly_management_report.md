# Weekly Executive Risk Report

_Generated: 2026-06-22 01:45:05_

> This report uses only synthetic data and is built for portfolio and demonstration purposes. It does not contain real company, customer, invoice, vendor, or personal data.

## Executive KPI Summary

| Metric | Value |
| --- | --- |
| total_open_work_items | 340 |
| total_attention_items | 392 |
| total_financial_exposure_usd | 18000640.98 |
| operational_delay_indicators | 340 |
| process_bottleneck_indicators | 152 |
| customer_sla_pressure_count | 182 |

## Risk Summary

| Metric | Value |
| --- | --- |
| total_risk_findings | 480 |
| critical_risk_count | 7 |
| high_risk_count | 396 |
| medium_risk_count | 77 |
| low_risk_count | 0 |
| average_severity_score | 71.35 |
| highest_severity_score | 100 |
| top_risk_category | Customer SLA |
| top_risk_department | HR |
| financial_exposure_from_risks_usd | 21598550.1 |

## AI Executive Summary

_Mode: demo_

The control tower currently tracks 340 open work items, with 392 items requiring management attention. Total financial exposure stands at $18,000,641, driven mainly by unpaid/on-hold invoices and pending approvals. Risk detection produced 480 findings (7 critical, 396 high), concentrated in 'Customer SLA' and most frequently in the HR department. Customer SLA pressure (182 tickets) and approval bottlenecks (70) are the leading operational concerns.

## Key Risks

- 7 critical risk finding(s) require immediate management decisions.
- 117 invoices overdue by more than 7 days and 16 high-value invoices still pending approval.
- 153 customer tickets have breached SLA, with 29 more at risk.
- 70 approval requests are bottlenecked (avg wait 21.16 days), holding $8,113,748 in pending value.

## Recommended Actions

- Convene a rapid review of all critical-impact pending approvals and assign decision owners today.
- Prioritize payment/approval of overdue and high-value pending invoices to reduce financial exposure.
- Escalate SLA-breached tickets to the escalations team and triage at-risk tickets before deadlines.
- Address approval bottlenecks by rebalancing approver workload and setting clear turnaround targets.

## Top 10 Risk Findings

| source | record_id | department | risk_name | risk_category | risk_level | severity_score | amount_usd | days_overdue | waiting_days | recommended_action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| approval_requests | REQ-30196 | HR | Critical Pending Request | Critical Business Impact | Critical | 100 | 199600.14 |  | 17.0 | Prioritize immediate management decision. |
| approval_requests | REQ-30109 | Customer Support | Critical Pending Request | Critical Business Impact | Critical | 100 | 173821.71 |  | 30.0 | Prioritize immediate management decision. |
| approval_requests | REQ-30190 | IT | Critical Pending Request | Critical Business Impact | Critical | 100 | 96917.76 |  | 20.0 | Prioritize immediate management decision. |
| approval_requests | REQ-30139 | Customer Support | Critical Pending Request | Critical Business Impact | Critical | 100 | 91813.7 |  | 9.0 | Prioritize immediate management decision. |
| approval_requests | REQ-30016 | Procurement | Critical Pending Request | Critical Business Impact | Critical | 100 | 44817.7 |  | 3.0 | Prioritize immediate management decision. |
| approval_requests | REQ-30200 | Finance | Critical Pending Request | Critical Business Impact | Critical | 100 | 26104.96 |  | 23.0 | Prioritize immediate management decision. |
| approval_requests | REQ-30097 | HR | Critical Pending Request | Critical Business Impact | Critical | 100 | 1658.17 |  | 40.0 | Prioritize immediate management decision. |
| invoices | INV-10204 | HR | Overdue Invoice (> 7 days) | Financial Delay | High | 75 | 272518.25 | 30.0 |  | Escalate overdue invoice review and confirm payment plan. |
| invoices | INV-10204 | HR | High-Value Pending Invoice | Financial Exposure | High | 75 | 272518.25 | 30.0 |  | Prioritize approval review for high-value pending invoice. |
| invoices | INV-10184 | Customer Support | Overdue Invoice (> 7 days) | Financial Delay | High | 75 | 248696.69 | 13.0 |  | Escalate overdue invoice review and confirm payment plan. |

## Management Questions

- Which critical pending approvals can be decided within the next 24 hours?
- What is the root cause of the recurring SLA breaches in the top-risk department?
- Are current approver capacity and thresholds appropriate for the volume of high-value requests?

---

_Portfolio/demo note: this report was generated automatically by `scripts/generate_weekly_report.py` in demo mode (no AI API, no email sent). It is intended to demonstrate automated weekly executive reporting via n8n._
