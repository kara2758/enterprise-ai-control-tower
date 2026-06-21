# Data

This folder holds the **synthetic business datasets** used by the Enterprise AI
Control Tower for the fictional company **ABC Global Services**.

> ⚠️ All data in this folder is **synthetic** and generated for demonstration
> purposes only. It does not contain real company, customer, invoice, vendor, or
> personal data.

## Status

✅ **Stage 2 complete** — synthetic datasets have been generated.

## Contents

| File | Description | Records |
|------|-------------|---------|
| `invoices.csv` | Accounts-payable invoices (spend, overdue, approvals) | 280 |
| `customer_tickets.csv` | Customer support tickets (SLA, resolution) | 320 |
| `approval_requests.csv` | Approval-workflow requests (bottlenecks) | 200 |
| `risk_rules.csv` | Reference table of risk rules | 6 |
| `dataset_dictionary.md` | Full documentation of every dataset and column | — |

> Record counts assume the default generator settings. Re-running the generator
> reproduces identical files (fixed random seed).

## How the data is generated

All datasets are produced by a single reproducible script:

```bash
python scripts/generate_synthetic_data.py
```

- **Fixed random seed** (`42`) → identical output every run.
- **Fixed reference date** (`2026-06-22`) → consistent `days_overdue`,
  `waiting_days`, and SLA-status calculations.
- Uses only `pandas` and the Python standard library; no external API calls.

The data intentionally includes **anomalies** (overdue invoices, high-value
pending invoices, breached and at-risk SLAs, approval bottlenecks) so that the
KPI and risk modules built in later stages have meaningful signals to detect.

## Documentation

See [dataset_dictionary.md](dataset_dictionary.md) for a complete description of
each dataset, its columns, example business uses, and synthetic-data notes.
