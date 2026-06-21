# Future Roadmap — Enterprise AI Control Tower

The current project is a complete portfolio prototype (Stages 1–10). This
document outlines how it could evolve toward a more production-oriented system.
These are **potential directions**, not commitments or claims of existing
functionality.

---

## Data & Storage

- **PostgreSQL / Supabase database** — replace flat CSV files with a real
  database for persistence, concurrency, and larger datasets.
- **Audit logging** — record who viewed what and when, and track data/version
  lineage.

## AI Capabilities

- **RAG over uploaded documents** — let users upload policies, contracts, or
  reports and ground the assistant's answers in them (retrieval-augmented
  generation).
- **Richer live summaries** — multi-section narratives, trend commentary, and
  scenario comparisons.
- **Multi-turn assistant** — conversational memory across questions.

## Security & Access

- **User authentication** — sign-in and session management.
- **Role-based dashboards** — tailor views and permissions to CEO / CFO / COO /
  analyst roles.

## Automation & Integration

- **Real n8n integration** — replace the demo email node with a configured
  Email/SMTP or Gmail node using securely-stored credentials; add alerting and
  conditional escalation.
- **Notifications** — Slack / Teams delivery of summaries and alerts.

## Reporting & BI

- **Power BI export** — publish KPIs and risk findings to Power BI for enterprise
  reporting.
- **Scheduled multi-format reports** — PDF / Markdown / email digests.

## Deployment & Operations

- **Cloud deployment** — host the dashboard (e.g. Streamlit Community Cloud or a
  container platform).
- **Docker packaging** — containerize the app and its dependencies for portable,
  reproducible deployment.
- **CI/CD** — automated testing and deployment pipelines.

---

> All future work would maintain the project's current principles: clear
> separation of concerns, privacy-conscious AI usage, and no exposure of secrets.
> Any move beyond synthetic data would require appropriate data governance,
> security review, and is out of scope for this portfolio prototype.
