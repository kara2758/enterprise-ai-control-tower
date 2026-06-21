# Business Requirements — ABC Global Services

> These requirements are written for a **fictional company, ABC Global
> Services**, used to give the Enterprise AI Control Tower a realistic context.
> All associated data is synthetic.

## 1. Company Context

**ABC Global Services** is a mid-sized B2B professional services company
(~1,200 employees) operating across multiple regions. It delivers consulting and
managed-services contracts to enterprise clients. Leadership wants better,
faster visibility into financial health, operational performance, and client
risk.

### Key business areas
- **Finance** — revenue, expenses, margins, cash flow.
- **Sales & Accounts** — pipeline, new contracts, client retention.
- **Operations / Delivery** — utilization, SLA adherence, delivery quality.
- **People** — headcount and attrition (high-level only).

## 2. Stakeholders

| Stakeholder | Primary interest |
|-------------|------------------|
| CEO | Overall company health, top risks |
| CFO | Revenue, margin, cash flow, cost control |
| COO | Operational performance, SLA adherence, utilization |
| Account Directors | Client retention and churn risk |
| Analysts | Reliable metrics layer to explore and extend |

## 3. High-Level Business Requirements

### BR-1 — Unified Performance View
Leadership must see core company KPIs (revenue, expenses, profit margin, growth,
client churn, SLA adherence) in **one consolidated dashboard**.

### BR-2 — Trend Visibility
Users must be able to see **how key metrics change over time** to distinguish
one-off blips from sustained trends.

### BR-3 — Early Risk Detection
The system must **automatically flag emerging risks** — e.g. declining margin,
rising churn, cash flow pressure, repeated SLA breaches — without manual review.

### BR-4 — Risk Prioritization
Detected risks must be **ranked by severity** so leaders focus on what matters
most first.

### BR-5 — Plain-Language Executive Summary
The system must produce an **AI-generated narrative** summarizing current
performance and key risks in clear, non-technical language.

### BR-6 — Conversational Insight Access
Managers must be able to **ask questions in natural language** (e.g. "Why did
margin drop last quarter?") and receive grounded answers.

### BR-7 — Automated Alerting (Demo)
The system should demonstrate **automated notifications/reports** (via n8n) when
critical thresholds are crossed.

### BR-8 — Data Integrity & Privacy
The system must operate on **synthetic data only** and must **never expose
secrets** (API keys handled via environment variables).

## 4. Non-Functional Requirements

- **Usability** — clear, executive-friendly UI requiring no training.
- **Modularity** — each engine (data, KPI, risk, AI) is independent.
- **Extensibility** — new metrics, risks, and data sources can be added easily.
- **Transparency** — KPI and risk logic is understandable and auditable.
- **Portability** — runs locally with minimal setup.

## 5. Assumptions & Constraints

- Data is provided as flat files (CSV) generated synthetically.
- AI features require an OpenAI API key supplied by the user via `.env`.
- The project prioritizes clarity and demonstration value over production scale.
