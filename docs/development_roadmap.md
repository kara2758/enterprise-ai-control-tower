# Development Roadmap — Enterprise AI Control Tower

This project is built **incrementally**. Each stage delivers one module or
artifact that is developed and validated independently, then integrated into the
overall control tower. This roadmap runs from the initial scaffold through the
final LinkedIn case study.

---

## Stage 1 — Project Scaffold & Documentation ✅ *(completed)*

**Goal:** Establish a clean, professional repository ready for step-by-step
development.

- Folder structure (`src/`, `data/`, `docs/`, `screenshots/`, `workflows/`).
- Root files: `README.md`, `requirements.txt`, `.gitignore`, `.env.example`.
- Placeholder `app.py` (Streamlit) and placeholder `src/` modules.
- Core documentation: project brief, business requirements, architecture,
  roadmap.

**Deliverable:** Documented scaffold with no business logic yet.

---

## Stage 2 — Synthetic Business Datasets ✅ *(completed)*

**Goal:** Generate realistic, synthetic data for ABC Global Services.

- Create CSV datasets (revenue, expenses, customers, operations).
- Ensure data has trends and anomalies suitable for KPIs and risk detection.
- Document dataset schemas in `data/README.md`.

**Deliverable:** Synthetic datasets in `data/`.

---

## Stage 3 — Data Loader Module ✅ *(completed)*

**Goal:** Reliably load and validate datasets.

- Implement `src/data_loader.py` with a `DataLoadingError` exception and
  per-dataset loaders (`load_invoices`, `load_customer_tickets`,
  `load_approval_requests`, `load_risk_rules`, `load_all_data`).
- Load CSVs into pandas DataFrames with column validation and date/numeric/
  boolean type conversion.
- Provide clean accessors for downstream engines.
- Add `scripts/test_data_loader.py` as a smoke check.

**Deliverable:** Working data loading layer.

---

## Stage 4 — KPI Engine ✅ *(completed)*

**Goal:** Compute core business KPIs.

- Implement `src/kpi_engine.py` with invoice, ticket, approval, and executive
  KPI functions plus `calculate_all_kpis`.
- Aggregation only — no risk labels (those are Stage 5).
- Return structured KPI results for the dashboard and AI layers.
- Add `scripts/test_kpi_engine.py` and `docs/kpi_methodology.md`.

**Deliverable:** KPI computation module.

---

## Stage 5 — Risk Detection Engine ✅ *(completed)*

**Goal:** Detect and prioritize business risks.

- Implement `src/risk_engine.py` with per-source detectors, a combined
  `all_risks` view, risk summary, top risks, and an executive risk register.
- Apply rule-based checks to records; assign risk level + severity score.
- Rank risks by severity (and amount / delay where available).
- Add `scripts/test_risk_engine.py` and `docs/risk_methodology.md`.

**Deliverable:** Risk detection module.

---

## Stage 6 — Streamlit Executive Dashboard ✅ *(completed)*

**Goal:** Visualize KPIs and risks in an executive-friendly UI.

- Build out `app.py` with Streamlit + Plotly (cached data, modular section
  renderers, defensive error handling).
- Display executive KPI cards, risk summary, six charts, the top-risks table,
  KPI detail tabs, and a dataset preview.
- Add `scripts/test_dashboard_imports.py` and `docs/dashboard_design.md`.
- (Optional) Capture screenshots into `screenshots/`.

**Deliverable:** Functional MVP dashboard.

---

## Stage 7 — AI Executive Summary Module ✅ *(completed)*

**Goal:** Generate plain-language executive briefings.

- Implement `src/ai_summary.py` with demo mode (deterministic, offline) and live
  mode (OpenAI), plus a safe fallback.
- Send only aggregated KPIs and top-risk records to the API — never full data.
- Surface the summary in the dashboard via a button (demo-mode checkbox).
- Add `scripts/test_ai_summary.py` and `docs/ai_summary_design.md`; add `openai`
  to requirements and `OPENAI_MODEL` to `.env.example`.

**Deliverable:** AI executive summary feature.

---

## Stage 8 — AI Manager Assistant ✅ *(completed)*

**Goal:** Enable conversational Q&A over business metrics.

- Implement `src/assistant.py` with demo mode (keyword-routed, deterministic),
  live mode (OpenAI), and a safe fallback.
- Answer natural-language questions grounded in compact KPI/risk context only.
- Integrate a Q&A panel (suggested questions + free text) into the dashboard.
- Add `scripts/test_assistant.py` and `docs/assistant_design.md`.

**Deliverable:** AI manager assistant feature.

---

## Stage 9 — n8n Automation Workflow Demo ✅ *(completed)*

**Goal:** Demonstrate automated alerting and reporting.

- Add `scripts/generate_weekly_report.py` (demo-mode weekly report → `reports/`).
- Export a safe demo workflow `workflows/n8n_weekly_risk_report.json` (manual +
  weekly schedule, no real email/credentials).
- Add `scripts/test_weekly_report.py`, `reports/README.md`, and
  `docs/automation_workflow_design.md`; update `workflows/README.md`.

**Deliverable:** Automation demo.

---

## Stage 10 — GitHub README & LinkedIn Case Study ✅ *(completed)*

**Goal:** Package the project for presentation.

- Rewrite the README as a professional portfolio case study (with badges).
- Write the LinkedIn case study, English + Turkish posts, a demo-video script,
  and a one-page executive summary.
- Add a GitHub release checklist, a future roadmap, screenshot guidance, and a
  combined test runner (`scripts/run_all_tests.py`).
- Run a final safety review (no secrets / real data committed).

**Deliverable:** Portfolio-ready project and case study.

---

## Final Status

✅ **MVP completed:** data → KPIs → risk → dashboard → AI summary → assistant →
automation demo → portfolio packaging.

All ten stages are complete. The project runs end-to-end on synthetic data, with
optional AI, a safe automation demo, full documentation, and a combined test
suite — packaged as a professional portfolio prototype (not a production
deployment).

---

## Guiding Principles

- **One module at a time** — no big-bang builds.
- **Integrate after validating** each module independently.
- **Synthetic data only** — no real company or personal data.
- **No hardcoded secrets** — configuration via `.env`.
