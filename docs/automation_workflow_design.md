# Automation Workflow Design — Enterprise AI Control Tower

This document describes the Stage 9 automation demo: a local weekly report
generator plus an n8n workflow that would run it on a schedule.

> ⚠️ This is a **portfolio demonstration**. It uses synthetic data, sends no real
> email, calls no real external service, and contains no real credentials.

---

## 1. Purpose of Stage 9

Demonstrate how the Enterprise AI Control Tower could **automate weekly executive
risk reporting** — turning the KPI and risk outputs into a management-ready
report on a recurring schedule and preparing it for delivery, without any manual
effort.

It deliberately stops short of production automation: no real emails, services,
or credentials are involved.

---

## 2. Weekly Report Automation Concept

The scenario: **every week**, a scheduled job generates a fresh executive risk
report and routes it to leadership.

```
(weekly schedule) ──► generate report ──► read report ──► prepare email ──► deliver
                       (demo mode)         (markdown)      (placeholder)     (demo: not sent)
```

In a real deployment, the "deliver" step would email the report to executives;
in this demo it stops at a placeholder so nothing is actually sent.

---

## 3. Local Report Generator

`scripts/generate_weekly_report.py` is the engine the automation invokes. It:

1. Loads data (`load_all_data`).
2. Computes KPIs (`calculate_all_kpis`).
3. Builds the risk register (`create_executive_risk_register`).
4. Generates the AI executive summary in **demo mode**
   (`generate_executive_summary(..., force_demo=True)`).
5. Renders a Markdown report and saves it to
   `reports/weekly_management_report.md`.

The report contains: title, generated timestamp, synthetic-data disclaimer,
executive KPI summary, risk summary, AI executive summary, key risks, recommended
actions, top 10 risk findings, management questions, and a portfolio/demo note.

It runs fully offline and **does not require an OpenAI API key**. The core
`generate_weekly_report()` function is importable, so it can be tested directly
(`scripts/test_weekly_report.py`).

---

## 4. n8n Workflow Structure

`workflows/n8n_weekly_risk_report.json` defines a 7-node demo workflow:

| # | Node | Type | Role |
|---|------|------|------|
| 1 | Manual Trigger | manualTrigger | Run on demand for testing |
| 2 | Schedule Trigger (Weekly) | scheduleTrigger | Run weekly (e.g. Mon 08:00) |
| 3 | Execute Report Generator | executeCommand | `python scripts/generate_weekly_report.py` |
| 4 | Read Report File | readBinaryFile | Read the generated Markdown |
| 5 | Prepare Executive Email (Demo) | set | Assemble placeholder email content |
| 6 | Email Node Placeholder (No Send) | set | Stand-in for a real email node; does not send |
| 7 | Final Note (Demo Only) | set | Explain no real email was sent |

Both triggers (1 and 2) feed the same Execute Command node, so the workflow can be
run manually or on schedule.

---

## 5. Manual Trigger vs Schedule Trigger

- **Manual Trigger** — lets you run the workflow on demand (useful for testing and
  demonstrations).
- **Schedule Trigger** — runs the workflow automatically on a weekly cadence,
  which is the actual automation value: hands-off recurring reporting.

Having both is intentional: the same downstream logic serves interactive testing
and unattended scheduling.

---

## 6. Why No Real Email Is Sent

This is a portfolio project. Sending real email would require real SMTP
credentials and real recipient addresses, which would be inappropriate to commit
and unnecessary for demonstrating the concept. Instead:

- The email content is assembled in a **Set node** with **placeholder addresses**
  (`executive@example.com`, `reports@example.com`).
- A second **Set node** explicitly represents the email step as **not sent**.
- A final note documents that this is a demo.

---

## 7. Security & Privacy Notes

- **No credentials in the workflow JSON.** In a live environment, use n8n's
  credential manager — never hardcode SMTP passwords or API keys.
- **Placeholder addresses only.**
- **No external services are called** in the demo.
- The report generator runs in **demo mode** (no OpenAI API call) and uses only
  **synthetic data**.
- Only the generated report file is read/handled — no raw datasets are emailed.

---

## 8. Future Production Improvements

- Replace the placeholder email node with a real **Email (SMTP)** / **Gmail** node
  using securely-stored credentials.
- Optionally generate the AI summary in **live mode** for richer narratives.
- Attach the report as a file (PDF/Markdown) and/or post it to Slack/Teams.
- Add conditional logic (e.g. only escalate when critical risks exceed a
  threshold).
- Add error handling / retry and run-status notifications.

---

## 9. Compatibility Note

The workflow JSON represents a demo **structure** for portfolio purposes. Because
n8n node type versions change over time, it may require minor adjustment (node
versions or parameter names) when imported into a specific live n8n instance.
