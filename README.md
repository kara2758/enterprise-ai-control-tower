# 🛡️ Enterprise AI Control Tower

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B)
![Pandas](https://img.shields.io/badge/Pandas-data-150458)
![Plotly](https://img.shields.io/badge/Plotly-charts-3F4F75)
![OpenAI](https://img.shields.io/badge/OpenAI-optional-412991)
![n8n](https://img.shields.io/badge/n8n-demo-EA4B71)
![Data](https://img.shields.io/badge/data-synthetic-success)

> AI-powered business process intelligence, risk monitoring, and executive
> decision support — built on synthetic enterprise data.

![Enterprise AI Control Tower Dashboard](screenshots/dashboard_overview.png)

---

## Short Description

**Enterprise AI Control Tower** is a modular, executive-facing decision-support
prototype. It consolidates business signals, computes KPIs, automatically detects
risks, presents everything in a Streamlit dashboard, and uses (optional) AI to
turn the numbers into a management-ready briefing and an interactive assistant —
all on 100% synthetic data.

## Demo Screenshots

> All screenshots use synthetic data only.

**Executive dashboard overview**

![Dashboard overview](screenshots/dashboard_overview.png)

**AI Executive Summary** — a management-ready briefing generated from KPIs and risks

![AI Executive Summary](screenshots/ai_summary.png)

**AI Manager Assistant** — natural-language Q&A over the metrics

![AI Manager Assistant](screenshots/manager_assistant.png)

**Weekly automated report** — generated for the n8n automation demo

![Weekly management report](screenshots/weekly_report.png)

## Executive Summary

Leaders rarely lack data; they lack a single, timely, interpreted view of it.
This project demonstrates how a "control tower" can pull together finance,
support, and approval signals, surface the few items that need attention, and
explain them in plain language. It is delivered as a clean, modular codebase that
runs end-to-end with no external dependencies, and can optionally call the OpenAI
API for richer narratives.

## Business Problem

- **Fragmented data** across finance, operations, support, and approvals.
- **Slow reporting** that arrives after decisions are due.
- **Reactive risk management** — issues (overdue invoices, SLA breaches, stalled
  approvals) are noticed only after they cause damage.
- **Information overload** — raw numbers without a prioritized narrative.

## Project Objective

Build a credible, modular prototype that proves the **core decision-support
loop**: data → KPIs → risk detection → dashboard → AI summary → assistant →
automated reporting, in a way that is clean, reproducible, and presentable as a
portfolio piece.

## Target Users

| User | Needs |
|------|-------|
| **C-Level Executives** (CEO, CFO, COO) | Health overview, top risks, plain-language briefings |
| **Operations & Business Managers** | KPI drill-down, early-warning signals |
| **Business / Data Analysts** | A structured, extensible metrics & risk layer |
| **Digital Transformation / AI teams** | A reference pattern for AI-enabled process intelligence |

## Key Features

- 📊 **Executive KPI dashboard** — financial, support, and approval metrics.
- 🚨 **Automated risk detection** — rule-based, prioritized findings with actions.
- 🧠 **AI Executive Summary** — management-ready briefing (demo or live AI).
- 💬 **AI Manager Assistant** — natural-language Q&A over KPIs and risks.
- 🔄 **Automation demo** — n8n weekly-report workflow + local report generator.
- 🧩 **Modular architecture** — independent, testable engines.

---

## Architecture Overview

A simple, layered, modular design. Data flows one way: raw datasets → processing
engines → presentation and AI layers.

```
            ┌──────────────────────────────────────────────┐
            │              Presentation Layer               │
            │            Streamlit Dashboard (app.py)        │
            └───────▲───────────────▲───────────────▲───────┘
                    │               │               │
        ┌───────────┘     ┌─────────┘     ┌─────────┘
┌───────┴───────┐ ┌───────┴───────┐ ┌─────┴──────────┐
│   AI Layer     │ │  Automation   │ │  (charts/tables)│
│ ai_summary.py  │ │  n8n + weekly │ │                 │
│ assistant.py   │ │  report (demo)│ │                 │
└───────▲───────┘ └───────▲───────┘ └─────────────────┘
        │                 │
┌───────┴─────────────────┴───────┐
│        Processing Layer          │
│  kpi_engine.py / risk_engine.py  │
└───────────────▲─────────────────┘
                │
┌───────────────┴─────────────────┐
│          Data Layer              │
│  data_loader.py  ←→  data/*.csv  │
└──────────────────────────────────┘
```

See [docs/system_architecture.md](docs/system_architecture.md) for detail.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Dashboard / UI | Streamlit |
| Data processing | pandas |
| Visualization | Plotly Express |
| AI / LLM (optional) | OpenAI API |
| Automation (demo) | n8n |
| Configuration | python-dotenv |
| Language | Python 3.10+ |

## System Workflow

1. **Generate** synthetic datasets (`scripts/generate_synthetic_data.py`).
2. **Load & validate** them (`src/data_loader.py`).
3. **Compute KPIs** (`src/kpi_engine.py`).
4. **Detect risks** (`src/risk_engine.py`).
5. **Visualize** in the dashboard (`app.py`).
6. **Summarize with AI** (`src/ai_summary.py`).
7. **Ask the assistant** (`src/assistant.py`).
8. **Automate** weekly reporting (`scripts/generate_weekly_report.py` + n8n).

---

## Datasets

All data is **synthetic**, generated reproducibly (fixed seed + fixed reference
date `2026-06-22`) for the fictional company **ABC Global Services**:

| Dataset | Represents | Records |
|---------|-----------|---------|
| `invoices.csv` | Accounts-payable invoices (spend, overdue, approvals) | 280 |
| `customer_tickets.csv` | Support tickets (SLA, resolution) | 320 |
| `approval_requests.csv` | Approval workflows (bottlenecks) | 200 |
| `risk_rules.csv` | Reference table of risk rules | 6 |

The data intentionally includes anomalies (overdue invoices, SLA breaches,
approval bottlenecks). See [data/dataset_dictionary.md](data/dataset_dictionary.md).

### Data flow & FAQ

```
scripts/generate_synthetic_data.py  →  data/*.csv  →  src/data_loader.py  →  KPI / Risk engines  →  Dashboard
   (reproducible generator,             (invoices,     (loads + validates)
    fixed seed = 42,                      tickets,
    reference date 2026-06-22)            approvals)
```

**Where does the data come from?**
It is 100% **synthetic**, produced by `scripts/generate_synthetic_data.py` for a
fictional company (ABC Global Services). The fixed seed makes it fully
reproducible. No real company, customer, invoice, vendor, employee, or personal
data is used — this is a deliberate choice for a privacy-safe portfolio demo.

**Is there manual data entry?**
No. The dashboard is a read-only decision-support tool. Data is loaded from the
generated CSV files through a single integration module, `src/data_loader.py`.

**How would this work with real data?**
`src/data_loader.py` is the only integration point. In a production version you
would point it at real sources (database, ERP/CRM, or APIs) and the KPI, risk,
AI, and dashboard layers would keep working unchanged. See
[docs/system_architecture.md](docs/system_architecture.md) and
[docs/future_roadmap.md](docs/future_roadmap.md).

## KPI Engine

`src/kpi_engine.py` computes four KPI groups — invoice, ticket, approval, and a
cross-domain executive roll-up (open work items, attention items, financial
exposure, SLA pressure, bottleneck indicators). Aggregation only — no risk
labels. See [docs/kpi_methodology.md](docs/kpi_methodology.md).

## Risk Engine

`src/risk_engine.py` applies clear business rules to individual records and emits
prioritized findings, each with a category, risk level, numeric severity score
(Critical 100 / High 75 / Medium 50 / Low 25), and a recommended action. It
produces a risk summary, top-risks list, and an executive risk register. See
[docs/risk_methodology.md](docs/risk_methodology.md).

## Dashboard

`app.py` (Streamlit) presents executive KPI cards, an AI summary section, the
manager assistant, a risk summary, six Plotly charts, the top-risks table, KPI
detail tabs, and a dataset preview — with defensive error handling throughout.
See [docs/dashboard_design.md](docs/dashboard_design.md).

## AI Executive Summary Module

`src/ai_summary.py` turns KPIs and top risks into a structured briefing
(executive summary, key risks, recommended actions, management questions). It
runs in **demo mode** (deterministic, offline) or **live mode** (OpenAI). Only
aggregated data is sent to the API. See
[docs/ai_summary_design.md](docs/ai_summary_design.md).

## AI Manager Assistant Module

`src/assistant.py` answers management-level questions over the KPI/risk context,
again in demo or live mode, with suggested questions and a safe fallback. See
[docs/assistant_design.md](docs/assistant_design.md).

## n8n Automation Workflow Demo

`workflows/n8n_weekly_risk_report.json` is a safe demo workflow (manual + weekly
schedule) that runs the report generator, reads the report, and prepares an
executive email — but **sends no real email**, uses **placeholder addresses**,
and contains **no real credentials**. See
[docs/automation_workflow_design.md](docs/automation_workflow_design.md).

## Weekly Report Generation

`scripts/generate_weekly_report.py` produces a management-ready Markdown report
(`reports/weekly_management_report.md`) from the KPIs, risk register, and demo AI
summary — fully offline.

---

## Folder Structure

```
enterprise-ai-control-tower/
├── app.py                      # Streamlit dashboard
├── requirements.txt
├── .env.example                # Env var placeholders
├── data/                       # Synthetic datasets + dictionary
├── src/                        # Core modules
│   ├── data_loader.py
│   ├── kpi_engine.py
│   ├── risk_engine.py
│   ├── ai_summary.py
│   └── assistant.py
├── scripts/                    # Generators, tests, automation
│   ├── generate_synthetic_data.py
│   ├── generate_weekly_report.py
│   ├── run_all_tests.py
│   └── test_*.py
├── reports/                    # Generated management reports
├── workflows/                  # n8n workflow demo
├── docs/                       # Project & portfolio documentation
└── screenshots/                # Dashboard screenshots
```

---

## Getting Started

### How to install

```bash
pip install -r requirements.txt
```

### How to generate synthetic data (first run only)

```bash
python scripts/generate_synthetic_data.py
```

### How to run the dashboard

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

### How to generate the weekly report

```bash
python scripts/generate_weekly_report.py
```

Output: `reports/weekly_management_report.md`.

### How to run all tests

```bash
python scripts/run_all_tests.py
```

This runs all seven smoke tests (data loader, KPI, risk, dashboard pipeline, AI
summary, assistant, weekly report). Individual tests can also be run, e.g.:

```bash
python scripts/test_data_loader.py
python scripts/test_kpi_engine.py
python scripts/test_risk_engine.py
python scripts/test_dashboard_imports.py
python scripts/test_ai_summary.py
python scripts/test_assistant.py
python scripts/test_weekly_report.py
```

All tests run offline in demo mode and do **not** require an API key.

---

## Demo Mode vs Live AI Mode

| | Demo Mode | Live AI Mode |
|---|-----------|--------------|
| **Trigger** | Default / no credentials / `force_demo` | `OPENAI_API_KEY` + `OPENAI_MODEL` set |
| **AI call** | None — deterministic | OpenAI API |
| **API key** | Not required | Required |
| **Fallback** | — | Falls back to demo on any error |

To enable live mode, copy `.env.example` to `.env` and fill in:

```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_model_here
```

`.env` is git-ignored.

## Security & Privacy Notes

- **No secrets in code** — API keys are read from the environment only; never
  hardcoded, printed, logged, or returned.
- **No full data sent to AI** — only aggregated KPIs and top-risk records.
- **`.env` is git-ignored**; only `.env.example` (placeholders) is committed.
- **Automation demo sends nothing** — placeholder addresses, no credentials, no
  external calls.
- **Synthetic data only.**

## Limitations

- Synthetic data only; not connected to any real systems.
- No authentication, role management, or database — runs locally.
- The AI assistant is stateless (no multi-turn memory) and grounded only in the
  compact KPI/risk context.
- The n8n workflow is a demonstration structure and may need adjustment in a live
  n8n instance.

## Future Improvements

RAG over uploaded documents, a real database (PostgreSQL/Supabase),
authentication and role-based dashboards, real n8n integration, Power BI export,
cloud deployment, audit logging, and Docker packaging. See
[docs/future_roadmap.md](docs/future_roadmap.md).

---

## Portfolio Disclaimer

> This project uses only synthetic data and is built for portfolio and
> demonstration purposes. It does not contain real company, customer, invoice,
> vendor, employee, or personal data.

> This is a professional prototype, not a production-ready enterprise deployment.
