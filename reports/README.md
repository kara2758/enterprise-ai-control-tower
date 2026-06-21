# Reports

This folder holds **generated management reports** for the Enterprise AI Control
Tower.

> ⚠️ All reports are generated from **synthetic data** for the fictional company
> **ABC Global Services**. They are for portfolio and demonstration purposes
> only and contain no real company, customer, invoice, vendor, or personal data.

## Contents

| File | Description |
|------|-------------|
| `weekly_management_report.md` | Weekly executive risk report (auto-generated) |

The report bundles the executive KPIs, risk summary, the demo-mode AI executive
summary, key risks, recommended actions, the top 10 risk findings, and
management questions into a single management-ready document.

## How to regenerate the weekly report

```bash
python scripts/generate_weekly_report.py
```

This runs entirely offline in **demo mode** (no OpenAI API required) and
overwrites `weekly_management_report.md` with a fresh report.

To verify generation:

```bash
python scripts/test_weekly_report.py
```

## Automation

This report is the artifact produced by the Stage 9 **n8n automation demo**
(`workflows/n8n_weekly_risk_report.json`), which would run the generator on a
weekly schedule and prepare it for delivery to executives. See
[../docs/automation_workflow_design.md](../docs/automation_workflow_design.md)
for details. No real emails are sent in the demo.
