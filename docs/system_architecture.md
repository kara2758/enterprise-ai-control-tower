# System Architecture — Enterprise AI Control Tower

## 1. Overview

The Enterprise AI Control Tower uses a **simple, modular, layered
architecture**. Each layer has a clear responsibility, and each engine is an
independent module that can be developed and tested on its own before
integration. Data flows in one direction: from raw datasets, through processing
engines, to the dashboard and AI layers.

## 2. Architecture Diagram (conceptual)

```
            ┌──────────────────────────────────────────────┐
            │              Presentation Layer               │
            │            Streamlit Dashboard (app.py)        │
            └───────────────▲───────────────▲───────────────┘
                            │               │
        ┌───────────────────┘               └───────────────────┐
        │                                                        │
┌───────┴────────┐                                     ┌─────────┴────────┐
│   AI Layer      │                                     │  Automation Layer │
│  ai_summary.py  │                                     │   n8n workflows   │
│  assistant.py   │                                     │   (workflows/)    │
└───────▲────────┘                                     └─────────▲────────┘
        │                                                        │
        └───────────────────┬────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │        Processing Layer        │
            │   kpi_engine.py / risk_engine  │
            └───────────────▲───────────────┘
                            │
            ┌───────────────┴───────────────┐
            │          Data Layer            │
            │  data_loader.py  ←→  data/*.csv │
            └────────────────────────────────┘
```

## 3. Layers & Responsibilities

### 3.1 Data Layer
- **Module:** `src/data_loader.py`
- **Source:** synthetic CSV files in `data/`
- **Responsibility:** load datasets, validate structure, and provide clean
  pandas DataFrames to the rest of the system.

### 3.2 Processing Layer
- **Modules:** `src/kpi_engine.py`, `src/risk_engine.py`
- **Responsibility:**
  - `kpi_engine` computes business KPIs from loaded data.
  - `risk_engine` evaluates KPIs and data against rules (and later AI checks) to
    detect and prioritize risks.

### 3.3 AI Layer
- **Modules:** `src/ai_summary.py`, `src/assistant.py`
- **Responsibility:**
  - `ai_summary` turns KPIs and risks into a plain-language executive briefing.
  - `assistant` answers manager questions grounded in the metrics.
- **External dependency:** OpenAI API (key via environment variable).

### 3.4 Presentation Layer
- **Module:** `app.py` (Streamlit)
- **Responsibility:** display KPIs, charts (Plotly), risk alerts, and AI output
  in an executive-friendly interface.

### 3.5 Automation Layer
- **Location:** `workflows/` (n8n)
- **Responsibility:** demonstrate automated alerting and scheduled reporting
  triggered by the system's outputs.

## 4. Data Flow

1. `data_loader` reads synthetic CSVs and returns validated DataFrames.
2. `kpi_engine` computes KPIs from those DataFrames.
3. `risk_engine` evaluates KPIs/data and produces ranked risk flags.
4. `ai_summary` / `assistant` generate narratives and answers from the results.
5. `app.py` renders everything for the user.
6. `n8n` workflows consume outputs to send alerts/reports (demo).

## 5. Design Principles

- **Separation of concerns** — one responsibility per module.
- **Loose coupling** — modules communicate through simple data structures.
- **Incremental build** — modules are added one stage at a time.
- **Security by default** — no hardcoded secrets; config via `.env`.
- **Synthetic-only data** — no real or sensitive information.

## 6. Configuration

- Environment variables are defined in `.env` (see `.env.example`).
- `python-dotenv` loads configuration at runtime.
- Secrets (e.g. `OPENAI_API_KEY`) are never committed to version control.
