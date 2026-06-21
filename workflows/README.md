# Workflows

This folder holds the **n8n automation workflow demo** for the Enterprise AI
Control Tower.

> ⚠️ This is a **portfolio demonstration**. The workflow uses synthetic data,
> sends **no real email**, calls **no real external service**, and contains
> **no real credentials** — only placeholders.

## Status

✅ **Stage 9 complete** — a demo workflow is provided.

## Contents

| File | Description |
|------|-------------|
| `n8n_weekly_risk_report.json` | Demo n8n workflow: weekly executive risk report |

## Workflow purpose

Demonstrate how the Enterprise AI Control Tower could **automate weekly executive
risk reporting**: on a weekly schedule, generate a management-ready report from
KPI and risk outputs, then prepare it for delivery to executives.

## Node sequence

```
Manual Trigger ─┐
                ├─► Execute Report Generator ─► Read Report File ─►
Schedule ───────┘     (python scripts/             (reads
Trigger (Weekly)       generate_weekly_report.py)    reports/weekly_management_report.md)

   ─► Prepare Executive Email (Demo) ─► Email Node Placeholder (No Send) ─► Final Note (Demo Only)
        (Set node: placeholder            (Set node: explicitly does          (Set node: explains this
         to/from/subject/body)             NOT send anything)                  is a demo, no email sent)
```

1. **Manual Trigger** — run on demand for testing.
2. **Schedule Trigger (Weekly)** — runs automatically once a week (e.g. Monday 08:00).
3. **Execute Report Generator** — runs `python scripts/generate_weekly_report.py`
   (demo mode, offline).
4. **Read Report File** — reads the generated `reports/weekly_management_report.md`.
5. **Prepare Executive Email (Demo)** — a Set node that assembles placeholder
   email content (placeholder addresses only).
6. **Email Node Placeholder (No Send)** — a Set node standing in for a real
   email/SMTP node; it intentionally does **not** send.
7. **Final Note (Demo Only)** — a Set node explaining no real email was sent.

## How it would work in a real n8n environment

1. Import `n8n_weekly_risk_report.json` into n8n.
2. Ensure the project is available on the n8n host so the **Execute Command** node
   can run the Python generator (correct working directory / Python environment).
3. Replace the **Email Node Placeholder** with a real **Email (SMTP)** or
   **Gmail** node, configured with your own credentials stored in n8n's
   credential manager.
4. Replace the placeholder addresses with real recipients.
5. Activate the workflow to enable the weekly schedule.

> **Compatibility note:** this JSON represents a demo workflow **structure**
> intended for portfolio demonstration. n8n node type versions evolve, so it may
> require minor adjustment (node versions, parameter names) when imported into a
> specific live n8n instance.

## Security notes

- **No real credentials** are included — never commit SMTP passwords or API keys
  to the workflow JSON. Use n8n's built-in credential manager instead.
- **Placeholder addresses only:** `executive@example.com`, `reports@example.com`.
- **No external services are called** in this demo; the email step is a Set-node
  placeholder that does not send.
- Reports are generated from **synthetic data** only.
